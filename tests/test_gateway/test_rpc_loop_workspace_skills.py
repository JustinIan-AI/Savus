"""Skills RPC endpoint tests for LoopDesk loop workspaces."""

from __future__ import annotations

from pathlib import Path

import pytest

from loopdesk.gateway.rpc import get_dispatcher
from loopdesk.loop_workspace.service import LoopWorkspaceService
from tests.support.loop_workspace_repos import init_git_repo


class _RpcContext:
    def __init__(self) -> None:
        self.principal = _FakePrincipal()
        self.config = None


class _FakePrincipal:
    role = "operator"
    scopes = frozenset(["operator.admin"])
    is_owner = True
    authenticated = True


@pytest.fixture()
def loop_service(tmp_path: Path) -> LoopWorkspaceService:
    return LoopWorkspaceService.from_root(tmp_path)


def test_rpc_loop_workspace_skills_list(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    payload = dispatcher.handle("loop_workspace.skills.list", {"root": root}, _RpcContext())
    assert "skills" in payload
    assert any(skill["id"] == "backend-engineer" for skill in payload["skills"])


def test_rpc_loop_workspace_skills_inspect(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    payload = dispatcher.handle(
        "loop_workspace.skills.inspect",
        {"root": root, "skill_id": "backend-engineer"},
        _RpcContext(),
    )
    assert payload["id"] == "backend-engineer"
    assert "body" in payload


def test_rpc_loop_workspace_skills_audit(loop_service: LoopWorkspaceService) -> None:
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    payload = dispatcher.handle("loop_workspace.skills.audit", {"root": root}, _RpcContext())
    assert payload["count"] >= 1
    assert "backend-engineer" in payload["template_ids"]
