"""Server-Sent Events (SSE) stream for real-time task and gate event broadcasts."""

from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator
from starlette.requests import Request
from starlette.responses import StreamingResponse
from starlette.routing import Route

# In-memory pub-sub event subscribers
_subscribers: set[asyncio.Queue[str]] = set()


async def broadcast_event(event_type: str, data: dict) -> None:
    """Broadcast an SSE event payload to all active subscribers."""
    payload = f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    dead_queues = set()
    for q in _subscribers:
        try:
            q.put_nowait(payload)
        except Exception:
            dead_queues.add(q)
    for q in dead_queues:
        _subscribers.discard(q)


async def sse_event_stream(request: Request) -> StreamingResponse:
    """Stream real-time events to connected clients."""
    queue: asyncio.Queue[str] = asyncio.Queue()
    _subscribers.add(queue)

    async def event_generator() -> AsyncGenerator[str, None]:
        # Send initial connected greeting
        init_payload = f"event: connected\ndata: {json.dumps({'status': 'connected', 'timestamp': 'now'})}\n\n"
        yield init_payload

        try:
            while True:
                # Check for client disconnect if receive channel is available
                try:
                    if hasattr(request, '_receive') and await request.is_disconnected():
                        break
                except RuntimeError:
                    pass
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield msg
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat ping
                    yield "event: ping\ndata: {}\n\n"
        finally:
            _subscribers.discard(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def register_event_routes(app) -> None:
    """Mount /api/v1/events on the app."""
    app.routes.append(Route("/api/v1/events", sse_event_stream, methods=["GET"]))
