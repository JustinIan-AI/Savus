# 诊断与重放

诊断与重放帮助解释 LoopDesk 回合期间发生了什么。当结果出乎意料、缓慢、昂贵、被中断，或仅凭对话记录难以复现时，使用它们。

## 诊断

诊断是通过 gateway 暴露的运行时日志开关。

检查状态：

```sh
loopdesk diagnostics status
loopdesk diagnostics status --json
```

启用诊断：

```sh
loopdesk diagnostics on
```

当维护者要求更深入的 provider 请求证据时，启用原始回合调用抓取：

```sh
loopdesk diagnostics on --raw
```

收集到足够证据后关闭诊断：

```sh
loopdesk diagnostics off
```

## 何时使用诊断

诊断适用于：

- provider 重试、超时或空响应；
- SquillaRouter 模型决策；
- prompt-cache 或缓存断裂调查；
- 压缩生命周期事件；
- 大型工具结果压缩；
- 渠道投递失败；
- 异常高的成本或延迟。

不要长期开启原始诊断。原始抓取可能包含私有 prompt、工具输出、本地路径或 provider 可见内容。

## 重放已记录的回合

重放从决策日志读取已记录的回合，并打印人类可读的记录。它是只读的：不会重新运行工具。

```sh
loopdesk replay --session <session-key> --turn <turn-id>
```

在以下情况使用重放：

- 对话已继续，但你需要检查更早的回合；
- 问题报告需要简洁的复现证据；
- 你想把记录输出与诊断、成本数据对照。

## 重放与会话配合

先找到会话：

```sh
loopdesk sessions list
loopdesk sessions show <session-key>
```

若精确上下文很重要，导出完整会话：

```sh
loopdesk sessions export <session-key> --output session.md
```

## 安全分享

公开分享诊断、重放输出或导出会话之前，请移除：

- provider key 与 bearer token；
- 私有本地路径；
- 私有渠道标识；
- 不应公开的客户、项目或账号名称；
- 含机密内容的原始 provider prompt 或工具输出。

接下来读：

- [`sessions.md`](sessions.md)
- [`usage-and-cost.md`](usage-and-cost.md)
- [`troubleshooting.md`](troubleshooting.md)

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
