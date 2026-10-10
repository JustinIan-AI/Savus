from __future__ import annotations

import os
import shlex
from typing import Any, Dict, List
from starlette.requests import Request
from starlette.responses import JSONResponse
from loopdesk.orchestration.pty_manager import PTYSessionManager
from loopdesk.orchestration.context_handoff import ContextHandoffManager
from loopdesk.memory import ContextResolver, HandoffEnveloper
from loopdesk.orchestration.parallel import WorktreeFanOutExecutor

pty_manager = PTYSessionManager()
handoff_manager = ContextHandoffManager()
context_resolver = ContextResolver()
handoff_enveloper = HandoffEnveloper()
fanout_executor = WorktreeFanOutExecutor()

# Strict executable whitelist for PTY creation
ALLOWED_COMMANDS = {
    "/bin/zsh",
    "/bin/bash",
    "/bin/sh",
    "zsh",
    "codex",
    "claude",
    "pi",
    "cat",
}

def _verify_pty_auth(request: Request) -> bool:
    """Enforce token or admin header authentication for PTY operations."""
    auth_header = request.headers.get("X-LoopDesk-Admin-Key") or request.headers.get("Authorization")
    expected_key = os.environ.get("LOOPDESK_ADMIN_KEY")
    if not expected_key:
        return False
    if auth_header:
        token = auth_header.replace("Bearer ", "").strip()
        if token == expected_key:
            return True
    return False

async def api_create_pty_session(request: Request) -> JSONResponse:
    if not _verify_pty_auth(request):
        return JSONResponse({"error": "Unauthorized PTY creation", "code": "FORBIDDEN"}, status_code=403)

    data = await request.json()
    session_id = data.get("session_id")
    command = data.get("command", ["/bin/zsh"])
    workdir = data.get("workdir", "/tmp")
    
    if not session_id:
        return JSONResponse({"error": "session_id is required"}, status_code=400)

    # Command whitelist verification
    cmd_list = command if isinstance(command, list) else shlex.split(str(command))
    if not cmd_list:
        return JSONResponse({"error": "command is empty"}, status_code=400)
    
    base_exe = os.path.basename(cmd_list[0])
    full_exe = cmd_list[0]
    if base_exe not in ALLOWED_COMMANDS and full_exe not in ALLOWED_COMMANDS:
        return JSONResponse({
            "error": f"Command '{cmd_list[0]}' is not in allowed execution whitelist",
            "code": "COMMAND_NOT_ALLOWED",
            "allowed": sorted(list(ALLOWED_COMMANDS))
        }, status_code=403)
        
    session = pty_manager.create_session(session_id=session_id, command=cmd_list, workdir=workdir)
    return JSONResponse({
        "ok": True,
        "session_id": session.session_id,
        "pid": session.pid,
        "alive": session.is_alive(),
        "detached": session.is_detached
    })

async def api_write_pty_session(request: Request) -> JSONResponse:
    if not _verify_pty_auth(request):
        return JSONResponse({"error": "Unauthorized PTY operation", "code": "FORBIDDEN"}, status_code=403)
    session_id = request.path_params["session_id"]
    data = await request.json()
    input_str = data.get("input", "")
    session = pty_manager.get_session(session_id)
    if not session or not session.is_alive():
        return JSONResponse({"error": "session not found or dead"}, status_code=404)
        
    written = session.write(input_str.encode("utf-8"))
    return JSONResponse({"ok": True, "written_bytes": written})

async def api_read_pty_session(request: Request) -> JSONResponse:
    if not _verify_pty_auth(request):
        return JSONResponse({"error": "Unauthorized PTY operation", "code": "FORBIDDEN"}, status_code=403)
    session_id = request.path_params["session_id"]
    session = pty_manager.get_session(session_id)
    if not session:
        return JSONResponse({"error": "session not found"}, status_code=404)
        
    output = session.read(max_bytes=4096, timeout=0.2)
    return JSONResponse({"ok": True, "output": output.decode("utf-8", errors="replace")})

async def api_terminate_pty_session(request: Request) -> JSONResponse:
    if not _verify_pty_auth(request):
        return JSONResponse({"error": "Unauthorized PTY operation", "code": "FORBIDDEN"}, status_code=403)
    session_id = request.path_params["session_id"]
    pty_manager.terminate_session(session_id)
    return JSONResponse({"ok": True, "terminated": True})

async def api_context_handoff(request: Request) -> JSONResponse:
    data = await request.json()
    source_agent = data.get("from_agent") or data.get("source_agent", "claude")
    target_agent = data.get("to_agent") or data.get("target_agent", "codex")
    task_id = data.get("task_id", "TASK-DEFAULT")
    context_data = data.get("context_data", {})
    
    token = handoff_manager.create_handoff_packet(
        source_agent=source_agent,
        target_agent=target_agent,
        task_id=task_id,
        data=context_data
    )
    packet = handoff_manager.consume_handoff_packet(token) or {}
    packet["from_agent"] = packet.get("source_agent", source_agent)
    packet["to_agent"] = packet.get("target_agent", target_agent)

    prompt_text = context_data.get("prompt", "")
    resolved_prompt = context_resolver.resolve_references(prompt_text) if prompt_text else ""
    envelope = handoff_enveloper.create_package(
        source_agent=source_agent,
        destination_agent=target_agent,
        task_id=task_id,
        code_diff=context_data.get("code_diff", ""),
        decisions=context_data.get("decisions", []),
    )
    return JSONResponse({
        "ok": True,
        "token": token,
        "handoff_packet": packet,
        "envelope": envelope,
        "resolved_prompt": resolved_prompt,
    })


async def api_fanout_execution(request: Request) -> JSONResponse:
    if not _verify_pty_auth(request):
        return JSONResponse({"error": "Unauthorized fanout operation", "code": "FORBIDDEN"}, status_code=403)
    data = await request.json()
    candidates = data.get("candidates", [])
    if not candidates:
        return JSONResponse({"error": "candidates list required", "code": "BAD_REQUEST"}, status_code=400)
    winner = fanout_executor.select_winner(candidates)
    return JSONResponse({
        "ok": True,
        "winner": {
            "agent": winner.winner_agent,
            "worktree": winner.winner_worktree,
            "score": winner.winning_score,
        },
    })

def register_orchestration_routes(app: Any) -> None:
    from starlette.routing import Route
    app.routes.extend([
        Route("/api/v1/orchestration/pty", api_create_pty_session, methods=["POST"]),
        Route("/api/v1/orchestration/pty/{session_id}/write", api_write_pty_session, methods=["POST"]),
        Route("/api/v1/orchestration/pty/{session_id}/read", api_read_pty_session, methods=["GET"]),
        Route("/api/v1/orchestration/pty/{session_id}", api_terminate_pty_session, methods=["DELETE"]),
        Route("/api/v1/orchestration/handoff", api_context_handoff, methods=["POST"]),
        Route("/api/v1/orchestration/fanout", api_fanout_execution, methods=["POST"]),
    ])
