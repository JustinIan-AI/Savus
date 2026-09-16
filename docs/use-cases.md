# 使用场景与配方

当你知道想让 LoopDesk 做什么，但不确定先看哪篇功能指南时，用本页。

## 第一次成功运行

目标：安装 LoopDesk、配置一个 provider，并发出真实消息。

```sh
loopdesk onboard
loopdesk gateway run
```

然后打开：

```text
http://127.0.0.1:18791/control/
```

如果你更偏好终端：

```sh
loopdesk chat
```

接下来读：

- [`quickstart.md`](quickstart.md)
- [`web-ui.md`](web-ui.md)
- [`providers-and-models.md`](providers-and-models.md)

## 降低模型成本

目标：让简单工作走更便宜的模型，把更强的模型留给困难回合。

```sh
loopdesk configure router --router recommended
loopdesk cost --by-model
```

想检查路由与运行时行为时用 diagnostics：

```sh
loopdesk diagnostics on
```

接下来读：

- [`features/squilla-router.md`](features/squilla-router.md)
- [`features/tool-compression.md`](features/tool-compression.md)
- [`features/compaction-and-cache.md`](features/compaction-and-cache.md)

## 处理大型工具结果

目标：让 agent 查看日志、网页、表格、搜索结果或 diff，而不淹没模型上下文。

先做一次有界工作区运行：

```sh
loopdesk agent \
  --workspace /path/to/project \
  --workspace-strict \
  -m "Inspect the latest logs and summarize the actionable failures"
```

如果该回合太慢或太贵：

```sh
loopdesk cost
loopdesk diagnostics on
```

接下来读：

- [`features/tool-compression.md`](features/tool-compression.md)
- [`tools-and-sandbox.md`](tools-and-sandbox.md)
- [`troubleshooting.md`](troubleshooting.md)

## 构建可复用工作流

目标：把重复性工作变成可复用的技能或 meta-skill。

查找已有技能：

```sh
loopdesk skills search report
loopdesk skills view <skill-name>
```

运行前先检查 meta-skill：

```sh
loopdesk skills inspect <meta-skill-name>
```

查看历史 meta-skill 运行：

```sh
loopdesk skills meta runs list
loopdesk skills meta runs show <run-id>
```

接下来读：

- [`features/skills.md`](features/skills.md)
- [`features/meta-skills.md`](features/meta-skills.md)
- [`artifacts-and-media.md`](artifacts-and-media.md)

## 记住有用的上下文

目标：保存偏好、项目笔记或可复用任务上下文，让后续回合能找到。

```sh
loopdesk memory status
loopdesk memory search "project preference"
loopdesk memory list
```

查看已存储的 memory 文件：

```sh
loopdesk memory show <path>
```

接下来读：

- [`features/memory.md`](features/memory.md)
- [`features/compaction-and-cache.md`](features/compaction-and-cache.md)

## 连接消息渠道

目标：在受支持的消息面上使用 LoopDesk，同时让 gateway 保持本地控制点。

```sh
loopdesk channels types
loopdesk channels describe telegram
loopdesk channels add telegram --name personal
loopdesk gateway restart
loopdesk channels status personal --json
```

接下来读：

- [`channels.md`](channels.md)
- [`configuration.md`](configuration.md)
- [`tools-and-sandbox.md`](tools-and-sandbox.md)

## 计划重复性工作

目标：让 LoopDesk 按周期运行任务，而无需手动打开对话。

```sh
loopdesk cron add \
  --every 1h \
  --text "Summarize important project updates" \
  --name hourly-project-check
```

查看作业与运行：

```sh
loopdesk cron list
loopdesk cron status <job-id>
loopdesk cron runs <job-id>
```

接下来读：

- [`operations.md`](operations.md)
- [`channels.md`](channels.md)
- [`scheduling.md`](scheduling.md)

## 发布用户可见的交付物

目标：让 agent 产出可查看、可分享的文件、报告、幻灯片、HTML 页面、图片或媒体资产。

```sh
loopdesk agent -m "Create a short HTML report from the current notes"
loopdesk sessions export <session-key>
```

接下来读：

- [`artifacts-and-media.md`](artifacts-and-media.md)
- [`features/skills.md`](features/skills.md)
- [`features/meta-skills.md`](features/meta-skills.md)

## 从坏运行中恢复

目标：弄清发生了什么、降低风险，并安全继续。

```sh
loopdesk doctor
loopdesk gateway status
loopdesk sessions show <session-key>
loopdesk cost
```

若某个工具被拒绝，或 agent 权限过大：

```sh
loopdesk sandbox status
loopdesk agent --permissions restricted -m "Read only"
```

接下来读：

- [`troubleshooting.md`](troubleshooting.md)
- [`tools-and-sandbox.md`](tools-and-sandbox.md)
- [`approvals-and-permissions.md`](approvals-and-permissions.md)
- [`diagnostics-and-replay.md`](diagnostics-and-replay.md)
- [`operations.md`](operations.md)

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
