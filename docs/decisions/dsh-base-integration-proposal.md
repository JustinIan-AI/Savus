# LoopDesk × DSH 集成提案 — 以 DSH 为 Agent Runtime 底座的企业个人工作台

> 状态：Proposal（待评审 / 待可行性验证）
> 版本：v0.3（新增 §5.5 长期二开路径与 §11 架构蓝图；补充 Cordis 插件二开事实）
> 日期：2026-07-30（v0.1 初稿）；2026-08-17（v0.3 新增长期二开路径与架构蓝图）
> 负责人：Product / Engineering
> 输入：`docs/prd/personal-loop-workspace-v1.1.zh.md`（含 2026-07-30 P0 修订）、`docs/research/prd-optimization-suggestions.md`、`docs/decisions/product-strategy.md`、`docs/decisions/desktop-web-im-product-boundary.md`、`docs/decisions/runtime-matrix.md`、`docs/plans/prd-v1.2-gap-backlog.md`，以及对 `deepseek-ai/deepseek-harness` 仓库的探查（npm 包 `@deepseek-ai/dsh`、`python/sdk`、`python/sdk-runtime`、`docs/user/guide/python-sdk.md`），以及本仓库后续调研：`docs/research/competitive-intel-deepseek-harness-runtime-fit.md`（fork + bundle 深度二开方案）、`docs/research/competitive-intel-huangruiteng-loopx.md`（LoopX 对照）、`docs/research/competitive-intel-longhorizon-harness.md`（LongHorizon 对照）
> 性质：**可行性方向的提案**，非已批准决策。需通过 §9 的验证清单后才能进入实施。

---

## 1. 背景与目的

LoopDesk 当前是自研 Python runtime（`src/loopdesk/...`）：gateway、loop engine、session、memory、skills、MCP client、sandbox、token meter 全部自己实现。这套 runtime 与 LoopDesk 的产品层（`LOOP-STATE.json`、Loop Engineering 六阶段、跨工具 continuity、CLI + 本地 Web UI）耦合在一起，工程量大、维护成本高。

本提案探讨：**以 DSH（DeepSeek Harness，`@deepseek-ai/dsh`）作为 Agent Runtime 底座做二次开发**，让 LoopDesk 聚焦于产品壳、企业外壳与差异化契约，而非重复造运行时。

目标场景从"独立开发者个人工作台"扩展为 **"企业内员工的个人工作台"**：每个员工有本地权威的 Agent 工作台，可跨 Claude Code、Codex、Trae、Gemini 等 Harness Agent 连续工作，同时企业获得审计与配额管控。

---

## 2. DSH 是什么（探查结论）

DSH 是一个 **cordis 插件化的 Agent Harness**（Node.js / TypeScript，MIT）。运行时由 profile + bundle + patch 层组合而成：`dsh --profile web|headless` 启动。核心事实：

- **官方 Python SDK 存在**：仓库根 `python/sdk` 提供 `deepseek-harness-sdk`（PyPI 分发，导入模块 `deepseek_harness`），通过 **JSON-RPC stdio** 驱动内置 runtime 子进程；`python/sdk-runtime` 提供 `deepseek-harness-runtime-bin` 平台 wheel（内置单文件 `dsh-jsonrpc-agent` 可执行，macOS/Linux，无需系统 Node）。这是 LoopDesk Python 层接入 DSH 的第一路径（详见 §5）。
- **npm 包 `@deepseek-ai/dsh` 是 CLI/profile 启动器**（纯 TS），与 Python SDK 并存；二者都源于同一 deepseek-harness 仓库。
- **对外接入面（除 Python SDK 外）**：
  1. **HTTP Typert RPC**：`dsh-api-gateway`（Host `ctx.typertGateway`）+ `dsh-host-webserver` 的 `/api` HTTP bridge + WebSocket downlink，JSON 序列化，任意语言可调用。
  2. **子代理 provider seam**：`dsh-subagent` 注册 provider（`spawn` / `fork` / `codex` / `claude-code` / `acp`），让一个 agent 把工作委托给子代理。
  3. **MCP client**：`dsh-mcp-client` 作为 *client* 连接外部 MCP server（方向是 DSH 消费外部，不是 DSH 对外暴露）。
