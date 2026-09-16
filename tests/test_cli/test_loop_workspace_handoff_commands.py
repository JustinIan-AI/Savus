"""CLI handoff tests for LoopDesk loop workspace commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from typer.testing import CliRunner

from loopdesk.loop_workspace.loop_workspace_cmd import workspace_app


@pytest.fixture()
def initialized_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "ws"
    CliRunner().invoke(
        workspace_app,
        ["init", str(workspace), "--intent", "Review bounded API change.", "--selected-template", "backend-engineer"],
        catch_exceptions=False,
    )
    return workspace


def test_update_workspace_changes_intent_and_template(initialized_workspace: Path) -> None:
    result = CliRunner().invoke(
        workspace_app,
        [
            "update",
            str(initialized_workspace),
            "--intent",
            "Ship bounded API fix.",
            "--selected-template",
            "frontend-engineer",
            "--status",
            "active",
            "--json",
        ],
        catch_exceptions=False,
    )

    state = json.loads(result.output.splitlines()[-1])
    assert state["intent"] == "Ship bounded API fix."
    assert state["selected_template"] == "frontend-engineer"
    assert state["status"] == "active"


def test_resume_work_item_sets_active_state(initialized_workspace: Path) -> None:
    result = CliRunner().invoke(
        workspace_app,
        [
            "resume",
            str(initialized_workspace),
            "work-1",
            "--summary",
            "Resumed from external tool.",
            "--source",
            "ui",
            "--json",
        ],
        catch_exceptions=False,
    )

    state = json.loads(result.output.splitlines()[-1])
    assert state["current_work_id"] == "work-1"
    assert state["current_work_source"] == "ui"
    assert state["status"] == "active"


def test_worktree_remove_can_retain_snapshot(tmp_path: Path) -> None:
    from tests.support.loop_workspace_repos import init_git_repo

    init_git_repo(tmp_path)
    workspace = tmp_path / "ws"
    workspace.mkdir()
    CliRunner().invoke(workspace_app, ["init", str(workspace)], catch_exceptions=False)
    CliRunner().invoke(
        workspace_app,
        ["worktree", str(workspace), "create", "--work-id", "goal-alpha", "--json"],
        catch_exceptions=False,
    )

    result = CliRunner().invoke(
        workspace_app,
        ["worktree", str(workspace), "remove", "--work-id", "goal-alpha", "--retain", "--json"],
        catch_exceptions=False,
    )

    payload = json.loads(result.output.splitlines()[-1])
    assert payload["retained"] is True
    assert (workspace / "worktrees" / "goal-alpha").exists()


def test_set_active_project_updates_project_name_and_state_snapshot(tmp_path: Path) -> None:
    workspace = tmp_path / "ws"
    CliRunner().invoke(workspace_app, ["init", str(workspace)], catch_exceptions=False)

    result = CliRunner().invoke(
        workspace_app,
        ["project", "set", str(workspace), "--name", "order-service", "--json"],
        catch_exceptions=False,
    )

    state = json.loads(result.output.splitlines()[-1])
    assert state["project_name"] == "order-service"
    assert state["active_loop_id"] == "order-service"


def test_set_active_loop_changes_current_work_without_mutating_loop_engine(tmp_path: Path) -> None:
    workspace = tmp_path / "ws"
    CliRunner().invoke(workspace_app, ["init", str(workspace)], catch_exceptions=False)
    CliRunner().invoke(
        workspace_app,
        ["engine", "start", str(workspace), "--goal", "Refactor order system.", "--json"],
        catch_exceptions=False,
    )

    result = CliRunner().invoke(
        workspace_app,
        ["loop", "set", str(workspace), "architecture-review", "--json"],
        catch_exceptions=False,
    )

    state = json.loads(result.output.splitlines()[-1])
    assert state["active_loop_id"] == "architecture-review"
    assert state["current_work_id"] == "architecture-review"
    assert state["loop_engine"]["goal"] == "Refactor order system."
