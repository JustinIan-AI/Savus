"""Persistence tests for LoopDesk durable memory."""

from __future__ import annotations

from pathlib import Path

import pytest

from loopdesk.loop_workspace.memory import DurableMemoryIndex


def test_memory_compact_keeps_recent_after_append_and_resume(tmp_path: Path) -> None:
    index = DurableMemoryIndex(tmp_path)

    first = index.append("Remember API contract notes", "Return JSON with `data` wrapper.", tags=["api", "backend"])
    second = index.append("Use architect template for review", "Scan risks before executing.", tags=["architect"])

    compact = index.compact(keep_recent=1)

    assert compact["kept"] == 1
    assert compact["removed_keys"] == [first.key]
    assert index.search("architect template")
    assert [entry["key"] for entry in index.resume_pack()["entries"]] == [second.key]


def test_memory_persists_entries_across_reload(tmp_path: Path) -> None:
    index = DurableMemoryIndex(tmp_path)
    index.append("Keep retry policy under five attempts", "Avoid unbounded loops.", tags=["reliability"])

    reloaded = DurableMemoryIndex(tmp_path)

    assert reloaded.search("retry policy")
    compact = reloaded.compact(keep_recent=1)
    assert compact["kept"] == 1
    assert reloaded.search("retry policy")
    assert compact["removed_keys"] == []
    assert [entry["key"] for entry in reloaded.resume_pack()["entries"]] == ["keep-retry-policy-under-five-attempts"]
