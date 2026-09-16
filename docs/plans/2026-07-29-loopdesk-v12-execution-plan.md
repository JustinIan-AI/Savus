# LoopDesk v1.2 Execution Plan

> Status: approved for execution
> Version: v1.2
> Date: 2026-07-29
> Owner: Product / Engineering
> Input: `docs/plans/prd-v1.2-gap-backlog.md`, `docs/decisions/loopdesk-v11-fdd-slices.md`, `docs/architecture/personal-loop-workspace.md`

## 1. Objective

Close the v1.1-to-v1.2 capability gaps without expanding beyond the approved personal-first, local-first loop workspace boundary. The first v1.2 slice makes the following explicit and testable:

- intent classification and planner boundary
- context sub-structure schema and compaction rules
- minimal agent runtime interface contract
- execution trace / run log schema
- task-level smart routing boundary with human override

## 2. Scope

### 2.1 In Scope

- Schema and service changes under `src/loopdesk/loop_workspace`
- Engine type and event additions under `src/loopdesk/engine`
- Gateway/turn-runtime instrumentation for trace/routing decisions
- Provider/runtime registry capability profile annotations
- Docs and focused tests for intent/planner/runtime/trace/router boundaries

### 2.2 Out of Scope

- OpenCode official support matrix expansion
- Multi-persona knowledge-workflow surface
- Team-room, cloud-sync, IM-first, or broad-media narratives
- Heavy desktop shell changes beyond existing local runtime boundary

## 3. Impact Modules

| Module | Impact | Reason |
| --- | --- | --- |
| `src/loopdesk/loop_workspace/schema.py` | High | Add intent/planner/context/trace/runtime-policy fields and validation. |
| `src/loopdesk/loop_workspace/service.py` | High | Expose read/write behavior for planner state, context compaction, and trace consumers. |
| `src/loopdesk/loop_workspace/repository.py` | Medium | Persist new schema fields with backward-compatible reads. |
| `src/loopdesk/loop_workspace/layout.py` | Medium | Add optional context file locations if B2 chooses hybrid file+state storage. |
| `src/loopdesk/engine/types.py` | High | Introduce intent, planner, runtime interface, trace, and router boundary types. |
| `src/loopdesk/engine/router_decision.py` | High | Replace implicit intent/routing logic with explicit, testable boundaries. |
| `src/loopdesk/engine/pipeline.py` | Medium | Thread intent/planner/trace/router decisions through turn pipeline. |
| `src/loopdesk/engine/runtime.py` | Medium | Emit trace events and respect runtime interface contracts. |
| `src/loopdesk/gateway/routing.py` | High | Carry runtime capability, routing decision, and override metadata in canonical envelopes. |
| `src/loopdesk/gateway/task_runtime.py` | Medium | Record structured trace entries and routing decisions per turn. |
| `src/loopdesk/gateway/rpc_sessions.py` | Medium | Expose trace query/export endpoints for Goal/Loop/time-range consumers. |
| `src/loopdesk/provider/registry.py` | Medium | Annotate runtime capability profiles for planner/router decisions. |
| `src/loopdesk/provider/selector.py` | Medium | Map provider/runtime capabilities to the new runtime interface contract. |
| `src/loopdesk/router_control.py` | Medium | Support human override points for task-level routing decisions. |
| `src/loopdesk/engine/steps/squilla_router.py` | Medium | Keep model-tier routing while exposing trace metadata for B4/B5. |
| `src/loopdesk/cli/loop_workspace_cmd.py` | Low | Add inspection commands for intent, context, trace, and runtime matrix. |
| `docs/architecture/personal-loop-workspace.md` | Medium | Update architecture narrative and diagrams for explicit planner/trace/router boundaries. |
| `docs/decisions/runtime-matrix.md` | Medium | Document runtime interface contract and capability profile expectations. |

## 4. Execution Plan

### Feature F1: Explicit Intent and Planner Boundary

**Feature goal**
Make intent classification and task planning explicit contracts instead of implicit triage behavior.

