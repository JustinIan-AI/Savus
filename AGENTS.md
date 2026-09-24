# LoopDesk — Project Agent Rules

## 1. Project Identity

- Product name: **LoopDesk**
- Target user:
  - **Primary**：小型研发团队、技术负责人，以及在团队中工作的独立开发者
  - **Secondary**：Operator-developer（在另一设备或 IM 查看状态、approve/reject）；Power user（对已批准的 bounded 工作做跨设备继续）
- Core promise: 在开发者自有机器上 **local-first** 统一编排 claude / codex / pi 等 agent 完成真实研发任务；跨 **agent / 会话 / 团队** 保持上下文、记忆与循环状态连贯；并通过 **git 原生**通道分发团队 AI 资产（Specs / Rules / Skills / MCP / 交付物）
- Differentiation（四条护城河，来源 PRD v2.0 §2.3「差异化空白」）：
  1. **可移植的 durable `LOOP-STATE.json`**——可机读、跨工具、可 diff / export；竞品的连续性均封在自家生态内
  2. **显式 Loop Engineering 方法论**——triage → maker → checker → escalation → run log → stop condition，外加 issue-fix / pr-commit / auto-research 固定长任务模板
  3. **零基础设施 local-first**——无服务器、无 DB、无云账号即可跑
  4. **git 原生的团队 AI 资产分发**——差异化于 Proma 的 Cloud 托管分发
- Not this：不是 AI IDE，不是终端 agent 包装器，不是 agent runtime（LoopDesk 是**控制 / 编排层**），不是强实时云房间，不是多租户 SaaS，不是重桌面 Electron 壳

### 1.1 定位演进：v0.1 个人版 → v2.0 团队版（2026-09-11 重新定义）

LoopDesk 的产品定位已于 **2026-09-11 完成一次重新定义**。**v0.1 的"单人 / 个人"边界与"不做团队协作"的排除项已作废**；凡涉及产品形态、目标用户、能力边界的旧表述，一律以 v2.0 为准。

| 维度 | v0.1（旧，已作废） | **v2.0（当前权威）** |
| --- | --- | --- |
| 目标用户 | independent developer（单人） | 小型研发团队 / 技术负责人 / 在团队中工作的独立开发者 |
| 产品形态 | personal loop workspace | **team loop workspace**（local-first） |
| 团队能力 | 明确排除（"not a team collaboration platform"） | **核心能力**：跨团队上下文传递 + 团队 AI 资产 git 化分发 + 一键下发 / 共享 |
| 系统集成 | 无 | JIRA / Plane 任务同步 + Confluence 知识接入（MCP 一等公民） |
| 长任务 | 单次 loop | LoopX 式长任务自动完成 + 固定模板（issue-fix / pr-commit / auto-research） |
| 资产治理 | 本地 Skills | Specs / Rules / Skills / MCP / 交付物 git 化、可版本化、可审计、可下发 |
| 明确不做 | — | 强实时云房间、多租户 SaaS、重桌面 Electron 壳、替代 agent runtime、SaaS 计费商业化 |

> **防偏差硬约束（MUST）**
> 1. 任何文档、代码注释、CLI help、Web UI 文案中出现"个人版 / 面向独立开发者 / 不做团队特性 / personal loop workspace / 单人控制台"等表述，一律视为**过期**，必须改写为 v2.0 团队定位。
> 2. **定位类文档权威顺序**（冲突时以序号靠前者为准）：① `docs/product-positioning.md` → ② `docs/prd/loopdesk-prd-v2.0.zh.md` → ③ `docs/plans/loopdesk-webui-design-spec.md` → ④ `docs/design-system.md`（token）。其余定位叙述（README、release note、设计稿文案、调研结论）均为**派生**，冲突以上述顺序为准。
> 3. **前端事实源唯一**：Ardot 设计文件 `724693301521075`（8 帧，dark 底 + teal 强调色 `#34D399`）。设计系统画布 `724676209058226`（TDesign 蓝方向）**已作废，不得再作为实现依据**。

## 2. Golden Rules

1. **本仓库拥有 v2.0 产品面。** 上游遗留 runtime 代码按"可复用的 runtime 库"对待，不得扩张为产品叙事；模块取舍以 `docs/decisions/module-audit-loopdesk-vs-opensquilla.md` 的 Cancel / Retain 分类为准（Cancel 代码可留在源码树，但**不得**出现在 CLI、Web UI、docs 或任何公开面）。
   > 原文为 "LoopDesk owns the v0.1 product surface ... legacy LoopDesk code"，其中的 "legacy LoopDesk" 是 `OpenSquilla` → `LoopDesk` 全局替换的残留错字（见 §4.6 B），本版已还原。
