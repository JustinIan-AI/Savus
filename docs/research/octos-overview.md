# Research — octos-org / octos

> 来源：`octos-org/.github` org profile README、`octos-org/octos` README、`octos-org/octos-web` README、`octos-org/octos-tui` README、`octos-org/octos-hub` README、本地 clone 的 `octos-org/octos` 代码树与文件内容。
> 日期：2026-07-28

## 1. 结论摘要

- `README.zh.md` 不是某个单文件项目的普通说明，而是 **`octos-org` 组织级 profile README**；它把 Octos 定义为一个 **Rust 开源 AI Agent 平台**，并把能力拆到 4 个主仓库：`octos`、`octos-web`、`octos-tui`、`octos-hub`。
- 对 LoopDesk 最值得关注的不是“又一个 Chat/Agent 客户端”，而是它把 **本地 runtime、多渠道接入、MCP/ACP、目标/循环 autonomy、技能系统、swarm 拓扑、审计/沙箱** 都放到一个统一后端里。
- 代码视角上，`octos` 不是单体大 crate，而是一个 **多 crate workspace**；核心能力分散在 `octos-agent`、`octos-bus`、`octos-memory`、`octos-llm`、`octos-pipeline`、`octos-plugin`、`octos-swarm`、`octos-cli` 等 crate 中。

## 2. 组织与产品定位

### 2.1 `octos-org` 的组织叙事

- `octos-org/.github` 的 profile README 将产品 slogan 定义为：“像章鱼一样——9 个大脑，每条触手独立思考，却共享同一个大脑。”
- 官方定位是 **“AI Agent 的后端操作系统”**：只部署一个 Rust 二进制，连接 LLM 与消息渠道，Octos 负责路由、会话、工具、记忆、故障切换和多租户隔离。
- 交付形态强调 **自包含、零运行时依赖的二进制**，并支持 macOS、Windows、Linux；安装方式包括 Homebrew、npm、PowerShell、install script、cargo。

### 2.2 四件套式产品结构

| 仓库 | 角色 |
| --- | --- |
| `octos-org/octos` | 核心平台：Rust 内核、LLM provider、工具、记忆、channel、REST/WebSocket、dashboard、UI Protocol |
| `octos-org/octos-web` | Web 客户端：React SPA，提供聊天、语音、Slides Studio、Sites、admin dashboard |
| `octos-org/octos-tui` | 终端客户端：Rust TUI，面向开发者，强调实时流式、审批、diff、引导 |
| `octos-org/octos-hub` | 社区技能注册表：安装和分享 agent skills |

## 3. 核心能力（来自 README）

### 3.1 后端与运行时

- **API-first Agentic OS**：80+ REST endpoints + UI Protocol v1，支持 Web/terminal/mobile/CI/CD 前端。
- **三套 runtime 模式**：`octos chat`（交互 CLI）、`octos gateway`（多渠道）、`octos serve`（Web dashboard + REST API + UI Protocol）。
- **多租户**：一台机器可运行 200+ profiles，每个 profile 都是隔离 OS process；支持 Family Plan 子账户。
- **多 LLM provider**：Anthropic、OpenAI、Gemini、Vertex AI、OpenRouter、DeepSeek、Moonshot/Kimi、Qwen、MiniMax、Zhipu/GLM、Z.AI、Groq、NVIDIA、Ollama、vLLM、r9s，以及兼容 base_url。
- **安装命令**：
  - `brew install octos-org/tap/octos`
  - `npm install -g @octos-org/octos`
  - `cargo install --path crates/octos-cli --features "api,telegram,discord,dingtalk,whatsapp,feishu,twilio,wecom,wecom-bot"`
  - `octos serve --solo` 以无密码本地登录启动 web app。

### 3.2 多渠道与消息接入

- 官方 README 列出 14 个渠道：Telegram、Discord、Slack、WhatsApp、Feishu/Lark、DingTalk、WeCom、WeChat、Matrix、LINE、QQ Bot、Email、Twilio、Web/API，外加 CLI。
- 会话控制命令是跨渠道的：`/new`、`/s <name>`、`/sessions`、`/back`。
- 代码层面，多频道实现集中在 `crates/octos-bus`，例如 `cron_service.rs` 已出现频道投递、原子写 `cron.json`、restart/reload 语义。

### 3.3 记忆与会话

- 三层记忆：长期记忆、情景记忆、会话记忆。
- 会话持久化是 JSONL，并带三层压缩；README 明确提到“thread_id + committed_seq”用于确定性回放。
- 本地侧有 `MEMORY.md` + `episodes.redb` + hybrid search；CLAUDE 中又提到 HNSW + BM25 混合检索。

### 3.4 工具、MCP、Sandbox、Office

- 工具系统统一用 `Tool` trait，支持 shell、文件、搜索、web、browser、MCP、office、spawn/cron。
- MCP 在代码里是显性一等公民：`crates/octos-agent/src/mcp.rs`、`mcp_server.rs`、`mcp_auth.rs`。
- Sandbox 有三层后端：Bwrap、macOS sandbox-exec、Docker；Windows 则回退到 NoSandbox 或 Docker。
- 还内置原生 Office 能力：PPTX/DOCX/XLSX。

