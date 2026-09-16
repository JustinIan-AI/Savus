"""Schema tests for LoopDesk loop workspace state."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.schema import LoopWorkspaceState, LoopWorkspaceStatus


def test_default_loop_state_round_trip(tmp_path: Path) -> None:
    state = LoopWorkspaceState.create(
        workspace_root=str(tmp_path),
        intent="Implement loop handoff between Codex and Claude Code.",
        tags=["codex", "claude-code", "handoff"],
    )

    payload = state.to_dict()
    restored = LoopWorkspaceState.from_dict(payload)

    assert restored.schema_version == 1
    assert restored.workspace_root == str(tmp_path)
    assert restored.status == LoopWorkspaceStatus.PLANNED
    assert restored.intent == state.intent
    assert restored.tags == state.tags
    assert restored.updated_at >= restored.created_at


def test_status_change_records_override_history(tmp_path: Path) -> None:
    state = LoopWorkspaceState.create(
        workspace_root=str(tmp_path), intent="Review PRD and draft plan."
    )
    previous = state.status
    state.status = LoopWorkspaceStatus.BLOCKED
    state.record_override(
        source="loop-engine", reason="Awaiting MCP adapter confirmation.", previous_status=previous
    )

    payload = state.to_dict()
    restored = LoopWorkspaceState.from_dict(payload)

    assert restored.status == LoopWorkspaceStatus.BLOCKED
    assert len(restored.override_history) == 1
    assert restored.override_history[0]["source"] == "loop-engine"
