"""Cost and run log RPC endpoint tests for LoopDesk loop workspaces."""

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


def test_rpc_loop_workspace_set_budget(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    payload = _dispatch_rpc(
        "loop_workspace.cost.set_budget",
        {"root": root, "budget_cap_usd": 1.25},
        _RpcContext(),
    )
    assert payload["cost_observatory"]["budget_cap_usd"] == 1.25


def test_rpc_loop_workspace_cost_history(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    _dispatch_rpc(
        "loop_workspace.record_run_log",
        {
            "root": root,
            "source": "loop",
            "workId": "work-1",
            "status": "active",
            "summary": "Did work.",
            "cost": {"cost_usd": 0.05, "model": "mock-model"},
        },
        _RpcContext(),
    )

    payload = _dispatch_rpc(
        "loop_workspace.cost.history",
        {"root": root, "limit": 10},
        _RpcContext(),
    )
    assert payload["total"] == 1
    cost = payload["history"][0].get("cost") or payload["history"][0]["toolEvent"]["cost"]
    assert cost["cost_usd"] == 0.05
    assert cost["model"] == "mock-model"


def test_rpc_loop_workspace_cost_history_persists_cost_from_run_log(
    loop_service: LoopWorkspaceService,
) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    _dispatch_rpc(
        "loop_workspace.record_run_log",
        {
            "root": root,
            "source": "loop",
            "workId": "work-history-1",
            "status": "active",
            "summary": "Did work.",
            "cost": {"cost_usd": 0.05, "model": "mock-model"},
        },
        _RpcContext(),
    )

    payload = _dispatch_rpc(
        "loop_workspace.cost.history",
        {"root": root, "limit": 10},
        _RpcContext(),
    )

    assert payload["total"] == 1
    cost = payload["history"][0].get("cost") or payload["history"][0]["toolEvent"]["cost"]
    assert cost["cost_usd"] == 0.05
    assert cost["model"] == "mock-model"


def test_rpc_loop_workspace_run_log_list(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    for index in range(4):
        _dispatch_rpc(
            "loop_workspace.record_run_log",
            {
                "root": root,
                "source": "loop",
                "workId": f"work-{index}",
                "status": "active",
                "summary": f"Step {index}",
            },
            _RpcContext(),
        )

    payload = _dispatch_rpc(
        "loop_workspace.run_log.list",
        {"root": root, "limit": 10, "offset": 0},
        _RpcContext(),
    )
    assert payload["total"] == 4
    assert payload["run_log"][-1]["summary"] == "Step 3"
