# LoopDesk v1.1 — Launch Completion Release Notes

> Status: candidate
> Version: v1.1
> Date: 2026-07-28
> Owner: Product / Engineering / QA
> Boundary: local-first personal loop workspace; IM remains an optional control/notification surface only.

## 1. Summary

LoopDesk v1.1 closes the remaining launch gaps from the PRD by adding explicit handoff CLI surfaces, guided handoff documentation, a minimal human model surface, and focused release/acceptance evidence.

## 2. Highlights

- `workspace project set` and `workspace loop set` provide an explicit cross-tool handoff entrypoint on top of `LOOP-STATE.json`.
- Guided handoff docs define the first handoff path: project -> loop -> worktree -> resume goal.
- Human profile state adds a minimal local-first `preferences`, `coding_style`, `architecture_preference`, `decision_pattern`, and `review_standard` payload.
- v1.1 release and acceptance docs are now present with focused test commands and launch criteria.

## 3. Boundary Reminders

- v1.1 keeps `LOOP-STATE.json`, memory, skills, artifacts, approvals, and worktrees as the durable source of truth.
- The official runtime matrix is locked in `docs/decisions/runtime-matrix.md`.
- Desktop packaging remains a local runtime + system launcher boundary; v1.1 does not introduce an Electron shell.
- v1.1 公共叙事明确不采用 team-room、cloud-sync、IM-first；这些方向在 docs/decisions/v0.2-channel-adapter.md 与 docs/decisions/handoff-cli-surface.md 中继续标注为 LoopDesk 不做的边界。

## 4. Verification

See `docs/acceptance/loopdesk-v1.1-acceptance-checklist.md` for QA commands and sign-off criteria.

## 5. Next Steps

- Complete F8 guided handoff enforcement in Web UI.
- Complete F9 human model inspection in local Web UI.
- Lock v1.1 public docs and CLI help to the personal-first, loop-state-first narrative.
