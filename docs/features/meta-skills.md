# Meta-Skill

Meta-skill 把可重复的多步工作打包为可复用、可检查的工作流。当一个请求需要不止一个普通技能、工具、检查点或最终综合阶段时，使用它们。

完整的面向用户指南见 [`meta-skill-user-guide.md`](meta-skill-user-guide.md)。编写规则见 [`../authoring/meta-skills.md`](../authoring/meta-skills.md)。

## Skill vs Meta-Skill

| 能力 | 用途 |
| --- | --- |
| Skill | 一个聚焦的任务模式、指令集、脚本或工具辅助。 |
| Meta-skill | 由多个步骤、技能、检查或输出组成的可复用工作流。 |

例如，"总结这份文档"是 skill 形态。"把这份合同、报价与邮件变成签署、拒绝或谈判的建议，并附风险与下一步动作"是 meta-skill 形态。

## 稳定的内置 MetaSkill

保留的稳定目录刻意很小：

| MetaSkill | 定位 |
| --- | --- |
| `meta-competitive-intel` | 把账号或竞品信号变成销售、BD 或竞品情报简报。 |
| `meta-daily-operator-brief` | 把今天的任务、上下文与约束变成一份运营简报。 |
| `meta-document-to-decision` | 把合同、报价、续约、通知或表格变成签署、拒绝或谈判决策。 |
| `meta-job-search-pipeline` | 把 JD、简历与求职目标变成申请材料与面试准备。 |
| `meta-kid-project-planner` | 为学校项目、展示或科学活动产出安全、适龄的计划。 |
| `meta-paper-write` | 支撑学术草稿、稿件结构、引用规划、实验占位与 LaTeX/PDF 路径。 |
| `meta-short-drama` | 产出短剧脚本、视觉提示、字幕与本地视频交付物。 |
| `meta-skill-creator` | 把重复出现的多技能协作模式变成新的 MetaSkill 提议。 |
| `meta-web-research-to-report` | 把有来源支撑的调研需求变成报告、简报或决策备忘。 |

开发树中可能存在实验性 meta-skill，但本页只列出应作为保留产品能力呈现的内置项。

## 环境要求

运行 MetaSkill 前，先看 Skill 页的详情对话框。其 **Requirements** 区显示该 MetaSkill 自身的要求，以及来自子技能的一跳要求。

- `meta-paper-write` 需要 `xelatex` 与 `bibtex` 进行 PDF 编译。
- `meta-short-drama` 需要 `ffmpeg` 与 `ffprobe` 进行本地视频渲染、合并与字幕步骤。
- 文档/报告类 MetaSkill 从子技能（如 `docx`、`xlsx`、`pdf-toolkit`、`pptx`、`multi-search-engine` 与 `weather`）继承就绪状态。

## 如何提出

提出结果与标准：

```text
Create a decision memo comparing travel eSIM, carrier roaming, and local SIM
options for my parents' 8-day Japan trip. Include sources, risks, a final
recommendation, and what I should order tonight.
```

对于重要或易混淆的工作，点名工作流：

```text
Use meta-skill `meta-web-research-to-report`.

Create a source-backed decision memo comparing travel eSIM, carrier roaming,
and local SIM options for my parents' 8-day Japan trip.
```

一个有力的请求通常包含：

- 结果；
- 上下文；
- 决策标准；
- 期望输出；
- 约束；
- agent 不得采取的动作。

## 发现 Meta-Skill

列出并搜索技能：

```sh
loopdesk skills list
loopdesk skills search meta
```

检查某个 meta-skill 的组合：

```sh
loopdesk skills inspect <meta-skill-name>
```

inspect 命令会在你依赖某个工作流之前，展示编译后的步骤形态。

## 查看运行历史

列出最近运行：

```sh
loopdesk skills meta runs list
```

查看单次运行：

```sh
loopdesk skills meta runs show <run-id>
loopdesk skills meta runs steps <run-id>
loopdesk skills meta runs failures --since 24h
```

在不执行实时工作的情况下预览重放形态：

```sh
loopdesk skills meta runs replay <run-id> --dry-run
```

## 提议

meta-skill 创建工作流在成为受管技能前，可能先写出提议。查看提议：

```sh
loopdesk skills meta proposals list
loopdesk skills meta proposals show <proposal-id>
```

审查之后再接受提议：

```sh
loopdesk skills meta proposals accept <proposal-id>
```

## 安全模型

MetaSkill 输出是可审查的工作产物与决策支持草稿。它们不是法律、医疗、金融、招聘、学术、安全或其他高风险情境下的最终专业建议。

发布、申请、安装、支付、签署、发送消息，或修改生产系统等动作，需要用户显式授权。

---

[文档索引](../README.md) · [产品指南](../../README.product.md) · [改进此页](../contributing-docs.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)
