# DeerFlow 调研报告

> 状态：已完成
> 仓库：`bytedance/deer-flow`
> 分支：`main`
> 提交：`1b5220e`
> 许可证：MIT
> 调研日期：2026-07-29
> 来源：`README.md`、`backend/README.md`、`backend/docs/ARCHITECTURE.md`、`backend/docs/CONFIGURATION.md`、`backend/AGENTS.md`、`frontend/AGENTS.md`、`config.example.yaml`、`extensions_config.example.json`、`backend/packages/harness/pyproject.toml`、`frontend/package.json`、根目录 `Makefile`

## 1. 一句话结论

DeerFlow 2.0 是一个 **ByteDance 开源的 LangGraph 超级 Agent Harness**，核心卖点不是单一模型能力，而是把 **sub-agent 编排、sandbox 执行、持久记忆、skills、IM 通道、MCP 扩展、Web UI / TUI** 打包成可运行、可调度、可监控的全栈 Agent 系统；对 LoopDesk 的参考价值主要在 **skill/tool/memory/sandbox 分层、sub-agent 任务分解、多 surface 控制面、后台 scheduled task**，但产品定位明显更偏“通用 Agent 平台/研究自动化工作台”，不是本地优先的个人 loop workspace。

## 2. 产品定位

- 官方定位从 v1 的 Deep Research 框架升级为 2.0 的 **super agent harness**： batteries included，支持研究、报告、幻灯片、网页、图片/视频生成、数据分析、自动化工作流等场景。
- 与 LoopDesk 的关键差异：DeerFlow 是 **full-stack agent runtime + web workspace + optional channels**，天然支持多任务、多工具、多通道；LoopDesk 明确收敛为 **personal-first / local-first / loop-first** 的个人工作流控制平面。
- 竞争叙事上，DeerFlow 更像 **Devin / LangGraph Crew 的可运行产品版**，而不是 LoopDesk 强调的“跨工具 Agent continuity layer”。

## 3. 核心功能

| 功能 | 说明 | LoopDesk 可借鉴点 |
| --- | --- | --- |
| Skills & Tools | `SKILL.md` 工作流模块，支持内置/自定义/组合技能，支持 `/skill-name` 单轮显式激活，`allowed-tools` 只约束已激活技能；技能失败时回退到 framework-safe 工具。 | skill 作为一等能力包、skill 权限策略、slash activation |
| Sub-Agents | lead agent 可按任务动态派生 sub-agent，支持并行执行、结构化回传、独立上下文/工具/终止条件；sub-agent 也复用同一 user-scoped skill catalog。 | task graph / planner / maker-checker 分层、run log 回传 |
| Session Goals | `/goal <completion condition>` 绑定线程级完成条件，每次 Gateway run 后用 evaluator 判断是否满足；支持自动 continuation、no-progress breaker、clear、thread-scoped state。 | loop stop condition、goal-aware run log、human override |
| Manual Context Compaction | `/compact` 手动压缩旧上下文，保留完整历史可见，但后续模型调用使用 summary + recent messages；run in flight 时禁止 compact。 | context sub-structure、compaction/prune、人类控制点 |
| Long-Term Memory | DeerMem 默认本地记忆，可选 OpenViking / mem0；支持长期 profile、preferences、knowledge、file-backed facts、agent-scoped facts、duplicate suppression、import/export。 | memory index、 durable memory、session-to-memory flush |
| Sandbox & File System | 提供本地 / Docker / Kubernetes 三类 sandbox；线程隔离目录映射 `/mnt/user-data/...` 和 `/mnt/skills`；支持 read/write/str_replace/bash/list_dir 等文件工具。 | worktree isolation、sandbox boundary、artifact 管理 |
| Scheduled Tasks | 后台 scheduled-task MVP：支持 `once` / `cron`、线程复用或 fresh thread、skip overlap、pause/resume/trigger/history；调度器必须复用 DeerFlow 正常 run lifecycle。 | loop scheduler、background automation、run ownership heartbeat |
| TUI | `deerflow` 终端工作台，内嵌 `DeerFlowClient`，不需要 Gateway / Docker / nginx 即可使用；支持 resume、`--print`、`--json`、slash commands、goal management。 | CLI-first surface、terminal control plane |
| IM Channels | 支持 Lark/Feishu、Slack、Telegram、Discord、DingTalk、WeCom、GitHub；通过 Gateway 接入同一 agent runtime。 | channel adapter 设计、IM remote control、optional continuation |
| Claude Code Integration | `claude-to-deerflow` skill 支持从 Claude Code 直接访问运行中的 DeerFlow 实例，选择执行模式、查看状态、管理 threads、上传文件。 | external coding agent handoff、cross-tool control |

