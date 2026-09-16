"""F3/F4 tests for LoopDesk v1.1 intent/router, task planner, and learning loop."""

from __future__ import annotations

from pathlib import Path

from loopdesk.engine.router_decision import build_router_decision_event, classify_intent
from loopdesk.engine.types import RouterDecisionEvent
from loopdesk.loop_workspace.schema import LoopWorkspaceState
from loopdesk.loop_workspace.service import LoopWorkspaceService


class DummyTurn:
    metadata = {
        "routed_tier": "balanced",
        "routed_model": "test-model",
        "baseline_model": "baseline-model",
        "routing_source": "router",
        "routing_confidence": "0.8",
        "routing_extra": {"probabilities": {"balanced": 0.8, "fast": 0.2}},
        "thinking_mode": "minimal",
        "prompt_policy": "default",
    }
    model = "test-model"
    session_key = "agent:main:cli:user"


def test_intent_classification_surface_returns_expected_intent() -> None:
    assert classify_intent("请帮我重构订单系统架构") == "planning"
    assert classify_intent("review 当前接口设计") == "planning"
    assert classify_intent("执行数据迁移并发布") == "execution"
    assert classify_intent("继续当前工作") == "continuity"
    assert classify_intent("") == "unknown"


def test_router_accepts_intent_context_and_returns_runtime_skill_tool_decision() -> None:
    turn = DummyTurn()
    event = build_router_decision_event(turn)

    assert isinstance(event, RouterDecisionEvent)
    assert event.tier == "balanced"
    assert event.probs == [0.8, 0.2]
    assert event.session_key == "agent:main:cli:user"


def test_router_preserves_human_override_path() -> None:
    turn = DummyTurn()
    turn.metadata["routing_source"] = "human-override"
    event = build_router_decision_event(turn)

    assert event is not None
    assert event.source == "human-override"
    assert event.fallback is False


def test_task_graph_supports_dag_nodes_and_dependencies(tmp_path: Path) -> None:
    state = LoopWorkspaceState.create(
        workspace_root=str(tmp_path),
        task_graph=[
            {"id": "task-1", "depends_on": [], "runtime": "planner"},
            {"id": "task-2", "depends_on": ["task-1"], "runtime": "maker"},
        ],
    )

    assert state.task_graph[0]["id"] == "task-1"
    assert state.task_graph[1]["depends_on"] == ["task-1"]
    restored = LoopWorkspaceState.from_dict(state.to_dict())
    assert len(restored.task_graph) == 2


def test_continuous_learning_loop_flushes_completed_goal_into_memory(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()
    service.record_work_item("work-1", "loop", "Refactor order system.")
    state = service.record_learning_loop_flush(
        {
            "source": "loop-engine",
            "workId": "work-1",
            "status": "completed",
            "summary": "Architecture accepted.",
            "learning_loop": {
                "stage": "improve",
                "memory_target": "memory/decisions/order-system-architecture.md",
                "skill_candidates": ["architecture-review", "release-check"],
            },
        }
    )

    learning_entry = state["learning_loops"][-1]
    run_entry = state["run_log"][-1]

    assert learning_entry["status"] == "completed"
    assert learning_entry["learning_loop"]["stage"] == "improve"
    assert learning_entry["learning_loop"]["memory_target"] == "memory/decisions/order-system-architecture.md"
    assert run_entry["learning_loop"]["stage"] == "improve"


def test_task_planner_output_can_create_goal_with_worktree(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()
    planned = service.create_goal_from_planner(
        goal_id="goal-1",
        summary="Migrate order service.",
        task_graph=[
            {"id": "analyze", "depends_on": []},
            {"id": "migrate", "depends_on": ["analyze"]},
        ],
    )

    assert planned["current_work_id"] == "goal-1"
    assert planned["task_graph"][0]["id"] == "analyze"
    worktree_state = service.create_worktree("goal-1", branch="loopdesk/goal/goal-1")
    assert worktree_state["workId"] == "goal-1"
    assert worktree_state["branch"] == "loopdesk/goal/goal-1"
    assert (tmp_path / "worktrees" / "goal-1").exists()


def _init_git_repo(path: Path) -> None:
    import subprocess

    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "dev@example.com"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Dev"], cwd=path, check=True, capture_output=True)
    (path / "README.md").write_text("loopdesk", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=path, check=True, capture_output=True)
