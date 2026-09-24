from __future__ import annotations

import pytest
from loopdesk.orchestration.pty_manager import PTYSessionManager, PTYSession
from loopdesk.orchestration.parallel import WorktreeFanOutExecutor, FanOutResult

def test_pty_session_lifecycle():
    manager = PTYSessionManager()
    
    session = manager.create_session(
        session_id="sess-001",
        command=["echo", "Hello LoopDesk PTY"],
        workdir="/tmp"
    )

    assert session.session_id == "sess-001"
    assert session.is_alive() is True
    
    # Detach and Re-attach
    manager.detach_session("sess-001")
    reattached = manager.get_session("sess-001")
    assert reattached is not None
    assert reattached.session_id == "sess-001"

    # Terminate
    manager.terminate_session("sess-001")
    assert reattached.is_alive() is False

def test_worktree_fanout_and_winner_selection():
    executor = WorktreeFanOutExecutor()

    # Fan out task to 2 agents in parallel worktrees
    candidates = [
        {"agent": "claude-code", "worktree": "/tmp/wt-1", "score": 92.5, "passed_tests": 10},
        {"agent": "codex-cli", "worktree": "/tmp/wt-2", "score": 98.0, "passed_tests": 12}
    ]

    result = executor.select_winner(candidates)
    assert result.winner_agent == "codex-cli"
    assert result.winner_worktree == "/tmp/wt-2"
    assert result.winning_score == 98.0
