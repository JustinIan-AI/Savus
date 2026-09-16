# LoopDesk · GOAI 新智基座 Agent Infra 赛道 · 初赛方案内核 v1.0

> 本文档是初赛提交物（作品简介 + 方案 PPT）的内容母版。PPT 与 500 字简介均从本文档裁剪生成。
> 编写日期：2026-08-13　初赛截止：2026-08-16

---

## 0. 事实边界声明（重要）

本方案对"已实现"与"待建"做严格区分。原因是赛事红线第 4、5 条规定：决赛封版后按 README 无法复现核心 Demo 可取消评奖资格；决赛展示与复赛承诺严重不符可取消成绩。因此本文档中任何能力都标注真实状态，PPT 中亦不得越界表述。

**状态标记约定**

| 标记 | 含义 |
| --- | --- |
| `[已实现]` | 代码已在 `src/` 中，可现场运行与验收 |
| `[增强]` | 底座已有，需在其上补一层，复赛交付 |
| `[新建]` | 当前不存在，复赛交付 |

**基线事实**（截至 v0.3.1）

- 代码规模：`src/` 668 个 Python 文件，约 182,767 行
- 测试规模：`tests/` 625 个 `test_*.py`（其中 functional 类 12 个需 API 密钥，其余可离线运行）
- 开源状态：Apache-2.0，已发布 v0.3.1 release
- 内置 Skill：62 个 bundled skill，格式为 YAML frontmatter + Markdown，符合 Agent Skills 开放规范

**必须澄清的一点**：项目名为 **LoopDesk**（非 LongDesk）。此前调研稿中出现的 Canonical State、Independent Verifier、Validation Receipt、Event Sourcing、Claim/Lease、Reconciliation Controller 六项能力，经全仓检索**均未实现**，本方案已将其重新归类为 `[新建]` 或 `[增强]`，不得作为既有能力表述。

---

## 1. 一页纸速览（对应 PPT P0）

| 项 | 内容 |
| --- | --- |
| **项目名称** | LoopDesk：可验证交付的 Agent 研发运行时 |
| **一句话定位** | AgentTeams 的第四种 Worker Runtime，让 AI Agent 的研发交付从"自己说完成"变成"被独立验证过" |
| **问题与场景** | 企业把 AI 编码 Agent 接入研发流程后，真正的瓶颈不是 Agent 不会写代码，而是 Agent 说它写完了却没人能证明。多 Agent 并行改同一代码库时，缺少工作区隔离、独立验证、证据留痕与回滚能力 |
| **核心解决方案** | 以 AgentTeams 为协同治理平面，LoopDesk 作为可插拔 Worker Runtime 承担长程执行；引入权限强制隔离的独立 Verifier Agent，其判定只依据真实测试与构建的退出码与产物，产出机器可读的 Validation Receipt；全链路证据沉淀 + 人工审批门禁 + worktree 级回滚 |
| **创新点** | ① 独立验证的三重工程强制（上下文隔离 / 权限隔离 / 证据锚定），不靠 prompt 约定；② 补齐 AgentTeams 官方声明不做的运行时可靠性层，而非另造一套编排框架 |
| **开放/复用价值** | Worker Runtime 适配层、Validation Receipt JSON Schema、7 个新 Skill 包、自举回归评测集，全部 Apache-2.0 开放；Receipt Schema 与 Skill 可被任意 AgentTeams 团队直接复用 |
| **当前进展** | LoopDesk v0.3.1 已发布并可运行：MCP 双向、62 个 Skill、向量记忆、Trace 回放、权限矩阵、human gate、git worktree 隔离、预算控制均已实现，625 个测试文件可作为运行证据。本次新增部分为 AgentTeams Runtime 适配层与独立验证链路 |

**备选项目名**（若嫌主名过长）

- LoopDesk — 让 Agent 交付可被验证
- LoopDesk：AI 研发交付的独立验证运行时

---

## 2. 场景与价值（PPT 第一章 · 评分 25%）

### 2.1 选题来源

选题来自 LoopDesk 项目自身的真实工程实践：一个开发者同时使用 Claude Code、Codex、Codebuddy、Trae 等多个 AI 编码工具改同一个代码库。把这个场景放大到企业，就是赛道方向三"软件研发全流程协同"。

### 2.2 目标用户

- 已引入 AI 编码 Agent 的企业研发团队（10 人以上、有 CI、有代码评审制度）
- 平台工程 / DevOps 团队：需要为业务团队提供可治理的 Agent 研发能力
- 开源项目维护者：需要处理大量外部 Issue 与 PR

### 2.3 核心痛点：AI 交付是"自报告"的

这是本方案的核心洞察，且可被官方文档直接印证。AgentTeams README 中 Worker 的标准交付回复是：

```
You: @alice implement a login page with React
Alice: On it... [a few minutes later] Done. PR submitted: https://github.com/xxx/pull/1
```

Manager 通过周期性心跳发现 Worker **卡住**，但**没有任何机制发现 Worker 错误地认为自己成功了**。具体展开为五个痛点，恰好对应赛道八步闭环的后四步：

| # | 痛点 | 现状 | 对应闭环步骤 |
| --- | --- | --- | --- |
| 1 | **自报告交付** | Agent 的"完成"是自然语言断言，不可机器校验 | 5 结果验证 |
| 2 | **验证与执行同源** | 让写代码的 Agent 判断自己写得对不对，等于让考生批自己的卷；上下文污染使其倾向确认既有判断 | 5 结果验证 |
| 3 | **并行冲突** | 多 Agent 改同一仓库，缺工作区隔离与租约，互相覆盖 | 3 上下文传递 |
| 4 | **证据断链** | 事后要回滚时，查不到改了什么、依据什么决策、验证跑没跑 | 6 证据沉淀 / 7 审批回滚 |
| 5 | **经验不沉淀** | 每个任务从零开始，上次的坑下次照踩 | 8 经验沉淀 |

