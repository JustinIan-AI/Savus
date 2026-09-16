"""Memory tests for LoopDesk durable memory."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.memory import DurableMemoryIndex


def test_memory_search_compacts_and_resumes(tmp_path: Path) -> None:
    index = DurableMemoryIndex(tmp_path)

    first = index.append("Remember API contract notes", "Return JSON with `data` wrapper.", tags=["api", "backend"])
    second = index.append("Use architect template for review", "Scan risks before executing.", tags=["architect"])

    hits = index.search("API notes")

    assert [hit.entry.key for hit in hits] == [first.key]
    assert "Return JSON" in hits[0].match

    compact = index.compact(keep_recent=1)

    assert compact["kept"] == 1
    assert compact["removed_keys"] == [first.key]
    assert index.search("architect template")

    pack = index.resume_pack()
    assert [entry["key"] for entry in pack["entries"]] == [second.key]

    export = index.export_state()
    assert Path(export["path"]).exists()