- **Codex / Claude Code provider 已内建但 dormant**：`dsh-base` README 原文 "Codex and Claude Code providers load dormant"，agent preset 的 `delegation` 组已含 `tool-subagent-codex`（`provider: codex`）与 `tool-subagent-claude-code`（`provider: claude-code`），默认 `disabled: true`，复制 preset 去掉 disabled 即可暴露。
- **架构核心是 event-sourced**：`dsh-session` 是 append-only 事件日志，LLM message history 是**派生**的；`dsh-goal` 是 event-sourced CAS 状态机（create/edit/pause/resume/complete/block/clear + revision fence）。持久化走 `dsh-session-persistence-jsonl`（.jsonl.zstd），搜索走 `dsh-session-query-sqlite`（FTS5）。

---

## 3. 能力映射：LoopDesk PRD 需求 ↔ DSH 实现

| LoopDesk PRD 需求 | DSH 对应实现 | 状态 |
| --- | --- | --- |
| Python 接入层（LoopDesk 产品壳调用底座） | `deepseek-harness-sdk`（JSON-RPC stdio，`DeepSeekHarness.run()` / `Session.run()` / `HarnessClient`） | ✅ 官方 SDK，PyPI 分发 |
| Loop Engine / Loop-Goal 分离 | `dsh-agent-loop`（唯一 loop 逻辑）+ `dsh-agent`（零 loop 依赖接口）+ `dsh-goal` | ✅ 已实现 |
| Session / durable source of truth | `dsh-session` + `dsh-session-persistence-jsonl` | ✅ 已实现 |
| 跨工具 adapter（Claude Code/Codex/Trae/Gemini） | `dsh-subagent` provider seam：`codex` / `claude-code` / `acp` / `spawn` / `fork` | ⚠️ codex/claude-code dormant，需启用 |
| Skills / meta-skills | `dsh-skill` + `dsh-skill-filesystem` | ✅ 已实现 |
| MCP adapter | `dsh-mcp-client`（stdio / streamable-http） | ✅ 已实现 |
| Memory / 本地搜索 | `dsh-session-query-sqlite`（FTS5） | ✅ 已实现 |
| Cost / Safety | `dsh-token-meter` + `dsh-sandbox` + `dsh-user-approval` + `dsh-permission-presets` | ✅ 已实现 |
| Worktree isolation | `dsh-sandbox-policy` + `dsh-fs-sandbox`（文件效果策略 + 路径围栏） | ✅ 已实现 |
| CLI + 本地 Web UI | `dsh` CLI + `dsh-web-app` + `dsh-host-webserver` + `dsh-host-apiproxy` | ✅ 已实现 |
| Workflow / 多步编排 | `dsh-workflow` + `dsh-workflow-worker-thread` | ✅ 已实现 |
| Human Model / persona | `dsh-persona` + `dsh-agent-instructions` | ✅ 已实现 |
| Scheduler | `dsh-schedule`（固定间隔/定时/一次性） | ✅ 已实现（但非 cron 完整语义） |
| 审计上报 | `dsh-session-telemetry-otel` + `dsh-session-log-export` | ✅ 已实现 |

**结论：LoopDesk PRD 里约 80% 的"runtime 层"能力 DSH 已实现且工程质量高（event-sourced + invariant + replay + CAS）。二次开发的杠杆点不在"造运行时"，而在"造产品壳 + 企业外壳 + 差异化契约"。**

---

## 4. 结合架构（四层）

