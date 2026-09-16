"""Observability and handoff tests for LoopDesk loop workspace."""

from __future__ import annotations

from pathlib import Path

import pytest

from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.loop_workspace.skills import LoopWorkspaceSkillRegistry


def test_service_context_pack_returns_safety_and_template_snapshot(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized(
        intent="Review bounded API change.",
        selected_template="backend-engineer",
    )
    state = service.record_work_item("work-1", "loop", "Scan risks.")
    service.record_approval(
        {
            "id": "approval-1",
            "action": "run-goal",
            "status": "pending",
            "payload": {"workId": "work-1"},
        }
    )
    service.set_kill_switch(True)
    service.set_denylist(["dangerous.sh", "network.send"])

    context_pack = service.get_context_pack()

    assert context_pack["current_work_id"] == "work-1"
    assert context_pack["status"] == state["status"]
    assert context_pack["selected_template"] == "backend-engineer"
    assert context_pack["open_approvals"][0]["id"] == "approval-1"
    assert context_pack["safety"]["kill_switch_enabled"] is True
    assert context_pack["safety"]["denylist"] == ["dangerous.sh", "network.send"]
    assert any(item["id"] == "backend-engineer" for item in context_pack["templates"])


def test_skill_registry_reads_custom_and_template_skills(tmp_path: Path) -> None:
    registry = LoopWorkspaceSkillRegistry(tmp_path)
    registry.write_skill("api-reviewer", "API Reviewer", "- Verify response schemas.\n- Keep clients backward compatible.")

    listed = registry.list_skills()
    assert any(skill["id"] == "api-reviewer" and skill["path"] is not None for skill in listed)
    assert any(skill["id"] == "backend-engineer" and skill["template"] is True for skill in listed)

    custom_skill = registry.read_skill("api-reviewer")
    assert custom_skill["name"] == "Api Reviewer"
    assert "Verify response schemas" in custom_skill["body"]

    template_skill = registry.read_skill("backend-engineer")
    assert template_skill["path"] is None
    assert "Backend Implementation" in template_skill["body"]
    assert "Goal steps" in template_skill["body"]

    audit = registry.audit()
    assert audit["count"] >= 2
    assert "backend-engineer" in audit["template_ids"]
