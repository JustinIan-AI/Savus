# LoopDesk v0.2 — Channel Adapter Implementation Plan

> Date: 2026-07-14
> Status: in progress
> Owner: Product / Engineering / QA
> Strategy reference: `docs/decisions/v0.2-channel-adapter.md`
> Product boundary: local-first personal loop workspace; IM is an optional control/notification surface only.

## 1. Goal

- Turn the v0.2 channel adapter draft into an executable build sequence.
- Deliver lightweight DingTalk, Feishu/Lark, Slack, and WeCom adapters without turning LoopDesk into an IM-first product.
- Keep `LOOP-STATE.json`, memory, skills, artifacts, approvals, and worktree isolation as the durable source of truth.
- Preserve LoopDesk naming: `LoopDesk` / `loop_workspace` / `LOOP-STATE.json`.

## 2. Current Baseline

### 2.1 Completed
- v0.1 local loop workspace, gateway RPC, approvals, cost observatory, and minimal local Web UI are implemented.
- Existing docs define v0.1 as workspace-first, MCP-first, and IM-deferred.
- Competitive research shows `cc-connect` already owns multi-platform IM bridge breadth; LoopDesk should win on portable loop state and local safety.
- Shared channel adapters, command registry, gateway RPC status surface, and loop workspace view scaffolding already exist in the codebase; v0.2 work should align with and extend them.
- v0.2 feature docs, release notes, and acceptance checklist are drafted.

### 2.2 Not Started
- Missing focused gateway tests for channel core, notifications, platform adapters, hardening, and local inspection.
- Channel docs, release notes, and boundary-lock documentation are not finalized for v0.2 sign-off.

## 3. Assumptions

- v0.2 work starts after v0.1 workspace surface, MCP adapter, memory, approvals, and loop engine are stable.
- Slack Socket Mode and Feishu WebSocket/long-connection are preferred first transports.
- WeCom public webhook is allowed only with explicit tunnel/review gate.
- Personal WeChat is excluded from v0.2.
- Each channel adapter can be disabled independently without deleting `LOOP-STATE.json`, memory, skills, artifacts, or worktrees.

## 4. Risks

| ID | Risk | Impact | Mitigation |
| --- | --- | --- | --- |
| R1 | IM breadth expands beyond v0.2 scope | high | Limit to DingTalk, Feishu/Lark, Slack, WeCom; defer others. |
| R2 | Channel adapter becomes IM-first UX | high | All commands must map to existing safe workspace actions. |
| R3 | Secret/config sprawl | medium | Centralize config in gateway config model; never expose raw secrets in logs or UI. |
| R4 | Platform API/account policy changes | medium | Disable-per-platform rollback; keep adapters thin. |
| R5 | Local safety controls weakened | high | Enforce kill switch, denylist, budget cap, approval, and allowlist checks on every write command. |
| R6 | Gateway pytest collection/stability blocks verification | medium | Use targeted test files and direct scripted validation paths until collection is restored. |

## 5. Dependencies

- v0.1 local loop workspace, gateway RPC, approval flow, run log, cost observatory, and local Web UI are stable.
- A shared channel config model exists or is added before platform adapters.
- Platform developer accounts, bot/app credentials, and test channels are available for Slack, Feishu/Lark, DingTalk, and WeCom before QA sign-off.

## 6. Feature Plan

| ID | Feature | Target Phase | Stop Condition |
| --- | --- | --- | --- |
| F1 | Shared Channel Foundation | Phase 0 | Disabled-by-default config, command parser, allowlist, audit logging, and unknown-command rejection are implemented and tested. |
| F2 | Approved Platform Adapters | Phase 1 + Phase 2 | Slack and Feishu/Lark deliver read commands and approval notifications; DingTalk and WeCom deliver minimal read/write command coverage with explicit WeCom review gate. |
| F3 | Hardening and Operator Controls | Phase 2 + Phase 3 | Cost alerts, rate limiting, retry/backoff, compact error templates, and immediate `/cancel` response are implemented and tested. |
| F4 | Local Inspection and Documentation | Phase 3 | Local status inspection, docs, release notes, acceptance checklist, and boundary-lock evidence are complete. |

### 6.1 Loop Engineering Run Format

For each feature/task:
- Triage: choose the smallest failing-test-first task that moves the feature forward.
- Maker: implement one task and keep changes minimal.
- Checker: run the focused test command listed with the task.
- Escalation: stop and update docs/plans if scope creep, legacy public-surface leak, or safety boundary risk appears.
- Run log: record started task, result, next step, and risk note in plan or loop workspace evidence.
- Stop condition: acceptance criteria are met and no unresolved public-surface leak remains.

## 7. Implementation Plan

### Phase 0: Shared Channel Foundation

