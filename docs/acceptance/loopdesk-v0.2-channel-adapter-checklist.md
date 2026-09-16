# LoopDesk v0.2 — Channel Adapter Acceptance Checklist

> Status: in progress
> Version: v0.2
> Date: 2026-07-14
> Owner: Product / Engineering / QA
> Sources: `docs/decisions/v0.2-channel-adapter.md`, `docs/plans/2026-07-13-v02-channel-adapter-implementation-plan.md`, `docs/features/loopdesk-v0.2-channel-adapter-feature-breakdown.md`

## How to Use This Checklist

- Mark each item as `Pass`, `Fail`, `N/A`, or `Blocked`.
- Add evidence links or test commands under each section.
- Do not treat partial progress as acceptance; each `Must` item should be independently verifiable.

## 1. Product Boundary

### 1.1 Local-First Workspace
- [ ] Local loop workspace remains the primary LoopDesk product surface.
- [ ] IM channels are documented as optional control/notification surfaces only.
- [ ] No channel adapter exposes unrestricted shell, legacy chat-first narrative, or team-room semantics as a v0.2 public feature.

Evidence:
- Docs: `docs/decisions/v0.2-channel-adapter.md`
- Docs: `docs/decisions/product-strategy.md`
- Command: `grep -R "IM-first\|team room\|personal WeChat" docs src || true`
- Result: expected zero public-surface leaks

### 1.2 Naming and Data Ownership
- [ ] Public docs, CLI, and Web UI continue to lead with `LoopDesk` / `loop_workspace` / `LOOP-STATE.json`.
- [ ] Channel adapters do not introduce a separate durable source of truth.

Evidence:
- Docs: `docs/releases/loopdesk-v0.2.md`
- Tests: `tests/test_gateway/test_channel_adapter_core.py`
- Command: `python -m pytest tests/test_gateway/test_channel_adapter_core.py -q`

## 2. Shared Channel Foundation

### 2.1 Config and Lifecycle
- [ ] Gateway loads disabled-by-default channel configs without changing local workspace behavior.
- [ ] Unknown inbound channel commands are rejected before workspace action execution.
- [ ] Allowlist, kill-switch, denylist, and budget checks block write commands consistently.
- [ ] Channel actions emit audit records with redacted secrets.

Evidence:
- Tests: `tests/test_gateway/test_channel_adapter_core.py`
- Command: `python -m pytest tests/test_gateway/test_channel_adapter_core.py -q`

### 2.2 Notifications
- [ ] Long summaries are truncated into compact notifications.
- [ ] Unsupported platform formatting falls back to plain text.
- [ ] Large artifact payloads and raw JSON dumps are not sent in v0.2 notifications.

Evidence:
- Tests: `tests/test_gateway/test_channel_notifications.py`
- Command: `python -m pytest tests/test_gateway/test_channel_notifications.py -q`

## 3. Platform Adapters

### 3.1 Feishu/Lark
- [ ] `/help`, `/status`, `/current`, `/list`, `/history`, `/memory`, `/skills`, `/model`, `/abort` work from Feishu/Lark.
- [ ] `/new`, `/approve`, `/reject`, `/cancel` work from Feishu/Lark.
- [ ] Approval request and reply flow is recorded in local run log and approval history.
- [ ] Disabling Feishu/Lark does not affect local workspace behavior.

Evidence:
- Tests: `tests/test_gateway/test_channel_feishu.py`
- Command: `python -m pytest tests/test_gateway/test_channel_feishu.py -q`

### 3.2 Slack
- [ ] `/help`, `/status`, `/current`, `/list`, `/history`, `/memory`, `/skills`, `/model`, `/abort` work from Slack Socket Mode.
- [ ] `/new`, `/approve`, `/reject`, `/cancel` work from Slack.
- [ ] Approval request and reply flow is recorded in local run log and approval history.
- [ ] Disabling Slack does not affect local workspace behavior.

