"""LoopDesk loop workspace CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from typer.core import TyperGroup

from loopdesk.cli.output import print_json
from loopdesk.loop_workspace.service import LoopWorkspaceService

workspace_app = typer.Typer(
    cls=TyperGroup,
    name="workspace",
    help="Manage a personal LoopDesk workspace without the gateway.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    invoke_without_command=True,
)


@workspace_app.callback()
def _workspace_callback(ctx: typer.Context) -> None:
    if ctx.resilient_parsing:
        return


def _render_state(payload: dict[str, object], json_output: bool) -> None:
    if json_output:
        print_json(payload)
        return
    typer.echo(
        "status={status} project={project_name} intent={intent} current_work={current_work_id} source={current_work_source}".format(
            status=payload.get("status"),
            project_name=payload.get("project_name"),
            intent=payload.get("intent"),
            current_work_id=payload.get("current_work_id") or "—",
            current_work_source=payload.get("current_work_source") or "—",
        )
    )
    if payload.get("state_file"):
        typer.echo("state_file={state_file}".format(state_file=payload["state_file"]))


@workspace_app.command("init")
def init_workspace(
    root: Path = typer.Argument(
        ...,
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    intent: str | None = typer.Option(None, "--intent", help="Initial workspace intent."),
    selected_template: str | None = typer.Option(
        None, "--selected-template", help="Personal workflow template id."
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable workspace state."),
) -> None:
    """Create or refresh a LoopDesk workspace and print its state."""

    service = LoopWorkspaceService.from_root(root)
    layout = service.ensure_initialized(intent=intent, selected_template=selected_template)
    payload = service.current_state()
    payload["state_file"] = str(layout.state_file)
    _render_state(payload, json_output=json_output)


@workspace_app.command("show")
def show_workspace(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable workspace state."),
) -> None:
    """Show the current LoopDesk workspace state."""

    _render_state(LoopWorkspaceService.from_root(root).current_state(), json_output=json_output)


@workspace_app.command("list")
def list_workspaces(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable workspace summary."),
) -> None:
    """List workspaces inside a parent directory."""

    entries = []
    for workspace in sorted(path for path in root.iterdir() if path.is_dir()):
        try:
            payload = LoopWorkspaceService.from_root(workspace).current_state()
        except Exception as exc:  # noqa: BLE001
            entries.append(
                {
                    "workspace_root": str(workspace),
                    "project_name": workspace.name,
                    "status": "error",
                    "error": str(exc),
                }
            )
            continue
        entries.append(
            {
                "workspace_root": payload.get("workspace_root"),
                "project_name": payload.get("project_name"),
                "status": payload.get("status"),
                "selected_template": payload.get("selected_template"),
                "updated_at": payload.get("updated_at"),
            }
        )
    payload = {"parent_root": str(root), "workspaces": entries}
    if json_output:
        print_json(payload)
        return
    for entry in entries:
        typer.echo(
            "{status} {workspace_root} template={selected_template} updated={updated_at}".format(
                status=entry.get("status"),
                workspace_root=entry.get("workspace_root"),
                selected_template=entry.get("selected_template") or "—",
                updated_at=entry.get("updated_at") or "—",
            )
        )


@workspace_app.command("update")
def update_workspace(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    intent: str | None = typer.Option(None, "--intent", help="Replace the current workspace intent."),
    status: str | None = typer.Option(None, "--status", help="Set the current workflow status."),
    selected_template: str | None = typer.Option(
        None, "--selected-template", help="Select a personal workflow template."
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable workspace state."),
) -> None:
    """Update selected LoopDesk workspace fields."""

    service = LoopWorkspaceService.from_root(root)

    def _mutator(state):
        if intent is not None:
            state.intent = intent
        if selected_template is not None:
            state.selected_template = selected_template
        if status is not None:
            state.status = state.status.__class__(status)

    service.apply_mutation(_mutator)
    _render_state(service.current_state(), json_output=json_output)


@workspace_app.command("resume")
def resume_workspace(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    work_id: str = typer.Argument(..., help="Work item id to resume."),
    summary: str = typer.Option(..., "--summary", "-s", help="Short summary for the resumed work."),
    source: str = typer.Option("external", "--source", help="Source of the resumed work item."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable workspace state."),
) -> None:
    """Resume an existing work item and mark the workspace active."""

    _render_state(
        LoopWorkspaceService.from_root(root).record_work_item(
            work_id, source, summary, status="active"
        ),
        json_output=json_output,
    )


@workspace_app.command("export")
def export_workspace(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Write exported state to this JSON file."
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable workspace state."),
) -> None:
    """Export the current LoopDesk workspace state."""

    payload = LoopWorkspaceService.from_root(root).export_state(output)
    if json_output:
        print_json(payload)
        return
    typer.echo("exported={path}".format(path=payload["path"]))


@workspace_app.command("worktree")
def worktree_workspace(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    action: str = typer.Argument(..., help="create, remove, or list."),
    work_id: str | None = typer.Option(None, "--work-id", help="Work id for create/remove."),
    branch: str | None = typer.Option(None, "--branch", help="Branch name for create."),
    retain: bool = typer.Option(False, "--retain", help="Retain snapshot on remove."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable worktree state."),
) -> None:
    """Manage isolated loop worktrees."""

    service = LoopWorkspaceService.from_root(root)
    if action == "create":
        if not work_id:
            typer.echo("Error: --work-id is required for create.", err=True)
            raise typer.Exit(1)
        payload = service.create_worktree(work_id, branch=branch)
    elif action == "remove":
        if not work_id:
            typer.echo("Error: --work-id is required for remove.", err=True)
            raise typer.Exit(1)
        payload = service.remove_worktree(work_id, retain_snapshot=retain)
    elif action == "list":
        payload = service.list_worktrees()
    else:
        typer.echo("Error: action must be create, remove, or list.", err=True)
        raise typer.Exit(1)
    if json_output:
        print_json(payload)
        return
    if action == "list":
        for item in payload.get("worktrees", []):
            typer.echo("{name} exists={exists}".format(**item))
        return
    typer.echo(
        "work_id={workId} path={path} branch={branch} retained={retained}".format(
            workId=payload.get("workId"),
            path=payload.get("path"),
            branch=payload.get("branch"),
            retained=payload.get("retained"),
        )
    )
