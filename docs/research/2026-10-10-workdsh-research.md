# WorkDSH 调研报告

> 调研对象：`techflag/workdsh`（GitHub，默认分支 `main`）
> 调研时间：2026-10-10
> 调研方法：GitHub MCP 直读仓库（README / AGENTS.md / docs / 源码树 / `upstream.json` / 提交历史），未克隆、未运行。
> 调研提交基准：`acbfd5a4be7bafc357fe22f9e195d9a7bb3eedc3`（main 最新 HEAD，`docs:` 提交 #50，2026-10-09）

---

## 1. 一句话结论

**WorkDSH 是一个「WorkBuddy 式」的本地 AI 工作空间桌面应用，技术内核是 DeepSeek 官方的 DeepSeek Harness（DSH）。它本身不做 AI runtime，而是把 DSH 作为版本锁定的官方发布包「搬运 + 二次集成」，在其之上叠加 Projects / Library / Experts / Skills / Connectors / 交付物工作区等 Workspace 能力，并提供可选的企业版（独立后端 `techflag/workdsh-admin` + 本地安装的 Enterprise Connection 插件）。**

证据等级：高（直接来自 README、架构文档、`upstream.json`、AGENTS.md 原文）。

---

## 2. 产品定位与三方关系

| 维度 | 说明 | 证据 |
| --- | --- | --- |
| 与 WorkBuddy 的关系 | **设计灵感来源（inspired by）**，复刻其「项目/资料库/专家/技能/连接器」组织方式，但并非 WorkBuddy 官方产品 | README："WorkBuddy inspired the workspace design"；AGENTS.md / README 均声明 **unaffiliated, not endorsed** |
| 与 DeepSeek 的关系 | 内核 = **DeepSeek Harness（DSH）**，官方发布包被版本锁定引入；WorkDSH = Electron「载体（carrier）」+ Workspace 功能包 | `upstream.json` 锁定 `deepseek-ai/deepseek-harness` `0.2.0-rc.2`；架构文档："no official source checkout is required" |
| 与 SkillHub / dsh-market | 接入两个**独立维护**的第三方目录（SkillHub 技能目录、dsh-market 插件目录），**非自有市场** | README："connects two independently maintained catalogs" |
| 法律身份 | 独立社区项目，MIT 许可；显式声明与 DeepSeek、WorkBuddy **无隶属/授权/背书** | README 末尾 "Community and acknowledgements" |

> ⚠️ 关键边界（AGENTS.md 强制）：**绝不克隆/导入/编译 DSH 官方源码**；`upstream.json` 只锁「已发布 npm 包 + 桌面安装包」的 URL / size / SHA-512。Electron 的 `app.asar` 内**不含第二份 DSH 安装**。

---

## 3. 技术架构

### 3.1 整体形态：Electron「载体」而非「重壳」

- **唯一应用入口**：`apps/desktop/src/workdsh-main.ts`（安装器入口）。
- Agent 与工具**跑在用户本地机器**（个人模式在本人电脑；企业模式在员工电脑，明确**不上 ECS**）。
- 后端（仅企业版）负责：账号、授权、协作数据、模型转发、可审计的成员级会话文本读取。
- 本地 DSH Web 服务由**内置 Node** 启动官方 Host（`runProfile` API），经可写 Profile 加载 WorkDSH 功能包；窗口加载本地 token URL。

```
Electron 窗口 → 本地 DSH Web 服务
内置 Node → Profile 内 DSH CLI → 官方 DSH 能力 + WorkDSH 功能包
```

### 3.2 版本锁定机制（核心工程约束）

- `upstream.json` 当前锁定 **`deepseek-harness 0.2.0-rc.2`**（候选发布版，需显式兼容性验证）。
- 桌面资源（Node/pnpm/Python/Office 资源/命令助手）从官方桌面安装包按 **SHA-512 + size** 校验抽取。
- 升级 = 更新 `upstream.json` 锁版本 + 兼容的 WorkDSH Profile + 捆绑资源，随后跑：
  `corepack yarn check:desktop-dsh-alignment` → Desktop 检查 → 打包运行时启动校验。
- **默认目标为官方最新 stable；pre-release 需显式产品决策。** 版本门禁不通过则禁止打 Desktop 发布 tag。

### 3.3 仓库结构（monorepo，Yarn 4.18 + pnpm 混合）

| 路径 | 职责 | 包管理器 |
| --- | --- | --- |
| `apps/desktop/` | Electron 载体、打包、发布测试 | 根 Yarn（`nodeLinker: node-modules`） |
| `apps/web/` | Web 启动/部署/校验；自有 **pnpm** 锁文件，不并入根 Yarn | pnpm（独立） |
| `packages/` | 共享 WorkDSH 功能包（插件/provider/UI/契约/打包） | Yarn |
| `profiles/` | Personal / Enterprise 插件组合（composition） | — |
| `scripts/` | 构建与发布校验（含 `package-desktop-release.mjs`） | — |
| `patches/` | 针对 `app-builder-lib@26.15.7` 的补丁 | — |

