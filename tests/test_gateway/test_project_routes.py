import pytest
from starlette.testclient import TestClient
from loopdesk.gateway.app import create_gateway_app
from loopdesk.gateway.config import GatewayConfig

def test_list_and_create_projects():
    app = create_gateway_app(config=GatewayConfig())
    client = TestClient(app)
    
    # 1. List projects - should include default local project
    resp = client.get("/api/v1/projects")
    assert resp.status_code == 200
    data = resp.json()
    assert "projects" in data
    assert any(p["id"] == "default" and p["mode"] == "local" for p in data["projects"])

    # 2. Create a new local project
    resp = client.post("/api/v1/projects", json={
        "id": "my-local-app",
        "name": "My Local App",
        "mode": "local",
        "root_path": "/tmp/my-local-app"
    })
    assert resp.status_code == 200
    proj = resp.json()["project"]
    assert proj["id"] == "my-local-app"
    assert proj["mode"] == "local"

    # 3. Create a remote project
    resp = client.post("/api/v1/projects", json={
        "id": "acme-repo",
        "name": "Acme Repo",
        "mode": "remote",
        "remote_url": "https://github.com/acme/repo.git",
        "required_connector": "jira"
    })
    assert resp.status_code == 200
    remote_proj = resp.json()["project"]
    assert remote_proj["id"] == "acme-repo"
    assert remote_proj["mode"] == "remote"
    assert remote_proj["required_connector"] == "jira"

def test_validate_task_creation_preflight():
    app = create_gateway_app(config=GatewayConfig())
    client = TestClient(app)

    # 1. Validate local task - should pass
    resp = client.post("/api/v1/projects/default/tasks/validate", json={
        "intent": "Fix local bug",
        "template_id": "issue-fix"
    })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    # 2. Validate remote task requiring JIRA connector when JIRA is not configured/active
    resp = client.post("/api/v1/projects/default/tasks/validate", json={
        "intent": "Fix JIRA issue",
        "template_id": "issue-fix",
        "remote": True,
        "required_connector": "jira"
    })
    assert resp.status_code == 200
    val = resp.json()
    assert val["ok"] is False
    assert val["code"] == "MCP_REQUIRED"
    assert val["required_connector"] == "jira"
    assert "JIRA MCP" in val["message"]
