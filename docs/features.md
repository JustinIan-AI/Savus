# 功能目录

LoopDesk 把个人 agent runtime 与模型路由、工具、memory、渠道、计划任务和可复用技能结合在一起。

## 产品使用面

| 使用面 | 用途 |
| --- | --- |
| Web UI | 本地控制台：配置、对话会话、审批、日志、渠道与用量视图。 |
| CLI chat | 交互式终端 agent 工作。 |
| CLI agent | 单回合自动化、类 CI 运行与基准测试式调用。 |
| Gateway RPC | 面向 Web UI、CLI 客户端、渠道与外部客户端的本地服务器面。 |
| Channels | Telegram、Slack、飞书/Lark、Discord、钉钉、WeCom、Matrix、QQ、终端与 websocket 风格集成。 |

## 特色功能

### SquillaRouter

用于模型档位选择的本地路由。它的设计目标是让简单回合保持便宜，把昂贵模型留给真正需要的工作。

阅读：[`features/squilla-router.md`](features/squilla-router.md)

### 工具压缩（Tool Compression）

大型工具输出会被投影成紧凑的、provider 可见的预览，同时运行时可在带外保留更丰富的原始结果。

阅读：[`features/tool-compression.md`](features/tool-compression.md)

### Meta-Skill

可重复的多步工作流可以被表示为技能，并可被检查、提议、重放与复用。

阅读：[`features/meta-skills.md`](features/meta-skills.md) 与 [`features/meta-skill-user-guide.md`](features/meta-skill-user-guide.md)

### Memory

durable memory 让 LoopDesk 能召回有用的用户偏好、项目笔记与过往任务轨迹，而无需把每段旧记录都塞进当前 prompt。

阅读：[`features/memory.md`](features/memory.md)

### 技能（Skills）

技能打包任务专用的指导与脚本，使 agent 只在任务需要时加载正确的操作指令。

阅读：[`features/skills.md`](features/skills.md)

### 压缩与缓存连续性

长会话可以压缩旧上下文、保留近期任务状态，并上报压缩生命周期事件。

阅读：[`features/compaction-and-cache.md`](features/compaction-and-cache.md)

### 会话与 Durable Agent

会话保留对话连续性、导出与运行中任务控制。Durable agent 为重复性工作流提供具名身份与默认值。

阅读：[`sessions.md`](sessions.md) 与 [`agents.md`](agents.md)

### 用量、诊断与权限

用量报告解释近期的模型花费。诊断与重放帮助在回合运行后检查它。权限与审批控制让工具访问与任务相匹配。

阅读：[`usage-and-cost.md`](usage-and-cost.md)、[`diagnostics-and-replay.md`](diagnostics-and-replay.md) 与 [`approvals-and-permissions.md`](approvals-and-permissions.md)

## 核心运行时能力

- 跨 Web UI、CLI 与渠道的统一 `TurnRunner` 路径。
- 面向 OpenAI 兼容 API、Anthropic、Ollama 及其他已配置后端的 provider 抽象。
- 流式响应、工具调用、重试、审批、交付物与最终用量核算。
- durable 会话存储，包含 transcript、摘要、上下文状态与重放支持。
- 每 agent 工作区与 durable agent 条目。
- 用于有界委派的 subagent 支持。

## 工具

LoopDesk 内置的工具用于：

- 文件系统读/写/编辑/列目录/glob/grep。
- Shell 命令、后台进程与代码执行。
- Git status、diff、log 与 commit。
- 网络搜索与网页抓取。
- Memory 搜索/保存/获取/删除。
- 会话搜索、会话 spawn/send/history/status。
- 交付物发布。
- 图片生成、PDF、TTS 与媒体工作流。
- 通过内置技能进行表格、PPTX、DOCX、CSV 与 PDF 创作。
- 飞书/Lark 文档、聊天、云盘、wiki、权限与媒体上传。
- Cron 与 gateway 管理。
- 技能的列出、查看、创建、编辑、安装依赖与 meta-skill 调用。

阅读：[`tools-and-sandbox.md`](tools-and-sandbox.md)

## 技能

内置的面向用户技能包括：

- `deep-research`
- `summarize`
- `memory`
- `cron`
- `github`
- `docx`
- `pptx`
- `xlsx`
- `pdf-toolkit`
- `html-to-pdf`
- `multi-search-engine`
- `weather`
- `tmux`
- `sub-agent`
- `skill-creator`

保留的内置 MetaSkill 包括 `meta-competitive-intel`、`meta-daily-operator-brief`、`meta-document-to-decision`、`meta-job-search-pipeline`、`meta-kid-project-planner`、`meta-paper-write`、`meta-skill-creator` 与 `meta-web-research-to-report`。开发树中可能存在实验性 MetaSkill，但它们不作为稳定的内置产品能力呈现。

阅读：[`features/skills.md`](features/skills.md)

## 计划任务

`cron` 命令组管理 LoopDesk 的计划运行：

```sh
loopdesk cron list
loopdesk cron add \
  --every 1h \
  --text "Summarize important project updates" \
  --name hourly-project-check
loopdesk cron status <job-id>
loopdesk cron run <job-id>
loopdesk cron runs <job-id>
```

计划作业可按配置通过渠道或 webhook 等已配置的使用面投递工作。

阅读：[`scheduling.md`](scheduling.md)

## 迁移

LoopDesk 可从 OpenClaw 与 Hermes Agent 导入兼容状态：

```sh
loopdesk migrate openclaw --json
loopdesk migrate openclaw --apply
loopdesk migrate hermes --json
loopdesk migrate hermes --apply
```

阅读：[`../MIGRATION.md`](../MIGRATION.md)

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