- 根 `package.json`：`packageManager: yarn@4.18.0`；`engines.node: ^22.19.0 || >=24`。
- `apps/web` 与 `apps/desktop` 必须声明**与 `upstream.json` 完全一致的 DSH 版本**；改动任一侧需跑 `check:web-dsh-alignment`。

### 3.4 内置功能插件清单（`packages/plugins/`）

官方默认 Workspace 能力：**library / experts / skills / connectors**（MCP）。
其余为**显式安装**的外部插件（不在基础运行时内）：

`access` · `activity` · `admin` · `applications` · `audit` · `automations` · `connectors` · `enterprise-collaboration` · `experts` · `identity` · `library` · `model-policy` · `office` · `pages` · `projects` · `skills` · `tables` · `usage` · `workbench`

> 注：AGENTS.md 明确「默认 WorkDSH 功能只有 library/experts/skills/MCP-connectors；audit/access/identity/browser 是必需基础设施；enterprise account 随运行时附带但仅企业登录后激活；projects/office/activity/collaboration/notifications 是显式安装的外部插件」。

---

## 4. 功能特性（来自 README 与 docs）

| 能力 | 说明 |
| --- | --- |
| **Projects** | 把指令、计划、任务、素材、能力设置聚合到长期目标的工作面 |
| **Library（资料库）** | 本地文件管理、搜索、预览；任务可引用素材及其修订；支持 CSV/XLSX 导入与 Office 预览（Alpha 阶段） |
| **Experts** | 保存角色与能力配置（不是插件本身，由一个 WorkDSH 插件管理） |
| **Skills** | 含 `SKILL.md` 的可调用指令与资源，可直接装进本地 DSH Skills 目录；由 SkillHub 发现安装 |
| **Connectors / MCP** | 接入外部数据与服务（MCP 一等公民） |
| **Deliverable Workspace（交付物工作区）** | 预览/编辑文档、表格、演示、HTML、PDF 的可用副本；格式预览/编辑/导出保真度因格式而异（Alpha 仍验证中） |
| **企业协作** | `@` 提及同事、分享分析文本与文件、协作收件/发件箱（需 Enterprise Connection 插件 + 公司登录） |
| **模型** | 个人 provider 与公司模型 API 共存；公司密钥留后端，成员经官方 Custom Model API 配置 |

---

## 5. 企业版模式（关键差异化）

- **基础 Desktop 安装器统一**：个人与企业同一份；企业能力来自**显式安装**的 Enterprise Connection 插件（`.tgz`，不走应用市场搜索）。
- **后端独立仓库**：`techflag/workdsh-admin`（账号、组织、权限、审计、Spring AI 内部模型 API 转发）。
- **登录边界**：管理员只把后端**公网 origin** 预置进 `workdsh-config.json`（`WORKDSH_DEPLOYMENT_CONFIG`），**不含凭证/模型密钥**。
- **可复用企业认证 `workdshEnterprise`**：Host 插件注入 `ctx.workdshEnterprise`，Desktop 主进程绑定当前成员登录（不返回 token/桥接凭证/密码），后端强制成员与业务权限。业务端点示例：`POST /api/extensions/reports/list`。
- **数据同步**：企业桌面在成员账号下同步**可见的用户/助手对话文本**到后端；思考链、工具 trace、附件**不作为对话文本上传**；管理员经审计只读访问。
- **不上云**：企业 Agent 执行**不部署在 ECS**；个人模式不激活协作。

---

## 6. 插件与生态治理

