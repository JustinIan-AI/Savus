"""Loop Engine runner tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from loopdesk.loop_workspace.engine.runner import LoopEngineRunner
from loopdesk.loop_workspace.engine.state_machine import LoopEngineState, LoopPhase
from loopdesk.loop_workspace.service import LoopWorkspaceService


def test_runner_executes_one_step_and_records_run_log(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    runner = LoopEngineRunner(service)
    state = LoopEngineState(phase=LoopPhase.TRIAGE, goal="X")
    result = runner.step(state, decision="act")

    assert result.phase == LoopPhase.MAKER
    assert len(service.repository.read().run_log) == 1
    assert service.repository.read().run_log[-1]["summary"] == "triage completed."
    assert service.repository.read().run_log[-1]["toolEvent"]["next_phase"] == "maker"
