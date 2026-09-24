from __future__ import annotations

from pathlib import Path
from loopdesk.loop_workspace.service import LoopWorkspaceService

import pytest
from starlette.testclient import TestClient
from loopdesk.gateway.app import create_gateway_app as create_app
from loopdesk.gateway.config import GatewayConfig

@pytest.fixture
def client(tmp_path: Path):
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized(intent="Test Orchestration Workspace")
    app = create_app(config=GatewayConfig())
    return TestClient(app)

def test_pty_gateway_routes(client, tmp_path: Path):
    # 1. 创建真实 PTY 会话
    res = client.post("/api/v1/orchestration/pty", json={
        "session_id": "gw-pty-test",
        "command": ["cat"],
        "workdir": "/tmp"
    }, headers={"X-LoopDesk-Test-Auth": "test-authorized"})
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["session_id"] == "gw-pty-test"
    assert data["pid"] > 0
    assert data["alive"] is True

    # 2. 写入数据
    res_write = client.post("/api/v1/orchestration/pty/gw-pty-test/write", json={"input": "echo from gateway\n"})
    assert res_write.status_code == 200
    assert res_write.json()["written_bytes"] > 0

    # 3. 读取回显
    res_read = client.get("/api/v1/orchestration/pty/gw-pty-test/read")
    assert res_read.status_code == 200
    assert "echo from gateway" in res_read.json()["output"]

    # 4. 终止会话
    res_term = client.delete("/api/v1/orchestration/pty/gw-pty-test")
    assert res_term.status_code == 200
    assert res_term.json()["terminated"] is True

def test_handoff_gateway_route(client, tmp_path: Path):
    res = client.post("/api/v1/orchestration/handoff", json={
        "from_agent": "claude-code",
        "to_agent": "codex-cli",
        "context_data": {"task_id": "TASK-999", "branch": "feat/loopx"}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["handoff_packet"]["from_agent"] == "claude-code"
    assert data["handoff_packet"]["to_agent"] == "codex-cli"


def test_pty_security_enforcement(client: TestClient, tmp_path: Path):
    # 1. Reject unauthenticated request
    res_unauth = client.post("/api/v1/orchestration/pty", json={"session_id": "bad-auth", "command": ["cat"]})
    assert res_unauth.status_code == 403
    assert res_unauth.json()["code"] == "FORBIDDEN"

    # 2. Reject disallowed arbitrary command even with auth
    res_disallowed = client.post(
        "/api/v1/orchestration/pty",
        json={"session_id": "bad-cmd", "command": ["rm", "-rf", "/tmp"]},
        headers={"X-LoopDesk-Test-Auth": "test-authorized"}
    )
    assert res_disallowed.status_code == 403
    assert res_disallowed.json()["code"] == "COMMAND_NOT_ALLOWED"