Evidence:
- Tests: `tests/test_gateway/test_channel_slack.py`
- Command: `python -m pytest tests/test_gateway/test_channel_slack.py -q`

### 3.3 DingTalk
- [ ] `/help`, `/status`, `/current`, `/list`, `/history`, `/memory`, `/skills`, `/model`, `/abort` work from DingTalk.
- [ ] `/approve` and `/reject` work from DingTalk.
- [ ] Unsupported rich formatting degrades to plain text without crashing the adapter.

Evidence:
- Tests: `tests/test_gateway/test_channel_dingtalk.py`
- Command: `python -m pytest tests/test_gateway/test_channel_dingtalk.py -q`

### 3.4 WeCom
- [ ] `/help`, `/status`, `/current`, `/list`, `/approve`, `/reject` work from WeCom.
- [ ] Public webhook mode requires explicit review flag and documented tunnel/config decision.
- [ ] Channel failures do not corrupt local loop workspace state.

Evidence:
- Tests: `tests/test_gateway/test_channel_wecom.py`
- Command: `python -m pytest tests/test_gateway/test_channel_wecom.py -q`

## 4. Hardening and Operations

### 4.1 Safety Controls
- [ ] Repeated bad commands are throttled and logged per channel and sender.
- [ ] Budget-cap exceeded events produce compact cost alerts in enabled channels.
- [ ] `/cancel` returns immediate status and never blocks the IM session.
- [ ] Disabling any adapter does not delete or alter `LOOP-STATE.json`, memory, skills, artifacts, or worktrees.

Evidence:
- Tests: `tests/test_gateway/test_channel_adapter_hardening.py`
- Command: `python -m pytest tests/test_gateway/test_channel_adapter_hardening.py -q`

### 4.2 Local Inspection
- [ ] Local Web UI exposes compact channel status inside the loop workspace view.
- [ ] Each configured channel row shows transport state, restart attempts, and last error or attention hint.
- [ ] Operator can disable a configured channel directly from the local inspection surface.
- [ ] Local Web UI stays workspace-first and does not promote IM as the primary product narrative.
- [ ] Disabling a channel from local UI or config preserves workspace state.

Evidence:
- Tests: `tests/test_gateway/test_rpc_loop_workspace_channels.py`
- Tests: `tests/test_gateway/test_loop_workspace_channels_static.py`
- Command: `python -m pytest tests/test_gateway/test_rpc_loop_workspace_channels.py tests/test_gateway/test_loop_workspace_channels_static.py -q`

## 5. Release Gate

### 5.1 Focused Test Gate
- [ ] Planned focused gateway test sequence passes with `python -m pytest ...` below.
- [ ] Local loop workspace behavior remains green with all v0.2 channels disabled.
- [ ] No public docs or Web UI leak legacy channels-first or team-collaboration-first narratives.
- [ ] Disable rollback evidence is recorded for every approved platform adapter.

Evidence:
- Command: `python -m pytest tests/test_gateway/test_channel_adapter_core.py tests/test_gateway/test_channel_notifications.py tests/test_gateway/test_channel_feishu.py tests/test_gateway/test_channel_slack.py tests/test_gateway/test_channel_dingtalk.py tests/test_gateway/test_channel_wecom.py tests/test_gateway/test_channel_adapter_hardening.py tests/test_gateway/test_rpc_loop_workspace_channels.py tests/test_gateway/test_loop_workspace_channels_static.py -q`
- Disable rollback evidence: record `channels status --json` before disable, then `enabled=false` in config, then rerun the focused gateway test gate.

### 5.2 Sign-Off
- [ ] Product approves v0.2 channel adapter scope and boundary lock.
- [ ] Engineering approves focused test gate and rollback procedure.
- [ ] QA approves platform adapter checklist and local workspace regression check.
- [ ] QA approves platform adapter checklist, local channel inspection surface, and local workspace regression check.

Approved by Product:
Approved by Engineering:
Approved by QA:
