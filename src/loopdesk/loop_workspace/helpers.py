"""Filesystem helpers for personal loop workspaces."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.schema import LoopWorkspaceState, LoopWorkspaceStatus
from loopdesk.loop_workspace.serialization import dump_loop_state


def ensure_loop_workspace(
    root: Path,
    *,
    intent: str | None = None,
    selected_template: str | None = None,
    directories: Iterable[str] | None = None,
) -> LoopWorkspaceLayout:
    resolved = root.resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    state_path = resolved / "LOOP-STATE.json"
    if state_path.exists():
        state = LoopWorkspaceState.model_validate_json(state_path.read_text(encoding="utf-8"))
        state.workspace_root = str(resolved)
        if intent is not None:
            state.intent = intent
        if selected_template is not None:
            state.selected_template = selected_template
        state.updated_at = _utc_now()
        dump_loop_state(state_path, state)
    else:
        state = LoopWorkspaceState(
            workspace_root=str(resolved),
            intent=intent,
            selected_template=selected_template,
            status=LoopWorkspaceStatus.PLANNED,
        )
        dump_loop_state(state_path, state)
    for directory in directories or ("memory", "skills", "artifacts", "worktrees", "personal_templates", "context"):
        (resolved / directory).mkdir(exist_ok=True)
    memory_index = resolved / "memory" / "INDEX.md"
    if memory_index.exists() and not state_path.exists():
        memory_index.write_text("# LoopDesk Memory Index\n\n", encoding="utf-8")
    return LoopWorkspaceLayout.ensure(resolved)


def _utc_now() -> str:
    from datetime import datetime

    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
