# 可借鉴功能清单 — Octos (`octos-org/octos`) 对 LoopDesk 的参考

> 日期：2026-07-28
> 来源：`docs/research/competitive-intel-octos.md`、`docs/research/octos-overview.md`、`docs/research/competitive-intel.md`、`docs/product-positioning.md`、`docs/prd/personal-loop-workspace-v1.0.zh.md`、`docs/prd/personal-loop-workspace.en.md`
> 原则：只借鉴产品/工程思路，不复制多租户控制面、cloud-first 叙事、重 shell 或 channel-first 执行模型；所有借鉴都必须回连 LoopDesk 的 durable loop state、adapter-first、loop engineering 与 local-first 边界。

## 1. 借鉴原则

- Octos 最有价值的是 **统一本地 runtime + autonomy primitives + MCP/ACP/channels 多 surface 组织方式**。
- LoopDesk 不应复制成“多租户 Agentic OS + Web dashboard + TUI + cloud tenant pair”。
- 所有借鉴功能都应强化 `LOOP-STATE.json`、memory、skills、artifacts、run log、approval、budget、worktree isolation 的 authority。
- 每个借鉴项都要回答：它如何让 **one developer 的外部工具 continuity** 更好，而不是只让单个 backend runtime 更完整。

## 2. Octos 可借鉴功能清单

### 2.1 Goal/Loop Autonomy Primitives
- **借鉴点**：`/goal`、`/loop`、checkpoint continuation、token budget、session rollback/resume。
- **LoopDesk 落地**：
  - 保留 LoopDesk 的 Loop/Goal/maker-checker 边界，不照搬 Octos 的 chat-first `/goal` 叙事；
  - 增加 Goal-level checkpoint、resume、rewind，作为本地 `LOOP-STATE.json` 的可恢复执行视图；
  - budget/token cap 与 stop condition 回写 run log；
  - interrupted sessions 可从 Desktop、Web、IM 发起 resume，但执行仍在本地 runtime。

### 2.2 Deterministic Session Replay / Time-Travel
- **借鉴点**：thread_id + committed_seq 绑定、session/rollback RPC、resume/rewind checkpoint picker。
- **LoopDesk 落地**：
  - 回放不依赖 chat history，而依赖 durable workspace event log；
  - 支持按 Goal / workspace / time range replay；
  - replay pack 保持 human-readable / diff-friendly；
  - Web/Desktop 可审查，IM 仅展示 compact replay 状态。

### 2.3 Multi-Agent Topology as Optional Extension
- **借鉴点**：sub-agent、peer agent、swarm dispatcher、validator gate、cost rollup。
- **LoopDesk 落地**：
  - v1.0 只保留 bounded review/verification 扩展，不引入通用 multi-agent OS；
  - 未来可做 multi-lens review：maker/checker 之外再加 reviewer agent，但仍受 approval + worktree isolation 约束；
  - 任何 fan-out 都要回写 unified run log、artifacts、cost；
  - 不引入 peer sovereign session 或 external swarm backend 作为默认路径。

### 2.4 MCP / ACP Unified Surface
- **借鉴点**：`octos mcp-serve`、外部 MCP client、Zed ACP stdio。
- **LoopDesk 落地**：
  - 继续 MCP-first adapter，并增强 tool call traceability：workspace、Goal、run、approval、budget；
  - ACP-second 只用于 session-rich tool，不替代 MCP；
  - MCP server 生命周期由 workspace 控制：enable/disable/retry/recover/audit；
  - 外部 orchestrator 可调用 LoopDesk，但 durable authority 仍是本地 `LOOP-STATE.json`。

### 2.5 Workspace-Scoped Skills / Plugin Registry
- **借鉴点**：per-profile skill layering、plugin SDK、registry、lifecycle。
- **LoopDesk 落地**：
  - Skills 按 workspace 组织，并绑定 loop context、memory、artifacts、approval policy；
  - 支持 inspect、replay、audit、version、enable/disable；
  - 支持 skill auto-triggering，但触发结果仍要回写 loop state；
  - 未来 registry 只作为 optional share/publish 层，不破坏 personal-first posture。

