"""Extended RPC tests for LoopDesk loop workspace methods."""

from __future__ import annotations

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


@pytest.fixture()
def loop_service(tmp_path: Path) -> LoopWorkspaceService:
    return LoopWorkspaceService.from_root(tmp_path)


def test_rpc_loop_workspace_extended_surface(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    create_payload = dispatcher.handle("loop_workspace.create", {"root": root}, _RpcContext())
    update_payload = dispatcher.handle(
        "loop_workspace.update",
        {"root": root, "intent": "Ship bounded fix.", "status": "active"},
        _RpcContext(),
    )
    resume_payload = dispatcher.handle(
        "loop_workspace.resume",
        {"root": root, "workId": "work-1", "summary": "Resume work.", "source": "ui"},
        _RpcContext(),
    )
    get_payload = dispatcher.handle("loop_workspace.get", {"root": root}, _RpcContext())
    run_log_payload = dispatcher.handle(
        "loop_workspace.record_run_log",
        {
            "root": root,
            "source": "loop",
            "workId": "work-1",
            "status": "completed",
            "summary": "Completed bounded task.",
            "cost": {"cost_usd": 0.12},
        },
        _RpcContext(),
    )
    kill_payload = dispatcher.handle(
        "loop_workspace.set_kill_switch", {"root": root, "enabled": True}, _RpcContext()
    )
    worktree_payload = dispatcher.handle(
        "loop_workspace.worktree.create", {"root": root, "workId": "goal-1"}, _RpcContext()
    )
    context_payload = dispatcher.handle("loop_workspace.context_pack", {"root": root}, _RpcContext())
    list_payload = dispatcher.handle(
        "loop_workspace.list", {"root": str(loop_service.layout.root.parent)}, _RpcContext()
    )
    export_payload = dispatcher.handle(
        "loop_workspace.export",
        {"root": root, "output": str(loop_service.layout.root / "exported.json")},
        _RpcContext(),
    )

    assert create_payload["status"] == "planned"
    assert update_payload["intent"] == "Ship bounded fix."
    assert resume_payload["current_work_id"] == "work-1"
    assert resume_payload["current_work_source"] == "ui"
    assert get_payload["current_work_id"] == "work-1"
    assert run_log_payload["cost_observatory"]["spend_usd"] == 0.12
    assert kill_payload["safety"]["kill_switch_enabled"] is True
    assert context_payload["current_work_id"] == "goal-1"
    assert any(run_log["summary"] == "Created worktree at {}.".format(worktree_payload["path"]) for run_log in context_payload["recent_run_log"])
    assert Path(worktree_payload["path"]).exists()
    assert next(workspace["workspace_root"] for workspace in list_payload["workspaces"] if workspace["workspace_root"] == root) == root
    assert Path(export_payload["path"]).exists()

    cost_payload = dispatcher.handle(
        "loop_workspace.record_cost",
        {"root": root, "cost_usd": 0.25, "budget_cap_usd": 0.2, "model": "test-model"},
        _RpcContext(),
    )

    assert cost_payload["status"] == "canceled"
    assert cost_payload["cost_observatory"]["spend_usd"] == 0.37
    assert cost_payload["cost_observatory"]["status"] == "paused"