**Scope in**
- `src/loopdesk/engine/types.py`
- `src/loopdesk/engine/router_decision.py`
- `src/loopdesk/loop_workspace/schema.py`
- `src/loopdesk/loop_workspace/service.py`
- `docs/decisions/loopdesk-v12-fdd-slices.md`

**Scope out**
- Full DAG visualization UI
- External planner service rewrite

**Affected files**
- `src/loopdesk/engine/types.py`
- `src/loopdesk/engine/router_decision.py`
- `src/loopdesk/loop_workspace/schema.py`
- `src/loopdesk/loop_workspace/service.py`
- `tests/test_engine/test_router_decision.py`
- `tests/test_loop_workspace/test_schema.py`
- `tests/test_loop_workspace/test_service.py`

**Loop Engineering run format**
1. Triage: choose smallest intent/planner contract that unblocks B2-B5.
2. Maker: add failing tests for intent enum, planner input/output contract, and schema/service storage rules.
3. Checker: run `pytest tests/test_engine/test_router_decision.py tests/test_loop_workspace/test_schema.py tests/test_loop_workspace/test_service.py -q`.
4. Escalation: if planner boundary forces runtime rewrite, reduce scope to contract-only and defer runtime migration.
5. Run log: record accepted intent categories, planner output schema, and deferred decisions.
6. Stop condition: intent/planner contracts have schema, service, and regression tests; docs state boundary clearly.

**Acceptance criteria**
- Intent classification returns a bounded, documented set instead of free-form keywords.
- Planner input/output schema is explicit in `LoopWorkspaceState` or adjacent types.
- Triage still works end-to-end after contract extraction.
- Docs explain the relationship between triage, intent, and planner.

**Rollback criteria**
- Revert engine/type additions and keep existing implicit triage behavior if turn pipeline regression exceeds one focused feature slice.

---

### Feature F2: Context Sub-Structure Schema

**Feature goal**
Define minimal `user` / `project` / `task` context fields, storage rules, and compaction/prune behavior.

**Scope in**
- `src/loopdesk/loop_workspace/schema.py`
- `src/loopdesk/loop_workspace/service.py`
- `src/loopdesk/loop_workspace/repository.py`
- `src/loopdesk/loop_workspace/layout.py`
- `tests/test_loop_workspace/test_layout.py`
- `docs/architecture/personal-loop-workspace.md`

**Scope out**
- Rich media context store
- Team-shared context sync

**Affected files**
- `src/loopdesk/loop_workspace/schema.py`
- `src/loopdesk/loop_workspace/service.py`
- `src/loopdesk/loop_workspace/repository.py`
- `src/loopdesk/loop_workspace/layout.py`
- `tests/test_loop_workspace/test_layout.py`
- `tests/test_loop_workspace/test_schema.py`
- `docs/architecture/personal-loop-workspace.md`

**Loop Engineering run format**
1. Triage: choose minimal field set and one compaction rule.
2. Maker: write failing schema/layout/service tests for context read/write/prune.
3. Checker: run `pytest tests/test_loop_workspace/test_schema.py tests/test_loop_workspace/test_layout.py tests/test_loop_workspace/test_service.py -q`.
4. Escalation: if file+state consistency is too large, defer file-backed context to a follow-up slice.
5. Run log: record chosen context schema, retention rule, and edit permission boundary.
6. Stop condition: context fields are defined, persisted, compactable, and documented.

**Acceptance criteria**
- `context.user`, `context.project`, and `context.task` have minimal typed fields and default values.
- Context compaction/prune keeps state size bounded without losing required task resume data.
- Context edits go through service mutation and repository write paths.

**Rollback criteria**
- Revert schema/layout changes and keep ad-hoc context dict behavior if compaction causes data-loss risk.

---

### Feature F3: Agent Runtime Interface Contract

**Feature goal**
Document and minimally implement a bounded runtime interface contract that adapters can implement without rewriting every runtime.

**Scope in**
- `src/loopdesk/engine/types.py`
- `src/loopdesk/engine/pipeline.py`
- `src/loopdesk/provider/registry.py`
- `src/loopdesk/provider/selector.py`
- `docs/decisions/runtime-matrix.md`
- `tests/test_loop_workspace/test_runtime_matrix.py`

