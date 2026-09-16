"""Skill registry tests for LoopDesk workspaces."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.loop_workspace.skills import LoopWorkspaceSkillRegistry


def test_skill_registry_lists_personal_templates(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    registry = LoopWorkspaceSkillRegistry(tmp_path)

    registry.write_skill("api-reviewer", "API Reviewer", "- Verify response schemas.\n- Keep clients backward compatible.")

    listed = registry.list_skills()

    assert any(skill["id"] == "api-reviewer" and skill["path"] is not None for skill in listed)
    assert any(skill["id"] == "backend-engineer" and skill["template"] for skill in listed)

    read_payload = registry.read_skill("backend-engineer")

    assert "Backend Implementation" in read_payload["body"]
    audit = registry.audit()
    assert audit["count"] >= 2
    assert "backend-engineer" in audit["template_ids"]
