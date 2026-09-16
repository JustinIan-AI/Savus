"""Durable repository for loop workspace state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from loopdesk.loop_workspace.schema import LoopWorkspaceState
from loopdesk.loop_workspace.serialization import dump_loop_state


class LoopWorkspaceRepository:
    def __init__(self, layout: "LoopWorkspaceLayout") -> None:
        self._layout = layout

    def read(self) -> LoopWorkspaceState:
        payload = json.loads(self._layout.state_file.read_text(encoding="utf-8"))
        return LoopWorkspaceState.from_dict(payload)

    def write(self, state: LoopWorkspaceState) -> None:
        state.updated_at = _utc_now()
        self._layout.state_file.write_text(
            json.dumps(state.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def update(self, mutator) -> LoopWorkspaceState:
        state = self.read()
        mutator(state)
        self.write(state)
        return state

    def append_run_log(self, run_log: dict[str, Any]) -> LoopWorkspaceState:
        return self.update(lambda state: state.append_run_log(run_log))


def _utc_now() -> str:
    from datetime import datetime

    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