## 4. 技术架构

### 4.1 服务拓扑

```
Client -> Nginx :2026
  /api/langgraph/* -> Gateway :8001 LangGraph-compatible runtime
  /api/*          -> Gateway :8001 REST / Models / MCP / Skills / Memory / Artifacts / Threads
  /*              -> Frontend :3000
Provisioner :8002 -> 可选，用于 sandbox/Kubernetes 模式
```

关键实现约束：

- Gateway 同时承担 **FastAPI REST API** 和 **embedded LangGraph runtime**。
- Nginx 是统一入口，但 durable authority 仍是 Gateway；前端、TUI、IM 都是接入面。
- 线程删除时，Web UI 会继续调用 Gateway 清理本地 `.deer-flow/threads/{thread_id}/` 数据。

### 4.2 Backend

- 核心包：`backend/packages/harness`，对外暴露 `deerflow.*`；Gateway 在 `backend/app`。
- Lead agent 通过 `make_lead_agent(config)` 创建，内部走 9 层 middleware：
  1. ThreadDataMiddleware：创建线程隔离目录
  2. UploadsMiddleware：注入上传文件
  3. SandboxMiddleware：获取 sandbox
  4. SummarizationMiddleware：压缩长上下文
  5. TodoListMiddleware：plan mode 任务跟踪
  6. TitleMiddleware：自动生成标题
  7. MemoryMiddleware：异步记忆提取
  8. ViewImageMiddleware：图像输入
  9. ClarificationMiddleware：澄清/中断执行
- 工具系统支持 built-in、MCP、community、sandbox 四类工具；MCP server 可独立 enable/disable，配置热更新通过 `PUT /api/mcp/config` 和 `POST /api/mcp/cache/reset` 完成。
- 模型工厂支持 OpenAI / Anthropic / Gemini / DeepSeek / MiMo / Ollama / Codex CLI / Claude Code OAuth 等多种 provider；对 thinking / reasoning / vision 有显式 adapter/patch。
- 可观测性支持 LangSmith、Langfuse、Monocle；scheduler MVP 依赖数据库做 singleton active-run 保护。

### 4.3 Frontend

- 前端为 **Next.js 16 + React 19 + Tailwind CSS 4 + Shadcn / MagicUI / React Bits**。
- 主要页面：`/`、`/chats`、`/chats/new`、`/chats/[thread_id]`。
- 前端通过 `@langchain/langgraph-sdk`、TanStack Query、Vercel AI Elements 与 Gateway / LangGraph 交互。
- E2E 覆盖：agent chat、artifact stream、branch thread、channels、integrations、scheduled tasks、subtask card、sidecar、browser control 等。

## 5. 技术栈

### 5.1 Backend

- 语言：Python 3.12+
- 运行时/编排：LangGraph、LangChain、LangGraph SDK、LangGraph API
- API：FastAPI、Uvicorn、SSE-Starlette
- 数据库/持久化：SQLAlchemy、Alembic、aiosqlite、可选 PostgreSQL / Redis
- Agent 能力：MCP adapters、Exa / Tavily / Firecrawl / DuckDuckGo、E2B、markitdown、readabilipy、tiktoken
- 安全/认证：bcrypt、PyJWT、lark-oapi、slack-sdk、python-telegram-bot、dingtalk-stream、wecom-aibot
- 测试：pytest、Hypothesis、blockbuster

