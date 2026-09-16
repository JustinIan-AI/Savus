# Memory

LoopDesk memory 帮助 agent 召回持久上下文，而不必重放每段旧对话。用它承载稳定的偏好、可复用的项目事实、过往决策，以及应跨会话存活的笔记。

Memory 与 skills 不同。Skills 教 agent 如何做某件事；memory 存 agent 之后可能需要的有用事实与上下文。

## 该存什么

好的 memory 条目稳定且可复用：

- 用户偏好；
- 项目约定；
- 重复性输出格式；
- 重要仓库、目录或服务的名称；
- 用户希望复用的决策；
- 已完成任务的简要笔记。

避免把以下内容放进 memory：

- API key 或密钥；
- 无需长期召回的原始私有数据；
- 当前回合的一次性指令；
- 会污染未来检索的噪音堆；
- 应改为导出为会话记录的精确记录。

## 常用命令

查看 memory 健康：

```sh
loopdesk memory status
loopdesk memory status --deep
```

索引并列出 memory 来源：

```sh
loopdesk memory index
loopdesk memory list
```

搜索并查看 memory：

```sh
loopdesk memory search "release note format"
loopdesk memory show <path>
```

同时搜索此前的会话与 memory：

```sh
loopdesk memory search "deployment decision" --source all
```

## 自然对话用法

当某事应被记住时，自然提出：

```text
Remember that I prefer concise release notes with a risk section.
```

之后引用该偏好：

```text
Use my usual release-note format for this changelog.
```

当 memory 看似过时时，让 agent 显式搜索：

```text
Search memory for my release-note preferences before drafting this.
```

## 会话派生的 Memory

对于很长或很重要的会话，在归档、压缩或切换任务前，把会话状态刷新进 memory：

```sh
loopdesk memory flush-session <session-key>
```

当精确的旧措辞很重要时，使用会话导出：

```sh
loopdesk sessions export <session-key>
```

Memory 用于有用的召回；会话导出用于精确记录。

## 维护与修复

编辑 memory 文件或更改 memory 配置后，刷新索引：

```sh
loopdesk memory index --force
```

查看回退与修复使用面：

```sh
loopdesk memory raw-fallbacks list
loopdesk memory repair list
```

在诊断指示时，显示或修复降级的压缩 memory 记录：

```sh
loopdesk memory repair show --summary-id <id>
loopdesk memory repair run --summary-id <id>
```

## 最佳实践

- 保持条目简短且可溯源。
- 优先"为项目 Y 记住 X"，而非含糊的"记住这个"。
- 在假设 agent 遗忘前，先搜索 memory。
- 移除或修订过时偏好，而不是添加相互矛盾的条目。
- 不要把密钥放进 memory。
- 大型参考资料使用交付物或文件。

---

[文档索引](../README.md) · [产品指南](../../README.product.md) · [改进此页](../contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
