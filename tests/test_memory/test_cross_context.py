from __future__ import annotations

import pytest
from loopdesk.memory.cross_context import ContextResolver, HandoffEnveloper

def test_big_at_reference():
    resolver = ContextResolver()
    resolver.register_agent_context(agent_name="planner", summary="Architected 3-tier memory engine")
    resolver.register_project_artifact(project="proj-core", artifact_path="docs/arch.md", content="# Architecture")

    prompt = "Review the plan from @agent/planner and compare with @proj-core/docs/arch.md"
    resolved_prompt = resolver.resolve_references(prompt)

    assert "[AgentContext: planner: Architected 3-tier memory engine]" in resolved_prompt
    assert "[ProjectArtifact: proj-core/docs/arch.md]" in resolved_prompt

def test_handoff_enveloper():
    enveloper = HandoffEnveloper()
    package = enveloper.create_package(
        source_agent="maker",
        destination_agent="checker",
        task_id="task-42",
        code_diff="@@ -1,3 +1,4 @@",
        decisions=["Adopted TDD discipline"]
    )

    assert package["source"] == "maker"
    assert package["dest"] == "checker"
    assert "TDD" in package["decisions"][0]
