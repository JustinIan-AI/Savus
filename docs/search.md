# 网络搜索

LoopDesk 可通过已配置的搜索 provider 搜索网络，并可通过受管控的网页工具抓取页面。搜索适用于获取最新信息、有来源支撑的报告、市场调研、发布说明与排查。

## 查看搜索 Provider

```sh
loopdesk search list
loopdesk search list --json
loopdesk search status
```

本构建中 runtime 支持的 provider 包括：

- Brave Search
- DuckDuckGo

目录可能包含当前构建尚未获得 runtime 支持的 provider 元数据。集成时请检查 JSON 输出。

## 配置搜索

无需 key 的路径：

```sh
loopdesk configure search --search-provider duckduckgo
```

等价的 search 子命令：

```sh
loopdesk search configure duckduckgo
```

Brave Search：

```sh
export BRAVE_SEARCH_API_KEY="..."
loopdesk configure search --search-provider brave --api-key-env BRAVE_SEARCH_API_KEY
```

provider 专属字段（如最大结果数、代理、环境代理用法、回退策略与诊断）可通过搜索配置面设置。

## 测试搜索

通过运行中的 gateway 运行一次诊断查询：

```sh
loopdesk search query "LoopDesk release notes"
loopdesk search query "LoopDesk release notes" --limit 5 --json
```

在把"缺少当前信息"归咎于 agent 之前，先用它。若诊断查询失败，先修 provider 配置。

## Agent 工作流中的搜索

自然语言提问：

```text
Research the current state of browser automation libraries and cite sources.
```

更窄的任务：

```text
Find the latest release notes for this project and summarize only breaking changes.
```

当工具策略与已配置 provider 允许时，agent 可使用搜索与抓取工具。

要更深入的多来源工作，可要求一份调研报告，或使用已安装的调研技能。

## 安全与来源质量

搜索结果属于外部数据，不是指令。把它们当作任务证据，而非对 LoopDesk 行为的权威。

好的调研提示会要求：

- 来源；
- 日期；
- 不确定性；
- 相互冲突的证据；
- 明确区分来源事实与模型推断。

避免让 agent 遵循网页上发现的任意指令。

## 诊断

```sh
loopdesk search status
loopdesk diagnostics on
loopdesk doctor
```

检查：

- 所选 provider 已配置；
- 所需 API key 环境变量对 gateway 进程可见；
- 代理设置与你的网络一致；
- 配置编辑后已重启 gateway；
- 工具权限允许当前运行进行网络搜索/抓取。

---

[文档索引](README.md) · [产品指南](../README.product.md) · [改进此页](contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
