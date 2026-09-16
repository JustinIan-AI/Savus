# Web UI

LoopDesk Web UI 是本地循环工作区的控制台。它采用 **Codex 三栏布局**——左栏导航、中栏主工作区、右栏任务上下文，并**默认进入任务看板**，支持按项目切换。

完整的页面与交互契约见 [`plans/loopdesk-webui-design-spec.md`](plans/loopdesk-webui-design-spec.md)（v2.0）；需求见 [`prd/loopdesk-prd-v2.0.zh.md`](prd/loopdesk-prd-v2.0.zh.md) §9.11。

## 启动 Web UI

前台运行 gateway：

```sh
loopdesk gateway run
```

打开：

```text
http://127.0.0.1:18791/control/
```

或启动托管的后台 gateway：

```sh
loopdesk gateway start --json
loopdesk gateway status
```

默认 gateway 绑定 `127.0.0.1`，以保证安全。

gateway 生命周期、host/port 与暴露方式见 [`gateway.md`](gateway.md)。

## 布局

| 区域 | 用途 |
| --- | --- |
| 左栏 — 导航 | 项目切换器、按状态分组的任务列表，以及三个主入口：任务 / 资产市场 / 设置。 |
| 中栏 — 主工作区 | **任务看板**（默认落地）；点开任务后显示任务详情。 |
| 右栏 — 上下文面板 | 所选任务的上下文：进度、成本/预算、审批、变更 diff、Agent/会话、证据。可折叠。 |
| 顶部栏 | 项目名、搜索、`+ 新建任务`、设置图标。 |

一级导航刻意只保留三个入口——**任务**、**资产市场**、**设置**。其余能力（Agents、Sessions、Skills、Memory、Logs、Providers、MCP、团队、模板、用量等）全部收进设置，主界面始终以任务为中心。

## 任务看板（默认落地）

- 四列（**等宽**，四列在 840px 中列内全部可见）：**待办**、**进行中**、**评审中**、**已完成**。
- **列 ≠ 门**：人工把关的**审批门（operator gate）**不是第五列，而是右栏的三级折叠区块——"评审中"是状态，"审批门"是卡在该状态里的动作。
- 任务卡显示：标题、项目、模板、Agent、状态、成本，以及建议的下一步。
- 用左栏的**项目切换器**切换看板；切换项目即切换整个工作区上下文。
- 支持按项目、状态、模板、Agent 筛选与搜索。

用 `+ 新建任务` 创建任务：

1. 选择归属项目（缺省为当前项目）。
2. 选择模板 —— `issue-fix`、`pr-commit`、`auto-research`，或自由形式。
3. 用一句话描述任务并启动。

## 任务详情

点开任务卡后，中栏显示该任务的单一连续工作视图：

- 流式输出；
- 工具调用卡；
- 交付物卡；
- 进度（分诊 → 执行 → 检查 → 完成）；
- `继续`（恢复被中断的工作）与手动 `/compact`（run 进行中时禁用）；
- 可用时显示按轮用量与节省信息；
- checkpoint / rewind 入口，基于 durable event log。

## 上下文面板（右栏）

右栏承载所选任务更深、更技术化的状态：

- 任务概览（标题、项目、模板、Agent、发起时间）；
- 进度明细（六阶段，默认折叠为简化视图）；
- 成本与预算，含超预算告警；
- 审批（approve / deny，集中处理）；
- 变更 diff，支持逐 hunk accept / reject 与内联注释；
- Agent / 会话状态与会话恢复；
- 证据 / 验证（validation receipt、integrity 徽标），按需展开；
- 交接（handoff）给其他 agent、成员或工具。

界面上这些内容**归并为三组 + 一条尾部**，每组右侧标注它的**生成依据**：

| 组 | 生成依据 | 收纳 |
| --- | --- | --- |
| 任务状态 | `card.state` | 概览 · 六阶段进度 · 处置·路由/验证 |
| 详情 | `card.detail` | Handoff · Agent/会话 · 审批门 · 证据 · diff |
| 交付物清单 | `card.state` | 外链（真实 URL）+ 内链（锚定详情页区块） |
| 尾部 · 成本/配额 | `card.state` | 成本与预算 |

- 看板**单击卡片 = 选中**，右栏随之重算（**不**跳转）；进入任务详情走右栏顶部「查看详情 →」或清单内链。
- 规范细节见 [`plans/loopdesk-webui-design-spec.md`](plans/loopdesk-webui-design-spec.md) §7.1。

## 团队资产市场

从左栏打开。资产市场像 Codex / VS Code 的扩展市场一样工作：

- 浏览团队 AI 资产：**rules**、**commands**、**skills**、**MCP**；
- **默认按当前项目筛选**；
- **个人用户为只读**——可浏览、可看到已启用项，但没有编辑入口；
- owner / admin 可将资产安装到项目、下发给成员、锁定版本、回滚；
- 资产详情展示版本历史、diff、来源 git 与适用范围。

## 设置

点击顶部栏（或左栏）的设置图标进入设置界面，采用 Codex 风格布局：左侧分类列表 + 右侧表单。

| 分类 | 内容 |
| --- | --- |
| 通用 | 语言、主题、启动视图、默认项目。 |
| 模型与 Provider | 渠道、模型、能力、限流、用量。 |
| Agent | Agent 注册表（runtime、指令、env、并发）。 |
| 连接器（MCP） | JIRA / Plane / Confluence / GitHub 的启用、重试、审计。 |
| 审批与安全 | 权限模式、path denylist、沙箱、secrets。 |
| 用量与额度 | 成本 rollup、预算、团队额度。 |
| 团队 | 成员、角色、额度池、分发范围。 |
| 模板 | 长任务模板（内置 / 自定义）。 |
| 外观 | Light / Dark、密度、图标。 |
| 高级 | 网关、网络、诊断、日志、导出。 |

## 审批

部分工具需要确认。审批队列为操作者提供一个持久的位置来 approve 或 deny 敏感动作，而不是把决策埋在对话文本里。在 Web UI 中做出的决策会写入与 CLI、IM 相同的本地审计流。

在以下情况使用审批：

- agent 想要写文件；
- 命令需要提权；
- 外部动作（工单、PR、渠道）需要人工确认；
- 无人值守自动化应在高风险操作前暂停。

## 手动压缩

长会话可从任务中压缩。如果无需压缩，界面会提示：

```text
Already within context budget; no compact was applied
```

如果压缩正在进行，请等待其终态再假定下一条消息已带上压缩后的上下文。详见 [`features/compaction-and-cache.md`](features/compaction-and-cache.md)。

## 交付物

当 agent 发布文件时，界面会显示交付物卡。交付物卡用于：

- 生成的 HTML 原型；
- 报告与简报；
- 导出的数据文件；
- PDF、幻灯片、图片及其他生成产物。

渠道投递限制与交付物恢复见 [`artifacts-and-media.md`](artifacts-and-media.md)。

## 日志与诊断

本地诊断：

```sh
loopdesk diagnostics on
loopdesk gateway status
loopdesk doctor
```

使用「设置 → 高级」中的日志与健康视图，关联 provider 就绪状态、连接器状态、任务状态与用户可见错误。

## 安全

Web UI 默认仅本地。若将 gateway 绑定到公网接口，请先配置 token 认证与网络控制：

```sh
loopdesk gateway run --listen 0.0.0.0 --port 18791
```

不要把未认证的 gateway 暴露到公网。

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
