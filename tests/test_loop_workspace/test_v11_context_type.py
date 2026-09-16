"""F1 tests for LoopDesk v1.1 workspace type and context model."""

from __future__ import annotations

from pathlib import Path

from loopdesk.loop_workspace.schema import LoopWorkspaceState, WorkspaceType
from loopdesk.loop_workspace.service import LoopWorkspaceService


def test_workspace_type_defaults_to_project_and_round_trips(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()
    state = service._repository.read()

    assert state.workspace_type == WorkspaceType.PROJECT
    assert service.current_state()["workspace_type"] == "project"


def test_context_surfaces_are_represented_in_state(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()
    service._repository.update(
        lambda state: state.context.update(
            {
                "user": {"preferences": "prefers-concise"},
                "project": {"stack": "python"},
                "task": {"goal": "ship F1"},
            }
        )
    )

    state = service._repository.read()
    assert state.context["user"] == {"preferences": "prefers-concise"}
    assert state.context["project"] == {"stack": "python"}
    assert state.context["task"] == {"goal": "ship F1"}
    assert LoopWorkspaceState.from_dict(state.to_dict()).context["task"]["goal"] == "ship F1"


def test_personal_and_business_types_are_accepted_but_not_required(tmp_path: Path) -> None:
    for workspace_type in {WorkspaceType.PERSONAL, WorkspaceType.BUSINESS}:
        service = LoopWorkspaceService.from_root(tmp_path)
        service.ensure_initialized()
        service._repository.update(
            lambda state: state.__setattr__("workspace_type", workspace_type)
        )

        assert service._repository.read().workspace_type == workspace_type
        assert service.current_state()["workspace_type"] == workspace_type.value


def test_layout_ensures_context_subdirectories(tmp_path: Path) -> None:
    workspace = tmp_path / "loop"
    workspace.mkdir()
    service = LoopWorkspaceService.from_root(workspace)
    layout = service.layout

    assert layout.context_dir.exists()
    assert layout.user_context_path.exists()
    assert layout.project_context_path.exists()
    assert layout.task_context_path.exists()


def test_service_context_snapshot_reads_project_context_files(tmp_path: Path) -> None:
    service = LoopWorkspaceService.from_root(tmp_path)
    service.ensure_initialized()
    service.record_work_item("work-1", "loop", "Context snapshot.")
    service.layout.project_context_path.write_text("stack: python", encoding="utf-8")
    service.layout.task_context_path.write_text("goal: ship F1", encoding="utf-8")

    context_pack = service.get_context_pack()
    assert context_pack["current_work_id"] == "work-1"
    assert context_pack["context"]["project"]["stack"] == "python"
    assert context_pack["context"]["task"]["goal"] == "ship F1"
    assert (tmp_path / "LOOP-STATE.json").exists()
