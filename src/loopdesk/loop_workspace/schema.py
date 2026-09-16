"""Loop workspace state schema and helper transitions."""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class LoopWorkspaceStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELED = "canceled"


class WorkspaceType(str, Enum):
    PROJECT = "project"
    PERSONAL = "personal"
    BUSINESS = "business"


class LoopWorkspaceState(BaseModel):
    """Portable source of truth for a personal loop workspace."""

    schema_version: int = 1
    workspace_root: str | None = None
    workspace_type: WorkspaceType = WorkspaceType.PROJECT
    project_name: str | None = None
    intent: str | None = None
    context: dict[str, Any] = Field(
        default_factory=lambda: {
            "user": {},
            "project": {},
            "task": {},
        }
    )
    status: LoopWorkspaceStatus = LoopWorkspaceStatus.PLANNED
    tags: list[str] = Field(default_factory=list)
    selected_template: str | None = None
    run_log: list[dict[str, Any]] = Field(default_factory=list)
    approvals: list[dict[str, Any]] = Field(default_factory=list)
    cost_observatory: dict[str, Any] = Field(
        default_factory=lambda: {
            "budget_cap_usd": 0.0,
            "spend_usd": 0.0,
            "request_count": 0,
            "last_event_at": None,
            "status": "ok",
        }
    )
    safety: dict[str, Any] = Field(
        default_factory=lambda: {
            "kill_switch_enabled": False,
            "denylist": [],
            "retained_worktrees": [],
        }
    )
    current_work_id: str | None = Field(
        default=None, description="Current frontend-facing work item id."
    )
    current_work_source: str | None = Field(
        default=None, description="Whether current work came from a Loop or external resume."
    )
    current_work_summary: str | None = None
    tasks: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Task collection the WebUI board reads. `current_work_id` is only the "
            "frontend-facing *cursor*; N tasks need N entries, so the board has a "
            "real collection instead of a single overwritten slot."
        ),
    )
    override_history: list[dict[str, Any]] = Field(default_factory=list)
    active_loop_id: str | None = Field(
        default=None,
        description="Active loop id selected for current handoff context.",
    )
    context_pack_schema: dict[str, Any] = Field(
        default_factory=lambda: {
            "include": ["user", "project", "task", "intent", "recent_run_log"],
            "compact_strategy": "ordered_then_summary",
            "max_user_chars": 400,
            "max_project_chars": 1200,
            "max_task_chars": 800,
        }
    )
    planner_output: dict[str, Any] = Field(default_factory=lambda: {"goal_id": "", "intent": "", "dag_enforced": False, "next_task_id": None})
    human_profile: dict[str, Any] = Field(
        default_factory=lambda: {
            "preferences": {},
            "coding_style": {},
            "architecture_preference": {},
            "decision_pattern": {},
            "review_standard": {},
        }
    )
    loop_engine: dict[str, Any] | None = None
    task_graph: list[dict[str, Any]] = Field(default_factory=list)
    learning_loops: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: _utc_now())
    updated_at: str = Field(default_factory=lambda: _utc_now())

    model_config = {"populate_by_name": True}

    @classmethod
    def create(cls, **data: Any) -> LoopWorkspaceState:
        coerced = {
            name: str(value) if name == "workspace_root" and not isinstance(value, str) else value
            for name, value in data.items()
        }
        return cls(**coerced)

    def to_dict(self) -> dict[str, Any]:
        return json.loads(self.model_dump_json())

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> LoopWorkspaceState:
        return cls.model_validate_json(json.dumps(payload))

    def serialize_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def serialize_json_payload(self, payload: object) -> str:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)

    def record_override(
        self, source: str, reason: str, previous_status: LoopWorkspaceStatus | None = None
    ) -> None:
        self.override_history.append(
            {
                "source": source,
                "reason": reason,
                "previous_status": previous_status.value if previous_status else None,
                "status": self.status.value,
                "updated_at": _utc_now(),
            }
        )
        self.updated_at = _utc_now()

    def append_run_log(self, entry: dict[str, Any]) -> None:
        run_log_entry = {
            "source": entry.get("source", "unknown"),
            "workId": entry.get("workId", self.current_work_id),
            "status": entry.get("status", self.status.value),
            "summary": entry.get("summary", ""),
            "previousStatus": entry.get("previousStatus"),
            "learning_loop": entry.get("learning_loop"),
            "toolEvent": entry.get("toolEvent") or {
                key: value
                for key, value in entry.items()
                if key not in {"source", "workId", "status", "summary", "previousStatus", "learning_loop"}
            },
            "updated_at": _utc_now(),
        }
        self.run_log = [*self.run_log[-49:], run_log_entry]
        self.current_work_id = run_log_entry["workId"]
        self.current_work_source = run_log_entry["source"]
        self.current_work_summary = run_log_entry["summary"]
        if run_log_entry["source"] != "loop-engine" and run_log_entry["status"] in {status.value for status in LoopWorkspaceStatus}:
            self.status = LoopWorkspaceStatus(run_log_entry["status"])
        if self._denylist_blocks_entry(run_log_entry):
            if self.status != LoopWorkspaceStatus.CANCELED:
                self.record_override(
                    source="denylist",
                    reason="Blocked by denylist.",
                    previous_status=self.status,
                )
                self.status = LoopWorkspaceStatus.CANCELED
            self.cost_observatory["status"] = "paused"
        elif self.cost_observatory.get("status") in {None, "ok", "paused"}:
            self.cost_observatory["status"] = self.status.value
        self.cost_observatory["request_count"] = self.cost_observatory.get("request_count", 0) + 1
        self.cost_observatory["last_event_at"] = _utc_now()
        self.updated_at = _utc_now()

    def _denylist_blocks_entry(self, entry: dict[str, Any]) -> bool:
        for value in entry.values():
            if isinstance(value, str) and self.denylist_contains(value):
                return True
            if isinstance(value, dict) and self._denylist_blocks_entry(value):
                return True
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and self.denylist_contains(item):
                        return True
                    if isinstance(item, dict) and self._denylist_blocks_entry(item):
                        return True
        return False

    def record_approval(self, approval: dict[str, Any]) -> None:
        approval.setdefault("updated_at", _utc_now())
        self.approvals = [entry for entry in self.approvals if entry.get("id") != approval.get("id")]
        self.approvals.append(approval)
        if approval.get("status") == "approved":
            self.cost_observatory["status"] = self.status.value
        self.updated_at = _utc_now()

    def record_cost(self, cost_payload: dict[str, Any]) -> None:
        cost = {
            key: cost_payload.get(key)
            for key in {
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "reasoning_tokens",
                "cached_tokens",
                "cache_read_tokens",
                "cache_write_tokens",
                "cost_usd",
                "billed_cost",
                "estimated_cost_usd",
                "model",
                "request_count",
                "cost_source",
            }
            if key in cost_payload
        }
        budget_cap = cost_payload.get("budget_cap_usd")
        if budget_cap is not None:
            self.cost_observatory["budget_cap_usd"] = float(budget_cap)
        spend_delta = float(cost.get("cost_usd") or cost.get("estimated_cost_usd") or 0.0)
        self.cost_observatory["spend_usd"] = round(self.cost_observatory.get("spend_usd", 0.0) + spend_delta, 8)
        request_count = cost.get("request_count")
        if request_count is not None:
            self.cost_observatory["request_count"] = self.cost_observatory.get("request_count", 0) + int(request_count)
        if self.kill_switch_enabled():
            self.cost_observatory["status"] = "paused"
        elif self.cost_observatory.get("status") in {None, "paused"}:
            self.cost_observatory["status"] = self.status.value
        budget_cap = self.cost_observatory.get("budget_cap_usd")
        if budget_cap and self.cost_observatory.get("spend_usd", 0.0) > float(budget_cap):
            if self.status != LoopWorkspaceStatus.CANCELED:
                self.record_override(
                    source="cost-observatory",
                    reason="Budget cap exceeded.",
                    previous_status=self.status,
                )
                self.status = LoopWorkspaceStatus.CANCELED
            self.cost_observatory["status"] = "paused"
        self.updated_at = _utc_now()

    def set_kill_switch(self, enabled: bool) -> None:
        self.safety["kill_switch_enabled"] = bool(enabled)
        self.cost_observatory["status"] = "paused" if enabled else self.status.value
        self.updated_at = _utc_now()

    def set_denylist(self, denylist: list[str]) -> None:
        self.safety["denylist"] = sorted({entry.strip() for entry in denylist if str(entry).strip()})
        self.updated_at = _utc_now()

    def retain_worktree(self, worktree_path: str) -> None:
        retained = [entry for entry in self.safety.get("retained_worktrees", []) if entry != worktree_path]
        retained.append(worktree_path)
        self.safety["retained_worktrees"] = retained[-20:]
        self.updated_at = _utc_now()

    def kill_switch_enabled(self) -> bool:
        return bool(self.safety.get("kill_switch_enabled"))

    def denylist_contains(self, entry: str) -> bool:
        return str(entry).strip().lower() in {item.lower() for item in self.safety.get("denylist", [])}

    def append_task_graph(self, nodes: list[dict[str, Any]]) -> None:
        self.task_graph = [*self.task_graph, *nodes]
        self.updated_at = _utc_now()

    def record_learning_loop_flush(self, entry: dict[str, Any]) -> None:
        learning_entry = {
            "source": entry.get("source", "unknown"),
            "workId": entry.get("workId", self.current_work_id),
            "status": entry.get("status", self.status.value),
            "summary": entry.get("summary", ""),
            "learning_loop": entry.get("learning_loop") or {},
            "updated_at": _utc_now(),
        }
        self.learning_loops = [*self.learning_loops, learning_entry]
        self.append_run_log(
            {
                "source": learning_entry["source"],
                "workId": learning_entry["workId"],
                "status": learning_entry["status"],
                "summary": learning_entry["summary"],
                "learning_loop": learning_entry["learning_loop"],
            }
        )
        self.updated_at = _utc_now()

    def create_goal_from_planner(
        self, goal_id: str, summary: str, task_graph: list[dict[str, Any]]
    ) -> dict[str, object]:
        self.task_graph = list(task_graph)
        self.intent = summary or self.intent
        self.planner_output = {
            "goal_id": goal_id,
            "intent": self.intent,
            "summary": summary,
            "task_graph": self.task_graph,
            "dag_enforced": False,
            "next_task_id": self._next_task_id(),
            "approved_runtime_ids": [],
        }
        self.current_work_id = goal_id
        self.current_work_summary = summary
        self.status = LoopWorkspaceStatus.PLANNED
        self.updated_at = _utc_now()
        return {
            "goalId": goal_id,
            "status": self.status.value,
            "task_graph": self.task_graph,
            "planner_output": self.planner_output,
            "current_work_id": self.current_work_id,
            "current_work_summary": self.current_work_summary,
        }

    def _next_task_id(self) -> str | None:
        root_ids: set[str] = set()
        for node in self.task_graph:
            if not isinstance(node, dict):
                continue
            for dependency in node.get("depends_on", []):
                root_ids.discard(str(dependency))
        for task_id in [node.get("id") for node in self.task_graph if isinstance(node, dict) and node.get("id")]:
            if task_id not in root_ids:
                return task_id
        return None


def serialize_json_payload(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"
