"""Serialization helpers for loop workspace state."""

from __future__ import annotations

import json
from pathlib import Path

from loopdesk.loop_workspace.schema import LoopWorkspaceState


def load_loop_state(path: Path) -> LoopWorkspaceState:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return LoopWorkspaceState.model_validate(payload)


def dump_loop_state(path: Path, state: LoopWorkspaceState) -> None:
    payload = json.dumps(state.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == payload:
        return
    path.write_text(payload, encoding="utf-8")
