"""Service tests for LoopDesk loop workspace operations."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.service import LoopWorkspaceService


def test_service_persists_and_exports_state(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)

    state = service.record_work_item(
        "work-1", "loop", "Draft architecture decision.", status="active"
    )
    exported = service.current_state()

    assert state["current_work_id"] == "work-1"
    assert exported["current_work_source"] == "loop"
    assert exported["directories"]["personal_templates"] is True
    assert any(template["id"] == "architect" for template in exported["templates"])