```
┌──────────────────────────────────────────────────────────┐
│ ④ 企业外壳（LoopDesk 新增，DSH 没有）                       │
│   员工隔离 · 企业审计/合规 · SSO · 集中配额/成本中心           │
├──────────────────────────────────────────────────────────┤
│ ③ 产品壳（LoopDesk Python 自研）                           │
│   loopdesk CLI · 本地 Web UI · Loop Engineering 六阶段 UX   │
│   成本/安全观测 · 跨工具 handoff 视图                        │
├──────────────────────────────────────────────────────────┤
│ ② 适配层（LoopDesk 薄层）                                  │
│   LOOP-STATE.json 投影 · 启用 codex/claude-code/acp provider │
│   Loop(后台发现)→Goal(收敛执行) 语义桥接                    │
│   Python ↔ DSH 的 HTTP Typert RPC 客户端                    │
├──────────────────────────────────────────────────────────┤
│ ① 底座（DSH，不动 / 仅加 patch）                           │
│   cordis + agent-loop + session + goal + subagent          │
│   skill + mcp-client + sandbox + token-meter + web-app     │
└──────────────────────────────────────────────────────────┘
```

### 4.1 底座层（DSH，最小改动）
DSH 运行时本身不动。LoopDesk 有两个启动入口选择：
- **Python SDK 内置 runtime（推荐主入口）**：`deepseek-harness-sdk` 直接 spawn 单文件 `dsh-jsonrpc-agent` 子进程，LoopDesk Python 层与它走 stdio JSON-RPC；通过 `cordis="..."` 传入 LoopDesk 自定义组合。
- **npm profile 入口（备选）**：`dsh --profile <name>` 启动常驻服务，LoopDesk 通过 HTTP Typert RPC 调用（适合多人共享一个 runtime 服务的场景）。

自定义组合统一通过复制 `standard`/`code` preset 去掉 `tool-subagent-codex` / `tool-subagent-claude-code` 的 `disabled` 来暴露 Codex / Claude Code 委托；通过 `cordis.patch.yml` 挂载企业治理插件（见 §4.4）。

### 4.2 适配层（LoopDesk 二次开发，薄）
这是核心二次开发面，三个关键设计决策：

**决策 1：`LOOP-STATE.json` 与 event-sourced log 的统一。**
DSH 的 durable authority 是 append-only 事件日志（写路径），LoopDesk 的差异化资产是 human-readable / diff-friendly / 可跨工具注入的 `LOOP-STATE.json`（读路径）。方案：**日志保持唯一权威，`LOOP-STATE.json` 退化为投影快照**——写一个小 projection 插件，从 `goal/change`、`subagent/descriptor`、run log、`workspace` registry 等事件折叠生成快照。这与 DSH 自身的 `session-projection` / `workspace` 模式同构（LLM history 从 log 派生、workspace 是 KV domain）。跨工具注入契约（PRD §11.4）的载荷从这个投影派生。

**决策 2：Loop（后台持续发现）层的落点。**
DSH 的 `dsh-goal` 是"单会话 goal 状态机"，没有 LoopDesk 的"Loop = 后台持续发现 + 分诊"上层概念。映射：
- Loop ≈ `dsh-schedule`（定时触发）+ triage skill + 收敛后 `ctx.goals.create()`。
- `dsh-tool-ralph`（fresh-agent 迭代 loop）可作为 Loop 实现的参考。
- LoopDesk 的 Project / Loop / Goal / Run 四层模型（PRD §7）在 DSH 上映射为：Project → `workspace` registry；Loop → schedule + 一个长命 session；Goal → `dsh-goal`；Run → goal round（`dsh-goal-round-driver`）。

**决策 3：跨工具兼容不写独立 adapter，复用 provider seam。**
- Claude Code → `provider: claude-code`；Codex → `provider: codex`。
- Trae / Gemini / 其他 → `acp` provider 或 `dsh-mcp-client`。
- 工程量从"每个工具一个 adapter"降到"配置 + 少量 provider 插件"。