- **两种 catalog，均第三方**：SkillHub（技能，[skillhub.cn](https://skillhub.cn/)）与 dsh-market（DSH 插件，[dshmarket.com](https://dshmarket.com/zh/)）。
- **Skill vs Plugin 区分**：Skill = 内容（指令+资源，`SKILL.md`），可直接装进本地 Skills 目录，**本身不是插件**；WorkDSH 的 skill manager 才是一个 DSH 插件。Expert 配置同理。
- **插件模型**：DSH 插件可单工具，也可组合 UI/服务/资源成场景；支持 skills、experts 与软件功能而不强制每技能/每专家各自成插件。
- **治理声明**：目录条目**非全部预装/审核/背书**；安装前需自查许可证、依赖、DSH 兼容性。不存在独立社区标准或在线市场运行时包（见 `plugin-ecosystem.en.md`）。
- 企业插件**不授予组织成员资格**：授权与「个人模式不激活」为强制约束（AGENTS.md 交付回归门禁）。

---

## 7. 工程与发布纪律（AGENTS.md）

- **单长生命周期产品分支 `main`**；开发/迁移分支临时，经 PR 回 main 后才算交付；临时分支合并验证后删除。
- **发布只从 main 可达 commit 打 tag**；临时分支构建成功 ≠ 发布。
- **完整无头回归门禁** `corepack yarn check`：双语文档校验 + 桌面/DSH 对齐 + Web/DSH 对齐 + Web 计划校验 + Desktop 检查；构建/类型/单测/Loader 冒烟必须 headless-safe。
- **双语文档纪律**：`.i18n.yaml` 记录 `.md` 的 Git blob 哈希；中英文与记录须同步更新（有 `scripts/bilingual-docs.test.mjs` 校验）。
- **交付回归门禁**：必需插件需过组合、归档依赖闭包、已装运行时、真实 UI 检查；缺插件/缺入口**不得宣称完成**。

---

## 8. 许可与合规

- 许可证：**MIT**（仓库 LICENSE）。
- 显式声明：独立社区项目，与 DeepSeek / WorkBuddy **无隶属、合作、授权、背书**；上游 GitHub 贡献者来自同步提交历史，不意味着维护本仓库。
- 致谢：DeepSeek Harness（运行时与插件系统基石）、Tencent SkillHub（公开 catalog API）、@cocofhu/skillhub（内置 SkillHub 插件）、dsh-market + awesome-dsh-plugin（社区插件发现）。

---

## 9. 版本与活跃度快照（截至 2026-10-10）

| 项 | 值 |
| --- | --- |
| 桌面版本 | `2.0.6-alpha.5`（2026-10-04 起，Alpha 阶段） |
| 锁定 DSH 版本 | `deepseek-harness 0.2.0-rc.2` |
| 近期主题 | 企业协作/模型配置、库 CSV·XLSX 导入、Desktop 浏览器 worker macOS 激活修复、专家切换保留 Library/MCP 上下文 |
| 发布渠道 | GitHub Releases（全量安装器）+ Gitee（国内分卷/SHA256 合并脚本）；GitHub 为唯一开发源 |
| 企业插件分发 | Releases 直接下 `.tgz`，不走第三方市场；含 DSH 版本清单与 `SHA256SUMS` |

---

## 10. 对 LoopDesk 的战略启示（参考性）

> 本节为基于上述事实的参考研判，非仓库原文。

1. **「载体而非内核」的架构选择值得借鉴**：WorkDSH 把 AI runtime（DSH）做成版本锁定的外部依赖，自己只做编排/工作空间层——与 LoopDesk「控制/编排层，不替代 agent runtime」的 Golden Rule 高度同构。区别在于 LoopDesk 选 local-first + 自有 `LOOP-STATE.json`，而 WorkDSH 选 Electron 桌面 + 官方向导。
2. **生态靠「接入而非自建」**：WorkDSH 不自营技能/插件市场，而是接 SkillHub / dsh-market 两个独立目录，并强调「非全部审核背书」。LoopDesk 的 git 原生 AI 资产分发（Specs/Rules/Skills/MCP/交付物）是更封闭的团队内闭环，二者治理哲学不同。
3. **企业版「后端独立 + 本地执行 + 可复用认证注入」**模式（不上云、凭证不落客户端）对 LoopDesk 的团队/企业扩展有参考价值，尤其 `@` 协作与成员级可审计会话同步。
4. **合规边界意识**：WorkDSH 反复声明与 DeepSeek/WorkBuddy 无隶属，并坚持不编译上游源码。LoopDesk 同理应持续明确与上游 runtime 的边界（见 AGENTS.md §2 Golden Rule 1）。
5. **风险/未证实项**：该项目仍处 **Alpha（2.0.6-alpha.5）**，其 README 多处明确「端到端项目文档引用、专家执行、Office 格式保真仍在验证中」；企业协作示例被标注为「完成的 Desktop 验收场景，非客户部署声明」。引用其能力成熟度时须谨慎。

---

## 11. 调研来源（可复现）

| 来源 | 内容 |
| --- | --- |
| `README.md`（SHA `7968f83f`） | 产品定位、企业模式、插件生态、下载 |
| `README.zh-CN.md`（SHA `aed7fc4`） | 中文版产品说明 |
| `AGENTS.md`（SHA `6ac38a4`） | 仓库规则、分支/发布策略、个人-企业边界、交付门禁 |
| `docs/architecture.en.md`（SHA `b5302cc`） | Desktop 架构、载体设计、Profile 加载 |
| `docs/README.en.md`（SHA `e2ea4f9`） | 文档索引 |
| `package.json`（SHA `4367fead`） | monorepo、Yarn 版本、scripts |
| `upstream.json`（SHA `56ee9cf`） | DSH 版本锁、桌面资源校验 |
| `packages/plugins/`、`profiles/` 目录树 | 内置功能插件与 Profile 组合 |
| `list_commits`（main） | 提交历史与发布节奏 |

> 所有内容来自公开仓库只读访问，未执行任何代码、未下载二进制、未涉及凭据。