2. **Docs and decisions are first-class deliverables.** If a decision, research result, risk plan, or task breakdown is produced, it must be saved under `docs/` or `AGENTS.md` before implementation claims completion.
3. **Feature-driven delivery first, test-driven execution second.** Each feature must have a small feature plan with scenarios and acceptance criteria before code starts; each task must start from a failing test.
4. **Loop Engineering is the operating method.** Use triage -> maker -> checker -> escalation -> run log -> stop condition as the default delivery loop for every feature and bugfix.
5. **v2.0 公开面优先级。** 公开文档、CLI 与 Web UI 优先呈现：任务看板（默认落地页）、local-first agent 编排、MCP / ACP 适配、团队 AI 资产市场、memory / skills / artifacts、成本与安全护栏（quota / gate）、worktree 隔离、团队资产下发。
   **不再排除团队协作能力**——v0.1 的 "defer team collaboration" 已随 §1.1 定位重定义作废。
   仍然排除：强实时云房间、多租户 SaaS、重桌面 Electron 壳、云托管计费、broad media skills、cron-first 叙事。
6. **Naming is part of the work.** Unify `LoopDesk` / `loop_workspace` / `LOOP-STATE.json` / `LoopWorkspaceState` / `loop` CLI terms. Do not expose legacy `session`, `workspace-state.json`, or channel-first copy on any public surface.
7. **默认中文。** 项目文档、PRD、设计规格、调研、计划、评审说明一律默认使用简体中文。除必须保留的英文专有名词（产品名、命令、字段名、代码标识、外部仓库名、UI 文案字面量）外，不写英文正文。

## 3. Project Requirements

**当前权威（v2.0，按 §1.1 权威顺序）：**
- 产品定位：`docs/product-positioning.md`
- **当前权威 PRD**：`docs/prd/loopdesk-prd-v2.0.zh.md`（v2.0 完整版：116 条能力清单 §9、Codex 三栏前端清单 §9.11）
- WebUI 设计规格：`docs/plans/loopdesk-webui-design-spec.md`（v2.0，Codex 三栏范式）
- 设计 token 唯一事实源：`docs/design-system.md`
- 偏差清单：`docs/design-system/prd-vs-design-draft-deviations.md`（2026-09-12 修正版）

**历史参考（已非权威，勿据此实现）：**
- `docs/prd/personal-loop-workspace.md`（v0.2 个人循环工作区）
- `docs/decisions/v0.2-channel-adapter.md`（v0.2 channel adapter 边界）
- `docs/plans/2026-07-14-loopdesk-v02-fdd-tdd-execution-plan.md`（v0.2 FDD/TDD 执行计划）
- `docs/features/core-feature-list.md`、`docs/architecture/personal-loop-workspace.md`
- `docs/decisions/product-strategy.md`（v0.1 期产品策略，定位部分已被 §1.1 取代）

### 3.1 v2.0 焦点（对应 PRD v2.0 §3.1 五条团队约束）

1. **MCP 与系统集成**：默认可从 JIRA、Plane 等任务管理系统同步任务，从 Confluence 等知识库获取项目知识。
2. **local-first agent 编排**：核心是 local-first 调度 claude、codex、pi 等 agents 完成任务。
3. **跨 agent / 跨会话 / 跨团队上下文传递**：任务上下文支持在 agent 之间、会话之间、团队之间传递。
4. **团队 AI 资产管理**：含但不限于 Specs、Rules、Skills、MCP、交付物，经 GitHub 等代码仓库共享；其中 Rules、Specs、Skills 支持下发。
5. **长任务自动完成与模板**：LoopX 式长任务自动完成；参考其 showcases 提供 issue-fix、pr-commit、auto-research 等场景，形成固定模板。

### 3.2 支撑面（v0.1 已实现，v2.0 继续复用）

- Workspace State Protocol with `LOOP-STATE.json`
- Cross-tool adapter layer, MCP-first and ACP-second
- Loop Engine with scheduler、triage、maker/checker split、stop conditions、run log
- Memory and session continuity with durable local storage
- Skills and reusable workflow knowledge
- Local CLI and local Web UI（Codex 三栏）
- Cost and safety controls（quota / gate）
- Worktree isolation

## 4. Project Status

### 4.1 权威文档索引（冲突时按序号取用，同 §1.1）

