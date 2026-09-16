"""Replay pack and session compaction RPC endpoint tests."""

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


def test_rpc_loop_workspace_replay_pack(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    payload = _dispatch_rpc("loop_workspace.replay.pack", {"root": root}, _RpcContext())

    assert "recent_run_log" in payload
    assert "templates" in payload


def test_rpc_loop_workspace_session_compact(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    for index in range(3):
        _dispatch_rpc(
            "loop_workspace.record_run_log",
            {"root": root, "source": "loop", "workId": f"work-{index}", "status": "active", "summary": f"Step {index}"},
            _RpcContext(),
        )

    payload = _dispatch_rpc(
        "loop_workspace.session.compact",
        {"root": root, "keep_recent": 2},
        _RpcContext(),
    )

    assert payload["kept"] == 2