痛点 2 是最本质的一条：**这不是模型能力问题，是组织设计问题**。人类工程组织花了几十年建立 code review、CI、QA 三道独立防线，而当前的 Agent 团队把这三道全交给了执行者本人。

### 2.4 输入与输出

**输入**：GitHub / GitLab Issue、线上错误日志、用户反馈工单、CI 失败记录

**输出**：
- 已验证的修复分支 + PR
- Validation Receipt（机器可读的验证回执，含命令、退出码、产物哈希、证据等级）
- Evidence Bundle（trace + 决策日志 + 工具调用记录）
- Rollback Packet（回滚指令包）
- 蒸馏出的新 Skill 或知识条目

### 2.5 可量化价值与评估方法

本方案**不预先编造收益数字**，而是给出可被评委复现的评测方法。这是刻意选择：赛事红线第 6 条禁止伪造实验结果。

**LoopDesk 自举回归集（Self-Hosted Regression Set）**

从 LoopDesk 自身 git history 中抽取真实修复过的 bug commit，剥离答案还原为 Issue 描述，构造 Golden Set；以该 commit 当时新增或修改的测试作为独立验收标准，让 Agent 团队重新修复。

设计优势：
- **零 Mock**：真实的 182K 行代码库、真实 pytest 套件、真实 git worktree
- **有客观标准答案**：原 commit 与原测试就是 ground truth
- **可复现**：仓库 Apache-2.0 开源，评委可自行拉取回放
- **直接命中红线第 3 条**对可验证材料的要求

**核心指标**

| 指标 | 定义 | 为什么重要 |
| --- | --- | --- |
| **误报完成率 False-Done Rate** | Agent 声称完成但 Verifier 判定未通过的比例 | 直接量化"自报告不可信"这一核心命题，是本方案的招牌指标 |
| 一次通过率 First-Pass Verify Rate | 首轮即通过独立验证的比例 | 衡量执行质量 |
| 修复重现率 | 能让原测试由红转绿的比例 | 衡量真实修复能力 |
| 平均验证轮次 | 到通过为止的 fix→verify 循环次数 | 衡量闭环效率 |
| 高风险动作拦截数 | 被权限矩阵或 human gate 阻断的次数 | 衡量安全边界有效性 |
| 端到端时延与 Token 成本 | 复用 LoopDesk 现有预算模块直接出数 | 衡量生产可行性 |

**Badcase 集**：额外构造"看起来修好了但实际没修"的样本（如改了测试而非改了代码、只处理了表面症状），用于证明 Verifier 能抓到 False-Done。这是最有说服力的 Demo 片段。

### 2.6 行业可复制性

痛点与机制均与语言、业务、云厂商无关：

- **横向到其他 Agent 场景**：Validation Receipt 与独立验证模式可直接迁移到运维自愈（验证服务真恢复）、金融理赔（验证处置真生效）、客服闭环（验证问题真解决）——凡是"Agent 声称完成"的场景都适用
- **纵向到其他技术栈**：Verifier 的判定依据是命令退出码与产物，替换测试命令即可支持任意语言；LoopDesk 已内置 Python / JS / Go / Rust / 通用五种栈追踪探针
- **对组织的可复制性**：一个跑通的 Team CR 声明，其他业务线拷贝即用（AgentTeams 声明式 CRD 的原生优势）

---

## 3. 方案总览（PPT 第二章）

### 3.1 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│  用户入口：Issue / 错误日志 / 工单 / 用户反馈                    │
├─────────────────────────────────────────────────────────────┤
│  AgentTeams 协作编排治理平面 (声明式 CRD，前身为 HiClaw)  [外部·必选]   │
│  Manager 平台管控 · TeamLeader 任务拆解 · Matrix Room 上下文    │
├─────────────────────────────────────────────────────────────┤
│  Worker Runtime 层 (spec.runtime 可插拔)                       │
│  OpenClaw · QwenPaw · Hermes · ▶ LoopDesk [本方案新增]         │
├─────────────────────────────────────────────────────────────┤
│  LoopDesk 运行时内核                                            │
│  ├ Loop Engine 长程执行 (maker/checker/stop)      [已实现]     │
│  ├ Independent Verifier + Validation Receipt      [新建]      │
│  ├ Skill 能力抽象层 (62 bundled + 7 新增)          [已实现/增强]│
│  ├ 证据链 (Trace + 决策日志 + 调用记录)            [已实现]     │
│  ├ 安全层 (权限矩阵 + human gate + worktree 隔离)  [已实现]     │
│  └ Rollback Packet 显式回滚包                      [新建]      │
├─────────────────────────────────────────────────────────────┤
│  工具连接层：MCP Client/Server [已实现] + 阿里云官方用云 Skills │
├─────────────────────────────────────────────────────────────┤
│  存储：SQLite 状态/记忆 · 向量 embedding · Trace JSONL [已实现] │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 关键技术选型与必要性

评审明确"不按工具数量评分，看必要性、接口契约、可替换性、权限边界"。故每项选型都给出为什么用它、能否替换。

