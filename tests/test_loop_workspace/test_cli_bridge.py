"""CLI bridge tests for LoopDesk cross-tool workflows."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.adapters import CrossToolAdapter
from loopdesk.loop_workspace.cli_bridge import LocalCliBridge
from loopdesk.loop_workspace.service import LoopWorkspaceService


def test_cli_bridge_records_tool_run_log_and_artifact(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized(intent="Ship API fix.")
    bridge = LocalCliBridge(service.repository, artifact_dir=service.layout.artifacts_dir)

    result = bridge.run("codex", ["echo", "delivery"])

    assert result["ok"] is True
    assert Path(result["artifact_path"]).exists()
    state = service.repository.read()
    assert state.current_work_id is None
    assert any(entry["summary"] == "codex.run_command completed." for entry in state.run_log)
