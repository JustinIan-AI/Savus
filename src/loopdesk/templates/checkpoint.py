from __future__ import annotations

from typing import Any, Dict, List, Optional

class NoProgressException(Exception):
    """Raised when the loop fails to make progress for consecutive turns."""
    pass

class CheckpointManager:
    """Manages execution checkpoints and supports rewinding state."""
    def __init__(self) -> None:
        self._checkpoints: Dict[str, Dict[str, Any]] = {}
        self._order: List[str] = []
        self.current_step: Optional[str] = None

    def save_checkpoint(self, step_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        self._checkpoints[step_id] = state.copy()
        if step_id not in self._order:
            self._order.append(step_id)
        self.current_step = step_id
        return self._checkpoints[step_id]

    def list_checkpoints(self) -> List[str]:
        return list(self._order)

    def rewind_to(self, step_id: str) -> Dict[str, Any]:
        if step_id not in self._checkpoints:
            raise KeyError(f"Checkpoint {step_id} not found")
        
        idx = self._order.index(step_id)
        # Prune checkpoints that occurred after step_id
        for abandoned_step in self._order[idx + 1:]:
            self._checkpoints.pop(abandoned_step, None)
        self._order = self._order[:idx + 1]
        self.current_step = step_id
        return self._checkpoints[step_id]

class HandoffPacket:
    """Encapsulates minimal, high-fidelity context for cross-agent or cross-session transfer."""
    def __init__(
        self,
        task_id: str,
        goal: str,
        current_step: str,
        evidence_summary: List[str],
        environment_snapshot: Dict[str, Any],
    ) -> None:
        self.task_id = task_id
        self.goal = goal
        self.current_step = current_step
        self.evidence_summary = evidence_summary
        self.environment_snapshot = environment_snapshot

    def to_compact_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "goal": self.goal,
            "current_step": self.current_step,
            "evidence": self.evidence_summary,
            "env": self.environment_snapshot,
        }

class NoProgressBreaker:
    """Breaker that trips when successive execution turns yield no concrete progress."""
    def __init__(self, max_unproductive_turns: int = 3) -> None:
        self.max_unproductive_turns = max_unproductive_turns
        self.consecutive_unproductive = 0
        self._tripped = False

    def record_turn(self, has_progress: bool, evidence: str = "") -> None:
        if has_progress or bool(evidence.strip()):
            self.consecutive_unproductive = 0
            self._tripped = False
        else:
            self.consecutive_unproductive += 1
            if self.consecutive_unproductive >= self.max_unproductive_turns:
                self._tripped = True
                raise NoProgressException(
                    f"No progress made for {self.consecutive_unproductive} consecutive turns. Breaker tripped."
                )

    def is_tripped(self) -> bool:
        return self._tripped