### 5.2 Frontend

- 框架：Next.js 16、React 19
- 样式：Tailwind CSS 4、Shadcn UI、MagicUI、React Bits
- 状态/数据：TanStack Query、Zod
- AI/流式：Vercel AI SDK、LangGraph SDK、streamdown、mermaid
- 测试：Rstest、Playwright、happy-dom
- 工程化：pnpm workspaces、Prettier、ESLint、TypeScript、Rsbuild

## 6. 运行与配置

### 6.1 部署形态

- 推荐 Docker：`make docker-init`、`make docker-start`
- 本地开发：`make setup`、`make dev`
- 终端直连：`uv pip install 'deerflow-harness[tui]'` 后运行 `deerflow`
- 资源建议：开发/轻量场景 4 vCPU / 8 GB RAM；长期服务 8–16 vCPU / 16–32 GB RAM；Linux + Docker 为推荐生产环境。

### 6.2 关键配置

- `config.yaml`：models、tools、sandbox、summarization、token budget、scheduler、auth、memory、browser control 等主配置。
- `extensions_config.example.json`：MCP servers、skills、mcpInterceptors、routing keywords。
- 运行时数据默认放在 `.deer-flow/`；可通过 `DEER_FLOW_HOME` 切换。
- 配置支持热更新；数据库 checkpoint 和 scheduler 部分字段需重启 Gateway。

## 7. 集成与扩展

- MCP：支持 stdio MCP server，例如 GitHub、Postgres；可在 Settings / extensions 中按 server / tool 配置 routing keywords。
- Skills：内置 research、report、slide、web page、image/video、data analysis 等 skill；支持 custom skills、compound workflows、install/update、slash activation。
- Channels：Feishu、Slack、Telegram、Discord、DingTalk、WeCom、GitHub；全部通过 Gateway 接入同一 agent runtime。
- Coding agents：Claude Code、Codex 等可通过 `claude-to-deerflow` skill 或 ACP adapter 接入。
- Tracing：LangSmith、Langfuse、Monocle；Gateway trace middleware 和 run event stream contract 可作为可观测基础。

## 8. 成熟度与社区

- 当前版本：2.1.0
- 许可证：MIT
- 主要语言/框架：Python、Next.js、LangGraph
- 社区信号：2026-02-28 曾登上 GitHub Trending #1；官方宣传推荐 Doubao-Seed-2.0-Code、DeepSeek v3.2、Kimi 2.5 等模型。
- 工程完整度较高：前后端分离、Docker、Playwright E2E、schema/contract 文件、docs、阻塞 IO 检测脚本、support bundle、scheduler MVP、TUI。
- 生态偏 ByteDance/Volcengine：InfoQuest、OpenViking、Coding Plan、BytePlus 生态整合较深。

## 9. 安全与边界

- 官方明确建议默认部署在本地可信环境，默认只监听 `127.0.0.1`。
- 高风险能力：system command execution、file read/write、business logic invocation、sandbox、MCP server 进程。
- 跨网部署建议：IP allowlist、认证网关、VLAN 隔离、及时升级。
- MCP security：server 独立进程、运行时环境变量注入、可独立开关。
- Sandbox security：支持 local / DooD / provisioner 三级隔离；Docker socket 被明确视为 host root，文档要求谨慎配置。

## 10. 与 LoopDesk 的关系

