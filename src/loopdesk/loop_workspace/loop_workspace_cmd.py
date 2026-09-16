"""LoopDesk loop workspace CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from typer.core import TyperGroup

from loopdesk.cli.output import print_json
from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
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

    payload = LoopWorkspaceService.from_root(root).current_state()
    if json_output:
        payload["state_file"] = str(LoopWorkspaceLayout.ensure(root).state_file)
    _render_state(payload, json_output=json_output)



@workspace_app.command("cost")
def record_cost(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    cost_usd: float | None = typer.Option(None, "--cost-usd", help="Observed cost in USD."),
    budget_cap_usd: float | None = typer.Option(None, "--budget-cap-usd", help="Budget cap in USD."),
    model: str | None = typer.Option(None, "--model", help="Model name for the observed cost."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable workspace state."),
) -> None:
    """Record cost observability data for the workspace."""

    payload: dict[str, object] = {}
    if cost_usd is not None or budget_cap_usd is not None or model is not None:
        payload = LoopWorkspaceService.from_root(root).record_cost(
            {
                "cost_usd": cost_usd,
                "budget_cap_usd": budget_cap_usd,
                "model": model,
            }
        )
    _render_state(payload, json_output=json_output)


@workspace_app.command("kill-switch")
def toggle_kill_switch(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    enabled: bool = typer.Option(..., "--enabled/--no-enabled", help="Enable or disable the kill switch."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable workspace state."),
) -> None:
    """Toggle the workspace kill switch."""

    _render_state(LoopWorkspaceService.from_root(root).set_kill_switch(enabled), json_output=json_output)


@workspace_app.command("denylist")
def set_denylist(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    entries: list[str] = typer.Option(..., "--entry", help="Denylist entry to set."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable workspace state."),
) -> None:
    """Set the workspace denylist."""

    _render_state(LoopWorkspaceService.from_root(root).set_denylist(entries), json_output=json_output)


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


project_app = typer.Typer(
    cls=TyperGroup,
    name="project",
    help="Select the active LoopDesk project context.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)
workspace_app.add_typer(project_app)

loop_app = typer.Typer(
    cls=TyperGroup,
    name="loop",
    help="Select the active LoopDesk loop context.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)
workspace_app.add_typer(loop_app)

engine_app = typer.Typer(
    cls=TyperGroup,
    name="engine",
    help="Operate the local LoopDesk loop engine from the workspace CLI.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)
workspace_app.add_typer(engine_app)


@engine_app.command("start")
def start_engine(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    goal: str | None = typer.Option(None, "--goal", help="Loop engine goal."),
    stop_condition: str | None = typer.Option(None, "--stop-condition", help="Stop condition for the loop."),
    max_iterations: int = typer.Option(10, "--max-iterations", help="Maximum loop iterations."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable engine state."),
) -> None:
    """Start the local loop engine for the workspace."""

    from loopdesk.loop_workspace.engine.state_machine import LoopEngineState, LoopPhase

    payload = LoopWorkspaceService.from_root(root).repository.update(lambda state: _set_loop_engine_state(state, goal=goal, stop_condition=stop_condition, max_iterations=max_iterations))
    if json_output:
        print_json(payload)
        return
    typer.echo(
        "phase={phase} goal={goal} stop_condition={stop_condition} current_iteration={current_iteration}".format(
            phase=payload["loop_engine"]["phase"],
            goal=payload["loop_engine"]["goal"],
            stop_condition=payload["loop_engine"]["stop_condition"],
            current_iteration=payload["loop_engine"]["current_iteration"],
        )
    )


@engine_app.command("stop")
def stop_engine(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable engine state."),
) -> None:
    """Stop the local loop engine for the workspace."""

    payload = LoopWorkspaceService.from_root(root).repository.update(lambda state: _set_loop_engine_state(state, phase=LoopPhase.PAUSED, goal=None, stop_condition=None))
    if json_output:
        print_json(payload)
        return
    typer.echo("phase={phase} goal={goal}".format(phase=payload["loop_engine"]["phase"], goal=payload["loop_engine"]["goal"]))


@engine_app.command("status")
def engine_status(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable engine state."),
) -> None:
    """Show the persisted loop engine state."""

    payload = LoopWorkspaceService.from_root(root).current_state()
    engine = payload.get("loop_engine") or {}
    if json_output:
        print_json({"loop_engine": engine})
        return
    typer.echo(
        "phase={phase} goal={goal} stop_condition={stop_condition} current_iteration={current_iteration}".format(
            phase=engine.get("phase", "planned"),
            goal=engine.get("goal"),
            stop_condition=engine.get("stop_condition"),
            current_iteration=engine.get("current_iteration", 0),
        )
    )


def _set_loop_engine_state(state, **overrides):
    from loopdesk.loop_workspace.engine.state_machine import LoopEngineState, LoopPhase

    engine = state.loop_engine or {}
    goal = overrides.get("goal", engine.get("goal"))
    stop_condition = overrides.get("stop_condition", engine.get("stop_condition"))
    max_iterations = int(overrides.get("max_iterations", engine.get("max_iterations", 10)) or 10)
    phase = overrides.get("phase")
    if phase is None:
        if goal is None:
            phase = LoopPhase.PAUSED
        else:
            phase = LoopPhase.PLANNED if engine.get("phase") in {None, "planned"} else LoopPhase(engine["phase"])
    engine_state = LoopEngineState(
        phase=phase,
        goal=goal,
        stop_condition=stop_condition,
        max_iterations=max_iterations,
        current_iteration=int(engine.get("current_iteration", 0) or 0),
        escalation_reason=engine.get("escalation_reason"),
    )
    state.loop_engine = {
        "phase": engine_state.phase.value,
        "goal": engine_state.goal,
        "stop_condition": engine_state.stop_condition,
        "max_iterations": engine_state.max_iterations,
        "current_iteration": engine_state.current_iteration,
        "escalation_reason": engine_state.escalation_reason,
    }
    return state


@workspace_app.command("worktree")


@project_app.command("set")
def set_active_project(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    name: str = typer.Option(..., "--name", help="Active project name for handoff context."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable workspace state."),
) -> None:
    """Set the active project and default active loop for the workspace."""

    _render_state(LoopWorkspaceService.from_root(root).set_project_name(name), json_output=json_output)


@loop_app.command("set")
def set_active_loop(
    root: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="LoopDesk workspace root.",
    ),
    loop_id: str = typer.Argument(..., help="Active loop id for handoff context."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable workspace state."),
) -> None:
    """Set the active loop without mutating the loop engine goal."""

    _render_state(LoopWorkspaceService.from_root(root).set_active_loop(loop_id), json_output=json_output)


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