### 4.3 产品壳层（LoopDesk Python，自研）
LoopDesk 的产品差异化仍由 Python 层承担：`loopdesk` CLI、本地 Web UI、Loop Engineering 六阶段 UX、成本/安全观测、跨工具 handoff 视图。**不复用 DSH 的 React `dsh-web-app` 作为产品面**（避免两套前端），但可参考其交互；产品壳通过官方 Python SDK（§5 主路径）控制 DSH 底座。

### 4.4 企业外壳层（LoopDesk 新增，DSH 没有）
"企业内员工个人工作台"需要 DSH 原生没有的能力：
- **员工隔离**：每个员工一个 workspace/profile + 独立 `LOOP-STATE.json`。
- **审计/合规**：复用 `dsh-session-telemetry-otel` + `dsh-session-log-export` 做只读审计上报。
- **SSO / 集中配额**：需自研或接入企业身份层（DSH 的 `dsh-credentials-local` 仅本地凭证）。
- **治理原则**：员工工作台保持 local-first（本地权威执行），企业治理只做**只读审计上报 + 集中配额**，**不做 team room / 实时协作 / 共享房间**——这延续 LoopDesk 的既定非目标，避免退化成 Tutti/Buzz/GOAI 的团队平台。

---

## 5. 技术栈事实与 Python 集成路径

**DSH 有官方 Python SDK。** 仓库根 `python/sdk` 提供 `deepseek-harness-sdk`（PyPI：`pip install deepseek-harness-sdk`，导入 `deepseek_harness`），它通过 **JSON-RPC stdio** 驱动一个内置 runtime 子进程（`deepseek-harness-runtime-bin` 平台 wheel 内打包的单文件 `dsh-jsonrpc-agent` 可执行，无需系统 Node）。Python 集成路径按优先级：

1. **官方 Python SDK（主路径）**：
   - 高层 API：`DeepSeekHarness(...)` 上下文管理器 + `harness.run(prompt)` / `harness.start_session(id).run(...)`，返回 `RunResult(session_id, final_response, finish_reason, events, notifications, session_root)`。
   - 低层 API：`HarnessClient` 暴露 `session_prompt()` / `request()` / `notify()` / `subscribe_session_notifications()` / `next_request()` / `respond()`——**Python 侧可以响应 runtime 发来的 inbound request**（如审批、用户提问），这是 LoopDesk approval queue / human-in-the-loop 的直接落点。
   - `notifications` 覆盖根会话 + 全部后代 subagent 谱系（`session/status` idle 判定、`session.event` 收集），与 LoopDesk 的 run log / 跨工具 trace 对齐。
   - 自定义组合：传入 `cordis="examples/jsonrpc-agent/cordis.yml"` 可跑自己的插件组合（含启用 codex/claude-code provider 的 preset）；SDK 保留 `@deepseek-ai/dsh-sdk-jsonrpc-server` 配置项。
2. **HTTP Typert RPC（备选/扩展）**：`dsh-api-gateway` + `dsh-host-webserver` 的 `/api` HTTP bridge + WebSocket downlink，Python 用 `httpx` 调用（agent / session / goal / subagent / workspace 等 remote 方法）。适合不需要 stdio 子进程、而是想连一个常驻 DSH 服务的场景；需处理鉴权（DSH v1 无 TLS/auth，见 §7 风险）。
3. **MCP server（辅路径）**：LoopDesk Python 层实现 MCP server，DSH 的 `dsh-mcp-client` 连接它——Python 提供工具（如企业审计、成本查询、文件系统扩展），DSH 消费。
4. **子代理 provider（跨工具，与 Python 无关）**：`codex` / `claude-code` / `acp` 是 DSH 拉起外部 CLI agent 的机制，是"兼容 Harness Agent"的落点。

> 备注：SDK 的 `HarnessClient` 在 runtime 进程生命周期内保留 subagent 谱系；`RunResult.events` 只含根会话事件，后代消息通过 notifications 传播。`cwd` / `session_root` 在启动前解析为绝对路径，`session_id` 复用可保留 session 内持久 Bash 状态（工作目录、导出变量、shell 函数）。

