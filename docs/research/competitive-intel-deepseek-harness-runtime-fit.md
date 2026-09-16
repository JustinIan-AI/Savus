# 竞争情报：DeepSeek Harness（dsh）——作为 LoopDesk 底层默认 Runtime 的可行性

- **Repo**: [github.com/deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)
- **开发商**: DeepSeek AI
- **协议**: MIT
- **技术栈**: TypeScript / Node.js ≥22.19，基于 [Cordis](https://github.com/cordiverse/cordis) 插件框架
- **定位**: "Everything is a Plugin" 的通用 Agent harness/runtime
- **状态**: Developer Preview（明确声明会有破坏性变更）
- **启动方式**:
  - `npx @deepseek-ai/dsh web`（默认 Web UI，端口 3080）
  - `dsh --profile headless "task"`（一次性 headless 运行）

## 1. dsh 不是“外层循环控制器”，而是一个完整 Agent Runtime

与前几个调研对象（LoopX、LongHorizon-Harness）不同，**DeepSeek Harness 不依赖外部 Agent（如 Codex CLI 或 Claude Code）作为执行器**。它自身就是一个可独立运行的 Agent 运行时：

- 自带 LLM 适配层（`ctx.llm`）
- 自带事件溯源会话日志（`ctx.sessions`）
- 自带工具注册表与执行流水线（`ctx.tools`）
- 自带 Agent Loop 驱动器（`ctx.agentLoop`）
- 自带文件系统、Shell、子 Agent、工作流、Web 搜索、终端等能力 seam
- 自带 Web UI 与 Headless CLI 两种形态

**一句话总结**：LoopX 和 LongHorizon-Harness 是“给 Claude Code/Codex 戴上的缰绳”；dsh 是“一匹马，可以戴上不同鞍具”。

## 2. 核心架构：Cordis 插件树

### 2.1 组合模型：Profile + Bundle + Patch

```
dsh 进程 = 空条目列表
  + 按序叠加的 bundle 层（如 dsh-base, dsh-web-app, dsh-headless）
  + profile 的 cordis.patch.yml
  + home 级 cordis.patch.yml
  + --patch 命令行覆盖
```

| 概念 | 含义 |
|------|------|
| **Profile** | 存放在 Harness home 中的具名组装，列出叠加的 bundles |
| **Bundle** | Cordis 配置行及其挂载代码的分发单元 |
| **Patch** | 按 id 替换或插入配置行的覆盖层 |

这意味着 dsh 的几乎所有行为都可以通过配置文件热插拔地替换，而无需改源码。

### 2.2 核心 Service Context

| ctx 键 | 职责 |
|--------|------|
| `ctx.sessions` | 仅追加的 SessionEvent 日志与内存存储 |
| `ctx.systemPrompt` | 提示词片段与工具 schema 组装 |
| `ctx.tools` | 作用域化工具注册表与带把关执行流水线 |
| `ctx.agents` | Agent 接口、活跃注册表、`agent/*` 事件 |
| `ctx.agentLoop` | 默认 Agent Loop 驱动器 |
| `ctx.llm` | 消息与流式词汇、模型适配 seam |
| `ctx.fs` | 文件系统能力 seam |
| `ctx.shell` | Shell 执行能力 seam |
| `ctx.subprocess` | 子进程能力 seam |
| `ctx.terminals` | 持久终端 |
| `ctx.subagents` | 子 Agent 能力（可多 provider 并存） |
| `ctx.workflowEngine` | 模型编写的工作流脚本引擎 |
| `ctx.goals` | 同会话目标管理 |

## 3. Turn / Step 生命周期

```text
turn/start
  claim next-step input plus one queued message
  assemble prompt sections + tool schemas
  -> agent/pre-step                   reject | enter(messages)
     reject 或 first enter 为空 -> 关闭 turn，无 step
     step/start
     append entered messages as user/message
     derive model history from the log
     agent/request -> llm/stream -> assistant/chunk* -> assistant/message
     tool/call* -> tools/pre-execute -> tools/execute -> tools/post-execute -> tool/result*
     step/end
     tools owe another request, 或 next-step input arrived -> claim -> next step
  -> agent/turn-stopping
turn/end
```

关键原则：**"Model-visible means logged"** —— 抵达模型请求的一切都必须能从日志重建。

## 4. 关键能力 seam

### 4.1 子 Agent（Subagent）

- 多 provider 并存：可注册 `spawn-in-process`、`fork`、`acp`、`codex`、`claude-code`、`dsh-sdk` 等后端。
- 支持一次性委托（one-shot）和可持续对话（continuable）两种子 Agent。
- 子 Agent 的 cwd、lineage、delegation depth 通过父会话传递。

### 4.2 工作流（Workflow）

- 模型可以调用 `workflow` 工具，提交一段 JavaScript 脚本。
- 脚本在 `node:worker_threads` 隔离环境中运行，可调用 `agent()` 启动子 Agent。
- 支持 `phase()` 进度分组、`log()` 叙述记录。
- 工作流结果作为 JSON 数据返回。

### 4.3 与外部 Agent 的 Hook Bridge

- `hooks-claude-code` 和 `hooks-codex` 两个 bridge 插件。
- 它们读取外部 Agent 的 `hooks.json` / 设置文件，把外部 shell hook 协议翻译到 dsh 的拦截扩展点上。
- 这意味着 dsh 既可以“自己跑”，也可以“监听/增强 Claude Code 和 Codex”。

### 4.4 Python SDK

- `deepseek-harness-sdk`：通过 stdio JSON-RPC 驱动 dsh runtime。
- `deepseek-harness-runtime-bin`：预打包的 runtime 二进制文件与默认配置。
- 允许 Python 进程把 dsh 作为子进程启动并与之通信。

## 5. 如果将 dsh 作为 LoopDesk 的底层默认 Runtime

### 5.1 定位重心的变化

当前 LoopDesk 的架构定位是：

> 本地优先的个人 Loop 工作空间，跨 Claude Code / Codex / Trae / Gemini 等工具保持上下文、记忆、Artifacts 一致。

如果把 dsh 作为底层默认 runtime，则 LoopDesk 的定位会自然演变为：

> **一个以 dsh 为执行引擎的个人 Loop 控制面与状态层**，同时保留对其他外部 Agent 的适配能力。

这不是“替换”现有计划，而是“多一个 strong default”。

### 5.2 融入方式一：dsh 作为 LoopDesk 的本地 Agent 执行器

LoopDesk 启动一个 headless dsh 子进程作为默认执行器：

```text
LoopDesk CLI (Python)
  ├─ LOOP-STATE.json / registry / skills / memory
  ├─ scheduler / triage / maker-checker loop engine
  └─ spawns dsh --profile headless "task"
            ├─ dsh-base bundle (llm, tools, fs, shell, agent-loop)
            ├─ executes task with DeepSeek/OpenAI-compatible model
            ├─ writes SessionEvent log to local directory
            └─ returns final answer + event log
```

LoopDesk 负责：
- 把 maker 任务转化为 dsh 的 task prompt；
- 为 dsh 选择 model / bundle / patch；
- 通过 Python SDK 或 stdio JSON-RPC 读取 dsh 的 session log；
- 把运行结果、token 消耗、审计摘要写回 `LOOP-STATE.json`；
- 调用 checker（可以是另一个 dsh run，也可以是本地测试套件）验证结果。

dsh 负责：
- 实际的模型调用、工具执行、Agent Loop；
- 生成可审计的事件日志；
- 提供 headless / web 两种运行形态。

### 5.3 融入方式二：dsh 替换部分 MCP/ACP 适配层

LoopDesk 当前规划是 MCP-first、ACP-second 的适配层。如果默认使用 dsh，则：

- 对 DeepSeek 模型的调用可直接走 dsh 的 `ctx.llm` + `ctx.agentLoop`；
- 对 Claude Code / Codex 的桥接可通过 `dsh hooks-*` 插件实现；
- 对 Trae / Gemini 等其他工具仍可保留原有 MCP/ACP 适配器。

这样 LoopDesk 的适配层变成：**dsh 原生优先 + 外部 Agent 桥接兜底**。

### 5.4 融入方式三：LoopDesk 的 Loop Engine 作为 dsh 的 Manager/Checker 外层

借鉴 LongHorizon-Harness 的 Manager-Executor-Auditor 模式：

| LongHorizon-Harness | 在 dsh + LoopDesk 体系中的映射 |
|---------------------|-------------------------------|
| Manager | LoopDesk Loop Engine / Triage |
| Executor | dsh headless run（或一个 dsh Agent） |
| Auditor | LoopDesk Checker（另一个 dsh run 或本地测试） |

具体流程：

1. LoopDesk 根据 `LOOP-STATE.json` 决定下一步要做什么；
2. 把 bounded task 提交给 dsh headless 执行；
3. dsh 完成执行后，返回 session log + final answer；
4. LoopDesk Checker 启动第二个 dsh run（或本地脚本）对结果进行审计；
5. 审计通过则更新 `LOOP-STATE.json`，不通过则把失败证据注入下一轮。

这样 LoopDesk 不需要自己实现 Agent Loop，只需实现：
- 目标分解与状态管理；
- 与 dsh 的进程间通信；
- 结果验收与循环控制。

### 5.5 融入方式四：LoopDesk Web UI 作为 dsh Web UI 的包装层或替代层

dsh 自带 Web UI（`dsh web`）。LoopDesk 可以选择：

- **包装层方案**：LoopDesk 启动 `dsh web`，并把自己的状态面板叠加在 dsh 的 Web UI 之上或作为 iframe/插件嵌入；
- **替代层方案**：LoopDesk 自己实现 Web UI，但底层调用 dsh 的 `ctx.sessions` / `ctx.agents` / `ctx.tools` 事件；
- **混合方案**：LoopDesk 使用 dsh 作为运行时，但把 UI 重点放在多目标管理、跨工具状态同步、Loop Engineering 决策流上，而不是替代 dsh 的聊天界面。

## 6. 收益

### 6.1 获得一个完整的、可审计的 Agent Runtime

LoopDesk 不需要自己从零实现：
- Agent Loop；
- 工具注册与执行流水线；
- 模型适配与流式响应；
- 事件溯源会话日志；
- 子 Agent / 工作流。

### 6.2 插件化带来的可扩展性

- 需要支持新模型？写一个 `ctx.llm` 适配器插件；
- 需要支持新工具？写一个 `ctx.tools` 工具插件；
- 需要远程沙箱？把 `ctx.fs` / `ctx.subprocess` 指向远程 provider；
- 需要支持 Claude Code？启用 `hooks-claude-code` bridge。

### 6.3 与 DeepSeek 生态的天然亲和

如果 LoopDesk 的目标用户包括中文开发者或 DeepSeek 用户，dsh 会是一个开箱体验更好的默认运行时。

### 6.4 Headless 模式便于集成

`dsh --profile headless "task"` 可以像调用一个命令行工具一样被 LoopDesk 调用，符合 LoopDesk 本地优先、文件状态驱动的设计理念。

## 7. 风险与挑战

### 7.1 架构复杂度高

dsh 不是一个小工具，而是一个完整的 Cordis 插件生态。把它作为默认 runtime 意味着 LoopDesk 需要理解并维护：
- Cordis 插件树组合模型；
- dsh 的事件词汇表；
- bundle / profile / patch 的配置体系；
- TypeScript / Node.js 构建链路。

### 7.2 Developer Preview 的不稳定性

仓库明确声明：

> "THERE WILL BE COMPATIBILITY-BREAKING CHANGES."

LoopDesk 如果深度绑定 dsh，需要准备版本隔离和兼容性垫层。

### 7.3 与现有 MCP/ACP 优先策略的张力

LoopDesk 当前强调 MCP-first、ACP-second 的适配层。引入 dsh 后，可能出现两套抽象：
- dsh 的 `ctx.tools` / `ctx.subagents`；
- 外部 Agent 的 MCP / ACP。

需要明确边界：dsh 是“默认运行时”，MCP/ACP 是“外部工具桥接协议”。

### 7.4 运行时资源 heavier

相比 LoopX 的纯 Python 零依赖，或 LongHorizon-Harness 的轻量 Python harness，dsh 需要 Node.js ≥22.19、pnpm、以及 Cordis 插件构建流程。对“只想本地跑一个 JSON 文件控制 loop”的用户来说，这会增加首次安装门槛。

### 7.5 会话模型与 LOOP-STATE.json 的融合成本

dsh 的持久化核心是 append-only `SessionEvent` 日志，而 LoopDesk 的核心是 `LOOP-STATE.json`。两者需要建立稳定的同步规则：
- 哪些 dsh session events 需要映射到 LOOP-STATE？
- 如何从中提取 `verified progress`、`todos`、`gates`？
- 如何处理 dsh 的多会话（subagents、forks）与 LoopDesk 的 goal 模型？

## 8. 推荐的融合策略：分层隔离，逐步加深

建议 LoopDesk 采用 **"dsh 作为可选/默认运行时，但不侵入 LoopDesk 状态协议"** 的分层策略：

```text
┌─────────────────────────────────────────┐
│  LoopDesk 产品层                         │
│  - LOOP-STATE.json                      │
│  - skills / memory / artifacts          │
│  - triage / maker / checker / loop      │
│  - Web UI (management surface)          │
├─────────────────────────────────────────┤
│  LoopDesk Runtime 适配层                 │
│  - DshRuntimeDriver                     │
│  - McpRuntimeDriver                     │
│  - AcpRuntimeDriver                     │
│  - LocalScriptDriver                    │
├─────────────────────────────────────────┤
│  外部运行时                               │
│  - dsh (headless / web)                 │
│  - Claude Code / Codex / Trae / Gemini  │
│  - local shell / pytest / etc.          │
└─────────────────────────────────────────┘
```

### 8.1 第一步：dsh 作为可选 Runtime Driver

- 实现 `DshRuntimeDriver`，支持 `run(task, config)` 接口；
- 返回结构化的 `{status, stdout, stderr, session_log_path, token_usage}`；
- LoopDesk 仍默认使用现有 MCP/ACP 驱动；
- dsh 驱动作为实验性选项，配置文件中开启。

### 8.2 第二步：作为默认 Maker 运行时

- 对简单/中等复杂度的任务，默认用 dsh headless 执行；
- LoopDesk 负责把任务打包成 dsh prompt；
- 对需要与 Claude Code / Codex 紧密集成的场景，仍用 MCP/ACP 驱动；
- 通过 `LOOP-STATE.json` 记录哪个 goal 用哪个 driver 执行。

### 8.3 第三步：Checker 也走 dsh

- 用第二个 dsh run（带 auditor persona 的 bundle/patch）执行结果验收；
- 复用 LongHorizon-Harness 的 Manager-Executor-Auditor 思想；
- 逐步把 LoopDesk 的 checker 从本地脚本/测试升级为 dsh 驱动的结构化审计。

### 8.4 第四步：Web UI 与 dsh 会话同步

- LoopDesk Web UI 读取 dsh 的 session event log；
- 展示 Plan / Execute / Audit 三段式卡片；
- 支持人工 gate、instruction injection、run continuation。

## 9. 对 LoopDesk 决策层的建议

1. **不要把 dsh 视为“又一个外部 Agent”**，它是一个完整的 runtime。应该放在 Runtime Driver 抽象层，而不是 MCP/ACP 适配层。
2. **保持 LOOP-STATE.json 的协议独立性**。即使默认 runtime 是 dsh，LoopDesk 的产品协议也不应被 dsh 的 SessionEvent 词汇表绑架。两者之间建立明确的映射层。
3. **优先使用 headless 模式**。Web UI 模式是可选的、面向人机交互增强的；headless 才是 LoopDesk 自动化 loop 的正确集成形态。
4. **保留多 runtime 切换能力**。用户可能只用 DeepSeek、只用 Claude Code、或混用。LoopDesk 的竞争力在于统一的 Loop 控制面，而不是绑定单一 runtime。
5. **密切关注 dsh 的破坏性变更**。在 v1.0 之前，避免深度依赖内部 API；优先使用 Python SDK 和 headless CLI 契约。

## 10. 总结

DeepSeek Harness 是三个竞品中**架构最完整、野心最大、但也最重**的一个。它不是 LoopDesk 的直接替代品，而是 LoopDesk 可以吸纳的“强默认运行时”：

- 它可以补齐 LoopDesk 目前缺失的**本地 Agent Loop 执行引擎**；
- 它的事件溯源设计可以补充 `LOOP-STATE.json` 的审计与可恢复性；
- 它的 Cordis 插件生态可以大幅降低 LoopDesk 扩展新模型、新工具、新环境的成本。

但 LoopDesk 必须保持自己的核心身份：**LoopDesk 不是 dsh 的包装，而是一个跨 runtime 的 Loop 控制面**。dsh 只是其中一个强大且值得默认启用的 driver。
