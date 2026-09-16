"""Loop Engine state machine for LoopDesk."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LoopPhase(str, Enum):
    PLANNED = "planned"
    TRIAGE = "triage"
    MAKER = "maker"
    CHECKER = "checker"
    ESCALATION = "escalation"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass(frozen=True)
class LoopEngineState:
    phase: LoopPhase = LoopPhase.PLANNED
    goal: str | None = None
    stop_condition: str | None = None
    max_iterations: int = 10
    current_iteration: int = 0
    triage_result: dict[str, Any] | None = None
    maker_result: dict[str, Any] | None = None
    checker_result: dict[str, Any] | None = None
    escalation_reason: str | None = None


class LoopEngineStateMachine:
    @classmethod
    def transition(cls, state: LoopEngineState, decision: str | None = None, checker_passed: bool = False) -> LoopEngineState:
        phase = state.phase
        if phase == LoopPhase.PLANNED:
            return LoopEngineState(phase=LoopPhase.TRIAGE, goal=state.goal, stop_condition=state.stop_condition, max_iterations=state.max_iterations, current_iteration=state.current_iteration, escalation_reason="No concrete goal provided." if not state.goal else None)

        if phase == LoopPhase.TRIAGE:
            if decision == "escalate" or not state.goal:
                return LoopEngineState(phase=LoopPhase.ESCALATION, goal=state.goal, stop_condition=state.stop_condition, max_iterations=state.max_iterations, current_iteration=state.current_iteration, escalation_reason=state.escalation_reason or "Triage could not form a concrete goal.")
            return LoopEngineState(phase=LoopPhase.MAKER, goal=state.goal, stop_condition=state.stop_condition, max_iterations=state.max_iterations, current_iteration=state.current_iteration, triage_result={"decision": decision or "act"})

        if phase == LoopPhase.MAKER:
            return LoopEngineState(phase=LoopPhase.CHECKER, goal=state.goal, stop_condition=state.stop_condition, max_iterations=state.max_iterations, current_iteration=state.current_iteration + 1, maker_result={"status": "produced"})

        if phase == LoopPhase.CHECKER:
            if checker_passed:
                return LoopEngineState(phase=LoopPhase.COMPLETED, goal=state.goal, stop_condition=state.stop_condition, max_iterations=state.max_iterations, current_iteration=state.current_iteration, checker_result={"passed": True})
            if state.current_iteration + 1 >= state.max_iterations:
                return LoopEngineState(phase=LoopPhase.FAILED, goal=state.goal, stop_condition=state.stop_condition, max_iterations=state.max_iterations, current_iteration=state.current_iteration + 1, checker_result={"passed": False}, escalation_reason="Max iterations exceeded.")
            return LoopEngineState(phase=LoopPhase.MAKER, goal=state.goal, stop_condition=state.stop_condition, max_iterations=state.max_iterations, current_iteration=state.current_iteration + 1, checker_result={"passed": False})

        if phase in {LoopPhase.ESCALATION, LoopPhase.FAILED, LoopPhase.COMPLETED, LoopPhase.PAUSED}:
            return state

        return state
