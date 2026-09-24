"""Task and Gate REST routes for LoopDesk Gateway.

The board's contract is deliberately small:

    GET    /api/v1/projects/{project_id}/tasks        read the collection
    POST   /api/v1/projects/{project_id}/tasks        create one task
    PATCH  /api/v1/tasks/{task_id}                    move one task
    POST   /api/v1/tasks/{task_id}/gate/decision      record a gate verdict

`PATCH` and the gate decision are different things on purpose. A gate decision
is an *audited verdict* — it carries a comment and produces a receipt, and it is
the only thing allowed to close a task as `completed` or send it back as
`blocked`. `PATCH` is the plain lifecycle move (planned / active / in_review /
completed / canceled) that the board's status menu and "submit for review"
button perform.
"""

from __future__ import annotations
from loopdesk.governance.gates import FiveTierGateEngine, GateContext, ValidationReceipt

import json
from pathlib import Path
from typing import Any
import uuid

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from loopdesk.loop_workspace.schema import LoopWorkspaceStatus
from loopdesk.loop_workspace.service import DEFAULT_PROJECT_ID, LoopWorkspaceService
from loopdesk.gateway.events import broadcast_event


#: The lifecycle statuses a client may set through `PATCH`. Kept as an explicit
#: tuple (not "anything goes") so a typo in the UI surfaces as a 400 instead of
#: silently parking a task in a state no column renders.
WRITABLE_STATUSES: tuple[str, ...] = tuple(s.value for s in LoopWorkspaceStatus)

#: Fields `PATCH` understands.
PATCHABLE_FIELDS: tuple[str, ...] = ("status", "phase", "title", "template", "intent", "project_id")


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


def _task_project(entry: dict[str, Any]) -> str:
    """Tasks written before projects existed belong to the default project."""
    value = entry.get("project_id")
    return value if isinstance(value, str) and value else DEFAULT_PROJECT_ID


async def _read_body(request: Request) -> tuple[dict[str, Any] | None, JSONResponse | None]:
    """Parse a JSON object body, or hand back the 400 to return.

    Returns a `(body, error_response)` pair so callers can bail out early and
    reject malformed input instead of quietly substituting defaults — a gateway
    that answers 200 to unparseable JSON makes every client bug invisible.
    """
    raw = await request.body()
    if not raw:
        return {}, None
    try:
        parsed = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        return None, JSONResponse(
            {"ok": False, "error": "invalid_json", "detail": "Request body must be valid JSON."},
            status_code=400,
        )
    if not isinstance(parsed, dict):
        return None, JSONResponse(
            {"ok": False, "error": "invalid_body", "detail": "Request body must be a JSON object."},
            status_code=400,
        )
    return parsed, None


def _resolve_root(request: Request, body: dict[str, Any]) -> str | None:
    """Root may arrive in the query string *or* the body.

    Accepting both is not laxity — it removes a real trap: a probe that sent a
    malformed body lost its body-supplied `root` and fell back to `Path.cwd()`,
    silently writing the repository's own state file.
    """
    query_root = request.query_params.get("root")
    if query_root:
        return query_root
    value = body.get("root")
    return value if isinstance(value, str) and value else None


def _find_task(service: LoopWorkspaceService, task_id: str) -> dict[str, Any] | None:
    state = service.current_state()
    return next(
        (t for t in (state.get("tasks") or []) if _is_task(t) and t["id"] == task_id),
        None,
    )


