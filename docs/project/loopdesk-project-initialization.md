# LoopDesk Project Initialization

> Status: completed
> Date: 2026-07-07
> Owner: product/engineering

> v0.2 execution update: 2026-07-14 — v0.1 is complete; v0.2 channel adapter FDD/TDD execution is in progress.

## 1. Decision

Adopt **LoopDesk** as the product name and initialize the repository for feature-driven, test-driven, Loop Engineering execution.

## 2. Product Definition

- **Product name**: LoopDesk
- **Product type**: local-first personal loop workspace for independent developers
- **Primary users**: solo developers who move between Claude Code, Codex, Codebuddy, Trae, Gemini, and local terminals
- **Core capability**: provide a unified cross-tool context view so tasks, decisions, memory, and loop state can continue across tools without manual re-explanation
- **Execution model**: automatically triage work, dispatch bounded Goals, and preserve local control, cost visibility, approval flow, and safety boundaries

## 3. Naming Contract

| Concept | Public Name | Internal/Code Boundary |
| --- | --- | --- |
| Product | LoopDesk | keep for docs, README, CLI help, and releases |
| Python package | loopdesk runtime reuse | `src/loopdesk` is the reusable runtime library |
| v0.1 module | loop workspace | `src/loopdesk/loop_workspace` is the owned product layer |
| State file | `LOOP-STATE.json` | portable loop task state only |
| Legacy install inventory | `workspace-state.json` | do not use as the personal loop source of truth |
| Session runtime | session | internal chat/history runtime semantics, not the v0.1 product boundary |
| CLI namespace | `loop` / `loop-workspace` | public loop commands live under `loop` |

## 4. Development Methodology

- **Feature-driven development**: split the project into features first, then into small executable tasks
- **Test-driven implementation**: every task starts from a failing test and keeps changes minimal
- **Loop Engineering as runtime**: each feature/task should follow triage -> maker -> checker -> escalation -> run log -> stop condition
- **Documentation-first discipline**: research, decisions, risk plans, architecture, PRD, feature plans, and status updates must be saved before implementation claims completion

## 5. Project Status Summary

- Completed:
  - competitive review
  - product positioning
  - architecture and diagrams
  - product strategy decision
  - PRD
  - risk handling plan
  - v0.1 implementation plan
- In progress:
- v0.1 loop workspace feature implementation
- v0.2 channel adapter FDD/TDD execution
- Next step:
- execute `docs/plans/2026-07-14-loopdesk-v02-fdd-tdd-execution-plan.md`
- keep channel adapters disabled by default and workspace-first
- restore green focused pytest coverage for the v0.2 channel adapter surface

## 6. Reference Documents

- `AGENTS.md`
- `docs/decisions/product-strategy.md`
- `docs/prd/personal-loop-workspace.md`
- `docs/decisions/risk-handling-plan.md`
- `docs/plans/2026-07-07-loopdesk-implementation-plan.md`
- `docs/features/core-feature-list.md`
- `docs/architecture/personal-loop-workspace.md`
- `docs/releases/loopdesk-v0.1.md`
- `docs/acceptance/loopdesk-v0.1-acceptance-checklist.md`
- `docs/decisions/v0.2-channel-adapter.md`
- `docs/features/loopdesk-v0.2-channel-adapter-feature-breakdown.md`
- `docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md`
- `docs/releases/loopdesk-v0.2.md`
- `docs/plans/2026-07-14-loopdesk-v02-fdd-tdd-execution-plan.md`

## 7. Important Constraints

- Do not treat legacy messaging channels, broad media skills, cron-first storytelling, or team collaboration as v0.1 public features.
- Do not expand the v0.1 surface without updating the risk handling plan and relevant docs first.
- Keep the public surface minimal: loop workspace, adapters, memory, skills, artifacts, approvals, cost controls, and worktree isolation.
