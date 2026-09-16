"""F1/F3/F4/F5 failing tests for LoopDesk v1.2 runtime contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

from loopdesk.engine.router_decision import build_router_decision_envelope
from loopdesk.engine.types import (
    ContextPackSchema,
    ExecutionTrace,
    PlannerOutput,
    RuntimeInterfaceContract,
    RouterDecisionEnvelope,
    TraceQuery,
)


class DummyTurn:
    def __init__(self, metadata: dict[str, object]) -> None:
        self.metadata = metadata
        self.model = metadata.get("routed_model", "")


def test_runtime_interface_contract_is_explicit_and_enforceable() -> None:
    contract = RuntimeInterfaceContract(
        runtime_id="codex-cli",
        execute_input_schema={"task": "object", "workspace": "object"},
        resume_input_schema={"run_id": "string"},
        status_output_schema={"run_id": "string", "status": "string"},
        cancel_output_schema={"run_id": "string", "canceled": "bool"},
        inspect_output_schema={"run_id": "string", "artifacts": "array"},
        capability_profile_keys=["execution", "resume", "status", "cancel", "inspect"],
    )

    assert contract.runtime_id == "codex-cli"
    assert "resume" in contract.capability_profile_keys
    assert contract.enforced is True


def test_planner_output_can_start_with_ordered_tasks_and_defer_dag_enforcement() -> None:
    planned = PlannerOutput(
        goal_id="goal-1",
        intent="planning",
        summary="Migrate order service.",
        task_graph=[
            {"id": "analyze", "depends_on": []},
            {"id": "migrate", "depends_on": ["analyze"]},
            {"id": "verify", "depends_on": ["migrate"]},
        ],
        dag_enforced=False,
    )

    assert planned.tasks == ["analyze", "migrate", "verify"]
    assert planned.next_task_id == "analyze"
    assert planned.dag_enforced is False


def test_context_pack_schema_requires_user_project_task_with_compact_strategy() -> None:
    schema = ContextPackSchema(
        include=["user", "project", "task", "intent", "recent_run_log"],
        compact_strategy="ordered_then_summary",
        max_user_chars=400,
        max_project_chars=1200,
        max_task_chars=800,
    )

    assert list(schema.required_context_keys) == ["user", "project", "task"]
    assert schema.compact_strategy == "ordered_then_summary"


def test_loop_workspace_persists_v12_context_and_planner_contract(tmp_path: Path) -> None:
    from loopdesk.loop_workspace.service import LoopWorkspaceService

    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()

    updated = service.update_context_pack_schema(
        {
            "include": ["user", "project", "task", "intent"],
            "compact_strategy": "ordered_then_summary",
            "max_user_chars": 400,
            "max_project_chars": 1200,
            "max_task_chars": 800,
        }
    )
    planned = service.create_goal_from_planner(
        goal_id="goal-1",
        summary="Migrate order service.",
        task_graph=[
            {"id": "analyze", "depends_on": []},
            {"id": "migrate", "depends_on": ["analyze"]},
        ],
    )

    assert updated["context_pack_schema"]["compact_strategy"] == "ordered_then_summary"
    assert updated["planner_output"]["dag_enforced"] is False
    assert planned["planner_output"]["next_task_id"] == "analyze"


def test_context_compaction_keeps_required_keys_and_bounded_size(tmp_path: Path) -> None:
    from loopdesk.loop_workspace.service import LoopWorkspaceService

    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()
    service.update_work_item(
        work_id="work-1",
        source="loop",
        summary="Heavy context work.",
        context_pack={
            "user": "u" * 500,
            "project": "p" * 1500,
            "task": "t" * 1000,
        },
    )

    compacted = service.compact_context_pack(goal_id="work-1")

    assert set(compacted.keys()) >= {"user", "project", "task"}
    assert len(compacted["user"]) <= 400
    assert compacted["project"].startswith("p")
    assert compacted["task"].startswith("t")


def test_execution_trace_records_runtime_skill_tool_and_human_override() -> None:
    trace = ExecutionTrace(
        trace_id="trace-1",
        goal_id="goal-1",
        loop_id="loop-1",
        runtime_id="codex-cli",
        skill_id="architecture-review",
        tool_name="read_file",
        action="Read order service module.",
        result="success",
        duration_ms=1200,
        cost_usd=0.04,
        decision="continue",
        approval_required=False,
        override_source=None,
    )

    assert trace.tool_name == "read_file"
    assert trace.skill_id == "architecture-review"
    assert trace.human_override is False


def test_run_log_supports_query_by_goal_loop_and_time_range() -> None:
    query = TraceQuery(goal_id="goal-1", loop_id="loop-1", time_range="7d")

    assert query.goal_id == "goal-1"
    assert query.loop_id == "loop-1"
    assert query.time_range == "7d"


def test_router_decision_event_carries_task_routing_and_approval_metadata() -> None:
    turn = DummyTurn(
        metadata={
            "routed_tier": "balanced",
            "routed_model": "test-model",
            "baseline_model": "baseline-model",
            "routing_source": "router",
            "routing_confidence": "0.8",
            "routing_extra": {"probabilities": {"balanced": 0.8, "fast": 0.2}},
            "thinking_mode": "minimal",
            "prompt_policy": "default",
            "goal_id": "goal-1",
            "loop_id": "loop-1",
            "trace_id": "trace-1",
            "task_routing_decision": {
                "path": "runtime+skill",
                "runtime_id": "codex-cli",
                "skill_id": "architecture-review",
                "tool_name": "read_file",
                "approval_required": False,
            },
        }
    )

    event = build_router_decision_envelope(turn)

    assert type(event).__name__ == "RouterDecisionEnvelope"
    assert event.task_routing_decision["path"] == "runtime+skill"
    assert event.task_routing_decision["approval_required"] is False
    assert event.approval_required is False


def test_human_override_can_reroute_task_execution_without_changing_model_tier() -> None:
    turn = DummyTurn(
        metadata={
            "routed_tier": "balanced",
            "routed_model": "test-model",
            "baseline_model": "baseline-model",
            "routing_source": "human-override",
            "routing_confidence": "0.0",
            "routing_extra": {},
            "task_routing_decision": {
                "path": "runtime",
                "runtime_id": "claude-code",
                "approval_required": True,
                "override_reason": "Use coding runtime for patch review.",
            },
        }
    )

    event = build_router_decision_envelope(turn)

    assert event.task_routing_decision["runtime_id"] == "claude-code"
    assert event.task_routing_decision["approval_required"] is True
    assert event.model == "test-model"


def test_unbounded_automatic_routing_remains_blocked() -> None:
    turn = DummyTurn(
        metadata={
            "routed_tier": "balanced",
            "routed_model": "test-model",
            "session_key": "session-1",
            "baseline_model": "baseline-model",
            "routing_source": "router",
            "routing_confidence": "0.9",
            "routing_extra": {},
            "approved_runtime_ids": ["claude-code", "codex-cli"],
            "task_routing_decision": {
                "path": "unbounded-auto",
                "approval_required": False,
                "runtime_id": "any-runtime",
            },
        }
    )

    with pytest.raises(ValueError, match="unbounded automatic routing is not allowed"):
        build_router_decision_envelope(turn)
    event = build_router_decision_envelope(
        DummyTurn(
            metadata={
                "routed_tier": "balanced",
                "routed_model": "test-model",
                "baseline_model": "baseline-model",
                "routing_source": "router",
                "routing_confidence": "0.9",
                "routing_extra": {},
                "task_routing_decision": {
                    "path": "runtime",
                    "approval_required": True,
                },
            }
        )
    )
    assert event.task_routing_decision["path"] == "runtime"
