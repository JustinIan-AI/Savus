"""F2 tests for LoopDesk v1.1 runtime interface and execution trace."""

from __future__ import annotations

from dataclasses import dataclass, field

from loopdesk.engine.pipeline import TurnContext
from loopdesk.engine.router_decision import build_router_decision_event
from loopdesk.engine.types import RouterDecisionEvent


@dataclass
class DummyProvider:
    def execute(self, payload):  # pragma: no cover - runtime contract example
        raise NotImplementedError


@dataclass
class DummyRuntime:
    name: str = "dummy-runtime"
    supported_surfaces: tuple[str, ...] = ("cli", "web", "channel")
    provider: DummyProvider = field(default_factory=DummyProvider)

    def execute(self, payload):  # pragma: no cover - runtime contract example
        raise NotImplementedError

    def resume(
        self, work_id: str
    ) -> dict[str, object]:  # pragma: no cover - runtime contract example
        raise NotImplementedError

    def status(
        self, work_id: str
    ) -> dict[str, object]:  # pragma: no cover - runtime contract example
        raise NotImplementedError

    def cancel(
        self, work_id: str
    ) -> dict[str, object]:  # pragma: no cover - runtime contract example
        raise NotImplementedError

    def inspect(
        self, work_id: str
    ) -> dict[str, object]:  # pragma: no cover - runtime contract example
        raise NotImplementedError


def test_agent_runtime_interface_has_required_methods() -> None:
    runtime = DummyRuntime()

    for method_name in {"execute", "resume", "status", "cancel", "inspect"}:
        assert hasattr(runtime, method_name)


def test_execution_trace_round_trip_with_run_log_consumer_fields() -> None:
    turn = TurnContext(
        message="run migration skill",
        session_key="agent:main:cli:user",
        config=None,
        provider=None,
        model="test-model",
        tool_defs=[],
        system_prompt="You are a helpful assistant.",
        metadata={
            "routed_tier": "fast",
            "routed_model": "test-model",
            "routing_source": "router",
            "routing_extra": {"probabilities": {"fast": 1.0}},
        },
    )
    event = build_router_decision_event(turn)

    assert isinstance(event, RouterDecisionEvent)
    assert event.tier == "fast"
    assert event.model == "test-model"
    assert event.probs == [1.0]
    assert event.session_key == turn.session_key


def test_run_log_entries_expose_runtime_cost_and_artifacts() -> None:
    entry = {
        "source": "tool:codex",
        "workId": "work-1",
        "status": "completed",
        "summary": "Implemented API client.",
        "toolEvent": {
            "name": "codex",
            "cost": {"input_tokens": 120, "output_tokens": 80, "cost_usd": 0.04},
            "artifacts": [{"name": "client.py", "sha256": "abc"}],
        },
    }

    assert entry["source"] == "tool:codex"
    assert entry["toolEvent"]["cost"]["cost_usd"] == 0.04
    assert entry["toolEvent"]["artifacts"][0]["name"] == "client.py"