---

## 5.5 长期演进路径：fork DSH 并构建 LoopDesk 专用 bundle/plugin 层

上述 §5 的 Python SDK 集成路径是**第一阶段**（"黑盒调用"），目标是快速验证 DSH 能否作为 runtime 底座。但随着 DSH 进入正式版本、LoopDesk 产品功能深化，仅靠 Python SDK 的进程间 JSON-RPC 通信会逐渐成为瓶颈：状态同步延迟、审批语义映射、Web UI 事件订阅、custom preset 定制能力都受限。

因此本提案同时规划**第二阶段：fork DSH 仓库，在 Cordis 插件树中新增 LoopDesk 专用 bundle 与 plugin 层**，使 LoopDesk 从"DSH 的外部消费者"升级为"DSH 的共建者"。

### 5.5.1 为何不是纯黑盒调用

| 维度 | Python SDK 黑盒调用 | fork + bundle/plugin 二开 |
|---|---|---|
| 状态同步 | 依赖 RunResult 与 events，后验读取 | 直接监听 `session/event`，实时投影 |
| 审批/human-in-the-loop | 依赖 `next_request()` / `respond()` 回调 | 直接注册 `agent/*` 事件监听，在 pre-step 拦截 |
| 自定义工具 | 无法新增 DSH 原生工具 | 注册 `ctx.tools` 工具 + `ctx.fs` / `ctx.shell` provider |
| Web UI 定制 | 无能力 | 替换或扩展 `dsh-web-app` |
| 事件溯源 | 只能读取 | 扩展 `SessionEventMap`，新增 LoopDesk goal 事件 |
| Loop Engine | DSH 自带，不可替换 | 在 `agent/*` 事件上实现 LoopDesk 的 triage/maker/checker 驱动 |
| 回退成本 | 低（纯 Python 侧） | 需维护 fork 版本与同步上游 |

### 5.5.2 二开核心原则

1. **只改上层，不动 spine**：不修改 `packages/core/`（`session`、`agent`、`agent-loop`、`tools`、`system-prompt`）与 `packages/llm/`。
2. **LoopDesk 作为 plugin 集合挂载**：在 `packages/` 下新增 `loopdesk/` 组，在 `packages/bundle/` 下新增 `loopdesk/` bundle。
3. **保留 Python SDK 作为控制面入口**：Python 层继续通过 SDK 或 HTTP RPC 与 DSH 进程通信；新增 bundle 是"可选的更深集成路径"，不取代 §5 的 Python 主路径。
4. **`LOOP-STATE.json` 仍是 LoopDesk 的事实源**：DSH session log 作为审计补充；LoopDesk 通过 state-bridge plugin 维护 `LOOP-STATE.json` 的投影。
5. **profile 可替换**：用户可通过 `dsh --profile loopdesk` 启动，也可通过 `dsh --profile headless` 回退到纯 DSH 模式。

### 5.5.3 新增包规划

| 包名 | 类型 | Cordis ctx key | 职责 | 对应 LoopDesk 概念 |
|---|---|---|---|---|
| `@loopdesk/loopdesk-bundle` | bundle | — | 组合所有 LoopDesk plugin rows 为 profile 顶层 | profile 组装单元 |
| `@loopdesk/loopdesk-loop-engine` | plugin | `ctx.loopdeskLoopEngine` | triage → maker → checker 循环驱动 | Loop Engineering |
| `@loopdesk/loopdesk-goal` | plugin | `ctx.loopdeskGoals` | goal/todos/gates 状态管理 | LOOP-STATE goal 层 |
| `@loopdesk/loopdesk-state-bridge` | plugin | `ctx.loopdeskStateBridge` | DSH session event ↔ `LOOP-STATE.json` 双向投影 | 状态同步 |
| `@loopdesk/loopdesk-runtime-adapter` | plugin | `ctx.loopdeskRuntimeAdapter` | 统一调用 DSH Agent / 外部 MCP / ACP / 本地脚本 | runtime driver |
| `@loopdesk/loopdesk-memory` | plugin | `ctx.loopdeskMemory` | skills / memory / artifacts 管理 | memory/skills |
| `@loopdesk/loopdesk-web-ui` | plugin | — | 替换/扩展 DSH Web UI，叠加 LoopDesk 管理面板 | Web UI |

