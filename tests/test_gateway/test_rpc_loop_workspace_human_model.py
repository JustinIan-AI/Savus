"""Gateway RPC tests for the LoopDesk v1.1 human model."""

from __future__ import annotations

from pathlib import Path

import pytest

from loopdesk.gateway.rpc import get_dispatcher
from loopdesk.loop_workspace.service import LoopWorkspaceService


class _FakePrincipal:
    role = "operator"
    scopes = frozenset(["operator.admin"])
    is_owner = True
    authenticated = True


class _RpcContext:
    def __init__(self) -> None:
        self.principal = _FakePrincipal()
        self.config = None


@pytest.fixture()
def loop_service(tmp_path: Path) -> LoopWorkspaceService:
    return LoopWorkspaceService.from_root(tmp_path)


def test_rpc_human_profile_returns_local_only_profile(loop_service: LoopWorkspaceService) -> None:
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    payload = dispatcher.handle(
        "loop_workspace.human.profile",
        {"root": root},
        _RpcContext(),
    )

    assert payload["preferences"] == {}
    assert payload["review_standard"] == {}
    assert payload["_meta"]["local_first"] is True
    assert payload["_meta"]["cloud_sync"] is False
    assert payload["_meta"]["team_context"] is False


def test_rpc_human_profile_can_update_preferences(loop_service: LoopWorkspaceService) -> None:
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    updated = dispatcher.handle(
        "loop_workspace.human.profile",
        {
            "root": root,
            "preferences": {"language": "python"},
            "review_standard": {"require_tests": True},
        },
        _RpcContext(),
    )

    assert updated["preferences"]["language"] == "python"
    assert updated["review_standard"]["require_tests"] is True
    assert updated["_meta"]["local_first"] is True
