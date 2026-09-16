"""Memory RPC endpoint tests for LoopDesk loop workspaces."""

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


def test_rpc_loop_workspace_memory_append(loop_service: LoopWorkspaceService) -> None:
    """Test memory.append RPC endpoint."""
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    payload = dispatcher.handle(
        "loop_workspace.memory.append",
        {
            "root": root,
            "title": "Test memory",
            "body": "This is a test memory entry.",
            "tags": ["test", "memory"],
            "source": "test",
        },
        _RpcContext(),
    )
    assert payload["key"] is not None
    assert payload["title"] == "Test memory"
    assert payload["source"] == "test"
    assert set(payload["tags"]) == {"test", "memory"}


def test_rpc_loop_workspace_memory_search(loop_service: LoopWorkspaceService) -> None:
    """Test memory.search RPC endpoint."""
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    dispatcher.handle(
        "loop_workspace.memory.append",
        {
            "root": root,
            "title": "Project convention",
            "body": "Always use snake_case for Python variables.",
            "tags": ["python", "convention"],
            "source": "manual",
        },
        _RpcContext(),
    )

    payload = dispatcher.handle(
        "loop_workspace.memory.search",
        {"root": root, "query": "snake case"},
        _RpcContext(),
    )
    assert len(payload["hits"]) == 1
    hit = payload["hits"][0]
    assert hit["entry"]["title"] == "Project convention"
    assert "snake_case" in hit["match"]


def test_rpc_loop_workspace_memory_compact(loop_service: LoopWorkspaceService) -> None:
    """Test memory.compact RPC endpoint."""
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    for i in range(5):
        dispatcher.handle(
            "loop_workspace.memory.append",
            {
                "root": root,
                "title": f"Entry {i}",
                "body": f"Content {i}",
                "tags": ["test"],
                "source": "test",
            },
            _RpcContext(),
        )

    payload = dispatcher.handle(
        "loop_workspace.memory.compact",
        {"root": root, "keep_recent": 3},
        _RpcContext(),
    )
    assert payload["kept"] == 3
    assert payload["removed"] == 2
    assert len(payload["kept_keys"]) == 3


def test_rpc_loop_workspace_memory_resume_pack(loop_service: LoopWorkspaceService) -> None:
    """Test memory.resume_pack RPC endpoint."""
    init_git_repo(loop_service.layout.root)
    dispatcher = get_dispatcher()
    root = str(loop_service.layout.root)

    dispatcher.handle(
        "loop_workspace.memory.append",
        {
            "root": root,
            "title": "Resume note",
            "body": "Remember to review the API contract.",
            "tags": ["api", "review"],
            "source": "manual",
        },
        _RpcContext(),
    )

    payload = dispatcher.handle(
        "loop_workspace.memory.resume_pack",
        {"root": root, "max_entries": 10},
        _RpcContext(),
    )
    assert len(payload["entries"]) == 1
    entry = payload["entries"][0]
    assert entry["key"] == "resume-note"
    assert entry["title"] == "Resume Note"