| 序 | 文档 | 作用 |
| --- | --- | --- |
| 1 | `docs/product-positioning.md` | 产品定位唯一权威（v2.0 团队版） |
| 2 | `docs/prd/loopdesk-prd-v2.0.zh.md` | 当前权威 PRD（v2.0 完整版） |
| 3 | `docs/plans/loopdesk-webui-design-spec.md` | WebUI 设计规格 v2.0（视觉 + 交互契约） |
| 4 | `docs/design-system.md` | 设计 token 唯一事实源（**v2.0，2026-09-14 定版**）。前端 MUST 以 CSS 自定义属性消费，不得硬编码原始色值 / 尺寸 / 间距 |
| 5 | `docs/design-system/prd-vs-design-draft-deviations.md` | PRD §9.11 × 真实前端设计稿的逐项偏差清单 |

### 4.2 设计稿与实现稿现状

**前端设计稿事实源**：Ardot 设计文件 `724693301521075`（dark 底 + teal 强调色 `#34D399`），共 8 帧：

| Frame | 页面 |
| --- | --- |
| `2:1` | 01 任务看板（默认落地页） |
| `2:236` | 02 团队资产（市场） |
| `2:600` | 03 设置 · Agent 编排 |
| `2:890` | 04 设置 · MCP 连接器 |
| `6:67` | 05 设置 · 其他配置 |
| `6:256` | 06 会话列表抽屉 |
| `6:295` | 07 弹窗 · 添加 Agent |
| `6:329` | 08 弹窗 · 添加连接器 |

**前端实现稿**：`frontend/` —— React 18 + TypeScript + Vite 6 + Tailwind v4，**不引入 UI 库**，手写内联样式 + `src/index.css` 中的 CSS 变量 token；画布 1440×900 原始像素 **1:1 不缩放**（侧栏 240 + 主列 + 预览栏 360）。

- 屏幕：`TaskBoard` / `TeamAssets` / `ControlCenter` / `SettingsAgent` / `SettingsMcp` / `SettingsOther` / `SettingsShell`
- 组件：`LeftRail` / `TopBar` / `ConversationDock` / `icons`
- 覆盖层：`SessionDrawer` / `Modals`

**已作废的旧事实源**：设计系统画布 `724676209058226`（TDesign 蓝"团队管理面"方向，基于错误基线产出）。**不得再作为任何实现依据。**

### 4.3 已删除文档（2026-09-12，移入废纸篓）

| # | 文件 | 作废原因 |
| --- | --- | --- |
| 1 | `docs/web-ui-menu-and-loop-workspace.md` | v0.1 菜单大纲，文件头自声明"已废弃（v0.1）"，PRD §9.11.9 亦标 legacy |
| 2 | `docs/design-system/loopdesk-team-workspace.md` | TDesign 蓝团队管理面设计系统，与已确认真实前端 teal 方向冲突 |
| 3 | `docs/design-system/loopdesk-team-workspace-tokens.css` | 同上（Design Token） |
| 4 | `docs/design-system/loopdesk-team-workspace-components.css` | 同上（组件实现） |
| 5 | `docs/design-system/loopdesk-team-workspace.tailwind.config.js` | 同上（Tailwind 预设） |

> - **恢复方式**：5 个文件均在 `~/.Trash`。其中 #2–#5 **未被 git 跟踪**（新建未提交），硬删不可恢复，故走废纸篓而非 `rm`。
> - **删除后已修正 3 处失效引用**：`docs/plans/loopdesk-webui-design-spec.md` 第 6 行（Companion 行）与 §16 Open Items、`docs/prd/loopdesk-prd-v2.0.zh.md` 第 545 行（落地状态）。
> - **未删但已过版本**（保留作历史）：`docs/prd/personal-loop-workspace-v1.1.zh.md`、`docs/features/loopdesk-v0.1-feature-breakdown.md`。
> - **保留现行**：`docs/design-system.md`（**v2.0 token 事实源**）、`docs/web-ui.md`（已按 v2.0 三栏范式重写）、`docs/design-system/prd-vs-design-draft-deviations.md`。

### 4.4 其余已批准文档

