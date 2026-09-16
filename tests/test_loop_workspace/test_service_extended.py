"""Extended service tests for LoopDesk run log, approvals, and safety."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.service import LoopWorkspaceService


def test_service_records_run_log_cost_approval_and_worktree(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()
    state = service.record_work_item("work-1", "loop", "Draft acceptance criteria.")

    approval_state = service.record_approval(
        {
            "id": "approval-1",
            "action": "run-goal",
            "status": "approved",
            "payload": {"workId": "work-1"},
        }
    )
    run_log_state = service.record_run_log(
        {
            "source": "tool:codex",
            "workId": "work-1",
            "status": "completed",
            "summary": "Implemented API client.",
            "previousStatus": "active",
            "cost": {
                "input_tokens": 120,
                "output_tokens": 80,
                "cost_usd": 0.04,
                "model": "test-model",
            },
        }
    )
    worktree_state = service.list_worktrees()
    kill_switch_state = service.set_kill_switch(True)
    denylist_state = service.set_denylist(["dangerous.sh", "network.send"])

    assert state["current_work_id"] == "work-1"
    assert approval_state["approvals"][0]["id"] == "approval-1"
    assert run_log_state["run_log"][-1]["status"] == "completed"
    assert run_log_state["cost_observatory"]["spend_usd"] == 0.04
    assert worktree_state["worktrees"] == []
    assert kill_switch_state["safety"]["kill_switch_enabled"] is True
    assert kill_switch_state["cost_observatory"]["status"] == "paused"
    assert denylist_state["safety"]["denylist"] == ["dangerous.sh", "network.send"]


def test_service_enforces_budget_cap_and_override_history(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()
    first = service.record_cost({"cost_usd": 0.05, "budget_cap_usd": 0.10})
    second = service.record_cost({"cost_usd": 0.06, "budget_cap_usd": 0.10})

    assert first["cost_observatory"]["spend_usd"] == 0.05
    assert first["status"] == "planned"
    assert second["cost_observatory"]["spend_usd"] == 0.11
    assert second["status"] == "canceled"
    assert second["cost_observatory"]["status"] == "paused"
    assert second["override_history"][-1]["source"] == "cost-observatory"
    assert second["override_history"][-1]["reason"] == "Budget cap exceeded."


def test_service_blocks_denylisted_tool_events(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()
    service.set_denylist(["dangerous.sh"])
    blocked = service.record_run_log(
        {
            "source": "tool:codex",
            "workId": "work-1",
            "status": "active",
            "summary": "Run dangerous.sh.",
            "toolEvent": {"argv": ["bash", "dangerous.sh"]},
        }
    )

    assert blocked["status"] == "canceled"
    assert blocked["cost_observatory"]["status"] == "paused"
    assert blocked["safety"]["denylist"] == ["dangerous.sh"]
    assert blocked["override_history"][-1]["source"] == "denylist"
