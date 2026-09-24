from __future__ import annotations

import re
from typing import Any, Dict, List

class ContextResolver:
    """Resolves @agent and @project references in prompts."""
    def __init__(self) -> None:
        self.agent_contexts: Dict[str, str] = {}
        self.project_artifacts: Dict[str, str] = {}

    def register_agent_context(self, agent_name: str, summary: str) -> None:
        self.agent_contexts[agent_name] = summary

    def register_project_artifact(self, project: str, artifact_path: str, content: str) -> None:
        self.project_artifacts[f"{project}/{artifact_path}"] = content

    def resolve_references(self, prompt: str) -> str:
        resolved = prompt
        
        # Resolve @agent/name
        def _replace_agent(m):
            name = m.group(1)
            summary = self.agent_contexts.get(name, "Unknown Agent")
            return f"[AgentContext: {name}: {summary}]"

        resolved = re.sub(r"@agent/([a-zA-Z0-9_\-]+)", _replace_agent, resolved)

        # Resolve @project/path
        def _replace_artifact(m):
            path = m.group(1)
            return f"[ProjectArtifact: {path}]"

        resolved = re.sub(r"@([a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-\./]+)", _replace_artifact, resolved)
        return resolved

class HandoffEnveloper:
    """Packages structured context for inter-agent handoff."""
    def create_package(
        self,
        source_agent: str,
        destination_agent: str,
        task_id: str,
        code_diff: str,
        decisions: List[str]
    ) -> Dict[str, Any]:
        return {
            "source": source_agent,
            "dest": destination_agent,
            "task_id": task_id,
            "code_diff": code_diff,
            "decisions": decisions
        }
