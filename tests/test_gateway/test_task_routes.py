"""Tests for Task and Gate REST endpoints in LoopDesk Gateway."""

from __future__ import annotations

from pathlib import Path
import pytest
from starlette.testclient import TestClient

from loopdesk.gateway.app import create_gateway_app
from loopdesk.gateway.config import GatewayConfig
from loopdesk.loop_workspace.schema import LoopWorkspaceStatus
from loopdesk.loop_workspace.service import LoopWorkspaceService


@pytest.fixture
def test_client(tmp_path: Path):
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized(intent="Test Task Workspace")
    
    config = GatewayConfig()
    app = create_gateway_app(config=config)
    return TestClient(app)


def test_get_tasks_endpoint(test_client: TestClient, tmp_path: Path):
    response = test_client.get(f"/api/v1/projects/default/tasks?root={tmp_path}")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert isinstance(data["tasks"], list)


def test_create_task_endpoint(test_client: TestClient, tmp_path: Path):
    payload = {
        "title": "Fix issue #102 serialization",
        "template": "issue-fix",
        "root": str(tmp_path),
        "intent": "Resolve empty bytes bug",
    }
    response = test_client.post("/api/v1/projects/default/tasks", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "task" in data
    assert data["task"]["title"] == "Fix issue #102 serialization"


def test_gate_decision_endpoint(test_client: TestClient, tmp_path: Path):
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()
    item = service.record_work_item("task-123", "loop", "Test Gate Task", status=LoopWorkspaceStatus.BLOCKED.value)
    
    decision_payload = {
        "decision": "approved",
        "comment": "LGTM, verified tests pass",
        "root": str(tmp_path),
    }
    response = test_client.post("/api/v1/tasks/task-123/gate/decision", json=decision_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["status"] in ["completed", "approved", "active"]


def test_create_task_keeps_both_tasks(test_client: TestClient, tmp_path: Path):
    """`current_work_id` is a cursor, so a second create must not eat the first."""
    first = test_client.post(
        "/api/v1/projects/default/tasks", json={"title": "A", "root": str(tmp_path)}
    ).json()["task"]["id"]
    second = test_client.post(
        "/api/v1/projects/default/tasks", json={"title": "B", "root": str(tmp_path)}
    ).json()["task"]["id"]

    ids = [t["id"] for t in test_client.get(f"/api/v1/projects/default/tasks?root={tmp_path}").json()["tasks"]]
    assert first in ids and second in ids


def test_patch_task_moves_status(test_client: TestClient, tmp_path: Path):
    task_id = test_client.post(
        "/api/v1/projects/default/tasks", json={"title": "A", "root": str(tmp_path)}
    ).json()["task"]["id"]

    response = test_client.patch(
        f"/api/v1/tasks/{task_id}", json={"status": "in_review", "root": str(tmp_path)}
    )
    assert response.status_code == 200
    task = response.json()["task"]
    assert task["status"] == "in_review"
    assert task["gate_status"] == "pending"
    assert task["title"] == "A"


def test_patch_only_touches_supplied_fields(test_client: TestClient, tmp_path: Path):
    task_id = test_client.post(
        "/api/v1/projects/default/tasks", json={"title": "原标题", "root": str(tmp_path)}
    ).json()["task"]["id"]

    test_client.patch(f"/api/v1/tasks/{task_id}", json={"status": "completed", "root": str(tmp_path)})
    assert test_client.get(
        f"/api/v1/projects/default/tasks?root={tmp_path}"
    ).json()["tasks"][0]["title"] == "原标题"


def test_patch_materialises_a_canvas_only_card(test_client: TestClient, tmp_path: Path):
    """Canvas cards exist only in the frontend, so a status move upserts them."""
    response = test_client.patch(
        "/api/v1/tasks/ACME-201",
        json={"status": "in_review", "title": "画布卡片", "root": str(tmp_path)},
    )
    assert response.status_code == 200
    assert response.json()["created"] is True


def test_patch_rejects_unknown_status(test_client: TestClient, tmp_path: Path):
    response = test_client.patch(
        "/api/v1/tasks/ACME-201", json={"status": "nope", "root": str(tmp_path)}
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_status"


def test_patch_requires_at_least_one_field(test_client: TestClient, tmp_path: Path):
    response = test_client.patch("/api/v1/tasks/ACME-201", json={"root": str(tmp_path)})
    assert response.status_code == 400
    assert response.json()["error"] == "no_fields"


def test_malformed_body_is_rejected(test_client: TestClient, tmp_path: Path):
    """A gateway that answers 200 to unparseable JSON hides every client bug."""
    response = test_client.post(
        "/api/v1/projects/default/tasks",
        content=b"not-json",
        headers={"Content-Type": "application/json"},
        params={"root": str(tmp_path)},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_json"


def test_gate_decision_rejects_unknown_verdict(test_client: TestClient, tmp_path: Path):
    response = test_client.post(
        "/api/v1/tasks/ACME-201/gate/decision", json={"decision": "maybe", "root": str(tmp_path)}
    )
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_decision"


def test_tasks_are_scoped_to_their_project(test_client: TestClient, tmp_path: Path):
    test_client.post("/api/v1/projects/default/tasks", json={"title": "默认项目", "root": str(tmp_path)})
    test_client.post("/api/v1/projects/other/tasks", json={"title": "另一个项目", "root": str(tmp_path)})

    default = test_client.get(f"/api/v1/projects/default/tasks?root={tmp_path}").json()
    other = test_client.get(f"/api/v1/projects/other/tasks?root={tmp_path}").json()
    unknown = test_client.get(f"/api/v1/projects/nope/tasks?root={tmp_path}").json()

    assert [t["title"] for t in default["tasks"]] == ["默认项目"]
    assert [t["title"] for t in other["tasks"]] == ["另一个项目"]
    assert unknown["tasks"] == []


def test_gate_decision_rejects_unverified_receipt(test_client: TestClient, tmp_path: Path):
    # Operator approved but validation exit code is non-zero -> Evidence Gate must fail and return 422
    response = test_client.post(
        f"/api/v1/tasks/task-unverified/gate/decision?root={tmp_path}",
        json={
            "decision": "approved",
            "comment": "LGTM but test actually failed",
            "validation_command": "pytest",
            "validation_exit_code": 1,
            "validation_stdout": "FAILED test_something.py",
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["failed_gate"] == "evidence"
    assert "Evidence Gate failed" in data["error"]


def test_gate_decision_runs_real_validation_command_and_rejects_failing_command(test_client: TestClient, tmp_path: Path):
    response = test_client.post(
        f"/api/v1/tasks/task-failing-cmd/gate/decision?root={tmp_path}",
        json={
            "decision": "approved",
            "comment": "trying to fake zero exit code in payload",
            "validation_command": "python3 -c \"import sys; sys.exit(1)\"",
            "validation_exit_code": 0,
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["ok"] is False
    assert data["failed_gate"] == "evidence"
    assert "exit code 1" in data["error"]


def test_gate_decision_executes_successful_validation_command_and_records_real_stdout_hash(test_client: TestClient, tmp_path: Path):
    import hashlib
    response = test_client.post(
        f"/api/v1/tasks/task-success-cmd/gate/decision?root={tmp_path}",
        json={
            "decision": "approved",
            "comment": "legitimate test run",
            "validation_command": "python3 -c \"print(\x27REAL_VERIFIED_OUTPUT\x27)\"",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    receipt = data["receipt"]
    assert receipt["exit_code"] == 0
    expected_hash = hashlib.sha256(b"REAL_VERIFIED_OUTPUT\n").hexdigest()
    assert receipt["stdout_hash"] == expected_hash


def test_newly_created_task_has_gate_status_not_evaluated(test_client: TestClient, tmp_path: Path):
    response = test_client.post(
        f"/api/v1/projects/default/tasks?root={tmp_path}",
        json={"title": "从未裁决的任务"},
    )
    assert response.status_code == 200
    task = response.json()["task"]
    assert task["gate_status"] == "not_evaluated"


def test_gate_decision_wires_continuous_learning_on_rejection(test_client: TestClient, tmp_path: Path):
    from loopdesk.gateway.tasks import get_learning_engine

    engine = get_learning_engine()
    initial_rejections = len(engine.rejection_signals)

    response = test_client.post(
        f"/api/v1/tasks/task-learn-reject/gate/decision?root={tmp_path}",
        json={
            "decision": "approved",
            "comment": "failing test",
            "validation_command": "python3 -c \"import sys; sys.exit(1)\"",
        },
    )
    assert response.status_code == 422
    assert len(engine.rejection_signals) == initial_rejections + 1
    sig = engine.rejection_signals[-1]
    assert sig.task_id == "task-learn-reject"
    assert "exit code 1" in sig.reason

    # Query learning health endpoint
    health_res = test_client.get(f"/api/v1/governance/learning/health?root={tmp_path}")
    assert health_res.status_code == 200
    data = health_res.json()
    assert data["ok"] is True
    assert "score" in data["health"]
    assert data["health"]["rejections_count"] >= 1


def test_gate_decision_wires_three_tier_memory_dream_on_completion(test_client: TestClient, tmp_path: Path):
    from loopdesk.gateway.tasks import get_memory_system

    mem = get_memory_system()
    initial_distilled = mem.get_long_term_count()

    response = test_client.post(
        f"/api/v1/tasks/task-memory-dream/gate/decision?root={tmp_path}",
        json={
            "decision": "approved",
            "comment": "All criteria met, closing task",
            "validation_command": "python3 -c \"print('OK')\"",
        },
    )
    assert response.status_code == 200
    assert mem.get_long_term_count() == initial_distilled + 1
