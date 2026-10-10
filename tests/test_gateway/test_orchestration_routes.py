from __future__ import annotations

from pathlib import Path
from loopdesk.loop_workspace.service import LoopWorkspaceService

import pytest
from starlette.testclient import TestClient
from loopdesk.gateway.app import create_gateway_app as create_app
from loopdesk.gateway.config import GatewayConfig

TEST_ADMIN_KEY = "test-loopdesk-secret-999"

@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LOOPDESK_ADMIN_KEY", TEST_ADMIN_KEY)
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized(intent="Test Orchestration Workspace")
    app = create_app(config=GatewayConfig())
    return TestClient(app)

def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {TEST_ADMIN_KEY}"}

def test_pty_gateway_routes(client, tmp_path: Path):
    # 1. 创建真实 PTY 会话
    res = client.post("/api/v1/orchestration/pty", json={
        "session_id": "gw-pty-test",
        "command": ["cat"],
        "workdir": "/tmp"
    }, headers=auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["session_id"] == "gw-pty-test"
    assert data["pid"] > 0
    assert data["alive"] is True

    # 2. 写入数据
    res_write = client.post(
        "/api/v1/orchestration/pty/gw-pty-test/write",
        json={"input": "echo from gateway\n"},
        headers=auth_headers(),
    )
    assert res_write.status_code == 200
    assert res_write.json()["written_bytes"] > 0

    # 3. 读取回显
    res_read = client.get("/api/v1/orchestration/pty/gw-pty-test/read", headers=auth_headers())
    assert res_read.status_code == 200
    assert "echo from gateway" in res_read.json()["output"]

    # 4. 终止会话
    res_term = client.delete("/api/v1/orchestration/pty/gw-pty-test", headers=auth_headers())
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
        headers=auth_headers(),
    )
    assert res_disallowed.status_code == 403
    assert res_disallowed.json()["code"] == "COMMAND_NOT_ALLOWED"


def test_pty_rejects_test_auth_header_backdoor(client: TestClient):
    # Sending X-LoopDesk-Test-Auth must no longer bypass authentication
    res = client.post(
        "/api/v1/orchestration/pty",
        json={"session_id": "backdoor-test", "command": ["cat"]},
        headers={"X-LoopDesk-Test-Auth": "test-authorized"},
    )
    assert res.status_code == 403
    assert res.json()["code"] == "FORBIDDEN"


def test_pty_read_write_terminate_require_auth(client: TestClient):
    # Create session with valid auth first
    client.post(
        "/api/v1/orchestration/pty",
        json={"session_id": "auth-lock-test", "command": ["cat"]},
        headers=auth_headers(),
    )
    # Unauthenticated write
    res_write = client.post("/api/v1/orchestration/pty/auth-lock-test/write", json={"input": "test"})
    assert res_write.status_code == 403
    assert res_write.json()["code"] == "FORBIDDEN"

    # Unauthenticated read
    res_read = client.get("/api/v1/orchestration/pty/auth-lock-test/read")
    assert res_read.status_code == 403
    assert res_read.json()["code"] == "FORBIDDEN"

    # Unauthenticated terminate
    res_term = client.delete("/api/v1/orchestration/pty/auth-lock-test")
    assert res_term.status_code == 403
    assert res_term.json()["code"] == "FORBIDDEN"

    # Clean up with auth
    client.delete("/api/v1/orchestration/pty/auth-lock-test", headers=auth_headers())


@pytest.mark.parametrize("bad_cmd", [["python3"], ["python"], ["bash"], ["sh"], ["node"]])
def test_pty_rejects_raw_interpreter_execution(client: TestClient, bad_cmd: list[str]):
    res = client.post(
        "/api/v1/orchestration/pty",
        json={"session_id": f"raw-{bad_cmd[0]}", "command": bad_cmd},
        headers=auth_headers(),
    )
    assert res.status_code == 403
    assert res.json()["code"] == "COMMAND_NOT_ALLOWED"


def test_handoff_gateway_resolves_context_and_creates_envelope(client: TestClient):
    res = client.post("/api/v1/orchestration/handoff", json={
        "from_agent": "claude",
        "to_agent": "codex",
        "task_id": "TASK-CTX-88",
        "context_data": {
            "prompt": "Please review @agent/reviewer suggestions and @repo/docs/spec.md",
            "code_diff": "+ def test_feature(): pass",
            "decisions": ["Follow strict TDD flow"]
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    envelope = data.get("envelope")
    assert envelope is not None
    assert envelope["source"] == "claude"
    assert envelope["dest"] == "codex"
    assert envelope["code_diff"] == "+ def test_feature(): pass"
    assert "[AgentContext: reviewer:" in data["resolved_prompt"]


def test_fanout_orchestration_route(client: TestClient, tmp_path: Path):
    res = client.post(
        "/api/v1/orchestration/fanout",
        json={
            "candidates": [
                {"agent": "claude", "worktree": str(tmp_path / "wt1"), "score": 0.78},
                {"agent": "codex", "worktree": str(tmp_path / "wt2"), "score": 0.95},
                {"agent": "pi", "worktree": str(tmp_path / "wt3"), "score": 0.81},
            ]
        },
        headers=auth_headers(),
    )
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    winner = data["winner"]
    assert winner["agent"] == "codex"
    assert winner["score"] == 0.95
