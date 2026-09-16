"""Test helpers to drive the LoopDesk workspace MCP server."""

from __future__ import annotations

import asyncio
import json
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, cast

from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.service import LoopWorkspaceService


async def _run_in_memory_client(
    root: Path,
    operation: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    async with _InMemoryMCPClient(root) as client:
        return await operation(client, *args, **kwargs)


class _InMemoryMCPClient:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._loop_thread = None
        self._event_loop = None
        self._ready = threading.Event()
        self._request_id = 1
        self._read_writer = None
        self._read_stream = None
        self._write_stream = None
        self._write_reader = None
        self._server_task = None

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        loop = self._event_loop
        if loop is None or loop.is_closed():
            raise RuntimeError("In-memory MCP client is not connected.")
        return loop

    async def __aenter__(self) -> "_InMemoryMCPClient":
        from anyio import create_memory_object_stream
        from mcp.server.session import ServerSession
        from mcp.types import JSONRPCMessage
        from loopdesk.loop_workspace.mcp import _build_server

        self._read_writer, self._read_stream = create_memory_object_stream[SessionMessage | Exception](0)
        self._write_stream, self._write_reader = create_memory_object_stream[SessionMessage](0)
        loop = asyncio.get_running_loop()
        self._event_loop = loop
        self._ready.set()
        server = _build_server()
        init_options = server.create_initialization_options()
        self._server_task = asyncio.ensure_future(
            ServerSession(
                self._write_reader,
                self._read_writer,
                init_options,
                raise_exceptions=True,
            ).run()
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._write_stream.aclose()
        await self._read_stream.aclose()
        await self._read_writer.aclose()
        self._server_task.cancel()
        try:
            await self._server_task
        except asyncio.CancelledError:
            pass
        self._server_task = None
        self._read_stream = None
        self._read_writer = None
        self._write_stream = None
        self._write_reader = None
        self._event_loop = None
        self._ready.clear()

    async def _send_raw(self, payload: dict[str, object]) -> dict[str, object]:
        import anyio.from_thread
        from mcp.types import JSONRPCError, JSONRPCResponse, JSONRPCMessage

        if self._write_stream is None or self._read_stream is None:
            raise RuntimeError("In-memory MCP client is not connected.")

        request_id = self._request_id
        self._request_id += 1
        session_message = SessionMessage(message=JSONRPCMessage.model_validate_json(json.dumps({**payload, "id": request_id})))

        def _send() -> None:
            self._write_stream.send_nowait(session_message)

        def _receive() -> dict[str, object]:
            while True:
                item = self._read_stream.receive_nowait()
                if isinstance(item, Exception):
                    raise item
                root = getattr(getattr(item, "message", None), "root", None)
                if root is None:
                    continue
                if getattr(root, "id", None) != request_id:
                    continue
                if isinstance(root, JSONRPCResponse):
                    return root.model_dump(by_alias=True, exclude_none=True)
                if isinstance(root, JSONRPCError):
                    raise RuntimeError(root.error.model_dump(by_alias=True, exclude_none=True))
                raise RuntimeError(f"Unexpected server response: {root.model_dump_json(by_alias=True, exclude_none=True)}")

        anyio.from_thread.run(_send, self.loop)
        return anyio.from_thread.run(_receive, self.loop)

    async def initialize(self) -> dict[str, object]:
        return await self.send(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "0.0.0"},
                },
            }
        )

    async def notify(self, payload: dict[str, object]) -> None:
        from mcp.types import JSONRPCNotification, JSONRPCMessage

        if self._write_stream is None:
            raise RuntimeError("In-memory MCP client is not connected.")
        await self._write_stream.send(
            SessionMessage(message=JSONRPCMessage.model_validate_json(json.dumps(payload)))
        )

    async def list_tools(self) -> list[dict[str, object]]:
        response = await self.send({"jsonrpc": "2.0", "method": "tools/list", "params": {}})
        return list(response.get("result", {}).get("tools", []))

    async def call_tool(self, name: str, arguments: dict[str, object]) -> dict[str, object]:
        response = await self.send({"jsonrpc": "2.0", "method": "tools/call", "params": {"name": name, "arguments": arguments}})
        result = response.get("result", {})
        content_list = result.get("content", [])
        payload_text = "\n".join(item.get("text", "") for item in content_list if item.get("type") == "text")
        return cast(dict[str, object], json.loads(payload_text))


