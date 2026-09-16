# Durable Agent

LoopDesk agent 是具名的运行时配置。当不同工作流需要不同默认值时（例如研究、写作工作区，或面向渠道的助手），使用它们。

内置的 `main` agent 始终可用。额外的 agent 通过 `loopdesk agents` 配置。

## 何时创建 Agent

在需要为以下用途提供稳定身份时，创建 durable agent：

- 专用工作区；
- 默认模型选择；
- 独立的渠道或自动化目标；
- 重复性任务配置；
- 专门的助手名称与描述。

不要为每次对话都新建 agent。普通对话连续性请使用会话。

## 列出 Agent

```sh
loopdesk agents list
loopdesk agents list --json
```

## 添加 Agent

```sh
loopdesk agents add research \
  --name Research \
  --description "Research and synthesis workspace" \
  --workspace /path/to/research \
  --model gpt-5.4-mini
```

Agent 变更会写入配置。依赖更新后的 agent 列表前，先重启 gateway：

```sh
loopdesk gateway restart
```

## 与会话一起使用 Agent

按 agent 过滤会话：

```sh
loopdesk sessions list --agent research
```

为某个 agent 创建计划任务：

```sh
loopdesk cron add \
  --agent research \
  --every 1h \
  --text "Summarize new research notes" \
  --name research-hourly-summary
```

取决于渠道配置，渠道也可把入站消息路由到已配置的 agent。

## 删除 Agent

```sh
loopdesk agents delete research
loopdesk agents delete research --force
```

删除 agent 条目不会触碰工作区文件与状态。只有在确认不再需要时，才单独清理它们。

## Agent vs Session vs Skill

| 概念 | 用途 |
| --- | --- |
| Agent | 某工作流的 durable 身份与默认值。 |
| Session | 对话历史与活跃任务的连续性。 |
| Skill | 可复用的工作流指导或工具例程。 |
| Meta-skill | 由多个技能步骤组合而成的工作流。 |

接下来读：

- [`sessions.md`](sessions.md)
- [`features/skills.md`](features/skills.md)
- [`features/meta-skills.md`](features/meta-skills.md)
- [`channels.md`](channels.md)

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
