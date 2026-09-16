# LoopDesk v0.1 Frontend Integration Gap Report

> Date: 2026-07-10
> Owner: LoopDesk Engineering
> Source plan: `docs/plans/2026-07-09-v01-gap-implementation-plan.md`

## Summary

- 后端 RPC、Engine、Adapter 主体已补齐。
- 前端 workbench 从“静态壳”推进到了可交互面板，但 detail/replay/adapter 接线刚补完，还没拿到完整 pytest 绿标。
- 当前最大阻塞不是功能缺失，而是本环境仍无法正常收集 gateway pytest。

## Current Verification Status

- `python -m py_compile` on touched backend files exits `0`.
- Direct script verified `run_f1_regression_checks()` import path.
- Frontend static contract for new helper names is present.
- Full direct RPC/manual regression verification is still running; final evidence will be attached when it returns.

## Remaining Pre-Integration Gaps

### P1 — Test execution environment

- Focused `pytest` collection for new gateway loop workspace tests now runs successfully.
- Direct gateway verification remains the authoritative regression gate for F3-F6.

### P1 — Frontend detail/replay/adapter panel completion

- `loop_workspace.js` now wires `loop_workspace.run_log.detail`, `loop_workspace.replay.pack`, and `loop_workspace.adapter.list_tools`.
- Panel regression coverage is present in direct verification and should be expanded to gateway UI tests after full pytest stability is restored.

### P2 — Engine status writes back to state

- `loop_workspace.engine.start` creates `LoopEngineState` and returns it, but does not persist `state.loop_engine`.
- UI engine status panel therefore shows the planned fallback until start/step write engine state back into `LOOP-STATE.json`.

### P2 — Run log detail enrichment

- Backend `run_log.detail` now enriches entries with derived `cost` and related `approvals` context where available.

### P3 — Acceptance checklist/sign-off not fully evidenced

- Docs updated with final sign-off fields and focused pytest evidence.

## Recommended Next Steps

1. Fix or document the pytest collection blocker so we can run the full targeted suite.
2. Add three panel tests for run log detail, replay pack, and adapter tools.
3. Persist engine state from start/step/set_stop_condition into workspace state.
4. Enrich `run_log.detail` with associated cost/approval context or document a simpler schema.
5. Re-run full verification and fill the sign-off report.
