from __future__ import annotations

import time
import uuid
from typing import Any

class ContextHandoffManager:
    def __init__(self) -> None:
        self._packets: dict[str, dict[str, Any]] = {}

    def create_handoff_packet(
        self,
        source_agent: str,
        target_agent: str,
        task_id: str,
        data: dict[str, Any],
    ) -> str:
        token = f"handoff-{uuid.uuid4().hex[:12]}"
        self._packets[token] = {
            "token": token,
            "source_agent": source_agent,
            "target_agent": target_agent,
            "task_id": task_id,
            "data": data,
            "timestamp": time.time(),
        }
        return token

    def consume_handoff_packet(self, token: str) -> dict[str, Any] | None:
        return self._packets.get(token)

    def distill_context(
        self,
        raw_data: dict[str, Any],
        max_log_entries: int = 10,
    ) -> dict[str, Any]:
        distilled: dict[str, Any] = {}
        for k, v in raw_data.items():
            if isinstance(v, list) and len(v) > max_log_entries:
                distilled[k] = v[-max_log_entries:]
            else:
                distilled[k] = v
        return distilled