| 层 | 选型 | 必要性 | 可替换性 |
| --- | --- | --- | --- |
| 协同编排 | AgentTeams | 赛道强制；提供声明式 CRD、Matrix 审计时间线、凭证隔离 | 编排语义可映射到其他框架，但赛道要求以其为基点，不替换 |
| Worker 运行时 | LoopDesk | 补齐 AgentTeams 声明不做的运行时可靠性 | 本方案主体，不可替换 |
| 工具连接 | MCP | 赛道推荐；LoopDesk 已双向实现 | 已有等价 adapter 契约，见第 7 章 |
| 官方 Skills | 阿里云用云 Skills | 评分项点名；LoopDesk 的 SKILL.md 符合开放规范，零适配加载 | 可退化为自建 Skill，但会丢失评分 |
| 存储 | SQLite + 本地向量 | 本地优先、可复现、零外部依赖 | 可替换为 PolarDB-for-PostgreSQL（赛道推荐项），迁移成本见第 8 章 |
| 可观测 | 自研 Trace JSONL | 已实现、可回放 | 可对接 LoongSuite / AgentLoop，语义可对齐 OpenTelemetry GenAI |

---

## 4. 多 Agent 协同设计（PPT 第三章 · 评分 25%）

### 4.1 Agent Identity 清单（4 个职能 Agent + 1 个人类角色，超出 ≥3 硬性要求）

严格按附录 A 的八个字段定义。Planner / Executor / Verifier 构成"拆解—执行—验证"的最小可信闭环，Curator 承接第 8 步经验沉淀，Approver 作为 AgentTeams Human CRD 承接高风险审批。其中 Verifier 与 Executor 的隔离是全案的灵魂。

#### Agent 1 — Planner（规划者 / 对应 TeamLeader 职能延伸）

| 字段 | 内容 |
| --- | --- |
| **Name** | `loopdesk-planner` |
| **Role** | 接收 Issue，拆解为有界任务图，管理任务状态流转 |
| **Capabilities** | 能：意图识别、任务拆解、上下文打包、路由决策、失败重规划。不能：直接改代码、直接执行高风险动作 |
| **Inputs** | Issue 正文、仓库上下文、历史相似案例（RAG）、错误日志 |
| **Outputs** | 结构化任务图（含每个子任务的验收标准 acceptance criteria）、上下文包引用 |
| **Dependencies** | Skill: `TaskDecompose`；MCP: github；Memory 检索（相似案例 RAG） |
| **Decision Boundary** | 可自主拆解与重规划；任务图涉及删除 / 迁移 / 生产变更时须 human gate |
| **Trace** | 每次拆解产出决策日志，记录依据的上下文与相似案例引用 |

#### Agent 2 — Executor（执行者 / 对应 Worker）

| 字段 | 内容 |
| --- | --- |
| **Name** | `loopdesk-executor` |
| **Role** | 在隔离 worktree 中实现单个子任务，产出代码变更 |
| **Capabilities** | 能：读代码、写代码、跑局部命令、生成 diff。不能：合入主干、跑生产部署、访问真实密钥（凭证经 Higress consumer token 隔离） |
| **Inputs** | 单个子任务 + 验收标准 + 上下文包 |
| **Outputs** | worktree 内的代码变更 + 自检说明 + 声称完成信号 |
| **Dependencies** | Skill: `ClaimAndLease`、`RepairTask`、stack-trace-*-probe；MCP: 文件/git 工具；worktree 隔离 |
| **Decision Boundary** | 可自主在自己的 worktree 内改动；**其"完成"声明不具备终局效力，必须经 Verifier 裁决** |
| **Trace** | 全部工具调用、命令、diff 进入 Evidence Bundle |

#### Agent 3 — Verifier（独立验证者）★核心差异化

| 字段 | 内容 |
| --- | --- |
| **Name** | `loopdesk-verifier` |
| **Role** | 独立判定 Executor 的交付是否真的达标，产出 Validation Receipt |
| **Capabilities** | 能：在干净环境跑测试/构建/lint、读取退出码与产物、比对验收标准、评定证据等级。**不能：修改任何代码**（只读权限强制），不能看到 Executor 的自检说明（上下文隔离） |
| **Inputs** | Executor 产出的 worktree（只读挂载）+ 任务原始验收标准（非 Executor 转述） |
| **Outputs** | Validation Receipt（PASS/FAIL + 命令 + 退出码 + 产物哈希 + 证据等级 + 缺口清单） |
| **Dependencies** | Skill: `IndependentVerify`、`EvidenceDeposit`；MCP: 测试/构建工具（只读令牌） |
| **Decision Boundary** | 完全自主判定 PASS/FAIL；FAIL 时回执打回 Planner 触发重规划；证据不足时输出"证据缺失"而非猜测通过 |
| **Trace** | Receipt 本身即审计凭证，带 TraceId 关联完整验证轨迹 |

#### Agent 4 — Curator（经验沉淀者）

| 字段 | 内容 |
| --- | --- |
| **Name** | `loopdesk-curator` |
| **Role** | 把已验证通过的执行路径与失败模式蒸馏为可复用 Skill 或知识条目 |
| **Capabilities** | 能：读取 Evidence Bundle 与 Receipt、归纳可复用模式、生成 SKILL.md、跑 Skill 质量校验。不能：改业务代码、直接发布未经校验的 Skill |
| **Inputs** | Evidence Bundle、Validation Receipt、失败轮次记录 |
| **Outputs** | 新 Skill 包（符合 Agent Skills 开放规范）或向量记忆知识条目 + 质量校验报告 |
| **Dependencies** | Skill: `ExperienceDistill`、`skill-creator`、`skill-creator-linter`、`skill-creator-smoke-test`；向量记忆写入 |
| **Decision Boundary** | 可自主生成候选 Skill；**新 Skill 发布进主库须经 linter + smoke-test 双门禁，并由 Approver 确认** |
| **Trace** | 每个新 Skill 记录来源 Receipt 与 TraceId，形成"能力从哪次真实任务长出来"的溯源链 |

