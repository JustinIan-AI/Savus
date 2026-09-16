"""F4/F5 failing gateway integration tests for LoopDesk v1.2."""

from __future__ import annotations

import json

import pytest

from loopdesk.gateway import rpc_sessions
from loopdesk.gateway.rpc import get_dispatcher


class _FakeTaskRuntime:
    def __init__(self) -> None:
        self.enqueue_calls: list[dict[str, object]] = []
        self._traces: list[dict[str, object]] = []

    async def enqueue(self, envelope, message: str, **kwargs: object):
        self.enqueue_calls.append({"envelope": envelope, "message": message, **kwargs})
        await self._execute_task(envelope, message)
        return type("TaskHandle", (), {"task_id": "task-1", "session_key": getattr(envelope, "session_key", message)})()

    async def _execute_task(self, envelope, message: str) -> None:
        await self.append_trace({
            "trace_id": "task-1",
            "session_key": getattr(envelope, "session_key", message),
            "goal_id": getattr(envelope, "metadata", {}).get("goal_id"),
            "loop_id": getattr(envelope, "metadata", {}).get("loop_id"),
            "runtime_id": getattr(envelope, "metadata", {}).get("runtime_id") or getattr(envelope, "source_name", "runtime"),
            "skill_id": getattr(envelope, "metadata", {}).get("skill_id"),
            "tool_name": getattr(envelope, "metadata", {}).get("tool_name"),
            "action": message,
            "result": "success",
            "decision": "continue",
            "approval_required": bool(getattr(envelope, "metadata", {}).get("approval_required")),
        })

    @property
    def traces(self) -> list[dict[str, object]]:
        return list(self._traces)

    async def append_trace(self, trace: dict[str, object]) -> None:
        self._traces.append(dict(trace))

    async def query_traces(self, session_key: str, **filters: object) -> list[dict[str, object]]:
        entries = [trace for trace in self._traces if trace.get("session_key") == session_key]
        goal_id = filters.get("goal_id")
        if goal_id:
            entries = [trace for trace in entries if trace.get("goal_id") == goal_id]
        loop_id = filters.get("loop_id")
        if loop_id:
            entries = [trace for trace in entries if trace.get("loop_id") == loop_id]
        time_range = filters.get("time_range")
        if time_range:
            entries = entries[-2:]
        return entries

    async def export_traces(self, session_key: str, **filters: object):
        return {
            "session_key": session_key,
            "traces": await self.query_traces(session_key, **filters),
        }


class _FakeSessionManager:
    def __init__(self, session):
        self.session = session
        self._storage = self
        self.transcript: list[object] = []

    async def get_session(self, key: str):
        return self.session if key == self.session.session_key else None

    async def append_message(self, key: str, role: str = "user", content: str = ""):
        self.transcript.append((key, role, content))
        return type("Msg", (), {"message_id": f"msg-{len(self.transcript)}", "role": role, "content": content})()


def _make_ctx(session_manager=None, task_runtime=None, **kwargs):
    role = kwargs.pop("role", "operator")
    scopes = kwargs.pop("scopes", None)
    principal = type("P", (), {"role": role, "scopes": frozenset(scopes or ["operator.admin"]), "is_owner": True, "authenticated": True})()
    defaults = {
        "conn_id": "test-conn",
        "principal": principal,
        "config": type("C", (), {"memory": type("M", (), {"flush_enabled": False})(), "attachments": type("A", (), {"media_root": "/tmp", "persist_transcripts": True})()})(),
    }
    defaults.update(kwargs)
    ctx = rpc_sessions.RpcContext(**defaults)
    ctx.session_manager = session_manager
    ctx.task_runtime = task_runtime
    return ctx


@pytest.fixture
def dispatcher():
    return get_dispatcher()


@pytest.fixture
def session():
    return type("S", (), {"session_key": "agent:main:abc123", "session_id": "abc123", "status": "running", "agent_id": "main", "created_at": 1000, "updated_at": 2000, "model": None, "model_override": None, "queue_mode": None})()


class TestTraceRpc:
    @pytest.mark.asyncio
    async def test_sessions_send_records_trace_entries_on_task_runtime(self, dispatcher, session):
        runtime = _FakeTaskRuntime()
        manager = _FakeSessionManager(session)
        ctx = _make_ctx(session_manager=manager, task_runtime=runtime)
        await dispatcher.dispatch(
            "r1",
            "sessions.send",
            {"key": session.session_key, "message": "run order review"},
            ctx,
        )

        assert len(runtime.traces) == 1
        trace = runtime.traces[-1]
        assert trace["session_key"] == session.session_key
        assert trace["action"] == "run order review"
        assert trace["result"] == "success"

    @pytest.mark.asyncio
    async def test_trace_query_filters_by_goal_and_time_range(self, dispatcher):
        runtime = _FakeTaskRuntime()
        runtime._traces.extend([
            {"session_key": "agent:main:abc", "goal_id": "goal-1", "runtime_id": "codex-cli"},
            {"session_key": "agent:main:abc", "goal_id": "goal-1", "runtime_id": "claude-code"},
            {"session_key": "agent:main:abc", "goal_id": "goal-2", "runtime_id": "claude-code"},
        ])
        ctx = _make_ctx(task_runtime=runtime)

        res = await dispatcher.dispatch(
            "r1",
            "sessions.trace.query",
            {"key": "agent:main:abc", "goal_id": "goal-1"},
            ctx,
        )

        assert res.ok is True
        assert len(res.payload["traces"]) == 2
        assert {trace["goal_id"] for trace in res.payload["traces"]} == {"goal-1"}
        assert {trace["runtime_id"] for trace in res.payload["traces"]} == {"codex-cli", "claude-code"}

    @pytest.mark.asyncio
    async def test_trace_export_returns_json_payload(self, dispatcher):
        runtime = _FakeTaskRuntime()
        runtime._traces.append({"session_key": "agent:main:abc", "goal_id": "goal-1", "runtime_id": "codex-cli"})
        ctx = _make_ctx(task_runtime=runtime)

        res = await dispatcher.dispatch(
            "r1",
            "sessions.trace.export",
            {"key": "agent:main:abc"},
            ctx,
        )

        assert res.ok is True
        assert res.payload["session_key"] == "agent:main:abc"
        exported = json.loads(res.payload["export"])
        assert exported["traces"][0]["goal_id"] == "goal-1"