- competitive research: `docs/research/competitive-intel-tutti-wesight-multica.md`（及 `docs/research/competitive-intel*.md` 共 25 份）
- product strategy decision: `docs/decisions/product-strategy.md`
- core feature list: `docs/features/core-feature-list.md`
- architecture: `docs/architecture/personal-loop-workspace.md`
- PRD（v0.2 历史）: `docs/prd/personal-loop-workspace.md`
- risk handling plan: `docs/decisions/risk-handling-plan.md`
- v0.1 implementation plan: `docs/plans/2026-07-07-personal-loop-workspace.md`
- v0.2 channel adapter decision: `docs/decisions/v0.2-channel-adapter.md`
- v0.2 channel adapter feature breakdown: `docs/features/loopdesk-v0.2-channel-adapter-feature-breakdown.md`
- v0.2 FDD/TDD execution plan: `docs/plans/2026-07-14-loopdesk-v02-fdd-tdd-execution-plan.md`
- module audit（模块取舍权威）: `docs/decisions/module-audit-loopdesk-vs-opensquilla.md`
- 全量包名迁移决策: `docs/decisions/full-package-rename.md`
- 前端实现 × PRD §9.11 核对与待优化清单: `docs/design-system/frontend-vs-prd-audit.md`（2026-09-14；含配套审计看板 `frontend-vs-prd-audit-board.png`）
- WebUI × Gateway 任务全生命周期前后端完备性验证: `docs/design-system/webui-frontend-backend-verification.md`（2026-09-16；**三轮记录，最新在前**——正文 §0 为 P1 补齐后 **39/39**、附录 A 为 P0 接线后 23/23、附录 B 为接线前 19/24；复跑脚本 `tests/verify_webui_lifecycle.py`，证据截图 `docs/design-system/webui-p1-status-menu.png` / `webui-p1-copy-feedback.png` / `webui-lifecycle-wired.png`）
- 任务生命周期 REST 契约（唯一权威 = 代码 + 上条报告 §0.3）：`GET|POST /api/v1/projects/{project_id}/tasks`、`PATCH /api/v1/tasks/{task_id}`（生命周期移动）、`POST /api/v1/tasks/{task_id}/gate/decision`（审计裁决）。**裁决 ≠ 状态移动**：只有裁决带批注、落 run log，是唯一能关单的动作；卡片四枚动作据此分成两条路
- 前端数据源模型：**看板 = 画布种子 ⊕ 后端任务集合**（`frontend/src/data.ts` 的运行时叠加层 `setRuntimeTasks` / `allTasks` / `columnOf` / `cardsInColumn` / `boardColumns`）。后端任务只覆盖 `state`，不动画布文案——改看板数据源前先读该文件顶部注释，勿改成「用后端数据替换画布」
- 画布修订 v2（主对象回归任务中心）: 主画布 `724693301521075`（改动落在 `2:1` 与新帧「09 弹窗 · 新建任务」`24:64`）；修订记录画布 `725718927556454`（**仅说明用途，非第二份事实源**）；修订截图 `docs/design-system/canvas-revision/`（2026-09-14）
  - 裁决：主对象 = 任务（Session 降为手动动作渠道）；看板第三列 = **评审中**；右栏三级术语分层（Goal / 审批门 / Run Log 默认折叠）
- LoopX 对标三层文档（**勿重复调研**）：
  - 认知层 `docs/research/competitive-intel-huangruiteng-loopx.md`
  - 建议层 `docs/decisions/loop-management-optimization.md`（优化建议 A~H）
  - 流程层 `docs/plans/2026-09-16-issue-fix-end-to-end-flow.zh.md`（2026-09-16；**细化原型的直接输入**：**两层架构** 任务控制面（LoopX）/ 能力供给面（Agent Runtime）+ 交界契约 + issue-fix 九步真实命令与 packet 字段 + **§5 字段驱动总表** + 20 步时序表 + §8 的 19 个设计点）
  - 术语层 `docs/glossary.md`（**中文为主**：LoopDesk 产品概念 + 循环治理术语 + 遗留词映射）
  - **PRD 回写已完成（2026-09-14）**：`docs/prd/loopdesk-prd-v2.0.zh.md` §9.11.2 架构图 / §9.11.3 L2·L5 / §9.11.4 C1 / §9.11.5 R4 已改写为「评审中（列）+ 审批门（右栏区块）」，并补「列名口径（2026-09-14 冻结）」注；两栏宽度按画布实测校正为 **240 / 360**（原写 ~260 / ~320）。
  - **连带同步**：`docs/plans/loopdesk-webui-design-spec.md` §3.1 架构图与 §4/§5 表格；`docs/web-ui.md` 任务看板段；`docs/design-system/prd-vs-design-draft-deviations.md`（§1 汇总计数 16 / 10 / 14 → **17 / 9 / 14**，与自身明细对齐）；`docs/design-system/frontend-vs-prd-audit.md`（新增 §10 二次复核，覆盖率 13 / 12 / 15 → **17 / 10 / 13**）；`docs/plans/2026-09-14-loopdesk-v2-gap-analysis-and-implementation-plan.md`（原「第三列改为待审批」结论标注作废）
  - 附带修复既有缺陷：看板四列 4×296+3×16=1232 > 主列 840 导致第 3 列被切半、第 4 列不可见 → 四列改等分；顶栏搜索 320→296

