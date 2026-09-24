from __future__ import annotations

import os
import signal
import subprocess
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

class MCPServerState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    OFFLINE = "offline"
    CIRCUIT_BROKEN = "circuit_broken"

class MCPConnectorManager:
    """Manages lifecycle, state, and circuit-breaking of dynamic MCP server processes."""
    def __init__(self, failure_threshold: int = 3) -> None:
        self.failure_threshold = failure_threshold
        self._servers: Dict[str, Dict[str, Any]] = {}
        self._failures: Dict[str, int] = {}
        self._states: Dict[str, MCPServerState] = {}
        self._processes: Dict[str, subprocess.Popen] = {}

    def register_server(self, name: str, command: str, args: List[str]) -> None:
        self._servers[name] = {"command": command, "args": args}
        self._failures[name] = 0
        self._states[name] = MCPServerState.IDLE

    def start_server(self, name: str) -> bool:
        """Starts real stdio MCP server process."""
        if name not in self._servers:
            raise KeyError(f"Server {name} not registered")
        if self._states.get(name) == MCPServerState.CIRCUIT_BROKEN:
            return False

        server_def = self._servers[name]
        cmd = [server_def["command"]] + server_def["args"]
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            self._processes[name] = proc
            self._states[name] = MCPServerState.RUNNING
            return True
        except Exception:
            self.record_failure(name)
            return False

    def stop_server(self, name: str) -> None:
        """Stops running MCP server process."""
        proc = self._processes.get(name)
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=1.0)
            except Exception:
                proc.kill()
            self._processes.pop(name, None)
        if self._states.get(name) == MCPServerState.RUNNING:
            self._states[name] = MCPServerState.OFFLINE

    def record_failure(self, name: str) -> None:
        self._failures[name] = self._failures.get(name, 0) + 1
        if self._failures[name] >= self.failure_threshold:
            self._states[name] = MCPServerState.CIRCUIT_BROKEN
            self.stop_server(name)

    def get_server_state(self, name: str) -> MCPServerState:
        # Check process liveness if RUNNING
        proc = self._processes.get(name)
        if proc and self._states.get(name) == MCPServerState.RUNNING:
            if proc.poll() is not None:
                # Process died unexpectedly
                self.record_failure(name)
                return self._states.get(name, MCPServerState.IDLE)
        return self._states.get(name, MCPServerState.IDLE)

    def is_available(self, name: str) -> bool:
        state = self.get_server_state(name)
        return state not in (MCPServerState.CIRCUIT_BROKEN, MCPServerState.OFFLINE)

    def reload_server(self, name: str) -> None:
        if name in self._servers:
            self.stop_server(name)
            self._failures[name] = 0
            self._states[name] = MCPServerState.IDLE

    def cleanup_all(self) -> None:
        for name in list(self._processes.keys()):
            self.stop_server(name)

class MCPCallTracer:
    """Records and traces all MCP tool calls with execution metrics and cost attribution."""
    def __init__(self) -> None:
        self._traces: List[Dict[str, Any]] = []

    def record_call(
        self,
        server_name: str,
        tool_name: str,
        params: Dict[str, Any],
        duration_ms: int,
        token_cost: int
    ) -> str:
        trace_id = str(uuid.uuid4())
        record = {
            "trace_id": trace_id,
            "server_name": server_name,
            "tool_name": tool_name,
            "params": params,
            "duration_ms": duration_ms,
            "token_cost": token_cost,
            "timestamp": time.time()
        }
        self._traces.append(record)
        return trace_id

    def get_traces_for_server(self, server_name: str) -> List[Dict[str, Any]]:
        return [t for t in self._traces if t["server_name"] == server_name]