> Curator 的三个依赖 Skill（`skill-creator` / `skill-creator-linter` / `skill-creator-smoke-test`）**均已在 LoopDesk 中实现**，构成现成的 Skill 自举生产与质量校验流水线，直接命中 Skill 评分项中的"版本、发布、回滚、质量评估"。

#### Agent 5 — Approver（人类审批者 / AgentTeams Human CRD）

| 字段 | 内容 |
| --- | --- |
| **Name** | `loopdesk-approver`（映射为 AgentTeams `Human` CRD，Human-in-the-Loop 默认机制） |
| **Role** | 高风险动作的人工确认节点，人类在多 Agent 系统中的一等公民身份 |
| **Capabilities** | 能：批准 / 驳回 / 要求补充证据、直接在 Matrix Room 介入对话。不能被 Agent 绕过（权限矩阵强制） |
| **Inputs** | 待审动作摘要 + Validation Receipt + Rollback Packet 预案 |
| **Outputs** | 审批记录（同意/驳回 + 理由 + 时间戳 + 身份） |
| **Dependencies** | Skill: `HumanGate`；AgentTeams Matrix Room / Element 客户端 |
| **Decision Boundary** | 终局裁决权；驳回即触发回滚或重规划 |
| **Trace** | 审批事件写入结构化日志，带 TraceId 关联，满足审计要求 |

### 4.2 Verifier 独立性的三重工程强制

这是全案技术壁垒所在。"独立验证"不能靠 prompt 里写一句"请客观评审"，而要靠工程约束让 Verifier 无法作弊、也无法被污染：

1. **上下文隔离**：Verifier 拿到的是任务的原始验收标准，看不到 Executor 的实现思路与自检说明，从源头切断"确认偏误"
2. **权限隔离**：Verifier 是只读角色（LoopDesk 权限矩阵强制），物理上不能改代码来让测试通过
3. **证据锚定**：判定依据只能是真实命令的退出码与产物哈希，不接受任何自然语言断言；产物哈希写入 Receipt，事后可核验

### 4.3 异常、冲突与多方案处理

| 情况 | 处理机制 | 实现状态 |
| --- | --- | --- |
| Verifier 判定 FAIL | Receipt 回打 Planner，携带具体缺口触发重规划，进入下一轮 fix→verify | `[新建]` 回执回环 |
| 并行 Worker 冲突 | ClaimAndLease Skill 抢占任务租约 + 独立 worktree 物理隔离 | worktree `[已实现]`；lease `[新建]` |
| 多修复方案 | Planner 产出候选，低成本方案先试，Verifier 结果决定是否换方案 | `[增强]` |
| 反复不通过 | stop condition 触发（最大轮次），升级为 human gate 人工介入 | stop `[已实现]`；升级策略 `[增强]` |
| 高风险动作 | 权限矩阵分级 + human gate 人工确认 + 生成 Rollback Packet | 矩阵/gate `[已实现]`；packet `[新建]` |

### 4.4 与 AgentTeams 的映射（详见独立对照表文档）

角色编排、任务拆解、上下文传递、协同执行、状态追踪五项如何映射到 AgentTeams 能力，见 `goai-agentteams-mapping.md`。核心一句话：**LoopDesk 不重造编排，而是作为 `spec.runtime: loopdesk` 的 Worker 镜像被 AgentTeams 调度**。

### 4.5 八步闭环逐步对应（赛道 8.3 强制说明项）

| 步 | 闭环环节 | 承担角色 | 机制与产物 | 状态 |
| --- | --- | --- | --- | --- |
| 1 | 任务输入 | Matrix Room → Planner | Issue / 错误日志 / 工单进入 Team Room，产出 TaskIntake | `[增强]` |
| 2 | 任务拆解 | Planner | 拆为带验收标准的有界任务图，落为 LoopDesk Goal | `[已实现]` 引擎 + `[增强]` 契约 |
| 3 | 上下文传递 | Matrix Room + LOOP-STATE.json + MinIO | 只传有界任务契约与状态引用，不传原始对话全文；大产物走共享存储 | `[已实现]` 状态 + `[新建]` 契约 |
| 4 | 工具调用 | Executor / Locator | Skill 作能力抽象层 → MCP 作工具连接层（经 Higress 统一鉴权） | `[已实现]` |
| 5 | **结果验证** | **Verifier** | 独立执行真实测试/构建/lint，产出 **Validation Receipt** | `[新建]` ★核心 |
| 6 | 执行证据沉淀 | 全体 | Trace JSONL + 决策日志 + 调用记录 + Receipt → Evidence Bundle | `[已实现]` 采集 + `[增强]` 打包 |
| 7 | 审批与回滚 | Approver + Executor | human gate 人工确认；worktree 级隔离回滚 + Rollback Packet | gate/worktree `[已实现]`；packet `[新建]` |
| 8 | 经验沉淀 | Curator | 已验证路径与失败模式 → 新 Skill（经 linter + smoke-test）或向量记忆条目 | `[已实现]` 工具链 + `[增强]` 自动触发 |

**闭环的关键特征**：第 5 步的 Receipt 是唯一的"通过"凭证。若 FAIL，闭环不前进而是回到第 2 步重规划——形成真正的 loop 而非单向流水线。这也是产品名 LoopDesk 的由来。

---

