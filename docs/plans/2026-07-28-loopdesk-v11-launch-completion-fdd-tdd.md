# LoopDesk v1.1 Launch Completion — FDD/TDD Execution Plan

> **For Codex:** REQUIRED SUB-SKILL: Use `writing-plans` to execute this plan task-by-task.

**Goal:** 补齐 PRD v1.1 中尚未落入实现面的 launch、multi-loop、onboarding、human model、release/acceptance 证据，并按 failing-test-first 交付。

**Architecture:** 在现有 `LOOP-STATE.json`、`loop_workspace`、CLI、local Web UI、gateway RPC 基础上做最小扩展；不推翻 v0.1/v0.2 已确定的本地优先、workspace-first、IM 为辅边界。

**Tech Stack:** Python 3.12、pytest、typer CLI、Starlette gateway、`src/loopdesk/loop_workspace`、`src/loopdesk/gateway`、`docs/prd/personal-loop-workspace-v1.1.zh.md`

---

## Feature F7: Project/Loop Switching CLI Surface

Stop condition: 项目 / Loop 切换在 CLI 中有明确命令、状态回写和测试锚点。

### Task F7.1: Add project and active-loop selection commands

**Files:**
- Edit: `src/loopdesk/loop_workspace/schema.py:1`
- Edit: `src/loopdesk/loop_workspace/service.py:1`
- Edit: `src/loopdesk/loop_workspace/loop_workspace_cmd.py:1`
- Test: `tests/test_cli/test_loop_workspace_handoff_commands.py:1`

**Step 1: Write the failing test**

- `test_set_active_project_updates_project_name_and_state_snapshot`
- `test_set_active_loop_changes_current_work_without_mutating_loop_engine`

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli/test_loop_workspace_handoff_commands.py -k "test_set_active_project_updates_project_name_and_state_snapshot or test_set_active_loop_changes_current_work_without_mutating_loop_engine" -x`
Expected: FAIL on missing CLI command / missing active-loop mutation.

**Step 3: Write minimal implementation**

- 在 schema/service 增加最小 project/active-loop 切换契约，不改 loop engine 执行语义。
- 在 CLI 增加 `loop project set` 与 `loop loop set`，输出 JSON/文本状态。

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli/test_loop_workspace_handoff_commands.py -k "test_set_active_project_updates_project_name_and_state_snapshot or test_set_active_loop_changes_current_work_without_mutating_loop_engine" -x`
Expected: PASS

**Run log**

```text
Run log: F7.1 completed at 2026-07-28; handoff CLI tests passed; evidence: docs/decisions/handoff-cli-surface.md; risk note: project/loop switching is state-selection only, not workspace migration.
```

---

## Feature F8: Guided Handoff and Anti-Room Guardrails

Stop condition: guided handoff 视图/文案和 anti-room guardrail 有可验收文档与静态检查测试。

### Task F8.1: Add guided handoff docs and guardrail tests

**Files:**
- Edit: `docs/guides/guided-handoff.md:1`
- Edit: `docs/prd/personal-loop-workspace-v1.1.zh.md:1`
- Test: `tests/test_docs_guardrails.py:1`

**Step 1: Write the failing test**

- `test_guided_handoff_doc_exists_and_mentions_project_loop_worktree_resume`
- `test_anti_room_guardrail_docs_do_not_leak_team_room_or_cloud_sync`

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_docs_guardrails.py -x`
Expected: FAIL on missing docs/tests.

**Step 3: Write minimal implementation**

- 增加 `docs/guides/guided-handoff.md`，明确首次 handoff：project -> Loop -> worktree -> resume Goal。
- 在 v1.1 PRD 与 guardrail test 中显式拒绝 team room / cloud sync / IM-first 作为主叙事。

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_docs_guardrails.py -x`
Expected: PASS

**Run log**

```text
Run log: F8.1 completed at <datetime>; docs guardrail tests passed; risk note: kept handoff docs local-first and CLI-first.
```

---

## Feature F9: Human Model Surface

Stop condition: human profile 在 workspace state、CLI、RPC 中有最小可读写契约和测试。

### Task F9.1: Add human profile schema and inspection surface

**Files:**
- Edit: `src/loopdesk/loop_workspace/schema.py:1`
- Edit: `src/loopdesk/loop_workspace/service.py:1`
- Edit: `src/loopdesk/gateway/rpc_loop_workspace.py:1`
- Test: `tests/test_loop_workspace/test_human_model.py:1`
- Test: `tests/test_gateway/test_rpc_loop_workspace_human_model.py:1`

**Step 1: Write the failing test**

- `test_human_profile_defaults_to_empty_local_first_payload`
- `test_human_profile_can_record_preferences_and_review_standard`
- `test_rpc_human_profile_returns_local_only_profile`

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_loop_workspace/test_human_model.py tests/test_gateway/test_rpc_loop_workspace_human_model.py -x`
Expected: FAIL on missing human profile fields/methods.

**Step 3: Write minimal implementation**

- 在 workspace state 增加最小 `human_profile` 结构，默认 local-first / inspectable / no cloud sync。
- 在 service 提供读取/更新方法；在 gateway RPC 暴露只读/轻量写入方法。

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_loop_workspace/test_human_model.py tests/test_gateway/test_rpc_loop_workspace_human_model.py -x`
Expected: PASS

**Run log**

```text
Run log: F9.1 completed at <datetime>; human model tests passed; risk note: kept profile local-first and avoided team sync semantics.
```

---

## Feature F10: v1.1 Release and Acceptance Evidence

Stop condition: v1.1 有 release notes、acceptance checklist 和高层 launch criteria 证据。

### Task F10.1: Add v1.1 release and acceptance artifacts

**Files:**
- Create: `docs/releases/loopdesk-v1.1.md:1`
- Create: `docs/acceptance/loopdesk-v1.1-acceptance-checklist.md:1`
- Edit: `docs/README.md:1`
- Edit: `README.md:1`

**Step 1: Write the failing test**

- `test_v11_release_notes_exist_and_mention_runtime_matrix_and_desktop_boundary`
- `test_v11_acceptance_checklist_references_focused_test_commands`

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_release_acceptance.py -x`
Expected: FAIL on missing v1.1 release/acceptance artifacts.

**Step 3: Write minimal implementation**

- 增加 `docs/releases/loopdesk-v1.1.md`，总结 F1–F10 的交付边界。
- 增加 `docs/acceptance/loopdesk-v1.1-acceptance-checklist.md`，列出 focused test commands 与 launch criteria。
- 更新 `docs/README.md` 与 `README.md`，加入 v1.1 文档入口。

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_release_acceptance.py -x`
Expected: PASS

**Run log**

```text
Run log: F10.1 completed at <datetime>; release/acceptance tests passed; risk note: kept v1.1 narrative aligned with v0.1/v0.2 boundaries.
```

---

## 21. Final v1.1 Launch Gate

- Focused gate for F7–F10 passes.
- No public docs or Web UI narrative leaks team-room, cloud-sync, or IM-first product story.
- Local-first authority remains with workspace + gateway + desktop runtime boundary.
