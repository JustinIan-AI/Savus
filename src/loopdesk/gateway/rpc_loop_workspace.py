"""Gateway RPC methods for LoopDesk loop workspaces."""

from __future__ import annotations

import json
from pathlib import Path

from loopdesk.gateway.rpc import get_dispatcher
from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.loop_workspace.service import _utc_now
from loopdesk.loop_workspace.templates import list_personal_templates

from loopdesk.loop_workspace.memory import DurableMemoryIndex
from loopdesk.loop_workspace.skills import LoopWorkspaceSkillRegistry
from loopdesk.loop_workspace.engine.runner import LoopEngineRunner
from loopdesk.loop_workspace.engine.state_machine import LoopEngineState, LoopPhase
from loopdesk.loop_workspace.adapters import McpClient


def _loop_workspace_service_from_params(params: dict[str, object]) -> LoopWorkspaceService:
    return LoopWorkspaceService.from_root(Path(params["root"]))


def _serialize_service(service: LoopWorkspaceService) -> dict[str, object]:
    service.ensure_initialized()
    return service.current_state()


def _register_loop_workspace_methods() -> None:
    dispatcher = get_dispatcher()

    @dispatcher.method("loop_workspace.create", scope="operator.read")
    async def loop_workspace_create(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        layout = service.ensure_initialized(
            intent=params.get("intent"),
            selected_template=params.get("selected_template"),
        )
        payload = _serialize_service(service)
        payload["state_file"] = str(layout.state_file)
        return payload

    @dispatcher.method("loop_workspace.get", scope="operator.read")
    async def loop_workspace_get(params: dict[str, object], context) -> dict[str, object]:
        return _serialize_service(_loop_workspace_service_from_params(params))

    @dispatcher.method("loop_workspace.list", scope="operator.read")
    async def loop_workspace_list(params: dict[str, object], context) -> dict[str, object]:
        root = Path(params["root"])
        workspaces = []
        for workspace in sorted(path for path in root.iterdir() if path.is_dir()):
            try:
                workspaces.append(_serialize_service(LoopWorkspaceService.from_root(workspace)))
            except Exception:  # noqa: BLE001
                continue
        return {"root": str(root), "workspaces": workspaces}

    @dispatcher.method("loop_workspace.update", scope="operator.write")
    async def loop_workspace_update(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)

        def _mutator(state):
            if "intent" in params:
                state.intent = params["intent"]
            if "selected_template" in params:
                state.selected_template = params["selected_template"]
            if "status" in params:
                state.status = state.status.__class__(params["status"])

        service.apply_mutation(_mutator)
        return _serialize_service(service)

    @dispatcher.method("loop_workspace.resume", scope="operator.write")
    async def loop_workspace_resume(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        return service.record_work_item(
            params["workId"],
            params.get("source", "external"),
            params.get("summary", ""),
            status=params.get("status", "active"),
        )

    @dispatcher.method("loop_workspace.record_work_item", scope="operator.write")
    async def loop_workspace_record_work_item(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        return service.record_work_item(
            params["workId"],
            params.get("source", "loop"),
            params.get("summary", ""),
            status=params.get("status", "active"),
        )

    @dispatcher.method("loop_workspace.export", scope="operator.read")
    async def loop_workspace_export(params: dict[str, object], context) -> dict[str, object]:
        destination = Path(params["output"]) if params.get("output") else None
        return _loop_workspace_service_from_params(params).export_state(destination)

    @dispatcher.method("loop_workspace.record_run_log", scope="operator.write")
    async def loop_workspace_record_run_log(params: dict[str, object], context) -> dict[str, object]:
        return _loop_workspace_service_from_params(params).record_run_log(
            {
                "source": params.get("source", "unknown"),
                "workId": params.get("workId"),
                "status": params.get("status", "active"),
                "summary": params.get("summary", ""),
                "previousStatus": params.get("previousStatus"),
                "cost": params.get("cost"),
                "toolEvent": params.get("toolEvent") or {
                    key: value
                    for key, value in params.items()
                    if key not in {"source", "workId", "status", "summary", "previousStatus"}
                },
            }
        )

    @dispatcher.method("loop_workspace.record_approval", scope="operator.write")
    async def loop_workspace_record_approval(params: dict[str, object], context) -> dict[str, object]:
        return _loop_workspace_service_from_params(params).record_approval(
            {
                "id": params.get("id"),
                "action": params.get("action"),
                "status": params.get("status", "pending"),
                "payload": params.get("payload", {}),
            }
        )

    @dispatcher.method("loop_workspace.set_kill_switch", scope="operator.write")
    async def loop_workspace_set_kill_switch(params: dict[str, object], context) -> dict[str, object]:
        return _loop_workspace_service_from_params(params).set_kill_switch(bool(params.get("enabled")))

    @dispatcher.method("loop_workspace.set_denylist", scope="operator.write")
    async def loop_workspace_set_denylist(params: dict[str, object], context) -> dict[str, object]:
        entries = params.get("entries", [])
        if isinstance(entries, str):
            entries = [entry.strip() for entry in entries.splitlines() if entry.strip()]
        return _loop_workspace_service_from_params(params).set_denylist(list(entries))

    @dispatcher.method("loop_workspace.record_cost", scope="operator.write")
    async def loop_workspace_record_cost(params: dict[str, object], context) -> dict[str, object]:
        return _loop_workspace_service_from_params(params).record_cost(
            {
                "input_tokens": params.get("input_tokens"),
                "output_tokens": params.get("output_tokens"),
                "total_tokens": params.get("total_tokens"),
                "reasoning_tokens": params.get("reasoning_tokens"),
                "cached_tokens": params.get("cached_tokens"),
                "cache_read_tokens": params.get("cache_read_tokens"),
                "cache_write_tokens": params.get("cache_write_tokens"),
                "cost_usd": params.get("cost_usd"),
                "billed_cost": params.get("billed_cost"),
                "estimated_cost_usd": params.get("estimated_cost_usd"),
                "model": params.get("model"),
                "request_count": params.get("request_count"),
                "cost_source": params.get("cost_source"),
                "budget_cap_usd": params.get("budget_cap_usd"),
            }
        )

    @dispatcher.method("loop_workspace.context_pack", scope="operator.read")
    async def loop_workspace_context_pack(params: dict[str, object], context) -> dict[str, object]:
        return _loop_workspace_service_from_params(params).get_context_pack()

    @dispatcher.method("loop_workspace.worktree.create", scope="operator.write")
    async def loop_workspace_worktree_create(params: dict[str, object], context) -> dict[str, object]:
        if not params.get("workId"):
            raise ValueError("workId is required for worktree create")
        return _loop_workspace_service_from_params(params).create_worktree(
            params["workId"], branch=params.get("branch")
        )

    @dispatcher.method("loop_workspace.worktree.remove", scope="operator.write")
    async def loop_workspace_worktree_remove(params: dict[str, object], context) -> dict[str, object]:
        if not params.get("workId"):
            raise ValueError("workId is required for worktree remove")
        return _loop_workspace_service_from_params(params).remove_worktree(
            params["workId"], retain_snapshot=bool(params.get("retain_snapshot"))
        )

    @dispatcher.method("loop_workspace.worktree.list", scope="operator.read")
    async def loop_workspace_worktree_list(params: dict[str, object], context) -> dict[str, object]:
        return _loop_workspace_service_from_params(params).list_worktrees()

    @dispatcher.method("loop_workspace.human.profile", scope="operator.write")
    async def loop_workspace_human_profile(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        allowed = {"preferences", "coding_style", "architecture_preference", "decision_pattern", "review_standard"}
        updates = {key: params[key] for key in allowed if key in params}
        payload = service.update_human_profile(updates) if updates else service.current_state()["human_profile"]
        payload = dict(payload)
        payload["_meta"] = dict(payload.get("_meta") or {})
        payload.setdefault("_meta", {})
        payload["_meta"].setdefault("local_first", True)
        payload["_meta"].setdefault("cloud_sync", False)
        payload["_meta"].setdefault("team_context", False)
        return payload


def _register_memory_methods() -> None:
    dispatcher = get_dispatcher()

    @dispatcher.method("loop_workspace.memory.append", scope="operator.write")
    async def loop_workspace_memory_append(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        memory = DurableMemoryIndex(service.layout.memory_dir)
        entry = memory.append(
            title=params["title"],
            body=params["body"],
            tags=params.get("tags", []),
            source=params.get("source", "manual"),
        )
        return {
            "key": entry.key,
            "title": entry.title,
            "body": entry.body,
            "tags": list(entry.tags),
            "source": entry.source,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
        }

    @dispatcher.method("loop_workspace.memory.search", scope="operator.read")
    async def loop_workspace_memory_search(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        memory = DurableMemoryIndex(service.layout.memory_dir)
        hits = memory.search(
            query=params["query"],
            max_results=params.get("max_results", 20),
        )
        return {
            "hits": [
                {
                    "entry": {
                        "key": hit.entry.key,
                        "title": hit.entry.title,
                        "body": hit.entry.body,
                        "tags": list(hit.entry.tags),
                        "source": hit.entry.source,
                        "created_at": hit.entry.created_at,
                        "updated_at": hit.entry.updated_at,
                    },
                    "score": hit.score,
                    "match": hit.match,
                }
                for hit in hits
            ]
        }

    @dispatcher.method("loop_workspace.memory.compact", scope="operator.write")
    async def loop_workspace_memory_compact(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        memory = DurableMemoryIndex(service.layout.memory_dir)
        result = memory.compact(keep_recent=params.get("keep_recent", 40))
        return result

    @dispatcher.method("loop_workspace.memory.resume_pack", scope="operator.read")
    async def loop_workspace_memory_resume_pack(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        memory = DurableMemoryIndex(service.layout.memory_dir)
        result = memory.resume_pack(max_entries=params.get("max_entries", 20))
        return result


_register_loop_workspace_methods()
_register_memory_methods()

def _register_skills_methods() -> None:
    dispatcher = get_dispatcher()

    @dispatcher.method("loop_workspace.skills.list", scope="operator.read")
    async def loop_workspace_skills_list(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        return {"skills": service.skills_registry().list_skills()}

    @dispatcher.method("loop_workspace.skills.inspect", scope="operator.read")
    async def loop_workspace_skills_inspect(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        return service.skills_registry().read_skill(params["skill_id"])

    @dispatcher.method("loop_workspace.skills.audit", scope="operator.read")
    async def loop_workspace_skills_audit(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        return service.skills_registry().audit()


def _register_approval_methods() -> None:
    dispatcher = get_dispatcher()

    @dispatcher.method("loop_workspace.approvals.list", scope="operator.read")
    async def loop_workspace_approvals_list(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        return service.approvals_list(params.get("status"))

    @dispatcher.method("loop_workspace.approval.respond", scope="operator.write")
    async def loop_workspace_approval_respond(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        service.record_approval(
            {
                "id": params["id"],
                "status": params["status"],
                "payload": params.get("payload", {}),
                "updated_at": _utc_now(),
            }
        )
        current_state = service.current_state()
        if params.get("status") == "denied":
            state = service.repository.read()
            state.current_work_id = None
            service.repository.write(state)
            current_state = service.current_state()
        return current_state


def _register_cost_methods() -> None:
    dispatcher = get_dispatcher()

    @dispatcher.method("loop_workspace.cost.set_budget", scope="operator.write")
    async def loop_workspace_cost_set_budget(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        service.record_cost({"budget_cap_usd": params["budget_cap_usd"]})
        return service.current_state()

    @dispatcher.method("loop_workspace.cost.history", scope="operator.read")
    async def loop_workspace_cost_history(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        history = [
            {**entry, "cost": entry.get("cost") or _extract_cost_from_tool_event(entry.get("toolEvent"))}
            for entry in service.repository.read().run_log
            if entry.get("cost") or _extract_cost_from_tool_event(entry.get("toolEvent"))
        ]
        start = max(0, params.get("offset", 0))
        end = start + params.get("limit", 50)
        return {"history": history[start:end], "total": len(history)}


def _register_run_log_methods() -> None:
    dispatcher = get_dispatcher()

    @dispatcher.method("loop_workspace.run_log.list", scope="operator.read")
    async def loop_workspace_run_log_list(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        return service.run_log_list(params.get("limit", 50), params.get("offset", 0))

    @dispatcher.method("loop_workspace.run_log.detail", scope="operator.read")
    async def loop_workspace_run_log_detail(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        entries = service.repository.read().run_log
        index = int(params.get("index", -1))
        if not entries or index >= len(entries) or index < -len(entries):
            return {"entry": None}
        entry = dict(entries[index])
        entry.setdefault("cost", _extract_cost_from_tool_event(entry.get("toolEvent")))
        entry.setdefault("approvals", _approvals_for_entry(service.repository.read().approvals, entry))
        return {"entry": entry}

    @dispatcher.method("loop_workspace.replay.pack", scope="operator.read")
    async def loop_workspace_replay_pack(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        state = service.repository.read()
        return {
            "workspace_root": state.workspace_root,
            "intent": state.intent,
            "selected_template": state.selected_template,
            "recent_run_log": state.run_log[-10:],
            "templates": [service._template_payload(template) for template in list_personal_templates()],
        }

    @dispatcher.method("loop_workspace.session.compact", scope="operator.write")
    async def loop_workspace_session_compact(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        keep_recent = int(params.get("keep_recent", 20) or 20)
        state = service.repository.read()
        state.run_log = state.run_log[-keep_recent:]
        service.repository.write(state)
        return {"kept": len(state.run_log)}


def _register_template_methods() -> None:
    dispatcher = get_dispatcher()

    @dispatcher.method("loop_workspace.templates.apply", scope="operator.write")
    async def loop_workspace_templates_apply(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        return service.apply_template(params["template_id"])


def _register_engine_methods() -> None:
    dispatcher = get_dispatcher()

    @dispatcher.method("loop_workspace.engine.start", scope="operator.write")
    async def loop_workspace_engine_start(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        state = service.repository.read()
        engine_state = LoopEngineState(
            phase=LoopPhase.PLANNED,
            goal=params.get("goal"),
            stop_condition=params.get("stop_condition"),
            max_iterations=int(params.get("max_iterations", 10) or 10),
            current_iteration=0,
        )
        state.loop_engine = {
            "phase": engine_state.phase.value,
            "goal": engine_state.goal,
            "stop_condition": engine_state.stop_condition,
            "max_iterations": engine_state.max_iterations,
            "current_iteration": engine_state.current_iteration,
            "escalation_reason": engine_state.escalation_reason,
        }
        service.repository.write(state)
        service.record_run_log(
            {
                "source": "loop-engine",
                "workId": engine_state.goal,
                "status": engine_state.phase.value,
                "summary": "Loop engine started.",
                "previousStatus": None,
            }
        )
        return {"phase": engine_state.phase.value, "goal": engine_state.goal, "stop_condition": engine_state.stop_condition, "max_iterations": engine_state.max_iterations, "current_iteration": engine_state.current_iteration}

    @dispatcher.method("loop_workspace.engine.stop", scope="operator.write")
    async def loop_workspace_engine_stop(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        goal = service.repository.read().loop_engine.get("goal") if service.repository.read().loop_engine else None
        service.record_run_log(
            {
                "source": "loop-engine",
                "workId": goal,
                "status": LoopPhase.PAUSED.value,
                "summary": "Loop engine stopped.",
                "previousStatus": None,
            }
        )
        return {"phase": LoopPhase.PAUSED.value, "goal": None, "stop_condition": None, "max_iterations": 10, "current_iteration": 0}

    @dispatcher.method("loop_workspace.engine.status", scope="operator.read")
    async def loop_workspace_engine_status(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        engine_state = service.repository.read().loop_engine or {}
        return {
            "phase": engine_state.get("phase", LoopPhase.PLANNED.value),
            "goal": engine_state.get("goal"),
            "stop_condition": engine_state.get("stop_condition"),
            "max_iterations": engine_state.get("max_iterations", 10),
            "current_iteration": engine_state.get("current_iteration", 0),
        }

    @dispatcher.method("loop_workspace.engine.step", scope="operator.write")
    async def loop_workspace_engine_step(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        engine_state = LoopEngineState(
            phase=LoopPhase(params.get("phase", LoopPhase.PLANNED.value)),
            goal=params.get("goal"),
            stop_condition=params.get("stop_condition"),
            max_iterations=int(params.get("max_iterations", 10) or 10),
            current_iteration=int(params.get("current_iteration", 0) or 0),
        )
        runner = LoopEngineRunner(service)
        next_state = runner.step(engine_state, decision=params.get("decision"), checker_passed=bool(params.get("checker_passed")))
        return {
            "phase": next_state.phase.value,
            "goal": next_state.goal,
            "stop_condition": next_state.stop_condition,
            "max_iterations": next_state.max_iterations,
            "current_iteration": next_state.current_iteration,
            "escalation_reason": next_state.escalation_reason,
        }

    @dispatcher.method("loop_workspace.engine.set_stop_condition", scope="operator.write")
    async def loop_workspace_engine_set_stop_condition(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        state = service.repository.read()
        state.loop_engine = {
            "phase": LoopPhase.PLANNED.value,
            "goal": params.get("goal"),
            "stop_condition": params.get("stop_condition"),
            "max_iterations": int(params.get("max_iterations", 10) or 10),
            "current_iteration": 0,
            "escalation_reason": None,
        }
        service.repository.write(state)
        return {
            "phase": state.loop_engine["phase"],
            "goal": state.loop_engine["goal"],
            "stop_condition": state.loop_engine["stop_condition"],
            "max_iterations": state.loop_engine["max_iterations"],
            "current_iteration": state.loop_engine["current_iteration"],
        }


_register_skills_methods()
_register_approval_methods()
_register_cost_methods()
_register_run_log_methods()
_register_template_methods()
_register_engine_methods()

def _extract_cost_from_tool_event(tool_event: dict[str, object] | None) -> dict[str, object] | None:
    if not isinstance(tool_event, dict):
        return None
    cost = tool_event.get("cost")
    if isinstance(cost, dict) and cost:
        return cost
    return None


def _approvals_for_entry(approvals: list[dict[str, object]], entry: dict[str, object]) -> list[dict[str, object]]:
    work_id = entry.get("workId")
    if not work_id:
        return []
    matched = []
    for approval in approvals:
        payload = approval.get("payload") or {}
        if approval.get("id") == work_id or payload.get("workId") == work_id or payload.get("action") == entry.get("summary"):
            matched.append(approval)
    return matched[-20:]


_adapter_clients: dict[str, McpClient] = {}


def _register_adapter_methods() -> None:
    dispatcher = get_dispatcher()

    @dispatcher.method("loop_workspace.adapter.connect", scope="operator.write")
    async def loop_workspace_adapter_connect(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        client = McpClient()
        client.connect(params["command"], params.get("args", []))
        _adapter_clients[str(service.layout.root)] = client
        return {"connected": True, "command": params["command"]}

    @dispatcher.method("loop_workspace.adapter.list_tools", scope="operator.read")
    async def loop_workspace_adapter_list_tools(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        client = _adapter_clients[str(service.layout.root)]
        return {"tools": client.list_tools()}

    @dispatcher.method("loop_workspace.adapter.call_tool", scope="operator.write")
    async def loop_workspace_adapter_call_tool(params: dict[str, object], context) -> dict[str, object]:
        service = _loop_workspace_service_from_params(params)
        client = _adapter_clients[str(service.layout.root)]
        result = client.call_tool(params["name"], params.get("arguments", {}))
        service.record_run_log(
            {
                "source": f"tool:{params.get('name')}",
                "workId": params.get("workId"),
                "status": "active",
                "summary": f"{params.get('name')} completed.",
                "previousStatus": None,
                "toolEvent": result,
            }
        )
        return result


_register_adapter_methods()