## 5. Skill 工程体系（PPT 第四章 · 评分 25% · 本赛题必选项）

### 5.1 分层原则

严格遵循赛道 9.2 的分层定义：**Skill 承担任务能力抽象层，MCP 承担工具连接层**。Agent 不裸调工具，一律经 Skill → MCP。

Skill 分三个来源，都要说清楚：

| 来源 | 说明 | 数量 |
| --- | --- | --- |
| **A. 阿里云官方用云 Skills** | 复用 skills.aliyun.com 收录的官方 Skill，避免重复建设基础能力 | 按需选用 |
| **B. LoopDesk 已有 Skill** | 62 个 bundled skill，其中研发相关可直接复用 | 12+ 可复用 |
| **C. 本方案新建核心 Skill** | 独立验证闭环所需的 7 个新 Skill | 7 |

### 5.2 关于阿里云官方用云 Skills 的兼容性（重要加分点）

阿里云 Skills 门户明确说明其 Skill **遵循 Agent Skills 开放规范**，兼容 Claude Code、Qwen Code、Qoder、Codex、Gemini CLI、GitHub Copilot、OpenClaw 等客户端。

LoopDesk 的 Skill 格式为 YAML frontmatter + Markdown 正文，字段含 `name` / `description` / `user-invocable` / `disable-model-invocation` / `provenance{origin,license}`，**与该开放规范同源**。实测样例（`stack-trace-rust-probe/SKILL.md`）：

```yaml
---
name: stack-trace-rust-probe
description: "Internal helper for meta-stack-trace-investigator..."
user-invocable: false
disable-model-invocation: true
provenance:
  origin: loopdesk-original
  license: Apache-2.0
---
```

**结论：官方用云 Skills 对 LoopDesk 是零适配成本直接加载**，无需编写集成代码。这既满足评分项对"合理使用官方 Skills"的要求，也证明 LoopDesk 的 Skill 层设计与生态标准对齐。

**规划用途**（具体 Skill ID 以门户实际收录为准，复赛落实）：
- 可观测 / 日志类 Skill：拉取线上错误日志作为缺陷输入源（对应闭环第 1 步）
- 弹性计算 / 容器类 Skill：拉起干净验证环境供 Verifier 使用（对应第 5 步）
- 数据库类 Skill：验证涉及数据变更的修复是否真生效

### 5.3 LoopDesk 已有可复用 Skill 清单（`[已实现]`）

| Skill | 用途 | 服务于哪个 Agent |
| --- | --- | --- |
| `git-diff` | 变更面提取与 diff 分析 | Executor / Verifier |
| `github` | Issue / PR 读写 | Planner / Executor |
| `stack-trace-python-probe` | Python 栈追踪定位与修复靶点 | Executor |
| `stack-trace-js-probe` | JS/TS 栈追踪定位 | Executor |
| `stack-trace-go-probe` | Go 栈追踪定位 | Executor |
| `stack-trace-rust-probe` | Rust 栈追踪定位 | Executor |
| `stack-trace-generic-probe` | 通用语言兜底 | Executor |
| `sub-agent` | 子 Agent 派生与并发执行 | Planner |
| `skill-creator` | 生成新 Skill 包 | Curator |
| `skill-creator-linter` | Skill 规范静态校验 | Curator |
| `skill-creator-smoke-test` | Skill 冒烟测试 | Curator |
| `memory` | 向量记忆读写 | 全体 |
| `summarize` | 长上下文压缩 | 全体 |
| `tmux` | 长时命令会话管理 | Executor / Verifier |

**这 14 个 Skill 已在代码中可运行**，是本方案区别于纯概念方案的实证基础，同时覆盖了五种语言的缺陷定位能力，支撑"行业可复制性"论证。

### 5.4 本方案新建核心 Skill 清单（`[新建]` · 7 个 · 附录 B 格式）

这 7 个 Skill 构成"独立验证闭环"的最小能力集，全部遵循官方附录 B 模板。它们**不替换**阿里云用云 Skills，而是补齐 AgentTeams 运行时层缺失的可靠性能力——前 6 个对应八步闭环的 2/3/5/6/7 步，第 7 个对应第 8 步经验沉淀。

#### Skill 1 — TaskDecompose（任务拆解与契约生成）

| 字段 | 内容 |
| --- | --- |
| **Skill 名称** | `TaskDecompose` |
| **Skill 类型** | 自定义 Skill |
| **使用场景** | Planner 接收 Issue 后，将其拆为带可执行验收标准的有界任务图 |
| **输入参数** | `issue_text`（原始 Issue/日志）、`repo_context`（仓库结构摘要）、`similar_cases`（RAG 召回的相似历史任务）、`max_depth`（拆解深度） |
| **输出结果** | 结构化任务图 JSON：每个节点含 `task_id` / `description` / `acceptance_criteria`（可执行判定，如"原测试 X 由红转绿"）/ `depends_on` / `assigned_agent` |
| **调用条件** | 新 Issue 进入 Team Room 且 Planner 路由判定需拆解时 |
| **依赖工具 / 系统** | Loop Engine（任务状态机）、Memory（相似案例 RAG）、github MCP、CaseRetrieval Skill |
| **失败处理** | LLM 拆解失败时降级为单任务直通（整 Issue 作为一个 task）；验收标准无法量化时标 `human_review_required` 并上抛 |
| **权限与安全** | 仅读仓库元数据与 Issue；不接触业务代码写入；拆解策略写入决策日志可审计 |
| **复用价值** | 任意"长任务→子任务图"场景（运维排障、工单分类）均可复用；结构化验收字段可被 Verifier 直接消费，打通验证闭环 |

