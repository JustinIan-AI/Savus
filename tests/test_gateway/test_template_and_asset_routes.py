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
