"""REST endpoints for Templates and Assets in LoopDesk Gateway."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from starlette.requests import Request
from starlette.responses import JSONResponse

from loopdesk.templates.engine import TemplateEngine
from loopdesk.templates.flows import IssueFixFlow, PRCommitFlow, AutoResearchFlow
from loopdesk.assets.models import AssetMetadata, AssetType
from loopdesk.assets.registry import AssetRegistry
from loopdesk.assets.distributor import AssetDistributor

_template_engine = TemplateEngine()
_template_engine.register_builtin_templates()

_asset_distributor = AssetDistributor()


async def api_list_templates(request: Request) -> JSONResponse:
    """List all registered templates."""
    templates = _template_engine.list_templates()
    return JSONResponse({
        "ok": True,
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "version": t.version,
                "description": t.description,
                "inputs": [
                    {"id": i.id, "label": i.label, "required": i.required, "default": i.default}
                    for i in t.inputs
                ],
                "steps": [
                    {"id": s.id, "name": s.name, "role": s.role, "description": s.description}
                    for s in t.steps
                ],
                "stop_conditions": t.stop_conditions,
            }
            for t in templates
        ]
    })


async def api_render_template(request: Request) -> JSONResponse:
    """Render a template into an executable goal skeleton."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body", "code": "BAD_REQUEST"}, status_code=400)

    template_id = body.get("template_id")
    if not template_id:
        return JSONResponse({"error": "template_id is required", "code": "BAD_REQUEST"}, status_code=400)

    params = body.get("params", {})
    try:
        skeleton = _template_engine.render_goal_skeleton(template_id, params)
        return JSONResponse({"ok": True, "skeleton": skeleton})
    except ValueError as e:
        return JSONResponse({"error": str(e), "code": "TEMPLATE_RENDER_ERROR"}, status_code=400)


# In-memory runtime persistent execution store for active flows (per task_id)
_ACTIVE_FLOW_STATES: dict[str, dict[str, Any]] = {}

