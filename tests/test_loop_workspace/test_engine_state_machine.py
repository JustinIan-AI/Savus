"""Loop Engine state machine tests."""

from __future__ import annotations

import pytest

from loopdesk.loop_workspace.engine.state_machine import LoopEngineState, LoopEngineStateMachine, LoopPhase


def test_state_machine_allows_triage_to_maker_when_goal_is_concrete() -> None:
    state = LoopEngineState(phase=LoopPhase.TRIAGE, goal="Fix login bug")
    result = LoopEngineStateMachine.transition(state, decision="act")

    assert result.phase == LoopPhase.MAKER
    assert result.goal == "Fix login bug"
    assert result.triage_result == {"decision": "act"}


def test_state_machine_escalates_when_triage_cannot_form_goal() -> None:
    state = LoopEngineState(phase=LoopPhase.TRIAGE, goal=None)
    result = LoopEngineStateMachine.transition(state, decision="escalate")

    assert result.phase == LoopPhase.ESCALATION
    assert result.escalation_reason == "Triage could not form a concrete goal."


def test_state_machine_retries_maker_until_max_iterations() -> None:
    state = LoopEngineState(phase=LoopPhase.CHECKER, goal="Fix bug", max_iterations=2, current_iteration=1)
    result = LoopEngineStateMachine.transition(state, decision=None, checker_passed=False)

    assert result.phase == LoopPhase.FAILED
    assert result.current_iteration == 2