### 5.5.4 数据流（二开模式）

```
用户输入 / 心跳触发
  │
  ▼
loopdesk-loop-engine    ← 读取 ctx.loopdeskGoals，决定下一步
  │
  ├─▶ loopdesk-runtime-adapter   ← 调 DSH Agent / MCP / ACP
  │      │
  │      ▼
  │   dsh session event log    ← turn/start, step/start, tool/call, ...
  │      │
  │      ▼
  │   loopdesk-state-bridge    ← 提取 verified progress, todos, gates
  │      │
  │      ▼
  │   LOOP-STATE.json          ← 本地事实源
  │
  └─▶ loopdesk-web-ui          ← 订阅 session/event，渲染 Card Feed
```

LoopDesk 的 loop engine 通过监听 `agent/turn-stopping` 事件，在每次 DSH turn 结束时判断 goal 是否完成；未完成则通过 `agent.inject()` 向 inbox 注入下一条 task prompt，驱动下一轮。

---


## 6. 与 LoopDesk 现有定位的关系

- **强化**：DSH 底座让 LoopDesk 的"workspace state 是产品，不是 shell"更纯粹——runtime 由 DSH 承担，LoopDesk 只做控制平面与差异化。
- **延续**：`LOOP-STATE.json` 作为投影快照，仍保持 human-readable / diff-friendly / 可导出，满足 local-first / portable 承诺。
- **扩展**：目标用户从"独立开发者"扩展到"企业内员工个人工作台"，但保持"个人 local-first 权威 + 企业只读治理"的边界，不引入 team room。
- **冲突待解**：PRD §4.2 的"不做 enterprise onboarding"需要修订为"不做 team collaboration / 实时共享房间，但提供个人工作台的企业审计与配额治理"。

---

## 7. 风险与缓解

| 风险 | 严重度 | 缓解 |
| --- | --- | --- |
| **Python SDK 仍是 dev 版本（pyproject 中 0.0.0.dev0），且 runtime wheel 仅覆盖 macOS 14+ arm64 / Linux x64+arm64** | 🔴 高 | 先验证 PyPI 发布的 `deepseek-harness-sdk` 实际可用版本与平台覆盖；企业 Windows 员工需评估备选（HTTP RPC 连常驻服务） |
| **DSH 是 rc 版本（npm 0.1.0-rc.6），API 不稳定** | 🔴 高 | 锁定版本；在适配层做隔离，避免 Python 产品壳直接依赖 DSH 内部结构 |
| **`dsh-host-webserver` 无 TLS/auth/origin policy**（README 明示） | 🔴 高 | 企业场景必须前置 reverse proxy + 鉴权层；LoopDesk 自研企业网关 |
| **技术栈转向（Python runtime → TS 底座）推翻既有决策** | 🟡 中 | 明确分阶段：先可行性验证，再决定退役 Python runtime 的哪些模块 |
| **codex/claude-code provider 是 dormant，实际行为未验证** | 🟡 中 | 验证启用后能否真正拉起外部 CLI、结果如何回写 session |
| **event-sourced log 与 `LOOP-STATE.json` 快照的一致性** | 🟡 中 | 投影插件必须幂等、可重放；快照只读，写路径走 log |
| **"企业"定位与 local-first 的张力** | 🟡 中 | 明确"个人权威 + 企业只读治理"边界，禁止实时共享房间 |
| **DSH 品牌与 DeepSeek 归属** | 🟢 低 | MIT 可二次开发；LoopDesk 产品面与 DSH 品牌分离 |

---

## 8. 非目标

