"""Budget enforcement tests for LoopDesk loop workspaces."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.service import LoopWorkspaceService


def test_service_reports_budget_status(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    service.record_cost({"cost_usd": 0.5})
    status = service.check_budget()

    assert status["status"] == "ok"
    assert status["spend_usd"] == 0.5
