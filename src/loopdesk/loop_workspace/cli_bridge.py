"""Local CLI bridge for cross-tool workflows."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from loopdesk.loop_workspace.adapters import CrossToolAdapter, ToolEvent


class LocalCliBridge:
    def __init__(self, repository, *, artifact_dir: Path | None = None) -> None:
        self._repository = repository
        self._artifact_dir = artifact_dir

    def run(self, tool: str, argv: list[str], *, work_id: str | None = None) -> dict[str, Any]:
        completed = subprocess.run(argv, capture_output=True, text=True, check=False)
        artifact_path = None
        if self._artifact_dir and completed.returncode == 0:
            artifact_path = self._artifact_dir / f"{tool}-{work_id or 'run'}.txt"
            artifact_path.write_text(completed.stdout, encoding="utf-8")
        event = ToolEvent(
            tool,
            "run_command",
            {
                "workId": work_id,
                "argv": argv,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "artifactPath": str(artifact_path) if artifact_path else None,
            },
        )
        run_log = CrossToolAdapter(self._repository).translate_event_to_run_log(event)
        return {
            "tool": tool,
            "ok": completed.returncode == 0,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "run_log": run_log,
            "artifact_path": str(artifact_path) if artifact_path else None,
        }

    def render_tool_context(self, state) -> dict[str, Any]:
        return CrossToolAdapter(self._repository).build_tool_context(state)

    def suggested_handoff_command(self, state) -> str:
        context = self.render_tool_context(state)
        parts = [
            "loopdesk",
            "workspace",
            "show",
            str(context["workspaceRoot"]),
            "--json",
        ]
        if context.get("currentWorkId"):
            parts.extend(["resume", context["currentWorkId"], "--summary", "Resumed from external tool."])
        return " ".join(parts)
