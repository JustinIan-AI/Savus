# LoopDesk v1.1 — Launch Acceptance Checklist

> Status: in progress
> Version: v1.1
> Date: 2026-07-28
> Owner: Product / Engineering / QA
> Boundary: local-first personal loop workspace.

## 1. Handoff and CLI Surface

### 1.1 Project/Loop Switching
- [ ] `workspace project set` updates the active project and default loop.
- [ ] `workspace loop set` updates handoff context without mutating `loop_engine` execution state.
- [ ] `current_state()` exposes `active_loop_id` and `loop_engine` for cross-tool consumers.

Evidence:
- Tests: `pytest tests/test_cli/test_loop_workspace_handoff_commands.py -q`
- Docs: `docs/decisions/handoff-cli-surface.md`

### 1.2 Guided Handoff
- [ ] Guided handoff docs describe the first handoff order: project -> loop -> worktree -> resume goal.
- [ ] Public docs do not leak team-room, cloud-sync, or IM-first as default v1.1 product narratives；LoopDesk 明确不做 team-room、cloud-sync、IM-first。
- [ ] `docs/acceptance/loopdesk-v1.1-acceptance-checklist.md` must not imply team-room, cloud-sync, or IM-first as v1.1 product narratives；LoopDesk 明确不做 team-room、cloud-sync、IM-first。

Evidence:
- Tests: `pytest tests/test_docs_guardrails.py -q`

## 2. Human Model Surface

- [ ] Workspace state includes a minimal `human_profile` payload.
- [ ] Service exposes read/update behavior for preferences, coding style, architecture preference, decision pattern, and review standard.
- [ ] Gateway RPC exposes local-first human profile inspection and lightweight update.

Evidence:
- Tests: `pytest tests/test_loop_workspace/test_human_model.py tests/test_gateway/test_rpc_loop_workspace_human_model.py -q`

## 3. Release Evidence

- [ ] v1.1 release notes mention runtime matrix and desktop boundary.
- [ ] v1.1 acceptance checklist references focused test commands.
- [ ] README/docs maps include v1.1 launch artifacts.

Evidence:
- Tests: `pytest tests/test_release_acceptance.py -q`

## 4. Launch Gate

- [ ] Focused F7-F10 test sequence passes.
- [ ] No public docs, Web UI, or CLI narrative leaks team-room, cloud-sync, or IM-first semantics.
- [ ] Local-first authority remains with workspace + gateway + desktop runtime boundary.