async def _call_tool_in_memory(
    root: Path,
    name: str,
    arguments: dict[str, object],
) -> dict[str, object]:
    async with _InMemoryMCPClient(root) as client:
        await client.initialize()
        await client.notify({"jsonrpc": "2.0", "method": "notifications/initialized", "params": None})
        return await client.call_tool(name, arguments)


def _prime_in_memory_client(client: dict[str, object], in_memory_client: _InMemoryMCPClient) -> None:
    client["process"] = None
    client["stdout_queue"] = queue.Queue()
    client["stderr_queue"] = queue.Queue()
    client["in_memory_client"] = in_memory_client


def build_client(root: Path, *, in_process: bool = True) -> dict[str, object]:
    if in_process:
        client: dict[str, object] = {}
        try:
            asyncio.run(_run_in_memory_client(root, _prime_in_memory_client, client=client))
        except RuntimeError as exc:
            raise RuntimeError(f"Failed to start in-process MCP server: {exc}") from exc
        return client

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
    stdout_queue: "queue.Queue[str | None]" = queue.Queue()
    stderr_queue: "queue.Queue[str | None]" = queue.Queue()
    threading.Thread(target=_enqueue_lines, args=(process.stdout, stdout_queue), daemon=True).start()
    threading.Thread(target=_enqueue_lines, args=(process.stderr, stderr_queue), daemon=True).start()
    return {"process": process, "stdout_queue": stdout_queue, "stderr_queue": stderr_queue}


def initialize_client(client: dict[str, object]) -> None:
    in_memory_client = client.get("in_memory_client")
    if in_memory_client is not None:
        asyncio.run(in_memory_client.initialize())
        asyncio.run(in_memory_client.notify({"jsonrpc": "2.0", "method": "notifications/initialized", "params": None}))
        return

    response = _send_jsonrpc(
        client,
        "initialize",
        {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "0.0.0"},
        },
        1,
    )
    assert response["result"]["protocolVersion"] == "2024-11-05"
    _send_jsonrpc(client, "notifications/initialized", None, 2)


def list_tools(client: dict[str, object]) -> list[dict[str, object]]:
    in_memory_client = client.get("in_memory_client")
    if in_memory_client is not None:
        return asyncio.run(in_memory_client.list_tools())

    response = _send_jsonrpc(client, "tools/list", {}, 3)
    return list(response["result"]["tools"])


def call_tool(client: dict[str, object], name: str, arguments: dict[str, Any]) -> dict[str, object]:
    in_memory_client = client.get("in_memory_client")
    if in_memory_client is not None:
        return asyncio.run(in_memory_client.call_tool(name, arguments))

    response = _send_jsonrpc(client, "tools/call", {"name": name, "arguments": arguments}, 4)
    result = response.get("result", {})
    content_list = result.get("content", [])
    payload_text = "\n".join(item.get("text", "") for item in content_list if item.get("type") == "text")
    return json.loads(payload_text)


async def _call_tool_process(
    root: Path,
    name: str,
    arguments: dict[str, object],
) -> dict[str, object]:
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
    stdout_queue: "queue.Queue[str | None]" = queue.Queue()
    stderr_queue: "queue.Queue[str | None]" = queue.Queue()
    threading.Thread(target=_enqueue_lines, args=(process.stdout, stdout_queue), daemon=True).start()
    threading.Thread(target=_enqueue_lines, args=(process.stderr, stderr_queue), daemon=True).start()

    try:
        client: dict[str, object] = {
            "process": process,
            "stdout_queue": stdout_queue,
            "stderr_queue": stderr_queue,
        }
        initialize_client(client)
        return call_tool(client, name, arguments)
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _enqueue_lines(
    stream: Any,
    output_queue: "queue.Queue[str | None]",
) -> None:
    for line in iter(stream.readline, ""):
        output_queue.put(line)
    output_queue.put(None)


def _drain(queue_to_drain: "queue.Queue[str | None]") -> str:
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


def _send_jsonrpc(
    client: dict[str, object],
    method: str,
    params: object,
    request_id: int,
) -> dict[str, object]:
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