async def api_execute_template_step(request: Request) -> JSONResponse:
    """Advance a step in a template flow with state persistence across calls."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body", "code": "BAD_REQUEST"}, status_code=400)

    template_id = body.get("template_id")
    safe_id = str(body.get("issue_id", body.get("topic", "default")))
    task_key = f"{template_id}:{safe_id}"

    root_str = request.query_params.get("root") or body.get("root")
    flow_file: Path | None = None
    if root_str:
        flows_dir = Path(root_str).expanduser().resolve() / ".loopdesk" / "flows"
        flow_file = flows_dir / f"{template_id}_{safe_id}.json"

    saved_state = _ACTIVE_FLOW_STATES.get(task_key)
    if not saved_state and flow_file and flow_file.exists():
        try:
            saved_state = json.loads(flow_file.read_text(encoding="utf-8"))
        except Exception:
            saved_state = None

    if template_id == "issue-fix":
        if saved_state:
            flow = IssueFixFlow.from_dict(saved_state)
        else:
            flow = IssueFixFlow(
                issue_id=body.get("issue_id", "0"),
                title=body.get("title", "Untitled"),
            )
        record = flow.next_turn(role=body.get("role", "maker"), output=body.get("output", ""))
        flow_dict = flow.to_dict()
        _ACTIVE_FLOW_STATES[task_key] = flow_dict
        if flow_file:
            flow_file.parent.mkdir(parents=True, exist_ok=True)
            flow_file.write_text(json.dumps(flow_dict, indent=2, ensure_ascii=False), encoding="utf-8")
        eval_context = {
            "tests_pass": flow.is_ready_for_review(),
            "no_regression": True,
            "review_gate_approved": flow.is_ready_for_review(),
        }
        stop_eval = _template_engine.evaluate_stop_conditions("issue-fix", eval_context)
        return JSONResponse({
            "ok": True,
            "record": record,
            "branch": flow.branch,
            "current_step_idx": flow.current_step_idx,
            "is_ready_for_review": flow.is_ready_for_review(),
            "history": flow.history,
            "stop_conditions": stop_eval,
        })
    elif template_id == "pr-commit":
        if saved_state:
            flow = PRCommitFlow.from_dict(saved_state)
        else:
            flow = PRCommitFlow(
                branch=body.get("branch", "main"),
                title=body.get("title", "PR"),
                commits=body.get("commits", []),
            )
        summary = flow.generate_8_section_pr_summary()
        flow_dict = flow.to_dict()
        _ACTIVE_FLOW_STATES[task_key] = flow_dict
        if flow_file:
            flow_file.parent.mkdir(parents=True, exist_ok=True)
            flow_file.write_text(json.dumps(flow_dict, indent=2, ensure_ascii=False), encoding="utf-8")
        eval_context = {
            "diff_clean": True,
            "pr_summary_approved": bool(summary),
        }
        stop_eval = _template_engine.evaluate_stop_conditions("pr-commit", eval_context)
        return JSONResponse({"ok": True, "pr_summary": summary, "stop_conditions": stop_eval})
    elif template_id == "auto-research":
        if saved_state:
            flow = AutoResearchFlow.from_dict(saved_state)
        else:
            flow = AutoResearchFlow(
                topic=body.get("topic", "research"),
                max_iterations=body.get("max_iterations", 3),
            )
        turn = flow.step(proposer_notes=body.get("notes", ""), eval_score=body.get("score", 0.0))
        flow_dict = flow.to_dict()
        _ACTIVE_FLOW_STATES[task_key] = flow_dict
        if flow_file:
            flow_file.parent.mkdir(parents=True, exist_ok=True)
            flow_file.write_text(json.dumps(flow_dict, indent=2, ensure_ascii=False), encoding="utf-8")
        eval_context = {
            "score": body.get("score", 0.0),
            "iteration": flow.iteration,
            "max_iterations": flow.max_iterations,
        }
        stop_eval = _template_engine.evaluate_stop_conditions("auto-research", eval_context)
        return JSONResponse({"ok": True, "turn": turn, "stop_conditions": stop_eval})
    else:
        return JSONResponse({"error": f"Unsupported flow template: {template_id}", "code": "BAD_REQUEST"}, status_code=400)


async def api_list_assets(request: Request) -> JSONResponse:
    """List assets in marketplace/repository."""
    root_str = request.query_params.get("root")
    if not root_str:
        return JSONResponse({"error": "root parameter is required", "code": "BAD_REQUEST"}, status_code=400)

    registry = AssetRegistry(Path(root_str))
    assets = registry.discover()
    role_filter = request.query_params.get("role")
    if role_filter:
        assets = [a for a in assets if role_filter in a.roles]

    return JSONResponse({
        "ok": True,
        "assets": [
            {
                "id": a.id,
                "name": a.name,
                "type": a.type.value,
                "version": a.version,
                "description": a.description,
                "roles": a.roles,
            }
            for a in assets
        ]
    })


async def api_distribute_asset(request: Request) -> JSONResponse:
    """Distribute an asset into a project worktree."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body", "code": "BAD_REQUEST"}, status_code=400)

    target_dir_str = body.get("target_dir")
    if not target_dir_str:
        return JSONResponse({"error": "target_dir is required", "code": "BAD_REQUEST"}, status_code=400)

    asset_data = body.get("asset")
    if not asset_data:
        return JSONResponse({"error": "asset object is required", "code": "BAD_REQUEST"}, status_code=400)

    asset = AssetMetadata(
        id=asset_data["id"],
        name=asset_data.get("name", asset_data["id"]),
        type=AssetType(asset_data["type"]),
        version=asset_data.get("version", "1.0.0"),
        content=asset_data.get("content", ""),
        roles=asset_data.get("roles", []),
    )

    conflict = _asset_distributor.check_conflict(asset, Path(target_dir_str))
    if conflict.get("has_conflict"):
        return JSONResponse({"error": "Asset modified locally, conflict detected", "conflict": conflict}, status_code=409)

    res = _asset_distributor.distribute(asset, Path(target_dir_str))
    return JSONResponse({"ok": True, "result": res})


async def api_evaluate_stop_conditions(request: Request) -> JSONResponse:
    template_id = request.path_params.get("template_id", "")
    try:
        body = await request.json()
    except Exception:
        body = {}
    context = body.get("context", {})
    try:
        res = _template_engine.evaluate_stop_conditions(template_id, context)
        return JSONResponse({"ok": True, **res})
    except ValueError as exc:
        return JSONResponse({"error": str(exc), "code": "NOT_FOUND"}, status_code=404)


def register_template_and_asset_routes(app: Any) -> None:
    from starlette.routing import Route

    app.router.routes.extend([
        Route("/api/v1/templates", api_list_templates, methods=["GET"]),
        Route("/api/v1/templates/render", api_render_template, methods=["POST"]),
        Route("/api/v1/templates/step", api_execute_template_step, methods=["POST"]),
        Route("/api/v1/templates/{template_id}/stop-conditions", api_evaluate_stop_conditions, methods=["POST"]),
        Route("/api/v1/assets", api_list_assets, methods=["GET"]),
        Route("/api/v1/assets/distribute", api_distribute_asset, methods=["POST"]),
    ])
