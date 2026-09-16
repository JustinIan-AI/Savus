"""Loop Engine RPC endpoint tests."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from loopdesk.gateway.rpc import get_dispatcher
from loopdesk.loop_workspace.service import LoopWorkspaceService
from tests.support.loop_workspace_repos import init_git_repo


class _RpcContext:
    def __init__(self) -> None:
        self.principal = _FakePrincipal()
        self.config = None


class _FakePrincipal:
    role = "operator"
    scopes = frozenset(["operator.admin"])
    is_owner = True
    authenticated = True


def _dispatch_rpc(name: str, params: dict[str, object], ctx: _RpcContext) -> dict[str, object]:
    async def _run() -> dict[str, object]:
        response = await get_dispatcher().dispatch("req", name, params, ctx)
        payload = response.payload if hasattr(response, "payload") else response
        if isinstance(payload, dict) and payload.get("ok") is None and "error" in payload:
            raise RuntimeError(payload.get("error", payload))
        return payload

    try:
        return asyncio.get_running_loop().run_until_complete(_run())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_run())
        finally:
            loop.close()


@pytest.fixture()
def loop_service(tmp_path: Path) -> LoopWorkspaceService:
    return LoopWorkspaceService.from_root(tmp_path)


def test_rpc_loop_workspace_engine_start_and_status(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    start = _dispatch_rpc(
        "loop_workspace.engine.start",
        {"root": root, "goal": "X", "stop_condition": "done"},
        _RpcContext(),
    )
    status = _dispatch_rpc("loop_workspace.engine.status", {"root": root}, _RpcContext())

    assert start["phase"] == status["phase"]
    assert start["current_iteration"] == 0
    assert status["current_iteration"] == 0


def test_rpc_loop_workspace_engine_stop_writes_run_log(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    _dispatch_rpc(
        "loop_workspace.engine.start",
        {"root": root, "goal": "X", "stop_condition": "done"},
        _RpcContext(),
    )
    _dispatch_rpc("loop_workspace.engine.stop", {"root": root}, _RpcContext())
    run_log = dispatcher.handle("loop_workspace.run_log.list", {"root": root, "limit": 10, "offset": 0}, _RpcContext())

    assert any(entry.get("summary") == "Loop engine started." for entry in run_log["run_log"])
    assert any(entry.get("summary") == "Loop engine stopped." for entry in run_log["run_log"])
