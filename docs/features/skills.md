# 技能（Skills）

技能是任务专用的指令包与脚本。它们让 LoopDesk 只在任务需要时加载相关指导，而不是把所有可能的指令都塞进每个 prompt。

技能与 memory 不同。Memory 存事实；技能描述可重复的工作方式。

## 技能用于什么

技能适用于可重复的工作模式，例如：

- 深度调研；
- 摘要；
- GitHub 与 PR 工作流；
- 文档生成；
- 表格、幻灯片、PDF 与 DOCX 工作；
- 网络搜索；
- 天气查询；
- 终端或 tmux 监控；
- subagent 委派；
- 技能创建与评审。

如果工作流组合了多个技能或可复用的多步计划，请使用 meta-skill。

## 发现已安装技能

列出当前安装中可用的技能：

```sh
loopdesk skills list
```

查看某个技能：

```sh
loopdesk skills view <skill-name>
```

搜索社区来源：

```sh
loopdesk skills search pdf
```

当可选依赖缺失，或某技能被刻意设为仅演示时，部分技能可能不可用。`skills list` 是你当前安装的事实源。

## 安装、更新与移除技能

安装受管技能：

```sh
loopdesk skills install <skill-name>
```

更新单个或全部受管技能：

```sh
loopdesk skills update <skill-name>
loopdesk skills update --all
```

移除受管技能：

```sh
loopdesk skills uninstall <skill-name>
```

## 管理技能来源

自定义来源仓库称为 taps：

```sh
loopdesk skills tap list
loopdesk skills tap add <owner/repo>
loopdesk skills tap remove <owner/repo>
```

当你的团队维护自己的技能目录时，使用 taps。

## 发布与检查

发布一个技能目录：

```sh
loopdesk skills publish <path-to-skill>
```

检查某个 meta-skill 的编译组合：

```sh
loopdesk skills inspect <meta-skill-name>
```

对于普通技能内容，使用：

```sh
loopdesk skills view <skill-name>
```

## 如何请求使用技能

提出结果：

```text
Create a PowerPoint deck summarizing this report.
```

优于：

```text
Load the pptx skill and run its script.
```

当任务匹配其描述与触发条件时，LoopDesk 可从当前目录中选择可用技能。

## 内置技能族

| 族 | 示例 |
| --- | --- |
| 调研 | 深度调研、多来源搜索、摘要 |
| 文档 | DOCX、PPTX、XLSX、PDF、HTML-to-PDF |
| 运维 | cron、GitHub、终端监控、subagent |
| Memory | memory 相关辅助与历史探索 |
| 创作 | 技能创建、技能评审、提议辅助 |

## 排查

如果某个技能未被选中：

1. 确认它出现在已安装目录中：

   ```sh
   loopdesk skills list
   ```

2. 查看其描述与可用性：

   ```sh
   loopdesk skills view <skill-name>
   ```

3. 用自然语言提出结果。技能名可提供帮助，但用户意图仍应清晰。

4. 如果可选依赖缺失，安装或更新该技能后重试。

项目范围的技能位于工作区内的 `.agents/skills/`。用它们承载应随仓库一起走的可重复工程工作流，例如分诊、诊断与测试驱动开发。

组合工作流见 [`meta-skills.md`](meta-skills.md)。完整的 MetaSkill 用户指南见 [`meta-skill-user-guide.md`](meta-skill-user-guide.md)。编写规则见 [`../authoring/meta-skills.md`](../authoring/meta-skills.md)。

---

[文档索引](../README.md) · [产品指南](../../README.product.md) · [改进此页](../contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