### 3.5 Autonomy：Goals & Loops

- `/goal <objective>`：让 agent 在多轮中持续执行直到完成，带 checkpoint continuation 和 token budget。
- `/loop`：按固定间隔或自定时执行 recurring task，可 resume、pause、list、fire now、delete。
- 代码里已看到 `task_supervisor.rs`、`loop_retry_state.rs`、`realtime_loop.rs` 等路径，说明不是文档口号，而是实现中的核心概念。

### 3.6 Agent 拓扑：Sub-agent / Peer / Swarm

- **Sub-agent**：`spawn_agent` 在进程内创建子 agent，结果只向上回传最终答案。
- **Peer agent**：`peer_handoff`/`peer_gather` 创建对等 session，最大深度 1，handoff 大小上限 64KB。
- **Swarm**：`Swarm::dispatch` 支持 Parallel / Sequential / Pipeline / Fanout，统一 validator gate 和 redb ledger cost rollup。
- 外部 agent 支持双向接入：
  - inbound：Zed/ACP、`octos mcp-serve`
  - outbound：swarm worker 通过 `--swarm-backend` 驱动外部 CLI/MCP agent

## 4. 关键代码线索

### 4.1 Workspace 结构

本地 clone 的 `octos-org/octos` 代码树已包含这些顶层元素：

- `CLAUDE.md`
- `Cargo.toml`
- `README.md`
- `README-zh.md`
- `docs/`
- `book/`、`book-zh/`
- `crates/octos-cli`
- `crates/octos-agent`
- `crates/octos-bus`
- `crates/octos-memory`
- `crates/octos-llm`
- `crates/octos-pipeline`
- `crates/octos-plugin`
- `crates/octos-sandbox`
- `crates/octos-swarm`
- `crates/app-skills/`
- `crates/platform-skills/`

### 4.2 架构声明（CLAUDE）

- `CLAUDE.md` 把 octos 描述成 **Rust-native, API-first Agentic OS**。
- 主链路是 `octos-cli -> octos-agent -> octos-memory / octos-llm -> octos-core`。
- 并行能力包括 `octos-bus`、`octos-pipeline`、`octos-plugin`、bundled app skills、platform skills。
- CLI 面覆盖 `chat / init / status / gateway / serve / clean / completions / cron / channels / auth / skills / mcp-serve / mcp / acp / office / update / docs`。

### 4.3 与 LoopDesk 最相关的能力边界

| 维度 | Octos 表现 | 对 LoopDesk 的意义 |
| --- | --- | --- |
| 本地状态与记忆 | 本地 JSONL、redb、MEMORY.md、HNSW+BM25 混合检索 | 说明单机 personal loop workspace 是可行且被验证的方向 |
| Loop/Goal 抽象 | `/goal`、`/loop`、checkpoint、token budget、time-travel | LoopDesk 的 triage/maker/checker 可以从这里借鉴 autonomy 设计 |
| 多 Agent 编排 | sub-agent / peer / swarm、`POST /api/swarm/dispatch` | 可作为未来多 lens review / bounded fan-out 的参考 |
| MCP / ACP | `mcp-serve`、外部 MCP client、Zed ACP | 与 LoopDesk 的 MCP-first / ACP-second 方向高度相关 |
| 多渠道控制 | 14 channels、统一 `/new`/`/sessions`、channel-safe 分片 | 可参考其 channel abstraction 与 allowlist 设计 |
| 安全与沙箱 | deny-wins policy、sandbox、blocked env、prompt injection tests | 与 LoopDesk 的 approval/safety 边界一致 |
| 客户端分层 | web / tui / ACP / channel | 支持 LoopDesk 的“Desktop-first + Web + IM continuation”分层 |

## 5. 不建议过度对标之处

- Octos 更偏 **统一 backend OS + 多租户控制面**，不是以 `LOOP-STATE.json` 这种 portable cross-tool handoff protocol 为中心。
- 其 web/TUI/cloud 叙事比 LoopDesk 更重；LoopDesk 不应复制成 multi-user SaaS 或多 shell 产品。
- Octos 的 swarm/multi-agent 复杂度很高；LoopDesk 当前只应吸收 bounded fan-out、audit、cost rollup 思想，不必整体复刻。
- Octos 当前 README 中明确说明 Zed ACP 路径下交互式 tool approval 暂不透明传递，说明其 editor-first 路线仍有能力边界。

## 6. 证据来源与局限

- 已验证一手来源：`octos-org/.github` org profile README、`octos-org/octos` README、`octos-org/octos-web` README、`octos-org/octos-tui` README、`octos-org/octos-hub` README、本地 clone 的 `octos-org/octos` 代码树。
- 未完全验证：`octos-web` 前端源码、`octos-tui` 交互细节、真实多 provider 路由日志、商业版/托管版与开源版之间的精确能力差异。
- 如要深入，建议下一步直接阅读：
  - `crates/octos-agent/src/agent.rs`
  - `crates/octos-agent/src/mcp.rs`
  - `crates/octos-bus/src/session.rs`
  - `crates/octos-bus/src/cron_service.rs`
  - `crates/octos-swarm/src/dispatcher.rs`
  - `docs/ARCHITECTURE.md`
