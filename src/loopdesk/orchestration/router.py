from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class AgentCapability(str, Enum):
    CODING = "coding"
    REFACTORING = "refactoring"
    TESTING = "testing"
    RESEARCH = "research"
    SUMMARY = "summary"
    REVIEW = "review"

class AgentStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"

@dataclass
class AgentNode:
    agent_id: str
    capabilities: list[AgentCapability]
    priority: int = 1
    status: AgentStatus = AgentStatus.HEALTHY
    failure_count: int = 0

class AgentRouter:
    def __init__(self) -> None:
        self._nodes: dict[str, AgentNode] = {}

    def register_agent(
        self,
        agent_id: str,
        capabilities: list[AgentCapability],
        priority: int = 1,
    ) -> None:
        self._nodes[agent_id] = AgentNode(
            agent_id=agent_id,
            capabilities=capabilities,
            priority=priority,
        )

    def get_status(self, agent_id: str) -> AgentStatus | None:
        node = self._nodes.get(agent_id)
        return node.status if node else None

    def report_failure(self, agent_id: str) -> None:
        node = self._nodes.get(agent_id)
        if not node:
            return
        node.failure_count += 1
        if node.failure_count == 1:
            node.status = AgentStatus.DEGRADED
        elif node.failure_count >= 2:
            node.status = AgentStatus.DOWN

    def report_success(self, agent_id: str) -> None:
        node = self._nodes.get(agent_id)
        if not node:
            return
        node.failure_count = 0
        node.status = AgentStatus.HEALTHY

    def route(self, capability: AgentCapability) -> str | None:
        # Filter nodes supporting capability and not DOWN
        candidates = [
            n for n in self._nodes.values()
            if capability in n.capabilities and n.status != AgentStatus.DOWN
        ]
        if not candidates:
            # If all are down, try degraded or fallback
            return None

        # Sort by healthy over degraded, then by priority desc
        def sort_key(n: AgentNode):
            health_score = 1 if n.status == AgentStatus.HEALTHY else 0
            return (health_score, n.priority)

        candidates.sort(key=sort_key, reverse=True)
        return candidates[0].agent_id
