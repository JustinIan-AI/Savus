"""LoopDesk workbench panel regression tests."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.service import LoopWorkspaceService


def test_loop_workspace_panel_helpers_exist() -> None:
    service = LoopWorkspaceService.from_root(Path("/tmp/loopdesk-panel-check"))
    assert hasattr(service, "record_run_log")
    assert hasattr(service, "check_budget")
    assert hasattr(service, "apply_template")
