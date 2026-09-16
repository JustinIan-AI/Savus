# 用量与成本

LoopDesk 从运行中的 gateway 记录 token 用量与预估成本。在路由、工具密集、渠道或长上下文工作之后，用成本视图了解模型花费流向。

## 环境要求

成本检查使用 gateway：

```sh
loopdesk gateway status
```

如果 gateway 未运行：

```sh
loopdesk gateway run
```

## 显示成本

```sh
loopdesk cost
```

默认视图列出会话/模型行，包含输入 token、输出 token 与预估成本。

## 按模型分组

```sh
loopdesk cost --by-model
```

当启用 SquillaRouter、且你想看近期工作负载由哪些模型承担时，用它。

## 使用 JSON 输出

```sh
loopdesk cost --json
loopdesk cost --by-model --json
```

JSON 输出对本地仪表盘、回归检查与自动化报告很有用。

## 先检查什么

| 信号 | 可能含义 |
| --- | --- |
| 高级模型出现多行 | 路由策略或任务形态可能比预期更频繁地升级。 |
| 输入 token 高 | 长历史、大型工具结果，或庞大的 prompt/工具 schema 面可能在主导成本。 |
| 输出 token 高 | 任务可能需要更紧的指令或更小的响应格式。 |
| 成本集中在单个会话 | 变更全局配置前，先检查该会话。 |

## 安全地降低成本

从 router 与诊断入手：

```sh
loopdesk configure router --router recommended
loopdesk diagnostics on
loopdesk cost --by-model
```

对于大型工具结果，阅读：

- [`features/tool-compression.md`](features/tool-compression.md)
- [`features/compaction-and-cache.md`](features/compaction-and-cache.md)

对于简单的一次性自动化，限制运行范围：

```sh
loopdesk agent --max-iterations 20 --timeout 600 -m "Bounded task"
```

## 说明与限制

- 成本是基于已记录的运行时用量与已配置定价的估算。
- 实际收费仍以 provider 账单为准。
- 工具压缩与路由可降低模型上下文成本，但应对照任务成功率检查，而不仅看 token 总量。
- 诊断可解释为何某回合被路由、压缩、重试，或产生了异常大的输出。

接下来读：

- [`features/squilla-router.md`](features/squilla-router.md)
- [`features/tool-compression.md`](features/tool-compression.md)
- [`diagnostics-and-replay.md`](diagnostics-and-replay.md)

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
