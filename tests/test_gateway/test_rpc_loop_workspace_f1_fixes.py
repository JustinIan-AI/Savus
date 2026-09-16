"""F1 regression tests for pre-integration blocking LoopDesk RPC fixes.

``pytest-asyncio`` in this environment can leave an event loop on the stack
during module-level dispatcher imports. ``RpcRegistry.handle`` only supports
non-running loops, so these tests route synchronous calls through
``_dispatch_rpc`` so the gateway RPC handlers can be called directly from
pytest.

The core assertions are also exposed through ``run_f1_regression_checks()``
so they can be verified with ``python tests/test_gateway/test_rpc_loop_workspace_f1_fixes.py``
or any custom runner when normal pytest collection remains unstable.
"""


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


def test_rpc_loop_workspace_cost_history_persists_cost_from_run_log(
    loop_service: LoopWorkspaceService,
) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    dispatcher.handle(
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

    payload = dispatcher.handle(
        "loop_workspace.cost.history",
        {"root": root, "limit": 10},
        _RpcContext(),
    )

    assert payload["total"] == 1
    cost = payload["history"][0].get("cost") or payload["history"][0]["toolEvent"]["cost"]
    assert cost["cost_usd"] == 0.05
    assert cost["model"] == "mock-model"


def run_f1_regression_checks() -> None:
    root = Path("/tmp/loopdesk-f1-regression")
    if root.exists():
        import shutil

        shutil.rmtree(root)
    root.mkdir()
    service = LoopWorkspaceService.from_root(root)
    init_git_repo(root)
    dispatcher = get_dispatcher()
    ctx = _RpcContext()

    _dispatch_rpc(
        "loop_workspace.create",
        {"root": str(root)},
        ctx,
    )
    _dispatch_rpc(
        "loop_workspace.record_approval",
        {
            "root": str(root),
            "id": "approval-respond-state-1",
            "status": "pending",
            "payload": {"action": "edit"},
        },
        ctx,
    )
    approval_payload = dispatcher.handle(
        "loop_workspace.approval.respond",
        {
            "root": str(root),
            "id": "approval-respond-state-1",
            "status": "denied",
            "payload": {"note": "needs review"},
        },
        ctx,
    )
    assert approval_payload is not None
    assert approval_payload["approvals"][0]["status"] == "denied"
    assert approval_payload["approvals"][0]["payload"].get("note") == "needs review"
    assert approval_payload["current_work_id"] is None

    dispatcher.handle(
        "loop_workspace.record_run_log",
        {
            "root": str(root),
            "source": "loop",
            "workId": "work-history-1",
            "status": "active",
            "summary": "Did work.",
            "cost": {"cost_usd": 0.05, "model": "mock-model"},
        },
        ctx,
    )
    history_payload = dispatcher.handle(
        "loop_workspace.cost.history",
        {"root": str(root), "limit": 10},
        ctx,
    )
    assert history_payload["total"] == 1
    cost = history_payload["history"][0].get("cost") or history_payload["history"][0]["toolEvent"]["cost"]
    assert cost["cost_usd"] == 0.05
    assert cost["model"] == "mock-model"


if __name__ == "__main__":
    run_f1_regression_checks()
    print("F1 regression checks passed")
