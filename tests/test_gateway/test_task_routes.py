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