### 4.5 实现状态

v0.1 complete；v0.2 channel adapter FDD/TDD 执行中。
**v2.0 产品定位与前端信息架构（Codex 三栏）已确立，前端实现稿 `frontend/` 已启动（TypeScript）。**
Module audit approved：5 Cancel 模块排除于公开面、16 Retain 模块以 LoopDesk 设计功能重述、1 Core 模块树（`src/loopdesk/loop_workspace/`）。Cancel 代码留在源码树，但不得出现在 CLI / Web UI / docs。

### 4.6 文档漂移修复记录（2026-09-14）

**A. `docs/design-system.md` 定为 v2.0**（原为 v0.1-draft，2026-07-15）
- 头部版本、范围与定位叙述改为 v2.0 团队版。
- **Token 值与实现稿重新对齐**：v0.1 值（浅色默认、teal `#0E8F86`、14px 基准、1200px 居中单页 + 双栏）与真实前端**逐项不符**。已按 `frontend/src/index.css` 实测值重写——深色唯一交付、主强调 emerald `#34D399`、基准字号 13px、三栏 240 / `fill` / 360、画布 1440×900 1:1、字体栈 `Geist` / `Geist Mono` / `Noto Sans SC` + `Sarasa Gothic SC`。
- 新增 §10「v0.1 → v2.0 迁移对照」表，旧值逐项标注作废，防止回退。

**B. `opensquilla` 替换残留全部清除**（源头提交 `1ac5cb9` "chore: batch rename opensquilla public surface to loopdesk"）
- **性质**：旧产品名 `OpenSquilla` / `opensquilla` 被无差别替换为 `LoopDesk` / `loopdesk`，凡"新旧对比"的句子即自相矛盾（如 "LoopDesk vs LoopDesk"、"容易把 LoopDesk 误解成 LoopDesk 的换壳"）。
- **修复原则**：只还原被替换破坏的新旧对比；正确的替换一概不动。
- **范围（9 个文件 / 69 处）**：

  | 文件 | 处数 |
  | --- | --- |
  | `docs/decisions/module-audit-loopdesk-vs-opensquilla.md` | 48 |
  | `docs/decisions/full-package-rename.md` | 5 |
  | `docs/prd/personal-loop-workspace.zh.md` | 5 |
  | `docs/prd/personal-loop-workspace-v1.0.zh.md` | 5 |
  | `docs/prd/personal-loop-workspace-v1.1.zh.md` | 5 |
  | `docs/deployment.md` · `docs/releases/loopdesk-v0.1.md` · `docs/plans/2026-07-07-loopdesk-implementation-plan.md` · `docs/plans/2026-07-07-personal-loop-workspace.md` | 各 1 |

- 另修 `docs/releases/loopdesk-v0.2.md` §1 一处**重复句**（同源损坏的不同形态）。
- **判定为语义正确、刻意保留**：`docs/releases/loopdesk-v0.2.md:37`（"Existing LoopDesk installations" 成立，v0.2 晚于 v0.1 品牌发布）、`docs/plans/2026-07-09-v01-loop-lag-implementation-plan.md:86`、`docs/research/competitive-intel-*.md` 中的 LoopDesk 对比表述。
- `AGENTS.md` 原文 golden rule #1 的 "legacy LoopDesk code" 属同源残留，已在 §2 修正。

**C. 连带失效引用已一并修正**（v2.0 定版后产生）
- `docs/plans/loopdesk-webui-design-spec.md` §2 关键 token 块：原写 `--accent #0E8F86 / #15B8A6`、字体基准 14px → 已改为 v2.0 值（emerald `#34D399`、仅深色、13px、三栏 240/`fill`/360）。**该文件是 §4.1 序位 ③ 的权威文档，必须与 ④ 同步。**
- `docs/design-system/prd-vs-design-draft-deviations.md` §9 配色结论：原称设计稿 `#34D399` 与"design-system.md teal 体系"一致——**该结论有误**（`#34D399` 是 emerald，v0.1 的 teal 是 `#15B8A6`）。已改写为"当时的 v0.1 文档与设计稿并不一致，2026-09-14 定版后才一致"。
- `docs/loopdesk-dsh-webui-theme-overlay.md`：引用"设计系统（teal `#15B8A6`）"→ 已改为 v2.0 emerald。