### 2.6 Channel Abstraction + Unified Commands
- **借鉴点**：14 channels、统一 `/new`/`/sessions`/`/back`、channel-safe message splitting。
- **LoopDesk 落地**：
  - 继续 v0.2 的 approved platforms 与 compact command surface；
  - IM/web/desktop 共享 canonical command model，不分裂口径；
  - channel 失败不得 corrupt `LOOP-STATE.json`、memory、skills、artifacts、worktrees；
  - 新增 platform 先评估 bounded approval/continuation fit，不追求 rich media。

### 2.7 Local-First Inspectable Runtime Data
- **借鉴点**：本地 JSONL/redb/config/auth 文件组织、diagnostics、config watcher。
- **LoopDesk 落地**：
  - `LOOP-STATE.json`、memory、artifacts、replay packs 保持 human-readable / diff-friendly；
  - 支持 partial export：Goal、workspace、time range；
  - 支持 local diagnostics、doctor-style health check、rollback；
  - 保留 local debugging 与 recovery affordances，不强制 cloud sync。

### 2.8 Sandbox / Tool Policy as Safety Baseline
- **借鉴点**：deny-wins policy、sandbox backends、blocked env vars、prompt injection tests。
- **LoopDesk 落地**：
  - 高风险 loop 默认进 worktree isolation + approval；
  - tool policy 支持 allow/deny + named groups + provider-specific rules；
  - env/path hardening 作为 shared baseline；
  - 测试覆盖危险权限、sandbox、hook  circuit breaker。

## 3. 优先级建议

| 优先级 | 借鉴项 | 理由 |
| --- | --- | --- |
| P0 | Goal/Loop Autonomy Primitives | 直接增强 LoopDesk 的可恢复执行与 bounded automation |
| P0 | MCP/ACP Unified Surface | 与现有 MCP-first/ACP-second 方向一致，提升可管理性 |
| P1 | Deterministic Replay / Time-Travel | 让 inspection/diagnostics 从“看当前状态”升级为“可审查历史” |
| P1 | Workspace-Scoped Skills/Plugin Registry | 与 v1.0 PRD 的 workspace-scoped extensibility 对齐 |
| P1 | Channel Abstraction + Unified Commands | 收紧 v0.2 adapter 边界，避免 Desktop/Web/IM 口径分裂 |
| P2 | Multi-Agent Topology as Optional Extension | 未来 review/validator 扩展有用，但 v1.0 不应成为主路径 |
| P2 | Local-First Inspectable Runtime Data | 已是 LoopDesk 方向，继续强化 diff/export/backup 体验 |
| P3 | Sandbox/Tool Policy Hardening | 重要，但当前重点应放在 loop continuity 与 surface 边界 |

## 4. 不建议借鉴

- 不要把 LoopDesk 做成 Octos 式的多租户 Agentic OS；
- 不要优先建设 cloud-hosted tenant pair、web dashboard admin、family plan；
- 不要把 Octos 的 slides/sites/voice/office  breadth 当成 v1.0 主路径；
- 不要把 swarm/external CLI backend 当成默认 developer experience；
- 不要为了 multi-surface runtime 而削弱本地 `LOOP-STATE.json` 的 durable source of truth 地位。

## 5. 后续验证

- 在 v1.0 feature breakdown 中确认 Goal checkpoint/resume/rollback 的 schema、run log 字段、surface 暴露边界；
- 在 adapter 设计中确认 MCP/ACP 的 workspace/run/approval/budget traceability；
- 在 channel adapter 设计中确认 unified command model、rate limit、audit log、disable rollback；
- 在 acceptance criteria 中确认 skills/MCP 的 inspectability、replay、export、cross-tool continuity 证据。
