from __future__ import annotations

import pytest
from pathlib import Path
from loopdesk.governance.gates import (
    FiveTierGateEngine,
    GateType,
    GateVerdict,
    ValidationReceipt,
    GateContext,
)

def test_five_tier_gates_and_receipt_success(tmp_path: Path):
    engine = FiveTierGateEngine()
    
    # 构造合规的上下文：Health 正常，人工批准，具备有效命令执行证据，写范围在白名单，配额充足
    context = GateContext(
        project_id="proj-alpha",
        task_id="task-101",
        operator_decision="approved",
        operator_comment="Code review passed with all unit tests green",
        validation_command="pytest tests/test_governance/ -v",
        validation_exit_code=0,
        validation_stdout="8 passed in 0.12s",
        touched_files=["src/loopdesk/governance/gates.py", "tests/test_governance/test_five_tier_gates.py"],
        allowed_write_scopes=["src/loopdesk/**", "tests/**"],
        consumed_tokens=1500,
        token_limit=100000,
    )
    
    result = engine.evaluate(context)
    assert result.passed is True
    assert result.failed_gate is None
    assert isinstance(result.receipt, ValidationReceipt)
    assert result.receipt.task_id == "task-101"
    assert result.receipt.sha256_digest != ""
    assert result.receipt.exit_code == 0

def test_five_tier_gates_health_failure():
    engine = FiveTierGateEngine(force_health_unhealthy="Service gateway down")
    context = GateContext(
        project_id="proj-alpha",
        task_id="task-101",
        operator_decision="approved",
    )
    result = engine.evaluate(context)
    assert result.passed is False
    assert result.failed_gate == GateType.HEALTH
    assert "Service gateway down" in result.reason

def test_five_tier_gates_operator_rejection():
    engine = FiveTierGateEngine()
    context = GateContext(
        project_id="proj-alpha",
        task_id="task-101",
        operator_decision="denied",
        operator_comment="Code does not meet quality bar",
    )
    result = engine.evaluate(context)
    assert result.passed is False
    assert result.failed_gate == GateType.OPERATOR
    assert "denied" in result.reason

def test_five_tier_gates_evidence_failure():
    engine = FiveTierGateEngine()
    # 证据门失败：没有验证命令，或者执行退出码非 0
    context = GateContext(
        project_id="proj-alpha",
        task_id="task-101",
        operator_decision="approved",
        validation_command="pytest",
        validation_exit_code=1,
        validation_stdout="FAILED tests/test_foo.py",
    )
    result = engine.evaluate(context)
    assert result.passed is False
    assert result.failed_gate == GateType.EVIDENCE
    assert "exit code 1" in result.reason

def test_five_tier_gates_focus_out_of_bounds():
    engine = FiveTierGateEngine()
    # Focus 门失败：修改了未授权的文件
    context = GateContext(
        project_id="proj-alpha",
        task_id="task-101",
        operator_decision="approved",
        validation_command="pytest",
        validation_exit_code=0,
        touched_files=["/etc/passwd", "src/loopdesk/governance/gates.py"],
        allowed_write_scopes=["src/loopdesk/**"],
    )
    result = engine.evaluate(context)
    assert result.passed is False
    assert result.failed_gate == GateType.FOCUS
    assert "/etc/passwd" in result.reason

def test_five_tier_gates_quota_exceeded():
    engine = FiveTierGateEngine()
    context = GateContext(
        project_id="proj-alpha",
        task_id="task-101",
        operator_decision="approved",
        validation_command="pytest",
        validation_exit_code=0,
        touched_files=["src/loopdesk/governance/gates.py"],
        allowed_write_scopes=["src/loopdesk/**"],
        consumed_tokens=150000,
        token_limit=100000,
    )
    result = engine.evaluate(context)
    assert result.passed is False
    assert result.failed_gate == GateType.QUOTA
    assert "Quota exceeded" in result.reason
