# 工具压缩

LoopDesk agent 会使用工具。工具调用可能产生大输出：命令日志、JSON、网页、搜索结果、diff、文件内容、表格与交付物。工具压缩让这些输出保持有用，同时不让它们吃掉整个模型上下文。

这是一个面向用户的上下文管理功能。它不改变工具返回了什么，只改变该结果中有多少被展示给模型用于下一步。

## 为什么重要

工具压缩适用于：

- 命令打印了很长的日志；
- 网页或搜索结果太长，不适合放进有用的 prompt；
- 文件读取返回的文本超过下一步所需；
- 长会话接近上下文预算；
- 你希望在保留原始结果的同时，让模型看到紧凑预览。

没有压缩时，一个大型工具结果就可能挤掉用户目标、近期对话与下一步动作。

## 用户可能看到什么

在很长或工具密集的回合中，模型可见结果可能包含：

- 一个紧凑预览；
- 一条结果被截短的说明；
- 一个用于带外存储结果的 `tool_result_handle`；
- 启用诊断时的预估 token 节省诊断信息。

这是预期的。它意味着 LoopDesk 在保护活跃上下文窗口。

## 产品级模型

LoopDesk 区分两种视图：

| 视图 | 目的 |
| --- | --- |
| 运行时视图 | LoopDesk 可保留、检查或导出的持久结果。 |
| Provider 视图 | 回传给模型用于下一步推理的有界文本。 |

agent 可从关键事实继续，同时大型原始材料在配置允许时仍可通过文件、会话导出、诊断或工具结果句柄获取。

## 压缩模式

取决于配置与工具输出形态，LoopDesk 支持若干压缩风格。

| 模式 | 最适合 | 权衡 |
| --- | --- | --- |
| `truncate` | 快速确定性的预览。 | 可能省略有用的中段。 |
| `summarize` | 受益于语义摘要的较慢/后台工作流。 | 增加一次模型调用，应选择性开启。 |
| Structured projection（结构化投影） | 日志、diff、JSON、表格与已知工具形态。 | 取决于该输出类型的 reducer 覆盖。 |

多数用户应保持默认行为，只在工作流仍然过大时才使用诊断。

## 如何应对大输出

请求聚焦的后续读取：

```text
Look at the failing test names and the last 80 lines of the log.
```

优先使用句柄、路径与摘要：

```text
Use the compacted result to identify likely causes, then read the exact file
sections you need.
```

除非精确文本就是交付物，否则避免让 agent 粘贴超大结果的每一行：

```text
Paste the entire 50,000-line log into chat.
```

## 检查与调试

当你需要理解上下文增长时，开启诊断：

```sh
loopdesk diagnostics on
```

当需要在对话使用面之外检查持久历史时，导出会话：

```sh
loopdesk sessions export <session-key>
```

在一次大型工具密集运行后，查看成本与用量：

```sh
loopdesk cost
```

## 最佳实践

- 保持工具请求具体。
- 只请求能回答问题的最小文件范围、日志尾部或 JSON 字段。
- 大型交付物使用交付物功能，而非把一切塞进对话。
- 审计与调试使用会话导出。
- 把工具压缩当作连续性功能，而非存储重要文件的替代品。

---

[文档索引](../README.md) · [产品指南](../../README.product.md) · [改进此页](../contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
