# LoopDesk v0.1 Release Notes

> Status: draft for review
> Version: v0.1
> Date: 2026-07-08
> Owner: Product / Engineering
> Boundary: local-first personal loop workspace for independent developers

## 1. Release Scope

LoopDesk v0.1 delivers the minimal personal loop workspace that keeps context, memory, and process state continuous across Claude Code, Codex, Codebuddy, Trae, and Gemini.

This release is intentionally narrow:
- one local workspace per project or focus area
- one continuous workflow surface from discovery to execution
- one durable source of truth: `LOOP-STATE.json`
- one local integration surface: MCP-first, ACP-second
- one local control surface: CLI + minimal local Web UI

Legacy LoopDesk multi-channel runtime, team/collaboration surfaces, cloud rooms, heavy desktop GUI, and broad media/skill marketplace are out of scope for v0.1 public surface.

## 2. What's New

### Workspace-first development model
- Creates a local loop workspace with `LOOP-STATE.json` as the portable source of truth.
- Default workspace layout includes `memory`, `skills`, `artifacts`, `worktrees`, and `personal_templates`.
- Supports workspace init, show, update, resume, export, and state recovery.

### Continuous workflow surface
- Backend uses `Loop` for discovery/triage/synthesis and `Goal` for bounded execution/verification.
- Frontend presents one continuous workflow; developers do not manually manage separate Loop/Goal UI modes.
- CLI and local Web UI show current work, run log, approvals, cost, and next actions in one place.

### Cross-tool continuity
- MCP-first local adapter integration for context handoff.
- Local CLI bridge records tool events back into workspace state.
- ACP is recognized as a second integration path, but v0.1 public delivery centers on MCP-first local workflows.

### Memory and template continuity
- Durable local memory with append, search, compaction, resume-pack, and export.
- Personal workflow templates for product manager, architect, backend engineer, frontend engineer, and test engineer workflows.
- Skills and templates can be inspected and reused within the personal workspace.

### Cost and safety controls
- Local cost observatory with request count and spend tracking.
- Budget cap, kill switch, denylist, approval queue, escalation, and worktree isolation.
- High-risk or ambiguous actions can be paused, blocked, or escalated to the developer.

### Local control surfaces
- `loop_workspace` CLI for init/show/update/resume/export and related workspace actions.
- Gateway RPC for programmatic workspace operations.
- Minimal local Web UI for inspecting loop/goal state, run log, approvals, and cost.
- Process-level MCP stdio server coverage for stable local integration testing.

### Loop Engine and workbench controls
- Loop Engine state machine and runner support triage/maker/checker/escalation/completed/paused workflows.
- Engine RPC persists loop state into `LOOP-STATE.json` and enforces budget/kill-switch pause checks.
- Local Web UI adds interactive run log detail, replay pack inspection, adapter tool inventory, and loop engine controls.

## 3. Key Changes

### Product boundary
- v0.1 public surface is `LoopDesk` / `loop_workspace` / `LOOP-STATE.json`.
- Legacy `session`, `workspace-state.json`, channel-first narratives, and broad media/skill catalogs are explicitly excluded from the v0.1 public story.

### Architecture boundary
- Loop and Goal remain backend orchestration boundaries.
- Frontend is an observability and approval surface, not a split-mode UI.
- Workspace state is the only durable source of truth for cross-tool continuity.

### Testing boundary
- Loop workspace tests are organized under `tests/test_loop_workspace`, `tests/test_cli/test_loop_workspace_cmd.py`, `tests/test_gateway/test_rpc_loop_workspace.py`, `tests/test_gateway/test_loop_workspace_view_static.py`, and `tests/test_loop_workspace_integration/test_developer_scenarios.py`.
- MCP stdio coverage is validated through process-level harness coverage due to current pytest/FastMCP stdio harness interaction.

## 4. Known Limitations

- ACP integration is not yet a primary public integration surface in v0.1.
- Loop scheduling defaults to local and ad hoc; cron/scheduler-heavy narratives are deferred.
- Team collaboration, cloud sync, marketplace skills, and heavy desktop GUI are not included.
- Some tests are implemented as integration smoke coverage rather than exhaustive end-to-end suites.

## 5. Known Issues

- The legacy `tests/test_loop_workspace/test_mcp_stdio.py` uses a pytest/FastMCP stdio harness that can hang in this environment. A process-level replacement coverage file exists under `tests/test_loop_workspace/test_mcp_stdio_process.py` to preserve MCP stdio verification.
- Gateway pytest collection can hang in this environment; direct runner scripts are used as an additional verification path for engine/adapter/run-log changes until collection is restored.
- Legacy LoopDesk channel/session terminology still exists in repository files outside the v0.1 public surface and is being contained by the risk handling plan.

## 6. Documentation

- Product strategy: `docs/decisions/product-strategy.md`
- PRD: `docs/prd/personal-loop-workspace.md`
- Implementation plan: `docs/plans/2026-07-07-loopdesk-implementation-plan.md`
- Risk handling plan: `docs/decisions/risk-handling-plan.md`
- Feature breakdown: `docs/features/loopdesk-v0.1-feature-breakdown.md`
- Architecture: `docs/architecture/personal-loop-workspace.md`
- Packaging and deployment: `docs/deployment.md`

## 7. Acceptance Criteria Summary

See `docs/acceptance/loopdesk-v0.1-acceptance-checklist.md` for the full feature acceptance checklist.

High-level acceptance criteria for v0.1:
- Workspace state can be created, inspected, updated, exported, and resumed.
- At least one local coding workflow is integrated via MCP and recorded in `LOOP-STATE.json`.
- Memory supports durable append, search, compaction, and resume.
- Cost and safety controls are observable and enforceable locally.
- Documentation covers install, connect tools, inspect state, run loops, recover from failures, and boundary limitations.

## 8. Launch Readiness

- Approved by Product:
- Approved by Engineering:
- Approved by QA:

## 9. Upgrade Notes

- This is the first LoopDesk-branded local-first workspace release.
- Existing OpenSquilla installations can continue to use legacy surfaces, but v0.1 public docs and CLI guidance lead with LoopDesk terminology.
- Workspace data remains local; no automatic cloud migration or team sharing is introduced.

## 10. Next Steps

- Finalize v0.1 acceptance review using `docs/acceptance/loopdesk-v0.1-acceptance-checklist.md`.
- Address known MCP stdio test harness issue before broader regression freeze.
- Collect feedback on template selection, cross-tool handoff, and cost observability for v0.2 planning.