#### Task 0.1: Add channel adapter contract and config model
**Files:**
- New: `docs/features/loopdesk-v0.2-channel-adapter-feature-breakdown.md`
- Edit: `docs/decisions/v0.2-channel-adapter.md`
- Test: `tests/test_gateway/test_channel_adapter_core.py`

**Steps:**
1. Finalize v0.2 feature breakdown and decision doc language.
2. Write failing tests for channel RPC context, disabled-by-default behavior, unknown command rejection, and allowlist/budget enforcement.
3. Make the smallest gateway/config/audit changes needed to satisfy those tests.

**Acceptance criteria:**
- Gateway can load a disabled-by-default channel config without changing local loop workspace behavior.
- An unknown inbound command is rejected before it reaches workspace actions.
- A write command blocked by allowlist or budget cap is logged and rejected consistently.

**Validation:**
```bash
python -m pytest tests/test_gateway/test_channel_adapter_core.py -q
```

> Note: if `tests/test_gateway` collection is unstable in this environment, validate with a direct runner script or by importing the test module in a focused Python process.

#### Task 0.2: Add shared notification and formatting helpers
**Files:**
- Test: `tests/test_gateway/test_channel_notifications.py`

**Steps:**
1. Add failing tests for outbound notification formatting, truncation, size limits, and plain-text fallback.
2. Implement the smallest shared notification/formatting layer needed to satisfy those tests.

**Acceptance criteria:**
- A long run-log summary is truncated into a compact notification.
- A platform-specific card formatter falls back to plain text when unsupported.
- Large artifact payloads and raw JSON dumps are not sent in v0.2 notifications.

**Validation:**
```bash
python -m pytest tests/test_gateway/test_channel_notifications.py -q
```

---

### Phase 1: Slack + Feishu/Lark

#### Task 1.1: Add Feishu/Lark adapter
**Files:**
- Test: `tests/test_gateway/test_channel_feishu.py`

**Steps:**
1. Write failing tests for Feishu/Lark config validation, command parsing, read commands, approval flow, and notification formatting.
2. Implement or verify the Feishu/Lark adapter behavior against those tests.
3. Keep webhook mode optional and document websocket as the preferred default.

**Acceptance criteria:**
- A developer can use `/current`, `/approve`, and `/reject` from Feishu/Lark without opening local Web UI.
- Channel actions are recorded in local run log and approval history.
- Disabling Feishu/Lark does not affect local Web UI, CLI, or other platforms.

**Validation:**
```bash
python -m pytest tests/test_gateway/test_channel_feishu.py -q
```

#### Task 1.2: Add Slack Socket Mode adapter
**Files:**
- Test: `tests/test_gateway/test_channel_slack.py`

**Steps:**
1. Write failing tests for Slack Socket Mode config, inbound commands, approval request/reply, and thread-aware reply formatting.
2. Implement or verify Slack adapter behavior against those tests.
3. Keep Socket Mode as the preferred transport and avoid heavy interactive card flows.

**Acceptance criteria:**
- A developer can use `/current`, `/new`, `/approve`, and `/reject` from Slack without opening local Web UI.
- Channel actions are recorded in local run log and approval history.
- Disabling Slack does not affect local Web UI, CLI, or other platforms.

**Validation:**
```bash
python -m pytest tests/test_gateway/test_channel_slack.py -q
```

#### Task 1.3: Add channel gateway plumbing and local Web UI status
**Files:**
- Edit: `src/loopdesk/gateway/rpc_loop_workspace.py`
- Edit: `src/loopdesk/gateway/scopes.py`
- Edit: `src/loopdesk/gateway/static/js/views/loop_workspace.js`
- Test: `tests/test_gateway/test_rpc_loop_workspace_channels.py`
- Test: `tests/test_gateway/test_loop_workspace_channels_static.py`

**Steps:**
1. Add minimal channel status/config RPC surface for local inspection.
2. Add local Web UI channel status view showing enabled platforms, transport state, last error, and disable action.
3. Ensure channel docs/docs links stay minimal/internal and do not become a v0.2 public marketing surface.

**Acceptance criteria:**
- Local Web UI shows channel status without exposing channel config as the primary product narrative.
- Disabling a channel from local UI or config does not delete workspace state.

**Validation:**
```bash
python -m pytest tests/test_gateway/test_rpc_loop_workspace_channels.py tests/test_gateway/test_loop_workspace_channels_static.py -q
```

---

### Phase 2: DingTalk + WeCom

#### Task 2.1: Add DingTalk adapter
**Files:**
- New: `src/loopdesk/gateway/channels/dingtalk.py`
- Test: `tests/test_gateway/test_channel_dingtalk.py`

**Steps:**
1. Write failing tests for DingTalk long-connection/stream-like transport, reconnect handling, inbound commands, and outbound text/markdown fallback.
2. Implement the adapter behavior against those tests.
3. Avoid complex card flows in v0.2; keep approval reply simple.

