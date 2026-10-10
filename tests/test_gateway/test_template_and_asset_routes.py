from __future__ import annotations

from pathlib import Path
import pytest
from starlette.testclient import TestClient

from loopdesk.gateway.app import create_gateway_app
from loopdesk.gateway.config import GatewayConfig
from loopdesk.loop_workspace.service import LoopWorkspaceService


@pytest.fixture
def client(tmp_path: Path):
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized(intent="Test Workspace")
    app = create_gateway_app(GatewayConfig())
    return TestClient(app)


def test_templates_routes(client: TestClient):
    res = client.get("/api/v1/templates")
    print("STATUS:", res.status_code, "BODY:", res.text)
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    ids = [t["id"] for t in data["templates"]]
    assert "issue-fix" in ids
    assert "pr-commit" in ids
    assert "auto-research" in ids

    res = client.post("/api/v1/templates/render", json={
        "template_id": "issue-fix",
        "params": {"issue_id": "42", "issue_url": "https://github.com/test/issues/42"}
    })
    print("STATUS:", res.status_code, "BODY:", res.text)
    assert res.status_code == 200
    render_data = res.json()
    assert render_data["ok"] is True
    assert render_data["skeleton"]["branch"] == "codex/fix-42"

    res = client.post("/api/v1/templates/step", json={
        "template_id": "issue-fix",
        "issue_id": "42",
        "title": "Fix null pointer",
        "role": "maker",
        "output": "Added null check in parser.py"
    })
    print("STATUS:", res.status_code, "BODY:", res.text)
    assert res.status_code == 200
    step_data = res.json()
    assert step_data["ok"] is True
    assert step_data["record"]["step"] == "triage"


def test_template_flow_state_persists_to_disk_and_restores(client: TestClient, tmp_path: Path):
    import loopdesk.gateway.templates_assets as ta

    # 1. First step
    res1 = client.post(f"/api/v1/templates/step?root={tmp_path}", json={
        "template_id": "issue-fix",
        "issue_id": "99",
        "title": "Fix memory crash",
        "role": "triage",
        "output": "Analyzed root cause",
    })
    assert res1.status_code == 200
    assert res1.json()["record"]["step"] == "triage"
    assert res1.json()["current_step_idx"] == 1

    # Verify flow state file written to disk
    flow_file = tmp_path / ".loopdesk" / "flows" / "issue-fix_99.json"
    assert flow_file.exists()

    # 2. Simulate process restart / memory cache wipe
    ta._ACTIVE_FLOW_STATES.clear()

    # 3. Second step must reload from disk rather than resetting to triage (step 0)
    res2 = client.post(f"/api/v1/templates/step?root={tmp_path}", json={
        "template_id": "issue-fix",
        "issue_id": "99",
        "title": "Fix memory crash",
        "role": "maker",
        "output": "Patched buffer allocation",
    })
    assert res2.status_code == 200
    assert res2.json()["record"]["step"] == "maker"
    assert res2.json()["current_step_idx"] == 2


def test_assets_routes(client: TestClient, tmp_path: Path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    rules_dir = repo_dir / "rules"
    rules_dir.mkdir()
    rule_file = rules_dir / "coding.md"
    raw_content = chr(45)*3 + chr(10) + "id: coding-standard" + chr(10) + "name: Coding Standard" + chr(10) + "type: rule" + chr(10) + "roles: [maker, checker]" + chr(10) + chr(45)*3 + chr(10) + "Be clean."
    rule_file.write_text(raw_content, encoding="utf-8")

    res = client.get(f"/api/v1/assets?root={repo_dir}")
    print("STATUS:", res.status_code, "BODY:", res.text)
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert len(data["assets"]) == 1
    assert data["assets"][0]["id"] == "coding-standard"

    target_project = tmp_path / "target_proj"
    target_project.mkdir()
    res = client.post("/api/v1/assets/distribute", json={
        "target_dir": str(target_project),
        "asset": {
            "id": "coding-standard",
            "name": "Coding Standard",
            "type": "rule",
            "content": "Clean code rules",
            "version": "1.0.0",
            "roles": ["maker"]
        }
    })
    print("STATUS:", res.status_code, "BODY:", res.text)
    assert res.status_code == 200
    assert (target_project / ".loopdesk" / "rules" / "coding-standard.md").exists()


def test_execute_template_step_evaluates_stop_conditions(client: TestClient, tmp_path: Path):
    res = client.post(f"/api/v1/templates/step?root={tmp_path}", json={
        "template_id": "auto-research",
        "topic": "compression-rate",
        "notes": "Optimal ratio reached",
        "score": 0.95,
        "max_iterations": 1,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    stop_eval = data.get("stop_conditions")
    assert stop_eval is not None
    assert stop_eval["all_conditions_met"] is True
    assert stop_eval["condition_results"]["score >= 0.85"] is True


def test_evaluate_template_stop_conditions_endpoint(client: TestClient):
    res = client.post("/api/v1/templates/issue-fix/stop-conditions", json={
        "context": {
            "tests_pass": True,
            "no_regression": True,
            "review_gate_approved": True,
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["all_conditions_met"] is True
    assert data["condition_results"]["tests_pass == True"] is True
