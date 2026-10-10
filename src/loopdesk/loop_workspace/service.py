"""Personal loop workspace service combining state and layout concerns."""

from __future__ import annotations

import json
import re
from datetime import UTC
from pathlib import Path

from loopdesk.loop_workspace.helpers import ensure_loop_workspace
from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.repository import LoopWorkspaceRepository
from loopdesk.loop_workspace.skills import LoopWorkspaceSkillRegistry
from loopdesk.loop_workspace.templates import list_personal_templates, load_personal_template
from loopdesk.loop_workspace.worktree import create_loop_worktree, remove_loop_worktree


def _utc_now() -> str:
    from datetime import datetime
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


#: A workspace state file is per-root, so a "project" is a *label on the task*,
#: not a partition of the state file. Tasks written before the label existed are
#: treated as members of the default project rather than becoming invisible.
DEFAULT_PROJECT_ID = "default"


def _gate_status_for(status: str) -> str:
    """Derive the gate column of a task from its lifecycle status."""
    if status == "blocked":
        return "blocked"
    if status == "in_review":
        return "pending"
    if status == "completed":
        return "passed"
    return "not_evaluated"


class LoopWorkspaceService:
    @classmethod
    def from_root(cls, root: Path) -> LoopWorkspaceService:
        instance = cls(LoopWorkspaceLayout.ensure(root))
        instance.ensure_initialized()
        return instance

    def __init__(self, layout: LoopWorkspaceLayout) -> None:
        self._layout = layout
        self._repository = LoopWorkspaceRepository(layout)

    @property
    def layout(self) -> LoopWorkspaceLayout:
        return self._layout

    @property
    def repository(self) -> LoopWorkspaceRepository:
        return self._repository

    def ensure_initialized(
        self, *, intent: str | None = None, selected_template: str | None = None
    ) -> LoopWorkspaceLayout:
        return ensure_loop_workspace(
            self._layout.root,
            intent=intent,
            selected_template=selected_template,
            directories=self._required_directories(),
        )

    def current_state(self) -> dict[str, object]:
        state = self._repository.read()
        return {
            "state_file": str(self._layout.state_file),
            "workspace_root": state.workspace_root,
            "project_name": state.project_name or _project_name_from_root(self._layout.root),
            "intent": state.intent,
            "status": state.status.value,
            "tags": state.tags,
            "selected_template": state.selected_template,
            "workspace_type": state.workspace_type.value,
            "active_loop_id": state.active_loop_id or _default_loop_id(self._layout.root, state.project_name),
            "loop_engine": state.loop_engine,
            "human_profile": _human_profile_payload(state),
            "current_work_id": state.current_work_id,
            "current_work_source": state.current_work_source,
            "current_work_summary": state.current_work_summary,
            "tasks": state.tasks[-50:],
            "context": state.context,
            "run_log": state.run_log[-20:],
            "approvals": state.approvals[-20:],
            "cost_observatory": state.cost_observatory,
            "safety": state.safety,
            "override_history": state.override_history[-20:],
            "updated_at": state.updated_at,
            "task_graph": state.task_graph,
            "context_pack_schema": state.context_pack_schema,
            "planner_output": state.planner_output,
            "learning_loops": state.learning_loops[-20:],
            "gate_receipts": getattr(state, "gate_receipts", [])[-50:],
            "directories": self._directory_snapshot(),
            "templates": [
                self._template_payload(template) for template in list_personal_templates()
            ],
        }

    def apply_mutation(self, mutator) -> None:
        self._repository.update(mutator)

    def update_human_profile(self, updates: dict[str, Any]) -> dict[str, object]:
        allowed_keys = {"preferences", "coding_style", "architecture_preference", "decision_pattern", "review_standard"}

        def _mutator(state):
            profile = dict(state.human_profile)
            for key in allowed_keys:
                profile.setdefault(key, {})
            for key, value in (updates or {}).items():
                if key in allowed_keys:
                    profile[key] = value if isinstance(value, dict) else {}
            profile["_meta"] = {
                "local_first": True,
                "cloud_sync": False,
                "team_context": False,
            }
            state.human_profile = profile
        self._repository.update(_mutator)
        return self.current_state()

    def record_work_item(
        self, work_id: str, source: str, summary: str, *, status: str = "active"
    ) -> dict[str, object]:
        self.ensure_initialized()
        def _mutator(state):
            state.current_work_id = work_id
            state.current_work_source = source
            state.current_work_summary = summary
            state.status = state.status.__class__(status)
            if state.status.value == "completed":
                state.tags = [tag for tag in state.tags if tag != "in_progress"]
            else:
                state.tags = list(dict.fromkeys([*state.tags, "in_progress"]))

        self._repository.update(_mutator)
        return self.current_state()

    def upsert_task(
        self,
        task_id: str,
        *,
        title: str,
        template: str = "issue-fix",
        status: str = "active",
        intent: str | None = None,
        phase: str | None = None,
        project_id: str | None = None,
    ) -> dict[str, object]:
        """Insert or update one entry of the task collection the board reads.

        `current_work_id` is only a cursor — writing it twice erases the first
        task. The collection is what lets N tasks coexist on the board, so both
        `POST .../tasks` and the gate decision go through here.
        """
        self.ensure_initialized()
        now = _utc_now()

        def _mutator(state):
            entry = next((t for t in state.tasks if t.get("id") == task_id), None)
            if entry is None:
                entry = {"id": task_id, "created_at": now}
                state.tasks = [*state.tasks, entry]
            entry["title"] = title
            entry["template"] = template
            entry["status"] = status
            entry["phase"] = phase or entry.get("phase") or "triage"
            if "receipt_digest" in entry and entry.get("gate_status") == "passed":
                pass
            else:
                entry["gate_status"] = _gate_status_for(status)
            if intent is not None:
                entry["intent"] = intent
            if project_id is not None:
                entry["project_id"] = project_id
            entry.setdefault("project_id", DEFAULT_PROJECT_ID)
            entry["updated_at"] = now

        self._repository.update(_mutator)
        return self.current_state()

    def set_project_name(self, name: str) -> dict[str, object]:
        self.ensure_initialized()

        def _mutator(state):
            state.project_name = name.strip()
            state.active_loop_id = name.strip()

        self._repository.update(_mutator)
        return self.current_state()

    def set_active_loop(self, loop_id: str) -> dict[str, object]:
        self.ensure_initialized()

        def _mutator(state):
            state.active_loop_id = loop_id.strip()
            if state.status.value == "completed" and state.current_work_id in {None, state.active_loop_id}:
                state.status = state.status.__class__("planned")
            state.current_work_id = state.active_loop_id
            state.current_work_source = "loop_workspace"
            state.current_work_summary = f"Switched to loop {loop_id}."

        self._repository.update(_mutator)
        return self.current_state()

    def create_worktree(self, work_id: str, *, branch: str | None = None) -> dict[str, object]:
        target = create_loop_worktree(self._layout, work_id, branch=branch)
        self._repository.append_run_log(
            {
                "source": "loop_workspace",
                "workId": work_id,
                "status": self._repository.read().status.value,
                "summary": f"Created worktree at {target}.",
            }
        )
        state = self._repository.read()
        state.current_work_id = work_id
        state.current_work_source = "loop_workspace"
        state.current_work_summary = f"Created worktree at {target}."
        if state.status.value != "completed":
            state.tags = list(dict.fromkeys([*state.tags, "in_progress"]))
        self._repository.write(state)
        return {
            "workId": work_id,
            "path": str(target),
            "branch": branch or f"loopdesk/goal/{work_id}",
        }

    def remove_worktree(self, work_id: str, *, retain_snapshot: bool = False) -> dict[str, object]:
        state = self._repository.read()
        if work_id in state.safety.get("retained_worktrees", []):
            retain_snapshot = True
        if retain_snapshot:
            state.retain_worktree(str(self._layout.worktrees_dir / work_id))
            self._repository.write(state)
            return {"workId": work_id, "retained": True}
        remove_loop_worktree(self._layout, work_id)
        self._repository.write(state)
        return {"workId": work_id, "retained": False}

    def list_worktrees(self) -> dict[str, object]:
        return {
            "worktrees": [
                {
                    "name": path.name,
                    "exists": path.exists(),
                }
                for path in sorted(self._layout.worktrees_dir.iterdir())
                if path.is_dir()
            ]
        }

    def record_run_log(self, run_log: dict[str, object]) -> dict[str, object]:
        self.ensure_initialized()
        state = self._repository.read()
        state.append_run_log(run_log)
        if run_log.get("cost"):
            state.record_cost(run_log["cost"])
        self._repository.write(state)
        return self.current_state()

    def record_approval(self, approval: dict[str, object]) -> dict[str, object]:
        self.ensure_initialized()
        state = self._repository.read()
        state.record_approval(approval)
        self._repository.write(state)
        return self.current_state()

    def set_kill_switch(self, enabled: bool) -> dict[str, object]:
        state = self._repository.read()
        state.set_kill_switch(enabled)
        self._repository.write(state)
        return self.current_state()

    def set_denylist(self, entries: list[str]) -> dict[str, object]:
        state = self._repository.read()
        state.set_denylist(entries)
        self._repository.write(state)
        return self.current_state()

    def record_cost(self, cost_payload: dict[str, object]) -> dict[str, object]:
        state = self._repository.read()
        state.record_cost(cost_payload)
        self._repository.write(state)
        return self.current_state()

    def export_state(self, destination: Path | None = None) -> dict[str, object]:
        payload = self.current_state()
        target = destination or (self._layout.root / "LOOP-STATE.export.json")
        target.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return {"path": str(target)}

    def get_context_pack(self) -> dict[str, object]:
        state = self._repository.read()
        context = dict(state.context)
        for key, path in {
            "user": self._layout.user_context_path,
            "project": self._layout.project_context_path,
            "task": self._layout.task_context_path,
        }.items():
            if context.get(key) in (None, {}) and path.exists():
                context[key] = _load_context_file(path)
        return {
            "workspace_root": state.workspace_root,
            "context_pack_schema": state.context_pack_schema,
            "intent": state.intent,
            "selected_template": state.selected_template,
            "workspace_type": state.workspace_type.value,
            "context": context,
            "status": state.status.value,
            "current_work_id": state.current_work_id,
            "current_work_summary": state.current_work_summary,
            "recent_run_log": state.run_log[-10:],
            "open_approvals": [
                entry for entry in state.approvals if entry.get("status") != "approved"
            ][-20:],
            "cost_observatory": state.cost_observatory,
            "safety": state.safety,
            "templates": [self._template_payload(template) for template in list_personal_templates()],
        }

    def _directory_snapshot(self) -> dict[str, bool]:
        return {
            "memory": self._layout.memory_dir.exists(),
            "skills": self._layout.skills_dir.exists(),
            "artifacts": self._layout.artifacts_dir.exists(),
            "worktrees": self._layout.worktrees_dir.exists(),
            "personal_templates": self._layout.personal_templates_dir.exists(),
            "context": self._layout.context_dir.exists(),
            "user_context": self._layout.user_context_path.exists(),
            "project_context": self._layout.project_context_path.exists(),
            "task_context": self._layout.task_context_path.exists(),
        }

    def _template_payload(self, template):
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "roles": template.roles,
        }

    def skills_registry(self) -> LoopWorkspaceSkillRegistry:
        return LoopWorkspaceSkillRegistry(self._layout.root)

    def approvals_list(self, status=None) -> dict[str, object]:
        entries = self._repository.read().approvals
        if status:
            entries = [entry for entry in entries if entry.get("status") == status]
        return {"approvals": list(entries)[-50:]}

    def run_log_list(self, limit=50, offset=0) -> dict[str, object]:
        entries = self._repository.read().run_log
        start = max(0, offset)
        end = start + max(1, limit)
        return {"run_log": entries[start:end], "total": len(entries)}

    def check_budget(self) -> dict[str, object]:
        state = self._repository.read()
        return {
            "status": state.cost_observatory.get("status", "ok"),
            "budget_cap_usd": state.cost_observatory.get("budget_cap_usd", 0.0),
            "spend_usd": state.cost_observatory.get("spend_usd", 0.0),
            "request_count": state.cost_observatory.get("request_count", 0),
        }

    def apply_template(self, template_id: str) -> dict[str, object]:
        template = load_personal_template(template_id)

        def _mutator(state):
            state.selected_template = template.id
            if not state.intent and template.description:
                state.intent = template.description

        self.apply_mutation(_mutator)
        return self.current_state()

    def create_goal_from_planner(
        self, goal_id: str, summary: str, task_graph: list[dict[str, object]]
    ) -> dict[str, object]:
        self.ensure_initialized()

        def _mutator(state):
            state.create_goal_from_planner(goal_id, summary, task_graph)

        self.apply_mutation(_mutator)
        return self.current_state()

    def update_context_pack_schema(self, schema: dict[str, object]) -> dict[str, object]:
        self.ensure_initialized()

        def _mutator(state):
            state.context_pack_schema = {
                "include": list(schema.get("include") or state.context_pack_schema["include"]),
                "compact_strategy": str(schema.get("compact_strategy") or state.context_pack_schema["compact_strategy"]),
                "max_user_chars": int(schema.get("max_user_chars", state.context_pack_schema["max_user_chars"])),
                "max_project_chars": int(schema.get("max_project_chars", state.context_pack_schema["max_project_chars"])),
                "max_task_chars": int(schema.get("max_task_chars", state.context_pack_schema["max_task_chars"])),
            }

        self.apply_mutation(_mutator)
        state = self._repository.read()
        return {
            "context_pack_schema": state.context_pack_schema,
            "planner_output": state.planner_output,
        }

    def update_work_item(
        self,
        work_id: str,
        source: str,
        summary: str,
        *,
        context_pack: dict[str, object] | None = None,
    ) -> dict[str, object]:
        self.ensure_initialized()

        def _mutator(state):
            state.current_work_id = work_id
            state.current_work_source = source
            state.current_work_summary = summary
            state.status = state.status.__class__("active")
            state.tags = list(dict.fromkeys([*state.tags, "in_progress"]))
            state.context_pack_schema.setdefault("context_packs", {})
            state.context_pack_schema["context_packs"][work_id] = _compact_context_pack(
                dict(context_pack or {}),
                state.context_pack_schema,
            )

        self.apply_mutation(_mutator)
        state = self._repository.read()
        return {
            "workId": work_id,
            "context_pack_schema": state.context_pack_schema,
            "context_pack": state.context_pack_schema.get("context_packs", {}).get(work_id, {}),
        }

    def compact_context_pack(self, goal_id: str) -> dict[str, object]:
        state = self._repository.read()
        context_packs = state.context_pack_schema.setdefault("context_packs", {})
        payload = dict(context_packs.get(goal_id, state.context))
        return _compact_context_pack(payload, state.context_pack_schema)

    def record_learning_loop_flush(self, entry: dict[str, object]) -> dict[str, object]:
        self.ensure_initialized()

        def _mutator(state):
            state.record_learning_loop_flush(entry)

        self.apply_mutation(_mutator)
        return self.current_state()

    def _required_directories(self):
        return ("memory", "skills", "artifacts", "worktrees", "personal_templates")


    def record_gate_receipt(self, receipt: Any) -> None:
        """Record a verified ValidationReceipt to LOOP-STATE.json and update task metadata."""
        receipt_data = receipt.to_dict() if hasattr(receipt, "to_dict") else dict(receipt)

        def _mutator(state: LoopWorkspaceState) -> None:
            if not hasattr(state, "gate_receipts") or state.gate_receipts is None:
                state.gate_receipts = []
            state.gate_receipts.append(receipt_data)

            task_id = receipt_data.get("task_id")
            for t in state.tasks:
                if isinstance(t, dict) and t.get("id") == task_id:
                    decision = receipt_data.get("operator_decision", "approved")
                    passed_gates = set(receipt_data.get("passed_gates", []))
                    required_gates = {"health", "operator", "evidence", "focus", "quota"}
                    t["gate_status"] = "passed" if (decision == "approved" and required_gates.issubset(passed_gates)) else "blocked"
                    t["receipt_digest"] = receipt_data.get("sha256_digest")
                    t["updated_at"] = _utc_now()
                    break

        self._repository.update(_mutator)

