"""Router decision event construction."""

from __future__ import annotations

from typing import Any, cast

from loopdesk.engine.pipeline import TurnContext
from loopdesk.engine.types import PlannerOutput, RouterDecisionEnvelope, RouterDecisionEvent
from loopdesk.router_tiers import normalize_text_tier, tier_index


def classify_intent(message: str) -> str:
    normalized = (message or "").strip().lower()
    if not normalized:
        return "unknown"
    planning_keywords = [
        "plan",
        "重构",
        "设计",
        "review",
        "评审",
        "拆解",
        "分解",
        "目标",
        "goal",
        "task",
        "架构",
    ]
    if any(keyword in normalized for keyword in planning_keywords):
        return "planning"
    execution_keywords = [
        "implement",
        "修复",
        "实现",
        "执行",
        "运行",
        "运行",
        "deploy",
        "发布",
        "提交",
    ]
    if any(keyword in normalized for keyword in execution_keywords):
        return "execution"
    return "continuity"


def _coerce_probs(value: object) -> list[float]:
    if isinstance(value, dict):
        items = sorted(value.items(), key=lambda item: str(item[0]))
        raw_values = [item_value for _item_key, item_value in items]
    elif isinstance(value, list | tuple):
        raw_values = list(value)
    else:
        raw_values = []

    probs: list[float] = []
    for raw_value in raw_values[:4]:
        try:
            probs.append(float(raw_value))
        except (TypeError, ValueError):
            probs.append(0.0)
    return probs


def _coerce_float(value: object, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(cast(Any, value))
    except (TypeError, ValueError):
        return default


def build_router_decision_event(turn: TurnContext) -> RouterDecisionEvent | None:
    """Construct a RouterDecisionEvent from post-pipeline turn metadata."""

    routed_tier = turn.metadata.get("routed_tier")
    if not routed_tier:
        return None

    extra = turn.metadata.get("routing_extra")
    if not isinstance(extra, dict):
        extra = {}

    probs = _coerce_probs(extra.get("probabilities", extra.get("probs")))

    tier_savings = extra.get("tier_savings")
    savings_pct = _coerce_float(turn.metadata.get("savings_pct"))
    if isinstance(tier_savings, dict):
        savings_pct = savings_pct or _coerce_float(tier_savings.get("pct"))

    routed_tier = normalize_text_tier(routed_tier) or routed_tier
    tier_idx = tier_index(routed_tier)

    source = str(turn.metadata.get("routing_source") or "none")
    routing_applied = turn.metadata.get("routing_applied")
    if routing_applied is None:
        routing_applied = True

    return RouterDecisionEvent(
        tier=str(routed_tier),
        tier_index=tier_idx,
        model=str(turn.metadata.get("routed_model") or turn.model or ""),
        baseline_model=str(turn.metadata.get("baseline_model") or ""),
        source=source,
        confidence=float(turn.metadata.get("routing_confidence") or 0.0),
        probs=probs,
        savings_pct=savings_pct,
        fallback=source == "fallback",
        thinking_mode=str(turn.metadata.get("thinking_mode") or ""),
        prompt_policy=str(turn.metadata.get("prompt_policy") or ""),
        routing_applied=bool(routing_applied),
    rollout_phase=str(turn.metadata.get("rollout_phase") or "full"),
    session_key=str(getattr(turn, "session_key", "")),
)


def build_router_decision_envelope(turn: TurnContext) -> RouterDecisionEnvelope:
    """v1.2 task-level router boundary that keeps model-tier events separate."""

    event = build_router_decision_event(turn)
    if event is None:
        raise ValueError("router decision event is required for task-level routing")
    task_routing_decision = dict(turn.metadata.get("task_routing_decision") or {})
    envelope = RouterDecisionEnvelope(
        event=event,
        goal_id=str(turn.metadata.get("goal_id") or ""),
        loop_id=str(turn.metadata.get("loop_id") or ""),
        trace_id=str(turn.metadata.get("trace_id") or ""),
        task_routing_decision=task_routing_decision,
    )
    envelope.validate_runtime(
        PlannerOutput(
            goal_id=envelope.goal_id,
            approved_runtime_ids=list(turn.metadata.get("approved_runtime_ids") or []),
        )
    )
    return envelope
