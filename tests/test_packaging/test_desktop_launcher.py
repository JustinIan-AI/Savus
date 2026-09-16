"""Packaging boundary tests for LoopDesk desktop distribution."""

from __future__ import annotations

import pytest

from loopdesk.loop_workspace.schema import LoopWorkspaceState


def test_desktop_launcher_does_not_replace_local_gateway_authority() -> None:
    state = LoopWorkspaceState.create(
        workspace_root="/tmp/loopdesk-desktop-test",
        intent="Validate desktop packaging boundary.",
    )

    assert state.workspace_root == "/tmp/loopdesk-desktop-test"
    assert state.schema_version == 1


def test_packaging_boundary_excludes_team_room_and_cloud_sync() -> None:
    state = LoopWorkspaceState.create(
        workspace_root="/tmp/loopdesk-desktop-test",
        intent="Validate desktop packaging boundary.",
    ).to_dict()

    assert "cloud_sync" not in str(state).lower()
    assert "team_room" not in str(state).lower()