#### Skill 2 — ClaimAndLease（任务租约与并行隔离）

| 字段 | 内容 |
| --- | --- |
| **Skill 名称** | `ClaimAndLease` |
| **Skill 类型** | 自定义 Skill |
| **使用场景** | 多 Executor 并行时，抢占任务租约并锁定独立 worktree，避免互相覆盖 |
| **输入参数** | `task_id`、`worker_id`、`lease_ttl`（租约时长）、`repo_url` |
| **输出结果** | 租约凭证（含 `worktree_path`、`lease_token`、`expire_at`）；失败返回 `LEASE_CONFLICT` |
| **调用条件** | Executor 开始处理某个子任务、需独占工作区时 |
| **依赖工具 / 系统** | git worktree（物理隔离，`[已实现]`）、LOOP-STATE.json（租约登记）、SQLite |
| **失败处理** | 租约冲突时退避重试；TTL 到期自动释放并标记 `stale`；超时未续租触发重新分配 |
| **权限与安全** | 每个 Worker 仅可操作自己名下的 worktree；租约登记进状态库，任何写入须持有效 `lease_token` |
| **复用价值** | 任何多 Agent 并行改同一资源（代码库、配置、数据库）的场景通用；租约协议可独立抽为库 |

#### Skill 3 — RepairTask（缺陷修复执行）

| 字段 | 内容 |
| --- | --- |
| **Skill 名称** | `RepairTask` |
| **Skill 类型** | 自定义 Skill（封装已有 stack-trace-*-probe 系列） |
| **使用场景** | Executor 在隔离 worktree 内依据验收标准修复缺陷、产出变更 |
| **输入参数** | `task_id`、`acceptance_criteria`、`worktree_path`、`error_context`（栈追踪/日志） |
| **输出结果** | worktree 内代码变更 + 局部自检说明 + `claim_done` 声明（**非终局**）；diff 进入 Evidence Bundle |
| **调用条件** | 持有有效 `lease_token` 且任务被路由到 Executor 时 |
| **依赖工具 / 系统** | `ClaimAndLease`、`stack-trace-*-probe` ×5、`git-diff`、文件/git MCP（仅本 worktree 范围） |
| **失败处理** | 局部命令失败时定位到具体栈帧重试；超出 worktree 范围的写入被权限矩阵拒绝；陷入死循环由 stop condition 终止 |
| **权限与安全** | 只读源码、写限本 worktree；不能合主干、不能跑生产部署、不能接触真实密钥（经 Higress consumer token 隔离） |
| **复用价值** | 缺陷定位链路（5 语言探针）已可运行，可直接服务于其他代码修复 Agent；封装契约可被任意 Worker 复用 |

#### Skill 4 — IndependentVerify（独立验证）★核心

| 字段 | 内容 |
| --- | --- |
| **Skill 名称** | `IndependentVerify` |
| **Skill 类型** | 自定义 Skill（全案技术壁垒） |
| **使用场景** | Verifier 在干净只读环境跑真实测试/构建/lint，独立判定交付是否达标 |
| **输入参数** | `worktree_path`（只读挂载）、`acceptance_criteria`（原始，非 Executor 转述）、`verify_env`（如干净容器规格） |
| **输出结果** | `Validation Receipt`：判定 `PASS/FAIL` + 命令序列 + 退出码 + 产物哈希 + 证据等级 + 缺口清单（FAIL 时） |
| **调用条件** | Executor 发出 `claim_done` 且 worktree 已锁定为只读状态后 |
| **依赖工具 / 系统** | 测试/构建 MCP（只读令牌）、`EvidenceDeposit`、Higress 提供的隔离验证环境、tmux（长时任务） |
| **失败处理** | 验证环境不可用时输出 `EVIDENCE_MISSING`（绝不猜测通过）；测试超时分级重试；产物哈希不符直接 FAIL |
| **权限与安全** | **三重工程强制**：① 上下文隔离（看不到 Executor 自检）；② 权限隔离（只读角色，物理不能改代码）；③ 证据锚定（只看真实退出码与哈希） |
| **复用价值** | 验证模式与语言/业务无关，替换测试命令即可支持任意栈；可直接迁移到运维自愈、金融理赔、客服闭环等"Agent 声称完成"场景 |

#### Skill 5 — EvidenceDeposit（证据沉淀与打包）

| 字段 | 内容 |
| --- | --- |
| **Skill 名称** | `EvidenceDeposit` |
| **Skill 类型** | 自定义 Skill |
| **使用场景** | 把 Trace、决策日志、工具调用、Receipt 聚合成可审计的 Evidence Bundle |
| **输入参数** | `trace_id`、`artifact_refs`（trace/jsonl、diff、receipt）、`storage_backend` |
| **输出结果** | `Evidence Bundle`（含 index 清单 + 各产物引用 + TraceId 关联索引），落 MinIO/本地存储 |
| **调用条件** | 任一闭环步骤产生需留痕产物时（验证完成、审批完成、回滚完成时） |
| **依赖工具 / 系统** | Trace JSONL 采集（`[已实现]`）、MinIO 或本地存储、SQLite 元数据索引 |
| **失败处理** | 单个产物缺失时标记 `partial` 并告警，不静默丢弃；存储不可达时降级落本地并补偿上传 |
| **权限与安全** | Bundle 写入后只读归档；索引带 TraceId 满足审计时间线要求；敏感字段脱敏后归档 |
| **复用价值** | 证据聚合契约独立，任意需要"动作—证据"绑定的 Agent 系统可复用；为审计与复现提供标准载体 |

