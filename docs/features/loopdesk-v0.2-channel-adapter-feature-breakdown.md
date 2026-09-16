# LoopDesk v0.2 — Channel Adapter Feature Breakdown

> Status: in progress
> Version: v0.2
> Date: 2026-07-14
> Owner: Product / Engineering / QA
> Inputs: `docs/decisions/v0.2-channel-adapter.md`, `docs/plans/2026-07-13-v02-channel-adapter-implementation-plan.md`, `docs/decisions/product-strategy.md`, `docs/prd/personal-loop-workspace.md`

## 1. Breakdown Principle

- IM adapters are **optional control and notification surfaces**, not the primary LoopDesk product surface.
- `LOOP-STATE.json`, memory, skills, artifacts, approvals, and worktree isolation remain the **only durable source of truth**.
- Frontend and channel surfaces should stay **workspace-first**: developers inspect or approve work; they do not run the loop inside IM.
- All inbound channel commands must map to **existing safe workspace actions**; no unrestricted shell or team-room semantics are introduced in v0.2.

## 2. Feature Summary

| ID | Feature | Priority | Boundary Note |
| --- | --- | --- | --- |
| F1 | Shared Channel Foundation | Must | config, command parser, disabled-by-default behavior, admin allowlist, audit log |
| F2 | Approved Platform Adapters | Must | Slack Socket Mode, Feishu/Lark WebSocket, DingTalk Stream, WeCom webhook review gate |
| F3 | Hardening and Operator Controls | Must | rate limiting, cost alerts, compact error templates, disable without data loss |
| F4 | Local Inspection and Documentation | Must | channel status view, release notes, acceptance checklist, boundary-locked docs |

## 3. Feature Details

### F1：Shared Channel Foundation

**目标**：在 gateway 内建立最小 channel adapter 公共底座，使 IM 事件可被安全地标准化为 workspace 命令和通知，且默认关闭。

**范围**
- in：gateway config schema、disabled-by-default 生命周期、command parser、admin sender allowlist、channel -> workspace RPC 映射、run-log/approval audit、redaction
- out：team rooms、public cloud room service、personal WeChat、rich media pipeline、IM-first 叙事

**验收条件**
- 未启用 channel 时，本地 CLI、Web UI、MCP adapter、memory、approvals、loop engine 行为不变
- 未知 channel 命令在到达 workspace 前被拒绝并记录
- allowlist/kill-switch/denylist/budget 阻止写命令时返回一致状态并记录
- channel 事件可追溯到 sender、channel、command、结果

**边界说明**
- 这是 gateway-owned 基础层，不是独立产品模块。
- `channels.status`、`channels.logout`、`channels.restart` 提供最小控制面；write commands 只走已有 workspace RPC。

---

### F2：Approved Platform Adapters

**目标**：交付四个 v0.2 批准平台的 minimal transport + inbound/outbound bridge，并在失败时优雅降级。

**范围**
- in：Feishu/Lark WebSocket、Slack Socket Mode、DingTalk Stream、WeCom webhook + review gate、read commands、write commands、approval notifications、status notifications、plain-text / limited markdown fallback
- out：QQ、Telegram、Discord、Matrix、MSTeams、personal WeChat、复杂卡片交互、artifact 主路径回传

**验收条件**
- 支持 `/help`、`/status`、`/current`、`/list`、`/history`、`/memory`、`/skills`、`/model`、`/abort`
- 支持 `/new`、`/approve`、`/reject`、`/cancel`
- Slack/Feishu 优先使用长连接；WeCom public callback 需显式 review gate
- 不支持的富文本能力降级为纯文本，不 crash adapter
- 所有平台共享同一份命令表，避免 IM 口径分裂

**边界说明**
- platform transport 细节留在 adapter 内部；对外只暴露 compact reply / notification。
- `/model` 只做展示或受控切换；`/dir` 与更激进命令 defer 到 v0.3。

---

### F3：Hardening and Operator Controls

**目标**：保证 channel 表面不会拖垮本地 workspace，也不会成为滥用入口。

**范围**
- in：per-channel / per-sender rate limiting、retry/backoff、cost alert notification、error escalation template、immediate `/cancel` response、disable without data loss
- out：team approval queue、marketplace skill 发现、多 workspace 管理、cloud sync 作为默认路径

**验收条件**
- 重复错误命令被 throttle 并记录
- budget-cap exceeded 事件在 enabled channel 中生成 compact cost alert
- `/cancel` 立即返回状态，不阻塞 IM session
- 禁用任一 adapter 不删除或修改 `LOOP-STATE.json`、memory、skills、artifacts、worktrees

**边界说明**
- hardening 是 shared gateway concern，不把失败转嫁给前端。
- channel failure 只影响对应 IM bridge；local workspace 保持可读写。

---

### F4：Local Inspection and Documentation

**目标**：让 operator 可在本地 Web UI 或 docs 中检查 channel 状态、启用/禁用影响和 v0.2 边界。

**范围**
- in：local Web UI channel status view、operator docs、v0.2 release notes、acceptance checklist、README/docs links
- out：public channel marketing page、multi-user onboarding flow、team dashboard

**验收条件**
- local Web UI 显示 enabled platform、transport state、last error、disable action
- docs 明确说明 IM 是 optional bridge，不是 primary loop surface
- acceptance checklist 覆盖 enable、read command、write command、notification、disable rollback
- focused gateway tests 覆盖 planned sequence 且可重复运行

**边界说明**
- docs 面向 operator，不是 end-user 增长页。
- 任何 channel 文档都要显式写出 rollback 步骤和 platform limit。

## 4. Execution Boundary Reminder

- `LoopDesk` = local-first personal loop workspace
- `loop_workspace` / `LOOP-STATE.json` = durable source of truth
- `channel adapter` = optional remote control/notification surface
- Frontend = observability and approval surface
- v0.2 excludes: team rooms, personal WeChat, cloud-first sync, heavy media skill matrix
