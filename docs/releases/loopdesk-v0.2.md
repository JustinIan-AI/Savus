# LoopDesk v0.2 — Channel Adapter Release Notes

> Status: candidate
> Version: v0.2
> Date: 2026-07-14
> Owner: Product / Engineering / QA
> Boundary: local-first personal loop workspace; IM is an optional control/notification surface only.

## 1. Summary

LoopDesk v0.2 adds optional IM channel adapters for DingTalk, Feishu/Lark, Slack, and WeCom on top of the existing local loop workspace.

The local workspace remains the only durable source of truth. IM becomes a remote control and notification surface for loop status, approvals, cost alerts, and compact run summaries. LoopDesk 不做 IM-first 叙事。

## 2. Highlights

- Shared channel adapter foundation with disabled-by-default behavior.
- Four approved platform adapters:
  - Slack Socket Mode
  - Feishu/Lark WebSocket/long-connection
  - DingTalk Stream Mode
  - WeCom webhook with explicit public-URL review gate
- Normalized read commands: `/help`, `/status`, `/current`, `/list`, `/history`, `/memory`, `/skills`, `/model`, `/abort`.
- Normalized write commands: `/new`, `/approve`, `/reject`, `/cancel`.
- Local safety controls enforced for every channel action: allowlist, kill switch, denylist, budget checks, audit logging.
- Local Web UI and docs surface keep LoopDesk workspace-first; IM is not positioned as the primary product.

## 3. Boundary Reminders

- v0.2 does not add team rooms, multi-user workspaces, or cloud sync as the default path.
- Personal WeChat, QQ, Telegram, Discord, Matrix, and other IM platforms are out of scope for v0.2.
- Rich media pipelines, voice replies, and complex card interactions are not the primary v0.2 flows.
- Channel adapters can be disabled independently without deleting `LOOP-STATE.json`, memory, skills, artifacts, or worktrees.

## 4. Upgrade Notes

- Existing LoopDesk installations keep their current local-first behavior.
- Channel adapters remain disabled after upgrade until the operator explicitly enables them.
- Rollback is supported per platform by setting `enabled = false` and restarting the gateway.

## 5. Verification

See `docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md` for QA commands and sign-off criteria.

## 6. Local Inspection

- The local loop workspace view now exposes a compact channel inspection panel with configured adapter status, transport state, restart attempts, and a disable action.
- This panel keeps LoopDesk workspace-first; for richer setup and channel onboarding, use guided setup or the CLI `channels` commands.

## 7. Next Steps

- Finalize operator channel docs.
- Complete platform QA with real bot/app credentials.
- Lock v0.2 public surface to workspace-first narrative only.