**Scope out**
- Full rewrite of all external runtime adapters
- Runtime capability auto-discovery network protocol

**Affected files**
- `src/loopdesk/engine/types.py`
- `src/loopdesk/engine/pipeline.py`
- `src/loopdesk/provider/registry.py`
- `src/loopdesk/provider/selector.py`
- `src/loopdesk/gateway/routing.py`
- `docs/decisions/runtime-matrix.md`
- `tests/test_loop_workspace/test_runtime_matrix.py`
- `tests/test_engine/test_router_decision.py`

**Loop Engineering run format**
1. Triage: choose smallest useful interface surface: `execute`, `resume`, `status`, `cancel`, `inspect`.
2. Maker: add failing tests for interface type, capability profile mapping, and runtime matrix consumers.
3. Checker: run `pytest tests/test_loop_workspace/test_runtime_matrix.py tests/test_engine/test_router_decision.py -q`.
4. Escalation: if pipeline coupling is too high, limit v1.2 to interface types/docs and defer enforcement.
5. Run log: record interface shape, capability profile fields, and Claude Code/Codex/Gemini mapping notes.
6. Stop condition: runtime interface exists as types/docs/tests and runtime matrix can read capability profiles.

**Acceptance criteria**
- A minimal runtime interface contract is documented and type-annotated.
- Claude Code, Codex, and Gemini entries map to the contract fields needed by v1.2 planner/router.
- Adapter authors can implement the contract without touching unrelated gateway surfaces.

**Rollback criteria**
- Revert interface type additions and keep adapter-specific behavior if gateway startup or routing regresses.

---

### Feature F4: Execution Trace and Run Log Schema

**Feature goal**
Make run logs structured enough for query, replay, export, and downstream automation.

**Scope in**
- `src/loopdesk/engine/types.py`
- `src/loopdesk/engine/pipeline.py`
- `src/loopdesk/engine/runtime.py`
- `src/loopdesk/gateway/task_runtime.py`
- `src/loopdesk/gateway/rpc_sessions.py`
- `src/loopdesk/loop_workspace/schema.py`
- `src/loopdesk/loop_workspace/service.py`

**Scope out**
- Full observability SaaS export
- Unlimited retention policy

**Affected files**
- `src/loopdesk/engine/types.py`
- `src/loopdesk/engine/pipeline.py`
- `src/loopdesk/engine/runtime.py`
- `src/loopdesk/gateway/task_runtime.py`
- `src/loopdesk/gateway/rpc_sessions.py`
- `src/loopdesk/loop_workspace/schema.py`
- `src/loopdesk/loop_workspace/service.py`
- `tests/test_engine/test_router_decision.py`
- `tests/test_gateway/test_rpc_sessions.py`
- `tests/test_loop_workspace/test_service.py`

**Loop Engineering run format**
1. Triage: choose minimum trace fields and one query axis: Goal or Loop.
2. Maker: write failing tests for trace schema, append behavior, and RPC query/export.
3. Checker: run `pytest tests/test_engine/test_router_decision.py tests/test_gateway/test_rpc_sessions.py tests/test_loop_workspace/test_service.py -q`.
4. Escalation: if retention/compaction is too broad, defer selective retention to B4 follow-up.
5. Run log: record chosen trace schema, query filters, and export format.
6. Stop condition: trace schema is stable, persisted, queryable, and has consumer tests.

**Acceptance criteria**
- Trace entries include action, tool/runtime, duration, cost, decision, result, and artifacts.
- Run log can be queried by Goal and Loop.
- Replay/export path exists for local inspection.

**Rollback criteria**
- Revert trace schema additions and keep unstructured run-log dicts if gateway latency regresses measurably.

---

### Feature F5: Task-Level Smart Routing Boundary

**Feature goal**
Separate model-tier routing from task-level routing decisions, and keep human override available.

**Scope in**
- `src/loopdesk/engine/router_decision.py`
- `src/loopdesk/engine/types.py`
- `src/loopdesk/provider/smart_routing.py`
- `src/loopdesk/gateway/routing.py`
- `src/loopdesk/router_control.py`
- `src/loopdesk/loop_workspace/schema.py`
- `src/loopdesk/gateway/config.py`

