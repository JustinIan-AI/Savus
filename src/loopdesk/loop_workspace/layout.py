"""Loop workspace directory layout constants and helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoopWorkspaceLayout:
    root: Path
    state_file: Path
    memory_dir: Path
    skills_dir: Path
    artifacts_dir: Path
    worktrees_dir: Path
    personal_templates_dir: Path
    memory_index_path: Path
    context_dir: Path
    user_context_path: Path
    project_context_path: Path
    task_context_path: Path

    @classmethod
    def ensure(cls, root: Path) -> LoopWorkspaceLayout:
        resolved = root.resolve()
        if resolved.parent == resolved:
            raise ValueError(
                "Requested loop workspace path is invalid or outside an existing workspace boundary."
            )
        instance = cls(
            root=resolved,
            state_file=resolved / "LOOP-STATE.json",
            memory_dir=resolved / "memory",
            skills_dir=resolved / "skills",
            artifacts_dir=resolved / "artifacts",
            worktrees_dir=resolved / "worktrees",
            personal_templates_dir=resolved / "personal_templates",
            memory_index_path=resolved / "memory" / "INDEX.md",
            context_dir=resolved / "context",
            user_context_path=resolved / "context" / "user.md",
            project_context_path=resolved / "context" / "project.md",
            task_context_path=resolved / "context" / "task.md",
        )
        instance.state_file.parent.mkdir(parents=True, exist_ok=True)
        for path in [
            instance.memory_dir,
            instance.skills_dir,
            instance.artifacts_dir,
            instance.worktrees_dir,
            instance.personal_templates_dir,
            instance.context_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)
        instance.memory_index_path.parent.mkdir(parents=True, exist_ok=True)
        if not instance.memory_index_path.exists():
            instance.memory_index_path.write_text("# LoopDesk Memory Index\n\n", encoding="utf-8")
        for context_path in [
            instance.user_context_path,
            instance.project_context_path,
            instance.task_context_path,
        ]:
            if not context_path.exists():
                context_path.write_text("", encoding="utf-8")
        return instance

    def require_under_workspace(self, path: Path) -> Path:
        resolved = Path(path).resolve()
        if not str(resolved).startswith(str(self.root.resolve())):
            raise ValueError("Requested path is outside the loop workspace.")
        return resolved
