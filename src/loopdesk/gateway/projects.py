"""Project management and Pre-flight Task Validation routes."""

from __future__ import annotations

import json
from typing import Any
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

# In-memory registry for projects initialized with default local project
_PROJECTS: dict[str, dict[str, Any]] = {
    "default": {
        "id": "default",
        "name": "Default Workspace",
        "mode": "local",
        "root_path": ".",
        "remote_url": None,
        "required_connector": None,
    }
}

# Simulated active MCP connectors (can be discovered or queried)
_ACTIVE_MCP_CONNECTORS: set[str] = set()


async def list_projects(request: Request) -> JSONResponse:
    """List all registered projects."""
    return JSONResponse({
        "projects": list(_PROJECTS.values()),
        "count": len(_PROJECTS),
    })


async def create_project(request: Request) -> JSONResponse:
    """Register or create a project (local or remote)."""
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body", "code": "INVALID_ARGUMENT"}, status_code=400)

    proj_id = payload.get("id") or f"proj-{len(_PROJECTS) + 1}"
    name = payload.get("name") or proj_id
    mode = payload.get("mode", "local")

    if mode not in ("local", "remote"):
        return JSONResponse({"error": "mode must be 'local' or 'remote'", "code": "INVALID_ARGUMENT"}, status_code=400)

    project_data = {
        "id": proj_id,
        "name": name,
        "mode": mode,
        "root_path": payload.get("root_path"),
        "remote_url": payload.get("remote_url"),
        "required_connector": payload.get("required_connector"),
    }
    _PROJECTS[proj_id] = project_data
    return JSONResponse({"ok": True, "project": project_data})


async def validate_task_creation(request: Request) -> JSONResponse:
    """Pre-flight validation for task creation (enforces MCP connector guardrails)."""
    proj_id = request.path_params.get("project_id", "default")
    proj = _PROJECTS.get(proj_id, _PROJECTS["default"])

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    is_remote = payload.get("remote", False) or proj.get("mode") == "remote"
    req_connector = payload.get("required_connector") or proj.get("required_connector")

    if is_remote and req_connector:
        req_conn_lower = req_connector.lower()
        if req_conn_lower not in _ACTIVE_MCP_CONNECTORS:
            return JSONResponse({
                "ok": False,
                "code": "MCP_REQUIRED",
                "required_connector": req_conn_lower,
                "message": f"该远端任务依赖 {req_connector.upper()} MCP 连接器，当前未配置。请前往「设置 ➔ MCP 连接器」进行挂载。",
            })

    return JSONResponse({"ok": True, "message": "Pre-flight validation passed."})


def register_project_routes(app: Any) -> None:
    """Mount project routes into the gateway application."""
    routes = [
        Route("/api/v1/projects", list_projects, methods=["GET"]),
        Route("/api/v1/projects", create_project, methods=["POST"]),
        Route("/api/v1/projects/{project_id}/tasks/validate", validate_task_creation, methods=["POST"]),
    ]
    app.router.routes.extend(routes)