**Scope out**
- Fully autonomous unbounded routing
- Team-wide routing policy server

**Affected files**
- `src/loopdesk/engine/router_decision.py`
- `src/loopdesk/engine/types.py`
- `src/loopdesk/provider/smart_routing.py`
- `src/loopdesk/gateway/routing.py`
- `src/loopdesk/router_control.py`
- `src/loopdesk/loop_workspace/schema.py`
- `src/loopdesk/gateway/config.py`
- `src/loopdesk/engine/steps/squilla_router.py`
- `tests/test_engine/test_router_decision.py`
- `tests/test_engine/test_runtime_router_fallback.py`
- `tests/test_gateway/test_readiness.py`

**Loop Engineering run format**
1. Triage: separate model-tier routing from task routing at the type/envelope level.
2. Maker: add failing tests for router boundary inputs/outputs, override path, and unbounded-routing rejection.
3. Checker: run `pytest tests/test_engine/test_router_decision.py tests/test_engine/test_runtime_router_fallback.py tests/test_gateway/test_readiness.py -q`.
4. Escalation: if task router needs scheduler coupling, defer automation and keep human override only.
5. Run log: record routing boundary decision, fallback policy, and approval requirement.
6. Stop condition: task router boundary is explicit, tested, and preserves existing model-router behavior.

**Acceptance criteria**
- Router input includes intent, context, runtime capability, and cost/safety policy.
- Router output includes selected runtime/skill/tool path and whether approval is required.
- Unbounded fully automatic routing remains blocked by design.

**Rollback criteria**
- Revert task-router additions and keep implicit triage/routing if model-router behavior regresses.

## 5. Execution Sequence

### Phase A: Contracts First
1. F1 intent/planner boundary
2. F3 runtime interface contract
3. F4 trace/run log schema

### Phase B: Behavior Boundaries
4. F2 context sub-structure
5. F5 task-level routing boundary

### Phase C: Docs and Integration
6. Backfill architecture docs and runtime matrix
7. Run v1.2 focused gate
8. Update `docs/plans/prd-v1.2-gap-backlog.md` with completion notes

## 6. Focused Test Commands

```bash
pytest tests/test_engine/test_router_decision.py -q
pytest tests/test_loop_workspace/test_schema.py -q
pytest tests/test_loop_workspace/test_layout.py -q
pytest tests/test_loop_workspace/test_service.py -q
pytest tests/test_loop_workspace/test_runtime_matrix.py -q
pytest tests/test_gateway/test_rpc_sessions.py -q
pytest tests/test_gateway/test_readiness.py -q
pytest tests/test_engine/test_runtime_router_fallback.py -q
pytest tests/test_docs_guardrails.py tests/test_release_acceptance.py -q
```

## 7. Stop Condition for v1.2 First Slice

- F1-F5 each have passing focused tests.
- `docs/architecture/personal-loop-workspace.md` and `docs/decisions/runtime-matrix.md` reflect explicit intent/planner/runtime/trace/router boundaries.
- No new public narrative leaks team-room, cloud-sync, IM-first, or broad-media semantics.
- v1.2 backlog is updated with completed items and next queue.

## 8. Open Decisions To Confirm

1. Should planner output always be a DAG, or can v1.2 start with ordered intent-bound tasks and defer DAG enforcement?
2. Should context prefer embedded state fields, separate files, or hybrid storage for v1.2?
3. Should runtime interface be advisory documentation first, or enforced adapter contract with failing tests?

## 9. Current Implementation Status

- Status: in progress on `feat/loopdesk-v12-intent-planner-and-runtime-contracts`
- Current gate: 21 focused v1.2 tests passing as of latest verification
- Closed items: added `src/loopdesk/gateway/rpc_sessions.py:7` `json` import; fixed `tests/test_gateway/test_rpc_sessions_v12.py:13` fake runtime trace API so `sessions.trace.query` / `sessions.trace.export` have passing integration coverage
- Next task: complete F1-F5 slice review, backfill docs/runtime matrix notes, then update backlog with completion notes
- Do not expand public scope to team-room, cloud-sync, IM-first, or broad-media narratives while closing v1.2.
