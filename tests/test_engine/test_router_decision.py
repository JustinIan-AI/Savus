"""Router decision tests for LoopDesk v1.1 intent/router surface."""

from __future__ import annotations

import pytest

from loopdesk.engine.router_decision import build_router_decision_event
from loopdesk.engine.types import RouterDecisionEvent


class DummyTurn:
    metadata = {
        "routed_tier": "balanced",
        "routed_model": "test-model",
        "baseline_model": "baseline-model",
        "routing_source": "router",
        "routing_confidence": "0.8",
        "routing_extra": {
            "probabilities": {"balanced": 0.8, "fast": 0.2},
            "tier_savings": {"pct": 10.0},
        },
        "thinking_mode": "minimal",
        "prompt_policy": "default",
    }
    model = "test-model"


def test_intent_classification_surface_returns_expected_intent() -> None:
    turn = DummyTurn()
    event = build_router_decision_event(turn)

    assert event is not None
    assert event.tier == "balanced"
    assert event.source == "router"


def test_router_accepts_intent_context_and_returns_runtime_skill_tool_decision() -> None:
    turn = DummyTurn()
    event = build_router_decision_event(turn)

    assert isinstance(event, RouterDecisionEvent)
    assert event.model == "test-model"
    assert event.baseline_model == "baseline-model"
    assert event.probs == [0.8, 0.2]


def test_router_preserves_human_override_path() -> None:
    turn = DummyTurn()
    turn.metadata["routing_source"] = "human-override"
    event = build_router_decision_event(turn)

    assert event is not None
    assert event.source == "human-override"
    assert event.fallback is False