- 不做 DSH 的 Python 重写（官方 `deepseek-harness-sdk` 已存在，复用优先）。
- 不复制 DSH 的 React `dsh-web-app` 作为 LoopDesk 产品面。
- 不引入 team room / 实时协作 / 共享房间（延续 LoopDesk 非目标）。
- 不在 v1 阶段替换 DSH 的 sandbox / token-meter / session 为自研（复用优先）。

---

## 9. 待验证清单（进入实施前的 gate）

1. **Python SDK 可用性验证**：`pip install deepseek-harness-sdk` 后，`DeepSeekHarness()` + `run()` 能否在本机（macOS/Linux）跑通首条 prompt？PyPI 上的实际版本号与平台覆盖是否满足要求？
2. **审批/human-in-the-loop 验证**：`HarnessClient` 的 `next_request()` / `respond()` 能否承接 runtime 的 inbound request（approval / 用户提问）？这决定 LoopDesk approval queue 能否直接建在 SDK 之上。
3. **自定义组合验证**：传入自定义 `cordis.yml`（含启用 `tool-subagent-codex` / `tool-subagent-claude-code` 的 preset）后，DSH 能否真正拉起本地 Codex / Claude Code CLI？子代理结果如何回写父 session？`acp` provider 的边界（one-shot、非 trace-enumerable，README 明示）是否满足 LoopDesk 的 run log 要求？
4. **投影插件验证**：从 DSH session log / notifications 折叠生成 `LOOP-STATE.json` 快照的最小字段集合与一致性保证。
5. **审计上报验证**：`dsh-session-telemetry-otel` + `dsh-session-log-export` 能否支撑企业只读审计（谁、何时、做了什么、花了多少）。
6. **沙箱/审批映射验证**：DSH 的 `dsh-sandbox-policy` + `dsh-user-approval` 是否能映射 LoopDesk 的 read-only / restricted / full-access 三档权限与 approval queue。
7. **成本边界验证**：Python SDK 的 stdio 子进程模型对 offline-first 的影响，以及 `session_id` 复用（持久 Bash 状态）是否符合 LoopDesk 的 Run 语义。

---

## 10. 建议的后续动作

1. 以本提案为输入，做一轮 **DSH Python SDK 深度可行性 spike**（验证 §9 的 1–4 项），产出可行性结论。
2. 若 spike 通过，更新 `docs/decisions/runtime-matrix.md`、`docs/decisions/desktop-web-im-product-boundary.md` 与 PRD §4.2（企业治理边界）。
3. 若 spike 证明 Python SDK 路径不可行（如平台覆盖不足、inbound request 不支持），回退到"DSH 仅作为跨工具子代理 provider（codex/claude-code/acp）+ HTTP Typert RPC"的降级方案——此时 DSH 只替换 PRD 的 cross-tool adapter 层，不替换 loop engine / session。

---

## 11. 长期二开架构蓝图（DSH as Chassis）

### 11.1 设计意图

"以 DSH 为底盘"的含义：DSH 提供**可运行的 Agent Runtime 骨架**（LLM 适配、会话日志、工具注册、Agent Loop、子 Agent、工作流、文件系统），LoopDesk 在此基础上叠加**产品控制面**（Loop Engine、goal/todos/gates、多 runtime 适配、企业审计治理、管理面 UI）。

这不是把 LoopDesk 改造成 DSH 的一部分，而是让 LoopDesk 的**差异化能力**以插件形式寄生在 DSH 的插件生态中。DSH 是发动机，LoopDesk 是车身。

### 11.2 分层架构

