"""CLI tests for LoopDesk loop workspace commands."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from loopdesk.loop_workspace.loop_workspace_cmd import workspace_app


def test_loop_workspace_init_creates_state_file(tmp_path: Path) -> None:
    workspace = tmp_path / "ws"
    result = CliRunner().invoke(workspace_app, ["init", str(workspace), "--json"], catch_exceptions=False, standalone_mode=False)

    assert (workspace / "LOOP-STATE.json").exists()
    payload = json.loads(result.output.splitlines()[-1])
    assert payload["status"] == "planned"
    assert payload["project_name"] == "ws"
    assert payload["workspace_root"] == str(workspace)


def test_loop_workspace_show_returns_current_state(tmp_path: Path) -> None:
    workspace = tmp_path / "ws"
    workspace.mkdir()
    CliRunner().invoke(workspace_app, ["init", str(workspace), "--intent", "Review architecture."], catch_exceptions=False, standalone_mode=False)
    result = CliRunner().invoke(workspace_app, ["show", str(workspace), "--json"], catch_exceptions=False, standalone_mode=False)

    state = json.loads(result.output.splitlines()[-1])
    assert state["intent"] == "Review architecture."
    assert state["status"] == "planned"


def test_loop_workspace_cost_record_updates_observability(tmp_path: Path) -> None:
    workspace = tmp_path / "ws"
    workspace.mkdir()
    CliRunner().invoke(workspace_app, ["init", str(workspace)], catch_exceptions=False, standalone_mode=False)

    result = CliRunner().invoke(
        workspace_app,
        ["cost", str(workspace), "--cost-usd", "0.15", "--budget-cap-usd", "0.2", "--model", "test-model", "--json"],
        catch_exceptions=False,
        standalone_mode=False,
    )

    state = json.loads(result.output.splitlines()[-1])
    assert state["cost_observatory"]["spend_usd"] == 0.15
    assert state["cost_observatory"]["budget_cap_usd"] == 0.2