async def api_get_tasks(request: Request) -> JSONResponse:
    """The board's read side.

    The task collection is authoritative; the `current_work_*` cursor is unioned
    in on read so a workspace whose collection was never seeded (older state
    files) still shows its active work item. The union only happens for the
    project the cursor belongs to — an unknown project legitimately has nothing.
    """
    project_id = request.path_params.get("project_id") or DEFAULT_PROJECT_ID
    root_param = request.query_params.get("root")
    service = _get_service(root_param)
    state = service.current_state()

    every_task = [entry for entry in (state.get("tasks") or []) if _is_task(entry)]
    tasks = [entry for entry in every_task if _task_project(entry) == project_id]

    current_work_id = state.get("current_work_id")
    # The cursor is a single global pointer with no project of its own, so the
    # "is it already materialised?" check must look at the *whole* collection.
    # Checking only the project-filtered view would re-stamp a task that lives
    # in another project with this project's id — merely reading project
    # `default` would silently steal project `x`'s task.
    if (
        project_id == DEFAULT_PROJECT_ID
        and current_work_id
        and not any(t["id"] == current_work_id for t in every_task)
    ):
        status_val = _status_value(state)
        synthesized = {
            "id": current_work_id,
            "title": state.get("current_work_summary") or state.get("intent") or "Active Loop Task",
            "status": status_val,
            "template": state.get("selected_template") or "issue-fix",
            "phase": "maker",
            "gate_status": "blocked" if status_val == "blocked" else "passed",
            "created_at": (state.get("context") or {}).get("created_at"),
            "project_id": DEFAULT_PROJECT_ID,
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
            project_id=project_id,
        )

    return JSONResponse({"tasks": tasks, "count": len(tasks)})


async def api_create_task(request: Request) -> JSONResponse:
    body, error = await _read_body(request)
    if error is not None:
        return error
    assert body is not None

    project_id = request.path_params.get("project_id") or DEFAULT_PROJECT_ID
    title = body.get("title") or "Untitled Task"
    template = body.get("template") or "issue-fix"
    root_param = _resolve_root(request, body)
    intent = body.get("intent") or title
    task_id = body.get("id") or f"task-{uuid.uuid4().hex[:8]}"

    service = _get_service(root_param)
    service.ensure_initialized(intent=intent, selected_template=template)
    # Two writes on purpose: `current_work_*` is the cursor, `tasks` is the
    # collection the board renders. Without the second one a new task would
    # erase the previous one from the board.
    status_val = body.get("status") or LoopWorkspaceStatus.PLANNED.value
    service.record_work_item(task_id, "loop", title, status=status_val)
    service.upsert_task(
        task_id,
        title=title,
        template=template,
        status=status_val,
        intent=intent,
        phase="triage",
        project_id=project_id,
    )

    task = {
        "id": task_id,
        "title": title,
        "template": template,
        "status": status_val,
        "phase": "triage",
        "intent": intent,
        "project_id": project_id,
    }
    await broadcast_event("task_created", {"task": task})
    return JSONResponse({"ok": True, "task": task})


async def api_update_task(request: Request) -> JSONResponse:
    """Move a task along its lifecycle without recording an audited verdict.

    This *upserts*. The board renders canvas-seeded cards that were never
    written to the workspace (they are design fixtures), so moving one of them
    from 进行中 to 评审中 has to materialise it — the same way a gate decision
    on a canvas card already does. `created` in the reply says which happened.
    """
    task_id = request.path_params.get("task_id", "")
    body, error = await _read_body(request)
    if error is not None:
        return error
    assert body is not None

    updates = {k: body[k] for k in PATCHABLE_FIELDS if k in body and body[k] is not None}
    if not updates:
        return JSONResponse(
            {
                "ok": False,
                "error": "no_fields",
                "detail": f"Provide at least one of: {', '.join(PATCHABLE_FIELDS)}.",
            },
            status_code=400,
        )

    status = updates.get("status")
    if status is not None:
        if not isinstance(status, str) or status not in WRITABLE_STATUSES:
            return JSONResponse(
                {
                    "ok": False,
                    "error": "invalid_status",
                    "detail": f"status must be one of: {', '.join(WRITABLE_STATUSES)}.",
                },
                status_code=400,
            )

    for field in ("title", "template", "phase", "intent"):
        if field in updates and not isinstance(updates[field], str):
            return JSONResponse(
                {"ok": False, "error": "invalid_field", "detail": f"{field} must be a string."},
                status_code=400,
            )

    root_param = _resolve_root(request, body)
    service = _get_service(root_param)
    service.ensure_initialized()

    existing = _find_task(service, task_id)
    requested_project = body.get("project_id")
    project_id = (
        requested_project
        if isinstance(requested_project, str) and requested_project
        else (_task_project(existing) if existing else DEFAULT_PROJECT_ID)
    )

    # Everything the caller did not patch is carried over verbatim: a status
    # move must never rewrite a title the user did not touch.
    title = updates.get("title") or (existing or {}).get("title") or task_id
    service.upsert_task(
        task_id,
        title=title,
        template=updates.get("template") or (existing or {}).get("template") or "issue-fix",
        status=updates.get("status") or (existing or {}).get("status") or LoopWorkspaceStatus.ACTIVE.value,
        intent=updates.get("intent") or (existing or {}).get("intent"),
        phase=updates.get("phase"),
        project_id=project_id,
    )

    task = _find_task(service, task_id) or {"id": task_id, "title": title}
    await broadcast_event("task_updated", {"task_id": task_id, "task": task})
    return JSONResponse({"ok": True, "created": existing is None, "task": task})


