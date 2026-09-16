# 可借鉴功能清单 — Proma (`proma-ai/proma`) 对 LoopDesk 的参考

> 日期：2026-07-16
> 来源：`docs/research/competitive-intel-proma.md`、`docs/research/competitive-intel.md`、`docs/research/competitive-intel-octos.md`、`docs/research/octos-overview.md`、`docs/prd/personal-loop-workspace-v1.0.zh.md`、`docs/prd/personal-loop-workspace.en.md`
> 原则：只借鉴产品思路，不照搬桌面 Chat/Agent shell 叙事；所有借鉴都必须回连 LoopDesk 的 durable loop state、adapter-first、loop engineering 与 local-first 边界。

## 1. 借鉴原则

- Proma 最有价值的是 **workspace-scoped Skills/MCP 组织方式** 和 **remote bot 轻量继续思路**。
- LoopDesk 不应复制成“内部 Chat + 内部 Agent 桌面客户端”。
- 所有借鉴功能都应强化 `LOOP-STATE.json`、memory、skills、artifacts、run log、approval、budget、worktree isolation 的 authority。
- 每个借鉴项都要回答：它如何让跨工具 continuity 更好，而不是只让单个 desktop client 更完整。

## 2. Proma 可借鉴功能清单

### 2.1 Workspace-Scoped Skills/MCP Configuration
- **借鉴点**：每个 workspace 独立配置 Skills 和 MCP Server。
- **LoopDesk 落地**：
  - 每个 loop workspace 支持独立 Skills/MCP 配置；
  - 不同 workspace 可启用不同 adapters、providers、skills、denylist；
  - Workspace-level MCP config 成为默认组织方式，而不是全局一刀切；
  - MCP config 与 `LOOP-STATE.json` 绑定，可导出、可复现、可审计。

### 2.2 MCP Lifecycle per Workspace
- **借鉴点**：MCP Server 可按需启用/关闭。
- **LoopDesk 落地**：
  - 支持 per-workspace MCP server 启用、禁用、重试、恢复；
  - MCP tool call 可追溯：workspace、Goal、run、approval、budget；
  - MCP 失败只影响当前 workspace/run，不直接 corrupt 本地 state；
  - 支持 stdio / HTTP MCP server，保留现有 gateway 安全边界。

### 2.3 Skills 作为 Reusable Judgment
- **借鉴点**：Skills 可沉淀成项目内可复用能力。
- **LoopDesk 落地**：
  - Skills 绑定 loop context、memory、artifacts、approval policy；
  - 支持 inspect、replay、audit、version；
  - 支持 workspace 内启用/禁用；
  - 支持 skill auto-triggering，但触发结果仍要回写 loop state。

### 2.4 Chat/Agent 分层思路
- **借鉴点**：简单问题和复杂任务分层处理。
- **LoopDesk 落地**：
  - 不复制 Chat/Agent shell；
  - 改为 loop 分层：read-only inspection / bounded continuation / approval-driven execution / risky automation；
  - 简单查询可在 lightweight surface 完成；
  - 复杂 bounded execution 回到 local runtime。

### 2.5 Remote Bot 作为 Lightweight Controller
- **借鉴点**：飞书/Lark、钉钉、微信桥接用于远程触发或继续工作。
- **LoopDesk 落地**：
  - IM/bot 只暴露 compact command/status/approval；
  - transport 留在 adapter 内部；
  - 新增 platform 先评估 bounded approval/continuation fit；
  - 优先 approved platforms，不追求 rich media/interaction breadth。

### 2.6 Local-First Inspectable Data
- **借鉴点**：JSON/JSONL 本地文件存储，便于备份、迁移、排查。
- **LoopDesk 落地**：
  - `LOOP-STATE.json`、memory、artifacts、replay packs 保持 human-readable / diff-friendly；
  - 支持 partial export：一个 Goal、一个 workspace、一个 time range；
  - 支持 backup/migration without cloud sync；
  - 保留 local debugging 和 recovery affordances。

### 2.7 Desktop Runtime + Remote Companion
- **借鉴点**：桌面为主，移动/聊天端为辅。
- **LoopDesk 落地**：
  - Desktop 永远是 authority；
  - Web/IM 是 continuation/control surface；
  - 不在 remote surface 上重建完整 runtime fidelity；
  - 若未来提供 companion experience，优先展示 status、approvals、next safe actions。

## 3. 优先级建议

| 优先级 | 借鉴项 | 理由 |
| --- | --- | --- |
| P0 | Workspace-scoped Skills/MCP | 直接增强 personal loop 的可组合性，且与现有 v0.1/v0.2 边界兼容 |
| P0 | MCP lifecycle per workspace | 让 MCP 从“可用”变成“可管理、可审计、可回写 loop state” |
| P1 | Remote bot bounded control | 与 v0.2 channel adapter 方向一致，可继续收紧为 lightweight controller |
| P1 | Skills bound to loop context | 避免 Skills 退化成 isolated desktop prompts |
| P2 | Chat/Agent layering insight | 影响 UI/UX 分层，但不急于改产品形态 |
| P2 | Local inspectable data | 已经是 LoopDesk 方向，继续强化 diff/export/backup 体验 |
| P3 | Companion-style remote surface | 未来考虑，前提是 desktop-first 和 state authority 不变 |

## 4. 不建议借鉴

- 不要把 LoopDesk 做成 Proma 式的桌面 Chat/Agent shell；
- 不要优先建设“内部聊天 + 内部 Agent”体验；
- 不要把 remote bot 做成 rich media / team messaging surface；
- 不要为了 remote UX 而削弱本地 gateway authority 或 `LOOP-STATE.json` 的 durable source of truth 地位。

## 5. 后续验证

- 在 v1.0 feature breakdown 中确认 workspace-scoped MCP 的配置 schema、auth、adapter mapping；
- 在 channel adapter 设计中确认 remote bot 的 command allowlist、rate limit、audit log、disable rollback；
- 在 acceptance criteria 中确认 Skills/MCP 的 inspectability、replay、export、cross-tool continuity 证据。
