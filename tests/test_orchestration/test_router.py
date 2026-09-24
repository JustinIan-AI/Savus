from __future__ import annotations

import pytest
from loopdesk.orchestration.router import AgentRouter, AgentCapability, AgentStatus

def test_agent_routing_by_task_type():
    router = AgentRouter()
    router.register_agent("claude-code", capabilities=[AgentCapability.CODING, AgentCapability.REFACTORING], priority=10)
    router.register_agent("codex-cli", capabilities=[AgentCapability.CODING, AgentCapability.TESTING], priority=8)
    router.register_agent("pi-cli", capabilities=[AgentCapability.RESEARCH, AgentCapability.SUMMARY], priority=10)

    # Route coding task -> claude-code has highest priority
    selected = router.route(capability=AgentCapability.CODING)
    assert selected == "claude-code"

    # Route research task -> pi-cli
    selected_research = router.route(capability=AgentCapability.RESEARCH)
    assert selected_research == "pi-cli"

def test_agent_failover_and_health_check():
    router = AgentRouter()
    router.register_agent("agent-primary", capabilities=[AgentCapability.CODING], priority=10)
    router.register_agent("agent-fallback", capabilities=[AgentCapability.CODING], priority=5)

    # Initially healthy
    assert router.route(capability=AgentCapability.CODING) == "agent-primary"

    # Report failure -> marks degraded or down
    router.report_failure("agent-primary")
    assert router.get_status("agent-primary") == AgentStatus.DEGRADED

    router.report_failure("agent-primary")
    assert router.get_status("agent-primary") == AgentStatus.DOWN

    # Now routes to fallback
    assert router.route(capability=AgentCapability.CODING) == "agent-fallback"

    # Recover primary
    router.report_success("agent-primary")
    assert router.get_status("agent-primary") == AgentStatus.HEALTHY
    assert router.route(capability=AgentCapability.CODING) == "agent-primary"