```
┌──────────────────────────────────────────────┐
│  LoopDesk 产品层（控制面）                     │
│  - LOOP-STATE.json（本地事实源）              │
│  - Loop Engineering 六阶段 loop              │
│  - 企业审计 / 配额 / SSO 治理               │
│  - Web UI 管理面板                            │
├──────────────────────────────────────────────┤
│  LoopDesk Plugin 层（寄生在 DSH Cordis 中）    │
│  - loopdesk-loop-engine   (ctx.loopdeskLoopEngine)  │
│  - loopdesk-goal          (ctx.loopdeskGoals)       │
│  - loopdesk-state-bridge  (ctx.loopdeskStateBridge) │
│  - loopdesk-runtime-adapter (ctx.loopdeskRuntimeAdapter)│
│  - loopdesk-memory        (ctx.loopdeskMemory)       │
│  - loopdesk-web-ui                          │
├──────────────────────────────────────────────┤
│  DSH Core Spine（不可修改）                   │
│  - dsh-session / dsh-agent-loop / dsh-tools  │
│  - dsh-llm / dsh-system-prompt               │
│  - dsh-subagent / dsh-workflow / dsh-shell   │
└──────────────────────────────────────────────┘
```

### 11.3 goal 在 DSH 中的表达

LoopDesk 的 goal 概念通过**扩展 `SessionEventMap`** 嵌入 DSH 的事件溯源日志：

```ts
interface SessionEventMap {
  // DSH 原生事件
  'turn/start': { turn: number }
  'tool/result': { turn: number; step: number; ... }

  // LoopDesk 扩展事件
  'loopdesk/goal-created':    { goalId: string; objective: string }
  'loopdesk/todo-added':      { goalId: string; todoId: string; body: string }
  'loopdesk/todo-completed':  { goalId: string; todoId: string }
  'loopdesk/gate-passed':     { goalId: string; gateKind: string }
  'loopdesk/gate-blocked':    { goalId: string; reason: string }
}
```

这样 LoopDesk 的 goal 状态变更会进入 append-only session log，与 DSH 的 turn/step/tool 事件共享同一个审计轨迹。`loopdesk-state-bridge` 从 session log 折叠投影为 `LOOP-STATE.json`。

### 11.4 maker / checker 在 DSH 中的映射

| LoopDesk 概念 | DSH 实现方式 |
|---|---|
| maker | `ctx.subagents.start({ provider: 'dsh-in-process', ... })` 或 `ctx.agentLoop.create()` 直接启动 |
| checker | 同上，用独立的 auditor preset / persona |
| multi-runtime 适配 | `loopdesk-runtime-adapter` 包装 DSH subagent / 外部 MCP / ACP / 本地脚本，统一接口 |
| gate / stop condition | 通过 `agent/turn-stopping` 事件决定下一轮是否继续 |

### 11.5 分阶段落地路线图

| 阶段 | 内容 | 产出 | 风险 |
|---|---|---|---|
| **Phase 1（1-2 周）** | fork DSH，新增空的 `@loopdesk/bundle-loopdesk`，验证 `dsh --profile loopdesk` 能启动 | 可启动的 fork + 空 bundle | 低 |
| **Phase 2（2-3 周）** | 新增 `loopdesk-state-bridge`，实现 session event → `LOOP-STATE.json` 投影 | 状态桥接可用 | 中（一致性保证） |
| **Phase 3（3-4 周）** | 新增 `loopdesk-loop-engine`，监听 `agent/turn-stopping` 实现 triage/maker/checker 循环 | Loop Engine 可用 | 中 |
| **Phase 4（4-6 周）** | 新增 `loopdesk-runtime-adapter` + `loopdesk-web-ui` | 多 runtime + Web UI | 高（Web UI 复杂度） |

### 11.6 与 §10 降级方案的兼容

若 §9 spike 证明 Python SDK 路径不可行（如平台覆盖不足、inbound request 不支持），本架构仍可降级：此时 Phase 1–4 中的 bundle/plugin 层可以只在 fork 中实现**跨工具子代理 provider**（`codex` / `claude-code` / `acp`）部分，`LOOP-STATE.json` 仍由 Python 层维护，DSH fork 只提供 cross-tool adapter 能力，不替换 loop engine / session。

---


## 12. 批准

| Role | Name | Status |
| --- | --- | --- |
| Product | | Pending |
| Engineering | | Pending |
| Design | | Pending |
