from __future__ import annotations

import pytest
from loopdesk.templates.checkpoint import CheckpointManager, HandoffPacket, NoProgressBreaker, NoProgressException

def test_checkpoint_and_rewind():
    manager = CheckpointManager()

    # Create checkpoints along the steps
    cp1 = manager.save_checkpoint(step_id="step-1", state={"file_modified": "a.py", "lines": 10})
    cp2 = manager.save_checkpoint(step_id="step-2", state={"file_modified": "b.py", "lines": 25})
    cp3 = manager.save_checkpoint(step_id="step-3", state={"file_modified": "c.py", "lines": 50})

    assert len(manager.list_checkpoints()) == 3

    # Rewind to step-2
    rewound_state = manager.rewind_to("step-2")
    assert rewound_state["file_modified"] == "b.py"
    assert rewound_state["lines"] == 25
    # Steps after step-2 should be pruned or current pointer updated
    assert manager.current_step == "step-2"

def test_handoff_packet_compression():
    packet = HandoffPacket(
        task_id="task-123",
        goal="Fix issue in auth",
        current_step="checker",
        evidence_summary=["test_login passed", "token_refresh passed"],
        environment_snapshot={"branch": "codex/issue-123", "commit": "abc1234"}
    )

    exported = packet.to_compact_dict()
    assert exported["task_id"] == "task-123"
    assert exported["goal"] == "Fix issue in auth"
    assert "test_login passed" in exported["evidence"]
    assert exported["env"]["branch"] == "codex/issue-123"

def test_no_progress_breaker():
    breaker = NoProgressBreaker(max_unproductive_turns=3)

    # Turn 1: progress made
    breaker.record_turn(has_progress=True, evidence="test passed")
    assert breaker.is_tripped() is False

    # Turn 2: no progress
    breaker.record_turn(has_progress=False, evidence="")
    assert breaker.is_tripped() is False

    # Turn 3: no progress
    breaker.record_turn(has_progress=False, evidence="")
    assert breaker.is_tripped() is False

    # Turn 4: no progress -> trips on 3 consecutive no progress
    with pytest.raises(NoProgressException):
        breaker.record_turn(has_progress=False, evidence="")

    assert breaker.is_tripped() is True
