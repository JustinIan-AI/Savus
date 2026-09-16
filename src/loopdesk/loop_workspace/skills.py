"""Skill audit helpers for personal LoopDesk workspaces."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from loopdesk.loop_workspace.templates import PERSONAL_LOOP_TEMPLATES, load_personal_template


class LoopWorkspaceSkillRegistry:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._skills_dir = root / "skills"
        self._skills_dir.mkdir(parents=True, exist_ok=True)

    def list_skills(self) -> list[dict[str, Any]]:
        skills: list[dict[str, Any]] = []
        for path in sorted(self._skills_dir.glob("*.md")):
            skills.append(
                {
                    "id": path.stem,
                    "name": _title_from_path(path),
                    "path": str(path),
                    "size_bytes": path.stat().st_size,
                }
            )
        for template in PERSONAL_LOOP_TEMPLATES:
            skills.append(
                {
                    "id": template.id,
                    "name": template.name,
                    "path": None,
                    "size_bytes": 0,
                    "template": True,
                }
            )
        return sorted(skills, key=lambda item: item["name"])

    def read_skill(self, skill_id: str) -> dict[str, Any]:
        path = self._skills_dir / f"{skill_id}.md"
        if path.exists():
            return {
                "id": skill_id,
                "name": _title_from_path(path),
                "path": str(path),
                "body": path.read_text(encoding="utf-8"),
            }
        template = load_personal_template(skill_id)
        return {
            "id": template.id,
            "name": template.name,
            "path": None,
            "body": "\n".join(
                [
                    f"# {template.name}",
                    "",
                    "## Loop steps",
                    *[f"- {step}" for step in template.loop_steps],
                    "",
                    "## Goal steps",
                    *[f"- {step}" for step in template.goal_steps],
                    "",
                    f"Roles: {', '.join(template.roles)}",
                ]
            ),
        }

    def write_skill(self, skill_id: str, title: str, body: str) -> dict[str, Any]:
        path = self._skills_dir / f"{_safe_id(skill_id)}.md"
        path.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")
        return {"id": path.stem, "name": title, "path": str(path)}

    def audit(self) -> dict[str, Any]:
        skills = self.list_skills()
        return {
            "count": len(skills),
            "skills": skills[:50],
            "template_ids": [template.id for template in PERSONAL_LOOP_TEMPLATES],
        }


def _title_from_path(path: Path) -> str:
    title = path.stem.replace("-", " ").replace("_", " ").strip()
    return title.title() if title else path.name


def _safe_id(skill_id: str) -> str:
    return skill_id.strip().lower().replace(" ", "-") or "skill"
