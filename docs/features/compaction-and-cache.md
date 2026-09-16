# 压缩与缓存连续性

长 agent 会话需要上下文管理。LoopDesk 使用压缩、有界历史、工具结果投影与缓存感知的 prompt 放置，让长任务持续推进。

压缩与 memory 不同。Memory 是持久召回；压缩是活跃会话的连续性工具。

## 压缩做什么

当会话历史接近配置的上下文预算时，LoopDesk 可把较早的记录条目压缩为持久摘要，并保留近期尾部为活跃。

目标是保留：

- 用户目标；
- 当前状态；
- 未完成步骤；
- 已变更的文件与交付物；
- 已知失败；
- 重要工具结果；
- 下一步动作。

压缩并不保证每个旧字词都仍对模型可见。当精确的历史文本很重要时，请导出会话或保存文件。

## 用户可见的生命周期

取决于使用面与触发条件，用户可能看到：

- 压缩已开始；
- 压缩已跳过；
- 压缩已完成；
- 压缩失败。

无需压缩时，LoopDesk 使用这条稳定消息：

```text
Already within context budget; no compact was applied
```

该消息是一次 no-op，不是失败。

## 何时手动压缩

手动压缩适用于：

- 会话很长，且你即将开始新阶段；
- 前一个工具密集的回合产生了大量上下文；
- UI 提示上下文压力；
- 你希望下一个答案聚焦当前状态，而非整段记录。

当 runtime 说会话已在预算内时，避免重复压缩。

## 被动压缩

当 LoopDesk 在 agent 工作之前或期间检测到上下文压力时，可能发生被动压缩。确切的触发取决于模型上下文限制、已配置预算、当前历史与工具输出大小。

如果被动压缩失败，最安全的用户响应通常是：

1. 让当前回合干净地结束或失败；
2. 若精确历史很重要，导出会话；
3. 用更窄的请求重试，或手动保存关键交付物；
4. 若失败重复出现，开启诊断。

## Prompt 缓存连续性

当稳定的 prompt 部分保持稳定时，prompt 缓存效果最好。LoopDesk 尝试保持：

- 稳定的 system prompt 与工具定义靠前；
- 当前请求、易变的运行时上下文、检索到的历史与工具结果靠近尾部；
- 在模型/provider 切换可能影响缓存连续性时，通过诊断使其可见。

缓存连续性是尽力而为。路由、工具、附件、provider 变化，或大量新上下文，都可能降低缓存复用。

## 相关命令与使用面

手动压缩主要在对话与 Web UI 流程中呈现。检查与恢复：

```sh
loopdesk sessions show <session-key>
loopdesk sessions export <session-key>
loopdesk diagnostics on
```

与降级压缩记录相关的 memory 修复使用面：

```sh
loopdesk memory repair list
loopdesk memory repair show --summary-id <id>
loopdesk memory raw-fallbacks list
```

## 最佳实践

- 把重要的最终交付物放进文件或已发布交付物。
- 用 memory 承载持久偏好与可复用项目事实。
- 用会话导出承载精确的旧记录。
- 在超长会话的新阶段之前使用手动压缩。
- 不要反复压缩一个很短或已在预算内的会话。

---

[文档索引](../README.md) · [产品指南](../../README.product.md) · [改进此页](../contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
