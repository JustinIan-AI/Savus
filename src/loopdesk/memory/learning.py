from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class RejectionSignal:
    task_id: str
    phase: str
    reason: str
    reverted_patch: str

@dataclass
class KBHealth:
    score: float
    stale_rules_count: int

class ContinuousLearningEngine:
    """Captures human gate rejections and distillations to improve rules and prompt templates."""
    def __init__(self) -> None:
        self.rejection_signals: List[RejectionSignal] = []
        self._rules_registry: List[Dict[str, Any]] = []

    def record_rejection(self, signal: RejectionSignal) -> None:
        self.rejection_signals.append(signal)

    def register_rule(self, rule_id: str, content: str, created_at: float | None = None) -> None:
        self._rules_registry.append({
            "id": rule_id,
            "content": content,
            "created_at": created_at or time.time()
        })

    def flush_insights(self) -> List[Dict[str, Any]]:
        insights = []
        for sig in self.rejection_signals:
            suggestion = f"Add boundary validation rule to avoid {sig.reason}"
            insights.append({
                "task_id": sig.task_id,
                "rule_suggestion": suggestion
            })
        self.rejection_signals.clear()
        return insights

    def get_kb_health(self) -> KBHealth:
        """Dynamically assesses Knowledge Base health based on rejection signals and rule recency."""
        rejection_count = len(self.rejection_signals)
        # Deduct score for each active unresolved rejection
        base_score = 100.0 - min(40.0, rejection_count * 10.0)
        
        # Check rule recency (> 30 days = stale)
        now = time.time()
        stale_count = 0
        for r in self._rules_registry:
            if (now - r.get("created_at", now)) > 30 * 86400:
                stale_count += 1

        score = max(20.0, base_score - (stale_count * 5.0))
        return KBHealth(score=round(score, 1), stale_rules_count=stale_count)
