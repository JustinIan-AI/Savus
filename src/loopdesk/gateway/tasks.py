"""Task and Gate REST routes for LoopDesk Gateway."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import uuid

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from loopdesk.loop_workspace.schema import LoopWorkspaceStatus
from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.gateway.events import broadcast_event


def _get_service(root_param: str | None) -> LoopWorkspaceService:
    root_path = Path(root_param).expanduser().resolve() if root_param else Path.cwd()
    return LoopWorkspaceService.from_root(root_path)


def _status_value(state: dict[str, Any]) -> str:
    value = state.get("status")
    if isinstance(value, LoopWorkspaceStatus):
        return value.value
    return value or "active"


def _is_task(entry: Any) -> bool:
    return isinstance(entry, dict) and bool(entry.get("id"))


async def api_get_tasks(request: Request) -> JSONResponse:
    """The board's read side.

    The task collection is authoritative; the `current_work_*` cursor is unioned
    in on read so a workspace whose collection was never seeded (older state
    files) still shows its active work item.
    """
    root_param = request.query_params.get("root")
    service = _get_service(root_param)
    state = service.current_state()

    tasks = [entry for entry in (state.get("tasks") or []) if _is_task(entry)]

    current_work_id = state.get("current_work_id")
    if current_work_id and not any(t["id"] == current_work_id for t in tasks):
        status_val = _status_value(state)
        synthesized = {
            "id": current_work_id,
            "title": state.get("current_work_summary") or state.get("intent") or "Active Loop Task",
            "status": status_val,
            "template": state.get("selected_template") or "issue-fix",
            "phase": "maker",
            "gate_status": "blocked" if status_val == "blocked" else "passed",
            "created_at": (state.get("context") or {}).get("created_at"),
        }
        tasks.append(synthesized)
        # 一次性回填：把旧状态文件里的 current_work_* 光标物化进任务集合。
        # 不回填的话，一旦集合里有了别的任务，这张本来就看得见的卡会因为
        # 光标挪走而凭空消失 —— 建任务把别人的卡「吃掉」是最难解释的 bug。
        service.upsert_task(
            current_work_id,
            title=synthesized["title"],
            template=synthesized["template"],
            status=status_val,
            phase=synthesized["phase"],
        )

    return JSONResponse({"tasks": tasks, "count": len(tasks)})


async def api_create_task(request: Request) -> JSONResponse:
    try:
        body = await request.json()
    except Exception:
        body = {}
    if not isinstance(body, dict):
        body = {}

    title = body.get("title") or "Untitled Task"
    template = body.get("template") or "issue-fix"
    root_param = body.get("root")
    intent = body.get("intent") or title
    task_id = body.get("id") or f"task-{uuid.uuid4().hex[:8]}"

    service = _get_service(root_param)
    service.ensure_initialized(intent=intent, selected_template=template)
    # Two writes on purpose: `current_work_*` is the cursor, `tasks` is the
    # collection the board renders. Without the second one a new task would
    # erase the previous one from the board.
    service.record_work_item(task_id, "loop", title, status=LoopWorkspaceStatus.ACTIVE.value)
    service.upsert_task(
        task_id,
        title=title,
        template=template,
        status=LoopWorkspaceStatus.ACTIVE.value,
        intent=intent,
        phase="triage",
    )

    task = {
        "id": task_id,
        "title": title,
        "template": template,
        "status": LoopWorkspaceStatus.ACTIVE.value,
        "phase": "triage",
        "intent": intent,
    }
    await broadcast_event("task_created", {"task": task})
    return JSONResponse({"ok": True, "task": task})


async def api_gate_decision(request: Request) -> JSONResponse:
    task_id = request.path_params.get("task_id", "")
    try:
        body = await request.json()
    except Exception:
        body = {}
    if not isinstance(body, dict):
        body = {}

    decision = body.get("decision", "approved")
    comment = body.get("comment", "")
    root_param = body.get("root")
    # A decision advances an *existing* work item; its title must survive. The
    # client may hand over the display title it renders (the board's canvas
    # titles are not stored server-side), otherwise the stored/current title is
    # reused and only a decision on a completely unknown id falls back to the
    # review comment.
    requested_title = body.get("title")

    service = _get_service(root_param)
    service.ensure_initialized()
    state = service.current_state()

    entry = next(
        (t for t in (state.get("tasks") or []) if _is_task(t) and t["id"] == task_id),
        None,
    )
    title = (
        requested_title
        or (entry or {}).get("title")
        or (state.get("current_work_summary") if state.get("current_work_id") == task_id else None)
        or f"Gate decision: {decision} ({comment})"
    )

    new_status = LoopWorkspaceStatus.COMPLETED if decision == "approved" else LoopWorkspaceStatus.BLOCKED

    service.upsert_task(
        task_id,
        title=title,
        template=(entry or {}).get("template") or state.get("selected_template") or "issue-fix",
        status=new_status.value,
        intent=(entry or {}).get("intent"),
        phase=(entry or {}).get("phase"),
    )
    service.record_work_item(task_id, "loop", title, status=new_status.value)

    await broadcast_event(
        "gate_decision_recorded",
        {"task_id": task_id, "decision": decision, "comment": comment, "status": new_status.value},
    )
    return JSONResponse(
        {
            "ok": True,
            "task_id": task_id,
            "title": title,
            "decision": decision,
            "comment": comment,
            "status": new_status.value,
        }
    )


def register_task_routes(app: Starlette) -> None:
    routes = [
        Route("/api/v1/projects/{project_id}/tasks", api_get_tasks, methods=["GET"]),
        Route("/api/v1/projects/{project_id}/tasks", api_create_task, methods=["POST"]),
        Route("/api/v1/tasks/{task_id}/gate/decision", api_gate_decision, methods=["POST"]),
    ]
    app.router.routes.extend(routes)
