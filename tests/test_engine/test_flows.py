from __future__ import annotations

import pytest
from loopdesk.templates.engine import TemplateEngine
from loopdesk.templates.flows import IssueFixFlow, PRCommitFlow, AutoResearchFlow, HandoffPacket, CheckpointManager

def test_issue_fix_flow_execution():
    flow = IssueFixFlow(issue_id="204", title="Fix auth token expiration bug")
    assert flow.branch == "codex/issue-204-fix-auth-token-expiration-bug"
    
    # Step 1: Triage
    turn1 = flow.next_turn(role="triage", output="Wrote failing test test_auth_expired")
    assert turn1["step"] == "triage"
    assert turn1["status"] == "completed"
    
    # Step 2: Maker
    turn2 = flow.next_turn(role="maker", output="Fixed token expiration check logic")
    assert turn2["step"] == "maker"
    
    # Step 3: Checker
    turn3 = flow.next_turn(role="checker", output="All tests pass, green evidence collected")
    assert turn3["step"] == "checker"
    assert flow.is_ready_for_review() is True

def test_pr_commit_packet_generation():
    flow = PRCommitFlow(
        branch="codex/fix-token",
        title="fix: token expiration handling",
        commits=["feat: add test", "fix: adjust expiry timestamp"]
    )
    sample_diff = """diff --git a/src/service.py b/src/service.py
--- a/src/service.py
+++ b/src/service.py
@@ -10,1 +10,2 @@
+if time.time() > expiry: return False
diff --git a/tests/test_service.py b/tests/test_service.py
--- a/tests/test_service.py
+++ b/tests/test_service.py
@@ -5,1 +5,3 @@
+def test_token_expired(): pass
"""
    packet = flow.generate_8_section_pr_summary(diff=sample_diff)
    assert "## 1. 背景与上下文" in packet
    assert "## 2. 变更内容" in packet
    assert "src/service.py" in packet
    assert "## 3. 测试覆盖" in packet
    assert "tests/test_service.py" in packet
    assert "## 8. 审计与安全" in packet
    assert "安全扫描: 无高危敏感词/密钥泄露" in packet

def test_auto_research_convergence():
    flow = AutoResearchFlow(topic="Optimal embedding chunk size", max_iterations=2)
    # Turn 1
    res1 = flow.step(proposer_notes="Try chunk size 512", eval_score=0.70)
    assert res1["converged"] is False
    # Turn 2
    res2 = flow.step(proposer_notes="Try chunk size 256", eval_score=0.92)
    assert res2["converged"] is True

def test_handoff_and_checkpoint_rewind():
    cp_mgr = CheckpointManager()
    packet = HandoffPacket(
        task_id="task-101",
        step="maker",
        branch="codex/fix-101",
        context_summary="Investigating jwt expiration in service.py",
        evidence=["test_auth_expired fails with 401 instead of 200"]
    )
    cp_mgr.save_checkpoint("step-1", packet)
    
    packet2 = HandoffPacket(
        task_id="task-101",
        step="checker",
        branch="codex/fix-101",
        context_summary="Code modified",
        evidence=["All 5 tests pass"]
    )
    cp_mgr.save_checkpoint("step-2", packet2)
    
    # Rewind to step-1
    restored = cp_mgr.rewind_to("step-1")
    assert restored.step == "maker"
    assert restored.context_summary == "Investigating jwt expiration in service.py"


def test_issue_fix_flow_from_dict():
    flow = IssueFixFlow(issue_id="303", title="Fix memory leak")
    flow.next_turn(role="triage", output="Identified leak in listener")
    flow.next_turn(role="maker", output="Removed stale listener on close")
    
    data = flow.to_dict()
    restored = IssueFixFlow.from_dict(data)
    assert restored.issue_id == "303"
    assert restored.title == "Fix memory leak"
    assert restored.current_step_idx == 2
    assert len(restored.history) == 2
    assert restored.branch == flow.branch
    
    # Advance restored flow
    turn3 = restored.next_turn(role="checker", output="Leak verified fixed")
    assert turn3["step"] == "checker"
    assert restored.is_ready_for_review() is True


def test_pr_commit_flow_from_dict():
    flow = PRCommitFlow(
        branch="codex/fix-leak",
        title="fix: memory leak in listener",
        commits=["fix: unsubscribe listener"],
    )
    data = flow.to_dict()
    restored = PRCommitFlow.from_dict(data)
    assert restored.branch == "codex/fix-leak"
    assert restored.title == "fix: memory leak in listener"
    assert restored.commits == ["fix: unsubscribe listener"]


def test_auto_research_flow_from_dict():
    flow = AutoResearchFlow(topic="Token pruning", max_iterations=3)
    flow.step(proposer_notes="Test pruning ratio 0.2", eval_score=0.75)
    data = flow.to_dict()
    restored = AutoResearchFlow.from_dict(data)
    assert restored.topic == "Token pruning"
    assert restored.iteration == 1
    assert len(restored.history) == 1