#### Skill 6 — HumanGate（人工审批门禁）

| 字段 | 内容 |
| --- | --- |
| **Skill 名称** | `HumanGate` |
| **Skill 类型** | 自定义 Skill（映射 AgentTeams Human CRD） |
| **使用场景** | 高风险动作（合主干/生产变更/删除迁移）前，向人类审批者发起确认 |
| **输入参数** | `action_summary`、`validation_receipt`、`rollback_packet`（预案）、`approver_id` |
| **输出结果** | 审批记录：同意/驳回 + 理由 + 时间戳 + 审批者身份，写入结构化日志 |
| **调用条件** | 权限矩阵判定动作属高风险，或 Verifier/Planner 显式上抛时 |
| **依赖工具 / 系统** | AgentTeams Matrix Room / Element 客户端、LoopDesk human gate（`[已实现]`）、`EvidenceDeposit` |
| **失败处理** | 审批超时按策略降级（默认驳回并触发回滚）；审批者不可达时阻塞而非自动放行 |
| **权限与安全** | 人类审批者身份一等公民，Agent 无法绕过；审批事件强审计，带 TraceId 关联 |
| **复用价值** | 门禁契约通用，可服务任何需"人类兜底"的 Agent 系统；与 AgentTeams Human CRD 天然对齐 |

#### Skill 7 — ExperienceDistill（经验蒸馏）

| 字段 | 内容 |
| --- | --- |
| **Skill 名称** | `ExperienceDistill` |
| **Skill 类型** | 自定义 Skill（封装已有 skill-creator 系列） |
| **使用场景** | Curator 把已验证路径与失败模式蒸馏为可复用 Skill 或向量记忆条目 |
| **输入参数** | `evidence_bundle`、`validation_receipt`、`failed_rounds`（失败轮次记录） |
| **输出结果** | 候选 Skill 包（符合 Agent Skills 开放规范）或向量记忆知识条目 + 质量校验报告 |
| **调用条件** | 任务验证通过后，Curator 触发；或同类失败模式累计达到阈值时自动触发 |
| **依赖工具 / 系统** | `skill-creator` / `skill-creator-linter` / `skill-creator-smoke-test`（`[已实现]`）、向量记忆写入 |
| **失败处理** | 蒸馏出的 Skill 未通过 linter + smoke-test 双门禁则退回候选池，不进主库；质量评分低则只落向量记忆 |
| **权限与安全** | 只能生成候选，新 Skill 发布进主库须经双门禁 + Approver 确认；不改动业务代码 |
| **复用价值** | 形成"能力从哪次真实任务长出来"的溯源链；Skill 自举流水线已可运行，直接命中评分项"版本/发布/回滚/质量评估" |

> **小结（Skill 评分项对应）**：本方案的 Skill 体系同时满足三项评分关注——① 覆盖关键任务能力（7 新 + 14 已有）；② 每个 Skill 的输入输出 / 调用条件 / 依赖 / 失败处理 / 权限 / 复用价值都按附录 B 说清；③ 考虑了版本、发布（双门禁）、回滚（worktree/packet）、质量评估（linter + smoke-test）。

---

## 6. 工程落地、运行验证与安全可审计（PPT 第五章 · 评分 20%）

### 6.1 可观测：Trace / Log / Metrics 三位一体

- **Trace JSONL** `[已实现]`：LoopDesk 记录每个 Agent 的每一步（意图 → 动作 → 工具调用 → 结果 → 决策），带 `TraceId`，支持回放。这是闭环可审计的主干。
- **结构化日志** `[已实现]`：决策日志 + 审批事件 + 权限校验记录，按 `TraceId` 关联，形成与 AgentTeams Matrix 审计时间线对齐的审计视图。
- **指标** `[已实现]`：复用 LoopDesk 预算模块直接出 Token / 成本 / 轮次 / 验证通过率，可对接 Grafana 面板。

关键设计：所有证据以 `TraceId` 串联，满足赛道 9.3 对"结构化记录决策依据、失败原因、权限校验与审批事件，通过 TraceId 与 Trace 关联"的硬性要求。

### 6.2 安全治理

| 机制 | 状态 | 说明 |
| --- | --- | --- |
| 权限矩阵 | `[已实现]` | 按 Agent 角色分级：Executor 可读写其 worktree、Verifier 只读、Approver 触发 gate |
| 凭证隔离 | `[已实现]` | 经 Higress AI Gateway `consumer token`，Worker 拿不到真实密钥 |
| 密钥管理 | `[已实现]` | 不在 Skill/Worker 内硬编码；统一经网关注入最小权限 token |
| 人工门禁 | `[已实现]` | human gate 拦截合主干 / 生产变更 / 删除迁移等高风险动作 |
| 回滚 | worktree `[已实现]` / packet `[新建]` | 回滚 = 删除隔离 worktree；Rollback Packet 把回滚指令显式化、可预演 |
| 预算控制 | `[已实现]` | Token 与成本硬上限，超限即停，杜绝成本失控 |

### 6.3 运行验证（复赛交付的实证材料）

不靠 PPT 叙事，而靠可复现证据，直接命中红线第 3 条（纯 PPT 无 PoC/日志/Trace/视频证据 → 淘汰）：

