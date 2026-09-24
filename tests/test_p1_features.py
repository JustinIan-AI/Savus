from __future__ import annotations

import os
import subprocess
from pathlib import Path
import pytest

from loopdesk.templates.engine import SafeConditionEvaluator, TemplateEngine
from loopdesk.templates.flows import IssueFixFlow, PRCommitFlow
from loopdesk.orchestration.parallel import WorktreeFanOutExecutor
from loopdesk.connectors.mcp_manager import MCPConnectorManager
from loopdesk.memory.learning import ContinuousLearningEngine, RejectionSignal


def test_safe_condition_evaluator():
    evaluator = SafeConditionEvaluator()
    ctx = {"tests_pass": True, "score": 95, "name": "issue-fix"}
    assert evaluator.evaluate("tests_pass == True", ctx) is True
    assert evaluator.evaluate("tests_pass == False", ctx) is False
    assert evaluator.evaluate("score >= 90", ctx) is True
    assert evaluator.evaluate("score < 80", ctx) is False
    assert evaluator.evaluate("name == 'issue-fix'", ctx) is True


def test_template_flow_serialization():
    flow = IssueFixFlow("ISSUE-100", "Fix NPE")
    assert flow.current_step == "triage"
    
    flow.next_turn("triage", "Null check needed")
    assert flow.current_step == "maker"

    serialized = flow.to_dict()
    assert serialized["current_step"] == "maker"
    assert len(serialized["history"]) == 1

    restored = IssueFixFlow("ISSUE-100", "Fix NPE", state=serialized)
    assert restored.current_step == "maker"
    assert restored.history[0]["role"] == "triage"


def test_mcp_subprocess_manager(tmp_path: Path):
    manager = MCPConnectorManager()
    server_id = "test-cat-server"
    
    manager.register_server(server_id, "cat", [])
    started = manager.start_server(server_id)
    assert started is True
    assert manager.is_available(server_id) is True

    manager.stop_server(server_id)
    assert manager.is_available(server_id) is False


def test_continuous_learning_dynamic_health():
    engine = ContinuousLearningEngine()
    health_initial = engine.get_kb_health()
    assert health_initial.score == 100.0
    assert health_initial.stale_rules_count == 0

    engine.record_rejection(RejectionSignal(
        task_id="T-1", phase="checker", reason="Lint failure", reverted_patch="diff"
    ))
    health_after_rejection = engine.get_kb_health()
    assert health_after_rejection.score == 90.0
