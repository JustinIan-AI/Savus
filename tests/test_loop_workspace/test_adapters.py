"""Adapter boundary tests for LoopDesk cross-tool integration."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.adapters import CrossToolAdapter, ToolEvent
from loopdesk.loop_workspace.adapters import AcpToolAdapter
from loopdesk.loop_workspace.service import LoopWorkspaceService


def test_adapter_translates_event_to_run_log(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    adapter = CrossToolAdapter(service.repository)

    run_log = adapter.translate_event_to_run_log(
        ToolEvent("codex", "run_goal", {"workId": "goal-1"})
    )

    assert run_log["source"] == "tool:codex"
    assert run_log["summary"] == "codex.run_goal completed."
    state = service.repository.read()
    assert state.current_work_id == "goal-1"
    assert state.current_work_source == "tool:codex"
    assert state.run_log[-1]["summary"] == run_log["summary"]


def test_acp_adapter_records_placeholder_run_log(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    adapter = AcpToolAdapter(service.repository)

    run_log = adapter.translate_event_to_run_log(
        ToolEvent("codex", "run_goal", {"workId": "goal-1"})
    )

    assert run_log["source"] == "tool:acp:codex"
    assert run_log["summary"] == "codex.run_goal queued via ACP placeholder."
    state = service.repository.read()
    assert state.current_work_id == "goal-1"
    assert state.current_work_source == "tool:acp:codex"
    assert state.run_log[-1]["toolEvent"]["payload"]["status"] == "placeholder"