| 维度 | DeerFlow | LoopDesk |
| --- | --- | --- |
| 核心定位 | 全栈 super agent harness | 个人 Agent 工作流控制平面 |
| 主要用户 | 通用 AI 工作流、研究、自动化开发者 | independent developer / personal coding loop |
| 状态载体 | thread / run / checkpoint / `.deer-flow/` | `LOOP-STATE.json` / local workspace |
| 上下文连续性 | summarization、memory、sub-agent 委托 | loop state、memory、skills、worktree isolation |
| 多工具 | MCP / built-in / community / sandbox / Claude Code / Codex | MCP-first / ACP-second / runtime adapter |
| 控制面 | Web UI + TUI + IM + Gateway API | CLI + local Web UI + optional IM |
| 沙箱 | Docker / K8s / local sandbox | worktree / local sandbox 边界 |
| 调度 | scheduler MVP / cron / once | loop engine / cron / fire-immediately |
| 团队/多租户 | 更偏平台化，无明确 team-room 叙事，但架构更重 | 明确排除 team workspace / cloud room / SaaS runtime |

## 11. 可借鉴清单

- **Skill Engineering**：`SKILL.md` 包边界、slash activation、`allowed-tools` 权限策略、skill install/update lifecycle。
- **Sub-Agent Playbook**：delegated task、并行执行、结构化回传、sub-agent card、父线程摘要。
- **Goal-Driven Loop**：`/goal` + evaluator + auto continuation + no-progress breaker 可直接映射到 LoopDesk 的 stop condition / run log / human override。
- **Context Compaction UX**：`/compact` 的人工压缩路径与 run-flight 互斥，适合 LoopDesk 的 context sub-structure / compaction boundary。
- **Memory Architecture**：file-backed facts、agent-scoped facts、duplicate suppression、import/export、可切换 backend。
- **Sandbox Isolation**：local / Docker / K8s 三级抽象，可映射成 LoopDesk 的 safer worktree / execution boundary。
- **Scheduled Task MVP**：后台 run、skip overlap、thread reuse / fresh thread、history，适合 LoopDesk v1.2+ 的 loop scheduler。
- **Multi-Surface Control**：Web UI + TUI + IM + embedded Python client 共享同一 Gateway/state，适合 LoopDesk 的 desktop/web/terminal/IM 控制面设计。
- **MCP Routing by Keywords**：`extensions_config.json` 里 per-tool routing keywords，可映射到 LoopDesk 的 smart router / capability profile。
- **Observability Contracts**：`contracts/*.json`、trace middleware、run event stream、support bundle，适合 LoopDesk 的 trace / run log / diagnostics。

## 12. 风险与注意点

- **范围过大**：DeerFlow 2.0 是“什么都想做”的平台级项目，直接对标会稀释 LoopDesk 的 personal-first 心智。
- **运维成本高**：Gateway + Nginx + Frontend + optional Provisioner + Docker sandbox + database/redis 的组合比 LoopDesk 的 local-first CLI + web 重很多。
- **生态绑定**：官方推荐模型、InfoQuest、OpenViking、ByteDance Coding Plan 都带有较强生态偏好，使用时需评估 vendor lock-in。
- **安全面更大**：system command、file write、MCP server、browser control、multi-channel 扩大了攻击面；不适合默认暴露到 untrusted network。
- **个人工作流叙事弱**：DeerFlow 强调通用 harness / deep research / automation，而不是 LoopDesk 强调的“人的工作连续性属于用户，不属于某个 Agent”。

## 13. 建议结论

- 若 LoopDesk 的目标是 **Personal Agent Control Plane**，应把 DeerFlow 当作“能力参照系”而不是产品对标：
  - 学习它的 skill/tool/memory/sandbox/scheduler/sub-agent 分层；
  - 吸收它的 goal-driven loop、context compaction、observability contract；
  - 但避免复制其平台化叙事、重服务拓扑、IM-first 扩展、cloud-room/team 歧义。
- 对 LoopDesk v1.2 / v1.3 最有价值的迁移项优先级建议：
  1. goal-aware run log + evaluator + auto continuation
  2. skill package boundary + slash activation + allowed-tools policy
  3. sub-agent runtime metadata + subtask card + run event contract
  4. scheduled task MVP with normal run lifecycle
  5. MCP keyword routing + runtime capability profile
  6. TUI / embedded client as optional local surface，而非主 runtime
