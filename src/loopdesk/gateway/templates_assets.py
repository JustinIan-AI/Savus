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
    task_key = f"{template_id}:{body.get('issue_id', body.get('topic', 'default'))}"

    if template_id == "issue-fix":
        saved_state = _ACTIVE_FLOW_STATES.get(task_key)
        flow = IssueFixFlow(
            issue_id=body.get("issue_id", "0"),
            title=body.get("title", "Untitled"),
            state=saved_state
        )
        record = flow.next_turn(role=body.get("role", "maker"), output=body.get("output", ""))
        _ACTIVE_FLOW_STATES[task_key] = flow.to_dict()
        return JSONResponse({
            "ok": True,
            "record": record,
            "branch": flow.branch,
            "current_step_idx": flow.current_step_idx,
            "is_ready_for_review": flow.is_ready_for_review(),
            "history": flow.history
        })
    elif template_id == "pr-commit":
        saved_state = _ACTIVE_FLOW_STATES.get(task_key)
        flow = PRCommitFlow(
            branch=body.get("branch", "main"),
            title=body.get("title", "PR"),
            commits=body.get("commits", []),
            state=saved_state
        )
        summary = flow.generate_8_section_pr_summary()
        _ACTIVE_FLOW_STATES[task_key] = flow.to_dict()
        return JSONResponse({"ok": True, "pr_summary": summary})
    elif template_id == "auto-research":
        saved_state = _ACTIVE_FLOW_STATES.get(task_key)
        flow = AutoResearchFlow(
            topic=body.get("topic", "research"),
            max_iterations=body.get("max_iterations", 3),
            state=saved_state
        )
        turn = flow.step(proposer_notes=body.get("notes", ""), eval_score=body.get("score", 0.0))
        _ACTIVE_FLOW_STATES[task_key] = flow.to_dict()
        return JSONResponse({"ok": True, "turn": turn})
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


def register_template_and_asset_routes(app: Any) -> None:
    from starlette.routing import Route

    app.router.routes.extend([
        Route("/api/v1/templates", api_list_templates, methods=["GET"]),
        Route("/api/v1/templates/render", api_render_template, methods=["POST"]),
        Route("/api/v1/templates/step", api_execute_template_step, methods=["POST"]),
        Route("/api/v1/assets", api_list_assets, methods=["GET"]),
        Route("/api/v1/assets/distribute", api_distribute_asset, methods=["POST"]),
    ])
