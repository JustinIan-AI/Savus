# SquillaRouter

SquillaRouter 是 LoopDesk 的本地模型路由层。它帮助 agent 为每个回合选择合适的模型档位，使日常事务不必总是跑在最昂贵的模型上。

当你想启用路由、了解它改变了什么，或判断某次运行是否更适合固定的 provider/模型时，用本页。

## 为什么用它

SquillaRouter 适用于你想要：

- 让简单对话、编辑、摘要与日常工具工作更便宜；
- 把更强的模型留给困难推理、恢复与长任务；
- 让同一个 LoopDesk 工作流跨 provider 配置路由；
- 本地做路由决策，而不必仅为选择模型就把 prompt 发给独立的外部分类器。

它不是必需的。LoopDesk 也可运行在直接单模型模式。

## 启用路由

推荐的首次配置：

```sh
loopdesk onboard --router recommended
```

重新配置既有安装：

```sh
loopdesk configure router --router recommended
```

使用 OpenRouter 混合默认值：

```sh
loopdesk configure router --router openrouter-mix
```

禁用路由并直接使用已配置的 provider/模型：

```sh
loopdesk configure router --router disabled
```

## 查看 Provider 支持

检查你安装中可用的 provider 目录：

```sh
loopdesk providers list
```

如果 gateway 在运行，查看运行时 provider 健康：

```sh
loopdesk providers status
```

Router 支持的配置取决于已安装的 LoopDesk 版本、可选依赖与已配置的 provider 凭据。常见配置包括 OpenRouter、OpenAI、DeepSeek、Gemini、DashScope、Moonshot、Volcengine、Zhipu，以及本地目录暴露的兼容 provider 档位。

## Router 会影响什么

取决于配置，SquillaRouter 可能影响：

- 选中的模型档位；
- 直接模型回退；
- 推理级别；
- 响应策略；
- 支持图片的模型选择；
- 近期更高档位回合的缓存连续性保护。

确切的决策可通过运行时元数据与诊断使用面获取。当你需要理解某回合为何被路由到特定模型时，开启诊断：

```sh
loopdesk diagnostics on
```

## 推荐运行模式

| 目标 | 建议模式 |
| --- | --- |
| 常规个人 agent 使用 | `recommended` |
| 通过 OpenRouter 做多 provider 成本优化 | `openrouter-mix` |
| Provider 评估、账单审计或可复现基准运行 | `disabled` |
| 调试某个 provider 专属行为 | `disabled` |

日常使用从 `recommended` 开始。只有当你测试的就是模型选择本身时，才禁用路由。

## 示例请求

对路由友好的好请求描述结果，而非档位：

```text
Summarize this long issue thread and list the decision points.
```

```text
Review my current diff and point out the highest-risk changes.
```

除非在调试，否则避免让 router 表现得像手动模型选择器：

```text
Use exactly this one model for every turn.
```

要固定模型，请改用直接路由配置。

## 排查

如果路由似乎不生效：

1. 确认 router 已启用：

   ```sh
   loopdesk config get router.enabled
   loopdesk config get llm.provider
   ```

2. 检查 provider 就绪情况：

   ```sh
   loopdesk providers status
   loopdesk doctor
   ```

3. 如果 SquillaRouter 的可选依赖缺失，LoopDesk 仍可用直接单模型路由运行。在 Windows 上，ONNX Runtime 可能需要 Visual C++ Redistributable。

4. 如果某次运行需要确定性的模型行为，请禁用路由：

   ```sh
   loopdesk configure router --router disabled
   ```

---

[文档索引](../README.md) · [产品指南](../../README.product.md) · [改进此页](../contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
