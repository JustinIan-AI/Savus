from __future__ import annotations

import pytest
from loopdesk.memory.learning import ContinuousLearningEngine, RejectionSignal

def test_continuous_learning_flush():
    engine = ContinuousLearningEngine()

    # Ingest a human gate rejection
    signal = RejectionSignal(
        task_id="task-99",
        phase="checker_gate",
        reason="Missing unit test for invalid input boundary",
        reverted_patch="def test(): pass"
    )

    engine.record_rejection(signal)
    
    # Process feedback and suggest new rule
    insights = engine.flush_insights()
    assert len(insights) == 1
    assert "boundary" in insights[0]["rule_suggestion"].lower()

    # Check KB Health score
    health = engine.get_kb_health()
    assert 0.0 <= health.score <= 100.0
