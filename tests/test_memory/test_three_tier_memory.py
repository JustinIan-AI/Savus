from __future__ import annotations

import pytest
from loopdesk.memory.three_tier import ThreeTierMemory, MemoryTier

def test_memory_dream_distillation():
    memory = ThreeTierMemory()

    # Add short-term run logs
    memory.add_short_term(
        run_id="run-001",
        content="Encountered pytest missing parameter error. Fixed by adding target_project_dir."
    )
    memory.add_short_term(
        run_id="run-002",
        content="Encountered pytest import error on distributor. Fixed by defining AssetConflictError."
    )

    # Trigger Memory Dream distillation into project long-term memory
    distilled_docs = memory.run_memory_dream()
    assert len(distilled_docs) > 0
    assert "distilled_knowledge" in distilled_docs[0]
    assert memory.get_long_term_count() == 1

def test_tier_retrieval():
    memory = ThreeTierMemory()
    memory.store(MemoryTier.TEAM, key="coding_standard", text="Use strict typing in all modules.")
    
    found = memory.retrieve(query="typing", tier=MemoryTier.TEAM)
    assert len(found) == 1
    assert "strict typing" in found[0]