**Acceptance criteria:**
- A developer can approve or reject a pending approval from DingTalk.
- Unsupported rich formatting degrades to plain text without crashing the adapter.

**Validation:**
```bash
python -m pytest tests/test_gateway/test_channel_dingtalk.py -q
```

#### Task 2.2: Add WeCom adapter with public-URL review gate
**Files:**
- New: `src/loopdesk/gateway/channels/wecom.py`
- Test: `tests/test_gateway/test_channel_wecom.py`

**Steps:**
1. Write failing tests for WeCom config review gate, webhook callback handling, minimal inbound commands, and compact outbound alerts.
2. Implement the adapter behavior against those tests.
3. Require explicit review flag before public-callback/webhook mode is usable.

**Acceptance criteria:**
- WeCom cannot be enabled without explicit public-URL review flag and documented tunnel/config decision.
- Channel failures do not corrupt local loop workspace state.

**Validation:**
```bash
python -m pytest tests/test_gateway/test_channel_wecom.py -q
```

#### Task 2.3: Harden channel safety and operational behavior
**Files:**
- Test: `tests/test_gateway/test_channel_adapter_hardening.py`

**Steps:**
1. Add per-sender and per-channel rate limiting and retry/backoff rules.
2. Add cost alert notifications when budget thresholds are crossed.
3. Add error escalation templates that stay compact per platform.
4. Ensure `/cancel` and high-risk commands return immediate status, never block the IM session.

**Acceptance criteria:**
- Repeated bad commands are throttled and logged.
- Budget-cap exceeded event produces a compact cost alert in enabled channels.
- A long-running local loop can still be cancelled from IM without hanging the platform session.

**Validation:**
```bash
python -m pytest tests/test_gateway/test_channel_adapter_hardening.py -q
```

---

### Phase 3: Documentation, Sign-off, and v0.2 Boundary Lock

#### Task 3.1: Update v0.2 docs and decision docs
**Files:**
- New: `docs/features/loopdesk-v0.2-channel-adapter-feature-breakdown.md`
- Edit: `docs/decisions/product-strategy.md`
- Edit: `docs/prd/personal-loop-workspace.md`
- Edit: `docs/releases/loopdesk-v0.2.md`
- Edit: `docs/README.md`

**Steps:**
1. Add minimal internal/operator-facing channel docs for Slack, Feishu/Lark, DingTalk, and WeCom.
2. Update product strategy and PRD to list IM as an optional v0.2 surface only.
3. Add release notes emphasizing local-first loop workspace and optional channel control surface.
4. Link the new plan and channel docs from `docs/README.md`.

**Acceptance criteria:**
- v0.2 docs do not position IM as the primary loop surface.
- Operator docs include enable/disable, rollback, and platform-limit notes.

**Validation:**
```bash
python -m pytest docs/ -q || true
```

#### Task 3.2: Acceptance and release gate
**Files:**
- New: `docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md`

**Steps:**
1. Define QA checklist for each platform: enable, read commands, write commands, notification delivery, disable rollback.
2. Require one focused test run per platform adapter plus channel-core hardening tests.
3. Require evidence that local loop workspace behavior is unchanged when all channels are disabled.

**Acceptance criteria:**
- All four adapters pass their focused test files.
- Channel adapters are disabled by default and can be removed without data loss.
- v0.2 sign-off explicitly limits IM scope to the four approved platforms.

**Validation:**
```bash
python -m pytest tests/test_gateway/test_channel_adapter_core.py tests/test_gateway/test_channel_notifications.py tests/test_gateway/test_channel_feishu.py tests/test_gateway/test_channel_slack.py tests/test_gateway/test_channel_dingtalk.py tests/test_gateway/test_channel_wecom.py tests/test_gateway/test_channel_adapter_hardening.py tests/test_gateway/test_rpc_loop_workspace_channels.py tests/test_gateway/test_loop_workspace_channels_static.py -q
```

## 8. Rollback Procedure

- Disable the affected platform in channel config and restart the gateway.
- Verify local CLI, local Web UI, MCP adapter, memory, approvals, and loop engine behavior remain green.
- If platform API or account-risk issues arise, disable the adapter first; remove config only after local workspace behavior is stable.
- Do not delete `LOOP-STATE.json`, memory, skills, artifacts, or worktrees during rollback.

## 9. Completion Criteria

This plan is complete when:
- Shared channel core, notification formatter, and four adapters are implemented.
- Slack and Feishu/Lark deliver read commands and approval notifications.
- DingTalk and WeCom deliver minimal command/notification coverage with explicit WeCom public-URL review gating.
- Local safety controls remain enforced for every channel action.
- v0.2 docs and acceptance checklist clearly state that IM is optional and local-first loop workspace remains the primary product promise.
- Focused gateway tests for channel adapters pass in the planned sequence.