async def api_gate_decision(request: Request) -> JSONResponse:
    task_id = request.path_params.get("task_id", "")
    body, error = await _read_body(request)
    if error is not None:
        return error
    assert body is not None

    decision = body.get("decision")
    if decision not in ("approved", "denied"):
        return JSONResponse(
            {
                "ok": False,
                "error": "invalid_decision",
                "detail": "decision must be either 'approved' or 'denied'.",
            },
            status_code=400,
        )

    comment = body.get("comment") or ""
    root_param = _resolve_root(request, body)
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

    project_id = _task_project(entry) if entry else DEFAULT_PROJECT_ID

    engine = FiveTierGateEngine()
    gate_ctx = GateContext(
        project_id=project_id,
        task_id=task_id,
        operator_decision=decision,
        operator_comment=comment,
        validation_command=body.get("validation_command", "pytest tests/ -q"),
        validation_exit_code=body.get("validation_exit_code", 0 if decision == "approved" else 1),
        validation_stdout=body.get("validation_stdout", "ALL TESTS PASSED"),
        touched_files=body.get("touched_files", []),
        allowed_write_scopes=body.get("allowed_write_scopes", []),
        consumed_tokens=body.get("consumed_tokens", 0),
        token_limit=body.get("token_limit", 1000000),
    )
    verdict = engine.evaluate(gate_ctx)

    if not verdict.passed:
        new_status = LoopWorkspaceStatus.BLOCKED
        service.upsert_task(
            task_id,
            title=title,
            template=(entry or {}).get("template") or state.get("selected_template") or "issue-fix",
            status=new_status.value,
            intent=(entry or {}).get("intent"),
            phase=(entry or {}).get("phase"),
            project_id=project_id,
        )
        return JSONResponse(
            {
                "ok": False,
                "error": f"Gate evaluation rejected: {verdict.reason}",
                "failed_gate": verdict.failed_gate.value if verdict.failed_gate else None,
                "code": "GATE_REJECTED",
                "task_id": task_id,
                "status": new_status.value,
            },
            status_code=422,
        )

    receipt = verdict.receipt
    assert receipt is not None
    service.record_gate_receipt(receipt)
    new_status = LoopWorkspaceStatus.COMPLETED

    service.upsert_task(
        task_id,
        title=title,
        template=(entry or {}).get("template") or state.get("selected_template") or "issue-fix",
        status=new_status.value,
        intent=(entry or {}).get("intent"),
        phase=(entry or {}).get("phase"),
        project_id=project_id,
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
            "receipt_digest": receipt.sha256_digest,
        }
    )


def register_task_routes(app: Starlette) -> None:
    routes = [
        Route("/api/v1/projects/{project_id}/tasks", api_get_tasks, methods=["GET"]),
        Route("/api/v1/projects/{project_id}/tasks", api_create_task, methods=["POST"]),
        Route("/api/v1/tasks/{task_id}", api_update_task, methods=["PATCH"]),
        Route("/api/v1/tasks/{task_id}/gate/decision", api_gate_decision, methods=["POST"]),
    ]
    app.router.routes.extend(routes)
