"""Integration scenarios for personal developer workflows."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.adapters import CrossToolAdapter, ToolEvent
from loopdesk.loop_workspace.cli_bridge import LocalCliBridge
from loopdesk.loop_workspace.memory import DurableMemoryIndex
from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.loop_workspace.templates import load_personal_template


def test_codex_to_claude_handoff_preserves_context(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    adapter = CrossToolAdapter(service.repository)

    next_state = service.record_work_item("work-1", "loop", "Draft API contract.")
    adapter.translate_event_to_run_log(ToolEvent("codex", "run_goal", {"workId": "work-1"}))
    next_state = service.record_work_item(
        "work-1", "claude-code", "Implement API client.", status="active"
    )

    assert next_state["current_work_source"] == "claude-code"
    assert next_state["status"] == "active"


def test_personal_template_flows_through_loop_to_goal(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    template = load_personal_template("backend-engineer")

    initialized = service.ensure_initialized(
        intent="Ship bounded API fix.", selected_template=template.id
    )
    state = service.record_work_item("work-2", "loop", f"Use {template.name} for discovery.")

    assert initialized.state_file.exists()
    assert state["selected_template"] == template.id
    assert state["project_name"] == tmp_path.name


def test_worktree_isolation_round_trip(tmp_path: Path) -> None:
    from tests.support.loop_workspace_repos import init_git_repo

    init_git_repo(tmp_path)
    service = LoopWorkspaceService.from_root(tmp_path)

    worktree_payload = service.create_worktree("goal-alpha")
    listed = service.list_worktrees()

    assert worktree_payload["branch"] == "loopdesk/goal/goal-alpha"
    assert Path(worktree_payload["path"]).exists()
    assert listed["worktrees"][0]["name"] == "goal-alpha"

    remove_payload = service.remove_worktree("goal-alpha")

    assert remove_payload["retained"] is False
    assert not Path(worktree_payload["path"]).exists()
    assert service.list_worktrees()["worktrees"] == []


def test_memory_compact_and_cli_bridge_handoff(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    memory = DurableMemoryIndex(tmp_path)
    bridge = LocalCliBridge(service.repository, artifact_dir=service.layout.artifacts_dir)

    memory.append("Keep retry policy under five attempts", "Avoid unbounded loops.", tags=["reliability"])
    hits = memory.search("retry policy")
    assert hits, "memory search should find appended entry"

    compact = memory.compact(keep_recent=1)
    assert compact["kept"] == 1
    assert memory.search("retry policy")
    assert compact["removed_keys"] == []
    assert [entry["key"] for entry in memory.resume_pack()["entries"]] == ["keep-retry-policy-under-five-attempts"]

    result = bridge.run("gemini", ["printf", "summary\\n"])
    assert result["ok"] is True
    state = service.repository.read()
    assert state.cost_observatory["request_count"] == 1
