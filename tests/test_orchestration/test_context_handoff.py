from __future__ import annotations

import pytest
from loopdesk.orchestration.context_handoff import ContextHandoffManager

def test_context_handoff_between_agents():
    mgr = ContextHandoffManager()

    # Step 1: Claude-code generates code & patch
    turn1_data = {
        "agent": "claude-code",
        "task_id": "task-101",
        "summary": "Implemented login endpoint with rate limiting",
        "patches": ["diff --git a/auth.py b/auth.py\n+def login(): ..."],
        "key_decisions": ["Used Redis for rate limiting token bucket"]
    }
    handoff_token = mgr.create_handoff_packet(
        source_agent="claude-code",
        target_agent="reviewer-bot",
        task_id="task-101",
        data=turn1_data
    )
    assert handoff_token is not None

    # Step 2: Reviewer retrieves packet
    packet = mgr.consume_handoff_packet(handoff_token)
    assert packet is not None
    assert packet["source_agent"] == "claude-code"
    assert packet["target_agent"] == "reviewer-bot"
    assert len(packet["data"]["patches"]) == 1
    assert "Redis" in packet["data"]["key_decisions"][0]

def test_context_distillation_and_pruning():
    mgr = ContextHandoffManager()
    
    # Large context with repetitive logs
    long_logs = ["log line " + str(i) for i in range(500)]
    raw_data = {
        "verbose_logs": long_logs,
        "crucial_facts": ["DB host is 127.0.0.1", "Port is 5432"],
        "code_diff": "--- a\n+++ b\n@@ -1 +1 @@\n-old\n+new"
    }
    distilled = mgr.distill_context(raw_data, max_log_entries=5)
    assert len(distilled["verbose_logs"]) == 5
    assert distilled["crucial_facts"] == raw_data["crucial_facts"]
    assert distilled["code_diff"] == raw_data["code_diff"]
