# Competitive Intelligence: tabtin-ai/TabTin

> 调研更新：2026-09-18（基于 GitHub 仓库页 / packages 目录 / commits 页 / ROADMAP.md / docs/architecture/product-concepts.md / 官网 tabtin.com）
> 关联：LoopDesk v2.0 团队版定位（`docs/product-positioning.md`、`docs/prd/loopdesk-prd-v2.0.zh.md`）——本项与 LoopDesk **同为「团队 Agent 协作工作台」形态**，是本仓库已收录竞品中定位重叠度最高之一。

- **Repo**: [github.com/tabtin-ai/TabTin](https://github.com/tabtin-ai/TabTin)
- **官网**: [tabtin.com](https://www.tabtin.com/)
- **组织/版权**: `tabtin-ai`；Copyright © 2026 Shanghai Mofan Technology Co., Ltd.（摹范科技）
- **License**: **AGPL-3.0-only**（另提供单独商业授权；商标归维护方）
- **Language**: TypeScript（主）/ Go / Python / JavaScript（pnpm monorepo，`apps/` + `packages/`，约 100 个 packages）
- **热度（抓取时点 2026-09-18）**: 398 Stars / 96 Forks / 4 Watchers
- **提交活跃度**: main 分支**仅 7 次提交**，集中于 2026-08-22 ~ 2026-08-29（详见 §6 工程治理信号）
- **阶段**: Public Preview（首次完整公开发布进行中）
- **Tagline**: "A workspace where people and multiple AI agents work together." / 官网主标题「目前最先进的开源团队 Harness」
- **中文定位**: 人与多个 AI Agent 共同工作的协作空间；团队级 AI Agent Harness（工作内核）+ 协作工作台

## 1. 定位与核心主张

TabTin 面向"想把 Agent 带进真实工作"的个人与团队，核心命题是一句话：

> **一个人已经完成的工作，能不能直接成为下一位同事的起点？**

其立论起点是：AI 已提升个人产出，但没有自动提升团队效率。团队越深入使用 Agent，越容易出现**重复调研、上下文与判断依据丢失、Token 重复消耗、方法难复用、结果责任不清**五类损耗。

官网自述的三要素：① 把任务、文档和团队协作放在同一工作面；② 团队每个人都能随时查看和接手（过程可检查、可交接、可回退）；③ 开源（"BUILD IN THE OPEN"）。

五条产品原则（`docs/architecture/product-concepts.md`）：**过程可见 · 权限可控 · 结果可检查 · 工作可交接 · 责任有人承担**。

### ⚠️ 主张可信度提示

官网设有一节 **"CODE-LEVEL COMPARATIVE AUDIT — 全球开源团队 Agent Harness 代码级对比审计"**，宣称「28 个候选项目完成代码级核查 / 4 个高相关项目进入固定提交深审 / 1 个项目通过全部审查，**TabTin 为本次审计唯一通过项目**」。

- 该结论属于**厂商自证式对比审计**：被审计项目清单、评分维度、4 个深审项目名称**均未披露**；三份"复核报告"是 ChatGPT / WorkBuddy / Claude 的对话分享链接，非独立第三方或可复现报告。
- **引用时应标注为"官方宣称"**，不可当作客观结论。

## 2. 架构分层（Organization / Workspace / Agent / App / Device）

```
Organization
├── Workspace ：成员的私有执行现场
├── Agent     ：AI 参与身份
├── App       ：工作应用与能力
└── Device    ：实际执行环境
```

| 概念 | 定义 | 关键边界 |
| --- | --- | --- |
| **Organization** | 组织与租户边界，拥有成员、资源与配置 | 不同 Organization 默认隔离 |
| **Workspace** | 成员的**私有**执行现场：工作根、文件、终端、Skill、Checkpoint | 每个 Workspace **只有一个执行根** |
| **Agent** | 具备角色、规则、模型、Skill、记忆、执行偏好的 AI 身份 | **表达「谁参与」，不表达「在哪里执行」** |
| **App** | 文档、表格、终端、浏览器、消息、集成等一等工作应用 | 人与 Agent 操作**同一份** App 结果 |
| **Device** | 提供终端、文件、浏览器或设备控制的实际运行环境 | 必须遵守 Organization / 成员 / Workspace 权限 |

> **核心断言**：**Agent 与 Device / Workspace 解耦**——身份归属与执行位置是两个正交维度。

**术语缺口（可作为教训）**：核心概念表**未定义** `Task`、`Skill`、`Checkpoint`、`执行根`、`上下文冻结` 等高频术语，它们仅在别处定义句中被引用，缺少同级别的边界说明。

## 3. 核心能力（四大项）

### 3.1 工作可以交接（差异化主能力）

提供**两种互补**的交接方式：

| 方式 | 载体 | 内容 | 接收动作 |
| --- | --- | --- | --- |
| **任务续接**（Task Handoff） | 同一 Organization 内的成员 | **冻结可共享的必要会话上下文快照**；记录任务引用的文档、表格、云端文件、本地文件 | 接收人选择**自己的 Agent 与 Workspace**，创建**独立的续接任务** |
| **交接包**（Handoff Package） | 团队会话 | 工作目标、当前进展、下一步、风险；可引用 Agent 会话、消息、文档、表格 | 查看 / 确认 / 接手 |

**两者共同约束**：不共享发送方整个本地目录；双方本地环境保持独立；交接材料**继续受原资源权限约束**（不绕过权限）。

**明确非目标**：① 不是共享所有成员本地目录的远程文件系统；② Agent 不自动获得全部权限；③ 交接不绕过已有资源权限；④ 代码中的过渡名称不会自动成为公共产品概念。

### 3.2 人和 Agent 操作同一份结果

消息、文档、多维表格（Smartsheet）、演示文稿等协作应用，**Agent 可直接创建和编辑**；浏览器采集的数据与媒体可继续进入工作应用。设计意图是消除"聊天框 → 下载文件 → 办公软件"之间的反复搬运。

### 3.3 团队方法可以复用

不同 Agent 角色可配置各自的**规则、模型、Skill 和记忆**——即"方法"沉淀在 Agent 角色上，而非依赖成员临时写的 Prompt。同时明确：**Agent 可执行工作，但重要判断、责任确认与结果验收仍由人完成**。

### 3.4 团队可以拥有自己的 Agent 工作系统

覆盖客户端、服务端、Agent Runtime、实时协作、工作应用与管理能力。个人与小团队可直接用官方服务；开发者可在本地运行 Community Server 或从源码修改；架构持续走向模块化与可插拔。

**官网功能面（7 大板块摘要）**：全能工作面（代码/文档/数据/联网任务）· 群聊协作（Agent 从群消息发现 Bug → 创建任务 → 指派 → 跟踪至发布）· 共享任务（实时查看 · **任意节点 Fork/分叉**）· 项目协作 · AI 分身（人设与规则 / 技能携带集 / 工具携带集 / 分身记忆）· 随时继续（多端 + **credit 额度看板**）· 组织设置（成员角色：组织所有者 / 编辑者 / 查看者）。

**工程侧可疑亮点**：**嵌套子 Agent**（主 Agent 拆为研究/实现/验证三条子任务，目标、团队规则、交付标准一同下发）、**Checkpoint 回退**（写入前保存状态，可回退）、**权限审批**（仓库写入需批准、发布动作需团队确认）、**Skill 市场**（48 个官方应用包）。

## 4. 技术栈与工程结构

- **工程化**: pnpm monorepo（`pnpm-workspace.yaml`、`pnpm-lock.yaml`、`tsconfig.base.json`）
- **端**：`tabtin-electron`（桌面）· `tabtin-web` · `AdminDash` · `tabtin-ios` / `tabtin-android`（移动端）
- **服务端**：Community Server；容器化以 4 份 compose 表达（`compose.yaml` / `compose.lan.yaml` / `compose.community-dev.yaml` / `docker-compose.dev.yml`）
- **实时协作**：**Centrifugo** + `collab-core`
- **接口契约**：`contracts/` 目录 + `wire-codegen`（协议代码生成）
- **双态开关**：`TABTIN_EDITION`、`AUTH_FIXED_VERIFICATION_CODE`（见 `.env.example`）

### 4.1 packages 分层（约 100 个，按命名可读出分层意图）

命名规范高度一致：`*-contracts`（契约层）→ `*-core`（核心层）→ `*-ui`（UI 层）→ `*-host-runtime`（宿主运行时）→ `*-adapter-{web,electron}`（平台适配）→ `*-capabilities`（能力探测）。

| 分区 | 代表包 | 规模 |
| --- | --- | --- |
| Agent / AI | `agent-runtime`、`agent-host`、`agent-wire`、`agent-modes`、`agent-prompt`、`prompt-contract`、`skills`、`action-tools`(+`-adapter`)、`agent-import` | 12 |
| 表格引擎（核心业务） | `table-kernel`、**`table-kernel-pglite`（WASM Postgres）**、`table-engine-canvas`、`smartsheet`(+`-ui`/`-adapter-web`/`-adapter-electron`)、`table-host-runtime` | 12 |
| 浏览器/采集 | `browser-core`、**`anti-detect`（反检测/指纹伪装）**、`crawlspace-core`、`crawl-contracts`、`extraction-core`、`platform-reach`、`platform-adapter` | 11 |
| 文档/站点/演示 | `tabdoc-ui`、`tabdoc-host-runtime`、`doc-editor`、`doc-renderer`、`local-docparse`、`office-preview-runtime`、`tabsite-core`、`tabslide` | 10 |
| 文件/存储/快照 | `file-pipeline`、`file-history-core`、**`checkpoint-core`**、`storage-manager`、`safe-fs`、`oss-client` | 6 |
| 运行时/终端 | `python-runtime`(+`-host`)、`terminal-core`、`pty-core`、`lsp-runtime`、`runtime-reporter` | 6 |
| CLI / SDK | `tabtin-cli`、**`tabtin-cli-go`**、`cli-routes`、`cli-server-core`、`tabtin-sdk`、`tabtin-sdk-python` | 6 |
| 安全/基础设施 | `security-policy`、`env-sanitize`、`os-errors`、`tool-errors` | 4 |
| 协作/搜索/媒体 | `collab-core`、`search`、`local-embedding`、`media-core`、`media-capabilities` | 5 |

**质量工具链**：ESLint（含自定义 `eslint-rules/`）· **Biome** · Prettier · markdownlint · **madge**（循环依赖检查）· **gitleaks**（密钥扫描）· `.githooks` · `.tool-versions`。

## 5. 使用方式与数据边界

**两种入口**：① 官方服务（不自行维护服务端，访问 tabtin.com）；② 本地运行源码（快速预览 `node scripts/dev.mjs community` / 全量预览 `pnpm dev`；中国大陆可加 `--region cn`）。

**预览模式**：快速预览 = Community 后端 + Collab + Centrifugo + Electron；全量预览 = 上述 + AdminDash + tabtin-web。

**关键限制（路线图已确认的 5 项待补边界）**：
1. 各组件成熟度与跨端体验不一致
2. **Community Server 当前主要面向本机运行**
3. **移动端不提供独立 Agent 执行环境**（须先由桌面端完成执行环境配置与设备绑定，并保持该电脑在线）
4. **Project 相关能力仍在建设中**（下一版本重点，产品形态待验证）
5. 部分模块只有默认实现，**替换与扩展成本较高**（以 IM 为例，替换需改较多内部代码）

**隐私边界**：Community Server 默认只监听本机地址，账号/配置/业务数据存于本机 Docker 数据卷；Community 客户端默认不连维护方 Sentry 与更新服务；完整诊断包仅在用户明确同意后上传。官方服务以公开隐私政策为准。

## 6. 工程治理信号（评估开源成熟度的关键）

**提交历史结构**（main 分支全部 7 次提交）：

| 日期 | SHA | 提交信息 | 署名 |
| --- | --- | --- | --- |
| 2026-08-29 | b033ade | `release: publish LAN community packaging from opensource/v1 (#8)` | zhouchongqing0325 + cursoragent |
| 2026-08-29 | 4fcdcda | `release: sync opensource/v1 to the public repository (#7)` | zhouchongqing0325 + cursoragent |
| 2026-08-23 | 38265b5 | `docs: record the public TabTin Agent identity` | tabtinagent |
| 2026-08-22 | 96bd619 | `scripts/backend: restore all local Celery workers` | zhangx |
| 2026-08-22 | c4aba1e | `Merge pull request #2 from tabtin-ai/release/v1.1.2` | tabtinagent |
| 2026-08-22 | 977a4ce | `release: align the public snapshot to product 1.1.2` | tabtinagent |
| 2026-08-22 | 7c84fca | `TabTin Go Public` | tabtinagent |

**判定：属于「快照式代码导入 + 整包发布同步」，而非连续性开源开发。** 依据：① 全部提交挤在 3 天内；② 存在明确的公开化起点提交 `TabTin Go Public`；③ release 措辞直指整体同步（"sync opensource/v1"、"align the public snapshot to product 1.1.2"）。因此公开仓库的提交历史**基本不反映原始逐行开发过程**。

**与"BUILD IN THE OPEN"主张存在张力**，且与自证式审计主张叠加，共同抬高了其开源可信度的验证成本。提交署名中 `cursoragent`（人 + Cursor AI 代理共同署名）也说明其公开提交流程高度自动化。

**商业模式**：AGPL-3.0-only + 单独商业授权咨询 + 商标约束（分支项目可称"基于 TabTin"但不得冒充官方）+ credit 额度体系（成员级额度分配、消耗可视、超额前提醒、组织所有者不限额度）。

## 7. 与 LoopDesk v2.0 的对照

### 7.1 ⚠️ 高重叠区（同为「团队 Agent 协作工作台」）

| 能力 | TabTin | LoopDesk v2.0 |
| --- | --- | --- |
| 任务主对象与看板 | 任务卡 + 看板视图 / 列表视图 + 共享任务实时查看 | 任务看板（默认落地页） |
| 任务交接 + 上下文传递 | 任务续接（冻结会话上下文快照）+ 交接包 | 跨 agent / 跨会话 / 跨团队上下文传递 |
| Agent 角色化资产 | 人设与规则 / 技能携带集 / 工具携带集 / 分身记忆 | Rules / Specs / Skills / MCP 下发 |
| 审批与护栏 | 仓库写入需批准、发布需人工确认、Checkpoint 回退 | 审批门（右栏区块）+ quota / gate |
| 额度治理 | 成员级 credit、消耗进度、超额前提醒 | 成本与安全护栏（quota / gate） |
| 状态可回退 | Checkpoint #03 已保存，可随时回退 | `LOOP-STATE.json` durable + git 可 diff |
| 多端继续 | 桌面推进 / 手机查看·回复·确认 | Operator-developer 跨设备 approve / reject |
| 资产市场 | Skill 市场（48 个官方应用包） | 团队 AI 资产市场 |
| 长任务 | 嵌套子 Agent（研究/实现/验证三条子任务） | LoopX 式长任务 + issue-fix / pr-commit / auto-research 模板 |

### 7.2 关键差异：TabTin 的路线与 LoopDesk 的「明确不做」高度重合

这是本次调研最有价值的发现——**TabTin 的几乎所有架构选择，都落在 LoopDesk v2.0 明确排除或明确不同的那一侧**：

| 维度 | TabTin | LoopDesk v2.0 护城河 / 排除项 |
| --- | --- | --- |
| 部署形态 | **重客户端 + 服务端**：Electron 桌面 + iOS/Android + Community Server + Centrifugo + Celery workers；官网提及约 720MB 落盘 | **零基础设施 local-first**：无服务器、无 DB、无云账号即可跑；明确"**不是重桌面 Electron 壳**" |
| 实时协作 | **Centrifugo 强实时协作**为一等能力（同群、实时查看、实时同步回群） | 明确不做**强实时云房间** |
| 商业化 | 官方 SaaS 服务 + **credit 额度体系** + AGPL 商业双授权 | 明确不做**多租户 SaaS / SaaS 计费商业化**；Apache-2.0 |
| 产品面宽度 | 办公套件级：文档（TabDoc）· 多维表格（Smartsheet / `table-kernel-pglite`）· 演示（TabSlide）· 站点（TabSite）· **反检测浏览器采集（`anti-detect`）** | 明确排除 **broad media skills**；定位是**控制 / 编排层**，不是工作应用套件 |
| 资产分发通道 | 官方 Skill 市场 + 服务端托管 | **git 原生**分发（Specs / Rules / Skills / MCP / 交付物） |
| 状态可移植性 | durable state 落在服务端/客户端内部实现，**未公开可机读的可移植格式** | 可移植、**可机读、可 diff / export** 的 `LOOP-STATE.json` |
| 方法论 | 以 "Harness" 为叙事锚点（Checkpoint、审批、PMO 执行模式） | 显式 **Loop Engineering** 方法论：triage → maker → checker → escalation → run log → stop condition |
| 移动端 | 非独立执行环境，须桌面端在线绑定 | 不做重桌面壳，Operator 场景走 Web / IM 查看与审批 |
| License | **AGPL-3.0-only**（+ 商业授权） | **Apache-2.0** |

### 7.3 直接竞争风险评估

- **风险等级：中**。形态重叠（团队 Agent 协作工作台 + 任务看板 + 交接 + 审批 + 额度），但**技术路线相反**：TabTin 重、LoopDesk 轻；TabTin 服务端依赖、LoopDesk 零基础设施；TabTin AGPL、LoopDesk Apache-2.0。
- **主要风险点**：① **概念先发占位**——TabTin 已把"任务可交接 / 上下文冻结 / 人机同工作面"讲成一套完整叙事并获得 398 stars、96 forks，LoopDesk v2.0 若在同一叙事空间表述，容易被认为跟随；② **办公套件级体验差**——TabTin 的"人机同操作一份在线文档/表格/PPT"是 LoopDesk 刻意不做的高成本体验，需在文档中明确这是**有意取舍**而非能力缺失；③ **AGPL 双授权的商业可读性**——对商业团队客户，TabTin 的 AGPL 反而是 LoopDesk 的 Apache-2.0 的对比优势。
- **反向信号（对 LoopDesk 有利）**：TabTin 的存在与热度**验证了团队 Agent 协作是真实市场**，而非伪需求；其 7 次快照式提交、自证式审计、Project 能力未完成、Community Server 仅本机可用等短板，说明"重服务端 + 重客户端 + 办公套件"路线**交付成本极高、公开可信度难建立**——这正是 LoopDesk "薄控制面 + 零基础设施 + git 原生" 的窗口。

## 8. 对 LoopDesk 的启示（可借鉴点）

1. **把「交接」显式建模为两种形态**：TabTin 区分「任务续接（上下文快照）」与「交接包（目标 / 进展 / 下一步 / 风险）」。建议 LoopDesk 在跨团队上下文传递设计中采纳"**交接物 = 快照 + 引用资源清单 + 权限不绕过**"三件套，但载体改为 **git 可 diff 的 `LOOP-STATE.json` 片段**，从而把"可携带"变成相对 TabTin 的差异化，而非跟随。
2. **非目标章节是防概念膨胀的有效手段**：TabTin 在 `product-concepts.md` 设 "Explicit Non-goals"。LoopDesk 的 `AGENTS.md` §1「Not this」已具备同等作用，建议在 `docs/product-positioning.md` 中**显式成节**，作为对外可引用的边界声明。
3. **术语定义缺口是可预防的教训**：TabTin 核心概念表漏定义了 `Task` / `Skill` / `Checkpoint` / `执行根` / `上下文冻结`，正文引用却无边界。LoopDesk 的 `docs/glossary.md` 已承担术语层职责，需确认**高频新概念（交接、上下文冻结、审批门、评审中）全部入表**，避免同类缺陷。
4. **身份与执行位置解耦的表述可直接采用**：TabTin 的 "**Agent 表示谁参与，不表示在哪里执行**" 是一句高质量的分层表述，与 LoopDesk 的 agent adapter（claude / codex / pi）+ worktree 隔离天然契合，建议用于"跨 agent / 跨会话 / 跨团队"的对外叙事。
5. **Checkpoint 与 `LOOP-STATE.json` 的关系需澄清**：TabTin 有明确的写入前 Checkpoint 回退。LoopDesk 的等价能力分散在 worktree 隔离 + git + durable state 三处，建议在 PRD 中补一段"回退语义"说明，避免被质疑缺失。
6. **开源可信度是资产**：TabTin 的 7 次快照提交 + 自证式"唯一通过审计"显著抬高验证成本。LoopDesk 应坚持真实提交历史 + 可复现证据（`LOOP-STATE.json`、run log、`tests/verify_webui_lifecycle.py` 等），把"可验证"作为对外信任基础。

## 9. 待核实与风险提示

- **热度与提交量的反差**：398 Stars / 96 Forks 对应仅 7 次提交，且 2026-08-25 ~ 09-08 期间在 B 站、AI 工具站、评测站点出现密集推广内容，Star 增长可能受推广驱动，**不宜直接作为产品成熟度指标**。
- **自证式审计结论不可复现**：引用"全球唯一通过代码级审计"必须标注为官方宣称。
- **时间戳缺失**：仓库页、README、官网、`ROADMAP.md` 与 `product-concepts.md` 均未提供发布日期；commits 页的 "Last commit date" 字段为空。本报告的活跃度结论仅基于提交日期（2026-08-22 ~ 08-29）。
- **Project 能力超前于实现**：官网"项目协作"板块描述较完整，但 ROADMAP 明确 Project **仍在建设中**、为下一版本重点、形态待验证。
- **packages 职责为推断**：§4.1 中各包职责系依据包名推断，未逐一读取各 `package.json` / `README.md` 验证（约 100 个包），若需精确职责应逐包核实。
- **GitHub API 匿名配额受限**：本次未取到 `created_at` / `pushed_at` / `size` / `language` 占比等字段，如需要可改用认证请求补取。

## 10. 数据来源

| 来源 | 用途 |
| --- | --- |
| `github.com/tabtin-ai/TabTin` 仓库页 | 简介、Stars / Forks、License、目录结构、Topics |
| `github.com/tabtin-ai/TabTin/tree/main/packages` | 约 100 个包的分区与分层命名 |
| `github.com/tabtin-ai/TabTin/commits/main` | 7 次提交的日期、信息与署名 |
| `ROADMAP.md`（raw） | 阶段、5 项待补边界、三大重点、Project 规划、可插拔三层 |
| `docs/architecture/product-concepts.md`（raw） | 唯一定义来源：五原则、四层概念表、两种交接方式、非目标 |
| `www.tabtin.com` | 定位主张、Harness 三层论述、7 大功能板块、credit 体系、可信度存疑的审计主张 |
| 抓取时点 | **2026-09-18** |

> **本报告定性**：结论基于公开页面与仓库文件；标注「官方宣称」的内容未经独立验证；§4.1 包职责与 §7 竞争评估含推断成分，已逐处说明。
