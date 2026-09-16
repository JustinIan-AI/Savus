"""RPC tests for LoopDesk loop workspace methods."""

from __future__ import annotations

import sys
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


def _load_dispatcher():
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    try:
        import loopdesk.gateway.rpc as rpc_module  # noqa: F401
        from loopdesk.gateway.rpc import get_dispatcher
        return get_dispatcher()
    finally:
        sys.path.remove(str(Path(__file__).resolve().parents[2] / "src"))


@pytest.fixture()
def loop_service(tmp_path: Path) -> LoopWorkspaceService:
    return LoopWorkspaceService.from_root(tmp_path)


def test_rpc_loop_workspace_create_and_get(loop_service: LoopWorkspaceService) -> None:
    dispatcher = _load_dispatcher()

    create_payload = dispatcher.handle(
        "loop_workspace.create", {"root": str(loop_service.layout.root)}, _RpcContext()
    )
    get_payload = dispatcher.handle(
        "loop_workspace.get", {"root": str(loop_service.layout.root)}, _RpcContext()
    )

    assert create_payload["status"] == "planned"
    assert get_payload["current_work_id"] is None
    assert (loop_service.layout.root / "LOOP-STATE.json").exists()


def test_rpc_loop_workspace_record_work_item(loop_service: LoopWorkspaceService) -> None:
    dispatcher = _load_dispatcher()
    dispatcher.handle(
        "loop_workspace.create", {"root": str(loop_service.layout.root)}, _RpcContext()
    )

    payload = dispatcher.handle(
        "loop_workspace.record_work_item",
        {
            "root": str(loop_service.layout.root),
            "workId": "work-1",
            "source": "loop",
            "summary": "Brainstorm API.",
            "status": "active",
        },
        _RpcContext(),
    )

    assert payload["current_work_id"] == "work-1"
    assert payload["current_work_source"] == "loop"
    assert payload["status"] == "active"
