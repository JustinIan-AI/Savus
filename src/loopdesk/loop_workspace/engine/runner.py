"""Loop Engine runner for LoopDesk."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from loopdesk.loop_workspace.engine.state_machine import LoopEngineState, LoopEngineStateMachine, LoopPhase
from loopdesk.loop_workspace.service import _utc_now


Handler = Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]]


class LoopEngineRunner:
    def __init__(self, service, handlers: Dict[str, Handler] | None = None) -> None:
        self._service = service
        self._handlers = {
            "triage": self._noop_handler,
            "maker": self._noop_handler,
            "checker": self._noop_handler,
            **(handlers or {}),
        }

    def step(self, state: LoopEngineState, decision: str | None = None, checker_passed: bool = False) -> LoopEngineState:
        if state.phase == LoopPhase.TRIAGE:
            self._handlers.get("triage", self._noop_handler)("triage", {"goal": state.goal})
        if state.phase == LoopPhase.MAKER:
            self._handlers.get("maker", self._noop_handler)("maker", {"goal": state.goal})
        if state.phase == LoopPhase.CHECKER:
            self._handlers.get("checker", self._noop_handler)("checker", {"goal": state.goal})
        if state.phase in {LoopPhase.COMPLETED, LoopPhase.FAILED, LoopPhase.PAUSED, LoopPhase.ESCALATION}:
            return state
        if self._is_budget_exceeded() or self._service.repository.read().kill_switch_enabled():
            paused = LoopEngineState(
                phase=LoopPhase.PAUSED,
                goal=state.goal,
                stop_condition=state.stop_condition,
                max_iterations=state.max_iterations,
                current_iteration=state.current_iteration,
                escalation_reason="paused by budget or kill switch",
            )
            self._record_run_log(state, paused)
            return paused
        next_state = LoopEngineStateMachine.transition(state, decision=decision, checker_passed=checker_passed)
        self._record_run_log(state, next_state)
        return next_state

    def run(self, state: LoopEngineState, decision: str | None = None, checker_passed: bool = False) -> LoopEngineState:
        return self.step(state, decision=decision, checker_passed=checker_passed)

    @staticmethod
    def _noop_handler(phase: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {"phase": phase, "status": "ok", "payload": payload or {}}

    def _record_run_log(self, state: LoopEngineState, next_state: LoopEngineState) -> None:
        self._service.record_run_log(
            {
                "source": "loop-engine",
                "workId": next_state.goal,
                "status": state.phase.value,
                "summary": f"{state.phase.value} completed.",
                "previousStatus": None,
                "toolEvent": {
                    "phase": state.phase.value,
                    "goal": next_state.goal,
                    "stop_condition": next_state.stop_condition,
                    "current_iteration": state.current_iteration,
                    "next_phase": next_state.phase.value,
                    "escalation_reason": next_state.escalation_reason,
                },
            }
        )
        persisted = self._service.repository.read()
        persisted.loop_engine = {
            "phase": next_state.phase.value,
            "goal": next_state.goal,
            "stop_condition": next_state.stop_condition,
            "max_iterations": next_state.max_iterations,
            "current_iteration": next_state.current_iteration,
            "escalation_reason": next_state.escalation_reason,
        }
        self._service.repository.write(persisted)

    def _is_budget_exceeded(self) -> bool:
        cost_observatory = self._service.repository.read().cost_observatory
        budget_cap = float(cost_observatory.get("budget_cap_usd") or 0.0)
        spend = float(cost_observatory.get("spend_usd") or 0.0)
        return budget_cap > 0 and spend > budget_cap