- **自举回归集** `[新建]`：从 LoopDesk 自身 git history 抽取真实修复过的 bug commit，剥离答案还原为 Issue，以原 commit 当时新增/修改的测试作为独立验收标准。零 Mock、有客观 ground truth、可复现。
- **端到端 Demo 路径**：`Issue(真实 bug)` → Planner 拆解 → Executor 在 worktree 修复 → Verifier 跑原测试出 Receipt → Approver 审批 → 合入。
- **Badcase Demo**（最有说服力片段）：构造"看起来修好实际没修"的样本（改了测试而非改代码、只处理表面症状），展示 Verifier 抓到 False-Done。
- **证据物清单**：样例输入输出（JSON）、Trace JSONL 片段、Validation Receipt 样例、指标截图、评测结果表（含 False-Done Rate）。

### 6.4 风险边界与失败处理

| 风险 | 处理机制 | 状态 |
| --- | --- | --- |
| 模型调用失败 | 降级 / 重试，超阈值升级 human gate | `[已实现]` 重试 + `[增强]` 升级策略 |
| MCP / 工具超时 | 重试 + 幂等，最终上抛人工 | `[已实现]` |
| 验证环境不可用 | Verifier 输出 `EVIDENCE_MISSING`，阻断发布而非猜测 | `[新建]` |
| 反复不通过 | stop condition（最大轮次）触发，升级人工 | stop `[已实现]` |
| 成本失控 | 预算模块硬上限，超限即停 | `[已实现]` |
| 越权动作 | 权限矩阵拒绝 + 强制 human gate | `[已实现]` |

---

## 7. 开放 / 开源计划（PPT 第六章 · 评分 5%）

### 7.1 开源范围与协议

- **LoopDesk 本体**：Apache-2.0，已发布 v0.3.1（复赛前持续维护）。
- **本次新增全部开放**：Worker Runtime 适配层、Validation Receipt JSON Schema、7 个新 Skill 包、自举回归集 → 全部 Apache-2.0。
- **生态贡献导向**：Validation Receipt Schema 与 7 个 Skill 设计为跨团队复用——任意 AgentTeams 团队可 `import` 直接采用，形成赛道内的可复用成果。

### 7.2 第三方依赖披露（满足 9.4 强制项）

- 开源依赖：见 `uv.lock` / `pyproject.toml`，复赛提交完整清单。
- 商业 API：若推理使用闭源模型，披露调用环节、费用假设、权限范围、可替代性与锁定风险。
- MCP 接口与外部权限：列出每个 MCP server 的权限范围与失败重试/幂等策略。
- 数据与授权边界：自举回归集取自自有开源仓库，无第三方数据授权问题。

### 7.3 迁移与替换成本（满足 8.4 "后续迁移成本"要求）

| 当前选型 | 可替换目标 | 迁移成本 |
| --- | --- | --- |
| SQLite + 本地向量 | PolarDB-for-PostgreSQL（赛道推荐项） | 数据模型同构，换 backend driver，低 |
| 自研 Trace JSONL | LoongSuite / AgentLoop | 语义对齐 OpenTelemetry GenAI，写适配器，低 |
| MCP（已双向实现） | 任意等价工具 | 仅新增 MCP server，契约不变，零改造 |

### 7.4 复用成果形态

- **文档**：架构说明、接口契约、示例方案、运行报告。
- **代码**：适配层 + 7 个 Skill 包 + 自举回归集。
- **契约**：Validation Receipt JSON Schema——可被赛道其他团队直接采用，是越过"单队自嗨"的开放贡献。

---

## 8. 落地计划与进展（PPT 第七章 · 进度说明）

### 8.1 当前进展（`[已实现]` 部分）

- LoopDesk v0.3.1 已发布，625 个 `test_*.py` 可离线运行（12 个 functional 类需 API 密钥除外）。
- 内核能力就绪：Loop Engine 长程执行、MCP 双向、62 个 bundled Skill、向量记忆（0.7 权重）、Trace 回放、权限矩阵、human gate、git worktree 隔离、预算控制。
- 14 个研发相关 Skill 已可运行（见 §5.3），覆盖 5 语言缺陷定位，是"非纯概念方案"的实证基础。
- 已全仓核查并澄清事实边界（§0），杜绝 PPT 越界表述触发红线。

### 8.2 复赛交付里程碑

| 里程碑 | 交付物 | 对应状态 |
| --- | --- | --- |
| M1 | AgentTeams Worker Runtime 适配层（`spec.runtime: loopdesk` 镜像 + CRD 映射，见 `goai-agentteams-mapping.md`） | `[新建]` |
| M2 | 独立验证链路（Verifier + 三重工程强制 + Validation Receipt） | `[新建]` 核心 |
| M3 | 7 个新 Skill 包 + Curator 自动蒸馏触发 | `[新建]` |
| M4 | 自举回归集 + Badcase 集 + Demo 视频 + 运行报告 | `[新建]` |

### 8.3 风险控制

| 风险 | 缓解 |
| --- | --- |
| 复现风险（决赛封版后无法复现 → 取消资格） | 用自有开源仓库 + 真实回归集，杜绝 Mock；README 给出回放步骤 |
| 越界风险（展示与承诺不符 → 取消成绩） | §0 事实边界声明全程约束 PPT 状态标记 |
| 依赖风险 | 阿里云 Skills 零适配；存储/可观测可替换（§7.3） |
| 时间风险 | 初赛 8.16、复赛 8.25–9.3、决赛 9.22；M1–M4 在复赛窗口内完成开发 + 证据 |

### 8.4 一句话总结

LoopDesk 不重造编排框架，而是作为 AgentTeams 的第四种 Worker Runtime，用"独立验证 + 证据留痕 + 人工门禁 + 经验蒸馏"补齐官方声明不做的运行时可靠性层——让 AI 研发交付从"自己说完成"变成"被独立验证过"。