**D. 调研期原型已清理（2026-09-14）**
- `artifacts/loop-management-enhancement.html`：LoopX 对标调研期的**等价 HTML 原型**，使用 v0.1 浅色 token（`--bg-base #FFFFFF`、`--accent #0E8F86`），且自称"配色对齐 docs/design-system.md"——v2.0 定版后该表述已失效，**已于 2026-09-14 删除**。
- **承接关系已核验**：调研结论完整并入 `docs/decisions/loop-management-optimization.md`（§5「本次画布增强范围（A / B / C / E）」与原型的 A/B/C/E 增强范围逐项一致），删除不丢信息。
- **恢复路径**：`~/.Trash/loop-management-enhancement.html`。该文件**未被 git 跟踪**（硬删不可恢复），故走废纸篓；SHA-256 留档：`7a2ae639ab5ec40a1739ea8c37a87a17727fe60ce5bb24e1a8862d1a634bcae6`。
- 空目录 `artifacts/` 一并移除（顶层目录，无 CI / 构建 / 脚本依赖；注意与文档中 **workspace-level `artifacts/` 目录契约**（`memory/skills/artifacts/worktrees`）无关，勿混淆）。

### 4.7 变更纪律

- **旧名/新名对比不得只留一个**：凡涉及 `OpenSquilla`（旧）与 `LoopDesk`（新）的对比表述，必须两个名字同时出现，禁止因批量替换退化为单名自指。
- **设计与实现同步**：任何 token 改动必须**同时**更新 `docs/design-system.md` 与 `frontend/src/index.css`，两侧不得独立演进。
- **视觉事实源唯一**：设计侧只认 Ardot `724693301521075`；`724676209058226` 已作废。

## 5. Development Workflow

### 5.1 Feature-driven task breakdown

- Break work into features first, then into small executable tasks.
- Each feature must have:
  - feature goal
  - scope in/out
  - affected files
  - Loop Engineering run format
  - acceptance criteria
  - rollback criteria
- Save feature plans under `docs/plans/` and link them from this file or `docs/README.md`.

### 5.2 Test-driven implementation

For every implementation task:
1. Write the minimal failing test first.
2. Run only that test and confirm the expected failure.
3. Implement the smallest code that makes the test pass.
4. Run the full targeted test suite for the touched area.
5. Fix regressions before moving to the next task.
6. Keep unrelated legacy surfaces untouched unless explicitly approved.

### 5.3 Loop Engineering execution

Default loop for each feature/task:
- Triage: choose the smallest useful next step
- Maker: implement one task with failing-test-first discipline
- Checker: run focused tests, lint, and boundary checks
- Escalation: stop and update docs/plans if scope, naming, or legacy coupling risk appears
- Run log: record started task, result, next step, and risk note in the plan/doc or loop state
- Stop condition: feature acceptance criteria are met and no unresolved public-surface leak remains

## 6. Review Gates

Run these gates before claiming any feature or task complete:
- feature docs are saved and versioned under `docs/`
- failing test exists before implementation
- targeted tests pass after implementation
- **定位一致性**：新增公开面 MUST 与 §1.1 的 v2.0 团队定位一致，不得回退到 v0.1 单人叙事（"个人版 / 独立开发者 / personal loop workspace"）
- **范围护栏**：不得意外暴露 强实时云房间、多租户 SaaS、重桌面 Electron 壳、云托管计费、broad media skills、cron-first 叙事（见 §1「Not this」与 PRD v2.0 §3.3「明确不采纳清单」）
- **事实源合规**：视觉与交互实现 MUST 取自 §4.1 的 ④⑤；设计侧以 Ardot `724693301521075` 为准，**不得**引用已作废画布 `724676209058226` 或已删除的 TDesign 蓝文档
- naming follows the unified `LoopDesk` / `loop_workspace` / `LOOP-STATE.json` boundary
- risk handling plan remains satisfied; if not, update `docs/decisions/risk-handling-plan.md`

## 7. How to Use This File

- Read this file before starting any LoopDesk implementation task.
- If this file conflicts with a more specific `AGENTS.md` in a subdirectory, the more specific instruction wins for files within that subdirectory's scope.
- If you change this file, also review whether `docs/project/loopdesk-project-initialization.md` needs the same update.
