"""Approval RPC endpoint tests for LoopDesk loop workspaces."""


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


def test_rpc_loop_workspace_approvals_list(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    _dispatch_rpc(
        "loop_workspace.record_approval",
        {"root": root, "id": "approval-1", "status": "pending", "payload": {"action": "edit"}},
        _RpcContext(),
    )

    pending = dispatcher.handle(
        "loop_workspace.approvals.list",
        {"root": root, "status": "pending"},
        _RpcContext(),
    )
    assert len(pending["approvals"]) == 1
    assert pending["approvals"][0]["id"] == "approval-1"


def test_rpc_loop_workspace_approval_respond(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    _dispatch_rpc(
        "loop_workspace.record_approval",
        {"root": root, "id": "approval-1", "status": "pending", "payload": {"action": "edit"}},
        _RpcContext(),
    )

    _dispatch_rpc(
        "loop_workspace.approval.respond",
        {"root": root, "id": "approval-1", "status": "denied", "payload": {"note": "nope"}},
        _RpcContext(),
    )
    fresh_service = LoopWorkspaceService.from_root(Path(root))
    assert fresh_service.approvals_list("pending")["approvals"][0]["id"] == "approval-1"
    assert fresh_service.approvals_list("denied")["approvals"][0]["id"] == "approval-1"
    assert fresh_service.approvals_list("denied")["approvals"][0]["payload"].get("note") == "nope"
    assert fresh_service.repository.read().current_work_id is None


def test_rpc_loop_workspace_approval_respond_returns_updated_state(
    loop_service: LoopWorkspaceService,
) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    _dispatch_rpc(
        "loop_workspace.record_approval",
        {
            "root": root,
            "id": "approval-respond-state-1",
            "status": "pending",
            "payload": {"action": "edit"},
        },
        _RpcContext(),
    )

    _dispatch_rpc(
        "loop_workspace.approval.respond",
        {
            "root": root,
            "id": "approval-respond-state-1",
            "status": "denied",
            "payload": {"note": "needs review"},
        },
        _RpcContext(),
    )
    fresh_service = LoopWorkspaceService.from_root(Path(root))
    approvals = fresh_service.approvals_list("denied")["approvals"]
    assert approvals[0]["id"] == "approval-respond-state-1"
    assert approvals[0]["status"] == "denied"
    assert approvals[0]["payload"].get("note") == "needs review"
    assert fresh_service.repository.read().current_work_id is None
