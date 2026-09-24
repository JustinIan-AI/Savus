from __future__ import annotations

import os
from typing import Any
from starlette.requests import Request
from starlette.responses import JSONResponse
from loopdesk.connectors.task_source import JiraRestAdapter, PlaneRestAdapter
from loopdesk.connectors.knowledge_source import ConfluenceRestAdapter

def _extract_token(request: Request) -> str:
    """Extract token securely from Authorization or custom connector header."""
    auth_header = request.headers.get("Authorization") or request.headers.get("X-Connector-Token")
    if auth_header:
        if auth_header.startswith("Bearer "):
            return auth_header[7:].strip()
        return auth_header.strip()
    return ""

async def api_fetch_remote_task(request: Request) -> JSONResponse:
    # Security: token must come from headers, disallow query param token
    if "token" in request.query_params:
        return JSONResponse({
            "ok": False,
            "error": "Query param 'token' is forbidden for security. Pass token in 'Authorization: Bearer <token>' or 'X-Connector-Token' header.",
            "code": "INSECURE_QUERY_TOKEN"
        }, status_code=400)

    source = request.query_params.get("source", "jira").lower()
    remote_id = request.query_params.get("remote_id", "")
    base_url = request.query_params.get("base_url", "https://example.atlassian.net")
    token = _extract_token(request) or os.environ.get(f"{source.upper()}_API_TOKEN", "")
    
    if not remote_id:
        return JSONResponse({"ok": False, "error": "remote_id is required"}, status_code=400)
        
    if source == "jira":
        adapter = JiraRestAdapter(base_url=base_url, api_token=token)
    elif source == "plane":
        slug = request.query_params.get("workspace_slug", "default")
        proj = request.query_params.get("project_id", "default")
        adapter = PlaneRestAdapter(base_url=base_url, workspace_slug=slug, project_id=proj, api_key=token)
    else:
        return JSONResponse({"ok": False, "error": f"unsupported source: {source}"}, status_code=400)
        
    task = adapter.fetch_task(remote_id)
    if not task:
        return JSONResponse({"ok": False, "error": "task not found or connection failed"}, status_code=404)
        
    return JSONResponse({
        "ok": True,
        "task": {
            "remote_id": task.remote_id,
            "title": task.title,
            "status": task.status,
            "description": task.description,
            "source": task.source
        }
    })

async def api_fetch_confluence_doc(request: Request) -> JSONResponse:
    if "token" in request.query_params:
        return JSONResponse({
            "ok": False,
            "error": "Query param 'token' is forbidden for security. Pass token in 'Authorization: Bearer <token>' or 'X-Connector-Token' header.",
            "code": "INSECURE_QUERY_TOKEN"
        }, status_code=400)

    doc_id = request.query_params.get("doc_id", "")
    base_url = request.query_params.get("base_url", "https://example.atlassian.net")
    token = _extract_token(request) or os.environ.get("CONFLUENCE_API_TOKEN", "")
    
    if not doc_id:
        return JSONResponse({"ok": False, "error": "doc_id is required"}, status_code=400)
        
    adapter = ConfluenceRestAdapter(base_url=base_url, api_token=token)
    content = adapter.fetch_doc(doc_id)
    return JSONResponse({"ok": True, "doc_id": doc_id, "content": content})

def register_connector_routes(app: Any) -> None:
    from starlette.routing import Route
    app.routes.append(Route("/api/v1/connectors/tasks", api_fetch_remote_task, methods=["GET"]))
    app.routes.append(Route("/api/v1/connectors/knowledge", api_fetch_confluence_doc, methods=["GET"]))