def _load_context_file(path: Path) -> dict[str, object]:
    payload: dict[str, object] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.+)$", line.strip())
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if value.lower() in {"true", "false"}:
            payload[key] = value.lower() == "true"
        else:
            try:
                payload[key] = int(value)
            except ValueError:
                try:
                    payload[key] = float(value)
                except ValueError:
                    payload[key] = value
        return payload


def _compact_context_pack(payload: dict[str, object], schema: dict[str, object]) -> dict[str, object]:
    compacted: dict[str, object] = {}
    for key in schema.get("include", ["user", "project", "task"]):
        if key not in {"user", "project", "task"}:
            continue
        value = payload.get(key)
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        limit = int(schema.get(f"max_{key}_chars", 0))
        if limit and len(text) > limit:
            text = text[: limit - 3] + "..."
        compacted[key] = text
    return compacted


def _project_name_from_root(root: Path) -> str:
    return _safe_name(root.name)


def _default_loop_id(root: Path, project_name: str | None) -> str | None:
    return project_name or _safe_name(root.name)


def _safe_name(value: str) -> str:
    cleaned = value.strip().replace(" ", "-")
    return cleaned or "loop"


def _human_profile_payload(state: LoopWorkspaceState) -> dict[str, Any]:
    profile = dict(state.human_profile)
    for key in {"preferences", "coding_style", "architecture_preference", "decision_pattern", "review_standard"}:
        profile.setdefault(key, {})
    profile.setdefault("_meta", {})
    profile["_meta"].setdefault("local_first", True)
    profile["_meta"].setdefault("cloud_sync", False)
    profile["_meta"].setdefault("team_context", False)
    return profile

