import asyncio
import pytest
from starlette.requests import Request
from starlette.responses import StreamingResponse
from loopdesk.gateway.events import sse_event_stream, broadcast_event

@pytest.mark.anyio
async def test_sse_event_stream_connect_and_broadcast():
    scope = {"type": "http", "method": "GET", "path": "/api/v1/events", "headers": []}
    req = Request(scope)
    resp = await sse_event_stream(req)
    assert isinstance(resp, StreamingResponse)
    assert resp.media_type == "text/event-stream"
    
    gen = resp.body_iterator
    # 1. Connect message
    init_chunk = await anext(gen)
    assert "event: connected" in init_chunk

    # 2. Broadcast a task event
    await broadcast_event("task_phase_changed", {"task_id": "T1", "phase": "maker"})
    broadcast_chunk = await anext(gen)
    assert "event: task_phase_changed" in broadcast_chunk
    assert "maker" in broadcast_chunk
