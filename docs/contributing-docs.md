# 为文档做贡献

LoopDesk 欢迎用户与贡献者改进文档。好的文档改动能帮助人们安装产品、选对功能，并在无需维护者背景知识的情况下从常见问题中恢复。

## 可以改进什么

有价值的文档 pull request 包括：

- 更清晰的安装或配置步骤；
- 可直接运行的命令示例；
- 让 Web UI 更易理解的截图或措辞；
- 缺失的 provider、channel、memory、skill 或 tool 工作流；
- 针对常见故障的排查说明；
- 当命令、选项或行为变化时的更正。

请让功能指南聚焦于用户价值与用法。除非细节有助于用户操作产品，否则避免加入深入的运行时内部实现。

## 如何编辑

1. 如果问题较小，在 GitHub 上打开受影响的 Markdown 页面，用铅笔编辑流程提出改动。没有仓库写权限的贡献者将通过 fork 与 pull request 提交。
2. 如果对修法不确定，请开一个[文档 issue](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml)，附上受影响的页面与预期结果。
3. 文档 pull request 请提交到 `dev` 分支。
4. 保持文档改动小而聚焦。
5. 仓库内页面使用相对链接。
6. 优先使用具体命令与示例，而非抽象描述。
7. 如果页面描述了某个 CLI 命令，请对照本地 CLI 或现有参考页核验命令名。

通用贡献规则见 [`../CONTRIBUTING.md`](../CONTRIBUTING.md)。

## 仅文档改动检查

对于仅文档改动，至少检查：

- 链接指向已存在的仓库文件；
- Markdown 代码围栏成对闭合；
- 示例不包含私有路径、密钥或真实 provider key；
- 截图或 UI 措辞与当前产品使用面一致；
- 产品表述保持面向用户，不暴露不必要的实现细节。

如果文档改动同时改动了代码、测试、打包、provider 行为、gateway 行为、渠道或浏览器 UI 行为，请遵循 [`../CONTRIBUTING.md`](../CONTRIBUTING.md) 中的完整项目清单。

## 页面结构

大多数面向用户的页面应回答：

1. 这个功能是做什么的？
2. 我什么时候该用它？
3. 我如何配置或运行它？
4. 它不工作时我该检查什么？
5. 我接下来该去哪？

独立功能应保持在独立页面。例如 memory、skills、meta-skills、SquillaRouter、tool compression、compaction、channels 与 artifacts 不应合并进一个宽泛的机制页。

---

[文档索引](README.md) · [产品指南](../README.product.md) · [报告文档问题](https://github.com/loopdesk/loopdesk/issues/new?template=docs_report.yml) · [贡献指南](../CONTRIBUTING.md)
