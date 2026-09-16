"""Process-level smoke coverage for the LoopDesk workspace MCP stdio server."""

from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import time

from pathlib import Path

from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.service import LoopWorkspaceService


def _build_process(root: Path) -> dict[str, object]:
    env = os.environ.copy()
    env["LOOPDESK_WORKSPACE"] = str(root)
    process = subprocess.Popen(
        [sys.executable, "-m", "loopdesk.loop_workspace.mcp"],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout_queue: queue.Queue[str | None] = queue.Queue()
    stderr_queue: queue.Queue[str | None] = queue.Queue()
    threading.Thread(
        target=_enqueue_lines, args=(process.stdout, stdout_queue), daemon=True
    ).start()
    threading.Thread(
        target=_enqueue_lines, args=(process.stderr, stderr_queue), daemon=True
    ).start()
    return {"process": process, "stdout_queue": stdout_queue, "stderr_queue": stderr_queue}


def _enqueue_lines(stream, output_queue: queue.Queue[str | None]) -> None:
    for line in iter(stream.readline, ""):
        output_queue.put(line)
    output_queue.put(None)


def _drain(queue_to_drain: queue.Queue[str | None]) -> str:
    parts = []
    while True:
        try:
            item = queue_to_drain.get_nowait()
        except queue.Empty:
            break
        if item is None:
            break
        parts.append(item)
    return "".join(parts)


def _send_jsonrpc(client: dict[str, object], method: str, params: object, request_id: int) -> dict[str, object]:
    request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
    client["process"].stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
    client["process"].stdin.flush()
    started = time.time()
    while time.time() - started < 10:
        try:
            line = client["stdout_queue"].get(timeout=0.1)
        except queue.Empty:
            continue
        if line is None:
            stderr = _drain(client["stderr_queue"])
            raise RuntimeError(f"MCP server closed stdout unexpectedly.{stderr}")
        stripped = line.strip()
        if not stripped:
            continue
        decoded = json.loads(stripped)
        if decoded.get("id") == request_id:
            return decoded
    stderr = _drain(client["stderr_queue"])
    raise RuntimeError(f"MCP server did not respond in time.{stderr}")


def test_mcp_process_exposes_context_and_template_tools(tmp_path: Path) -> None:
    layout = LoopWorkspaceLayout.ensure(tmp_path / "workspace")
    service = LoopWorkspaceService.from_root(layout.root)
    service.ensure_initialized(intent="MCP integration", selected_template="backend-engineer")
    service.record_work_item("work-1", "loop", "Validate MCP handoff.")
    service.set_kill_switch(True)
    service.set_denylist(["dangerous.sh"])

    client = _build_process(layout.root)
    try:
        init = _send_jsonrpc(client, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "0.0.0"}}, 1)
        assert init["result"]["protocolVersion"] == "2024-11-05"
        assert init["result"]["serverInfo"]["name"] == "loopdesk-workspace"

        tools = _send_jsonrpc(client, "tools/list", {}, 2)["result"]["tools"]
        assert [tool["name"] for tool in tools] == [
            "loopdesk.get_context_pack",
            "loopdesk.list_templates",
            "loopdesk.read_template",
            "loopdesk.run_local_command",
        ]

        context_pack = _send_jsonrpc(client, "tools/call", {"name": "loopdesk.get_context_pack", "arguments": {}}, 3)["result"]
        template = _send_jsonrpc(client, "tools/call", {"name": "loopdesk.read_template", "arguments": {"template_id": "backend-engineer"}}, 4)["result"]
        command = _send_jsonrpc(client, "tools/call", {"name": "loopdesk.run_local_command", "arguments": {"argv": ["printf", "mcp-handoff\\n"], "work_id": "work-1"}}, 5)["result"]

        context_pack_payload = json.loads(context_pack["content"][0]["text"])
        template_payload = json.loads(template["content"][0]["text"])
        command_payload = json.loads(command["content"][0]["text"])

        assert context_pack_payload["current_work_id"] == "work-1"
        assert context_pack_payload["selected_template"] == "backend-engineer"
        assert context_pack_payload["safety"]["kill_switch_enabled"] is True
        assert context_pack_payload["safety"]["denylist"] == ["dangerous.sh"]
        assert template_payload["name"] == "Backend Implementation"
        assert template_payload["loop_steps"][0] == "Review failing tests, issues, and task backlog."
        assert command_payload["ok"] is True
        assert command_payload["stdout"].strip() == "mcp-handoff"
    finally:
        process = client["process"]
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
