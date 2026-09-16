# 竞品调研：mindfold-ai/Trellis

> 调研时间：2026-09-09
> 调研对象：https://github.com/mindfold-ai/Trellis（AGPL-3.0，Mindfold LLC）
> 定位：开箱即用的 AI 编码工程框架（agent harness）
> 关联项目：LoopDesk（本仓库 v0.1 个人循环工作区）
> 调研口径：基于 main 分支公开源码、README、`.trellis/` 体系与 `packages/` 实现

---

## 1. 一句话结论

Trellis 是一个**“项目层的 agent harness”**：把规范（specs）、任务（tasks/PRD）、记忆（memory/journal）持久化进仓库，通过 CLI 生成适配 22 个 AI 编码平台的配置文件，并用一套 4 阶段循环（Plan → Implement → Verify → Finish）+ 子代理（sub-agent）机制驱动任意编码代理按团队工程标准工作。它与 LoopDesk 高度同质——同样是“local-first、跨工具、记忆/规范/任务入仓”路线，但 Trellis 走 **TypeScript/Python CLI + 平台配置生成 + 大量 hooks/skills** 的实现路径，并已具备 **channel（并行多 worker 调度）** 这一 LoopDesk 当前没有的能力维度。

---

## 2. 基本信息

| 项 | 值 |
| --- | --- |
| 仓库 | `mindfold-ai/Trellis`（Public） |
| 标语 | "The best agent harness."（最好的代理套件/框架） |
| 协议 | **AGPL-3.0**（注意：强 copyleft，商业闭源集成有合规风险） |
| 热度 | ⭐ ~14.6k Stars ｜ 🍴 817 Forks ｜ 1,358 Commits |
| 官方文档 | https://docs.trytrellis.app/ |
| 运行时 | Node.js >= 18.17，Python >= 3.9 |
| 包形态 | npm 全局 CLI `@mindfoldhq/trellis@latest`（别名 `tl`），pnpm monorepo |
| 版本 | CLI / core 均为 `0.6.16` |
| 主题标签 | `agentic-coding`、`ai-workflow`、`claudecode`、`codex`、`harness` |

> ⚠️ 合规提示：AGPL-3.0 对 LoopDesk 的直接代码复用不友好。若需借鉴，应只吸收**设计思路/工作流结构**，避免复制源码或衍生闭源产品。

---

## 3. 解决的痛点（与 LoopDesk 完全一致）

1. AI 每次会话从零开始，无项目记忆、无团队约定、无需求上下文。
2. `CLAUDE.md` / `AGENTS.md` / `.cursorrules` 容易变成 monolithic 单文件，难以按范围注入。
3. 多 AI 工具间工作流无法复用——每换一个工具就要重建一遍规范。
4. 团队标准难以被审查、版本化、像普通代码 artifact 一样改进。

Trellis 的差异化主张：**把规范做成可作用域注入（scoped injection）+ 任务 PRD + 工作流门禁 + 跨会话 workspace 记忆 + 平台感知生成文件**，围绕它们组织。

---

## 4. 架构总览

### 4.1 仓库形态

- **Monorepo（pnpm workspace）**：`packages/cli`（CLI 入口）、`packages/core`（SDK：`channel` / `mem` / `task` / `testing` 领域原语）。
- **Git 子模块**：`docs-site`（文档站）、`marketplace`（技能/模板市场）。
- **工程辅助**：Husky + lint-staged（`.husky` / `.lintstagedrc`）、Pyright（`pyrightconfig.json`，核心 Python 脚本做类型检查）、Prettier、ESLint、Vitest。
- **根级契约文件**：`AGENTS.md` / `CLAUDE.md` / `README.md` / `CONTRIBUTING.md`（含中文 `README_CN.md` / `CONTRIBUTING_CN.md`）。

### 4.2 核心数据层：`.trellis/`

```
.trellis/
├── config.yaml            # 项目级配置（包声明、channel worker guard、Codex dispatch、注入上限等）
├── workflow.md            # 工作流状态机“单一事实源”（被 hooks 解析，非散文）
├── .version / .template-hashes.json / .gitignore
├── spec/                  # 规范：按 package/layer 组织，index.md 入口 + 具体规则文件
│   ├── <package>/<layer>/index.md
│   ├── guides/            # 跨包的thinking guides
│   ├── tech/  cli/  core/  docs-site/
├── tasks/                 # 任务：每个任务一个目录
│   └── {MM-DD-name}/
│       ├── task.json  prd.md  design.md  implement.md
│       ├── implement.jsonl  check.jsonl   # 子代理上下文清单（spec/research 引用）
│       └── research/  archive/
├── workspace/             # 记忆：按开发者隔离
│   ├── <developer>/journal-N.md   # 会话日志，单文件上限 2000 行自动轮转
│   └── index.md
├── agents/                # 子代理/skill 定义（plan/implement/check/research/architect…）
└── scripts/               # Python 实现的引擎脚本（task.py / add_session.py / get_context.py…）
```

**关键设计**：`.trellis/` 是“真源”，各平台目录（`.claude/`、`.cursor/`、`.codex/`、`.opencode/`、`.agents/`、`.pi/`、`.omp/` 等）是 `trellis init/update` 据此**生成/同步**出来的派生文件。这与 LoopDesk 的“runtime library + 平台适配器生成”思路高度同源。

### 4.3 CLI 命令面（`packages/cli/src/commands/`）

| 命令 | 作用 |
| --- | --- |
| `trellis init` | 在仓库初始化，按平台（--cursor/--codex/--opencode…）生成适配文件；`-u <name>` 设定开发者身份 |
| `trellis update` | 把模板/工作流新版本推送到下游用户项目（block 级受控替换，保留用户手动编辑） |
| `trellis upgrade` | 升级 CLI 自身 |
| `trellis uninstall` | 永久移除 Trellis 产物 |
| `trellis ablate` / `restore` | 临时移除/精确恢复项目内 Trellis 文件，做“有/无”A/B 对比（带 verifiable recovery transaction，路径冲突即拒绝写入） |
| `trellis workflow` | 查看/管理工作流 |
| `trellis mem` | 记忆相关操作 |
| `trellis channel *` | **并行多 worker 调度**（见第 7 节） |

依赖：`commander`（CLI）、`inquirer`（交互）、`chalk`、`figlet`、`giget`、`undici`、`zod`（>=4，配置校验）、`@mindfoldhq/trellis-core`。

---

## 5. 三大核心概念（spec / task / workspace）

### 5.1 Spec（规范，作用域注入）
- 路径 `.trellis/spec/<package>/<layer>/index.md`，内含 **Pre-Development Checklist** + **Quality Check**；具体规则放被引用的 `.md`。
- 通过 hook/skill **按需注入**到会话，而不是靠记忆召回（“Specs injected, not remembered”）。
- `get_context.py --mode packages` 列出所有 package + spec 层级及路径。
- 可让 AI 先从现有代码起草 spec，再人工收紧高信号规则。

### 5.2 Task（任务中心工作流）
- 每任务独立目录 `.trellis/tasks/{MM-DD-name}/`，含 `task.json`、`prd.md`（轻量任务可仅 PRD）、`design.md`/`implement.md`（复杂任务必需）、`research/`、`implement.jsonl`/`check.jsonl`。
- 生命周期（Python `task.py`）：`create` → `start`（status: planning→in_progress）→ `finish`（清活动指针）→ `archive`（移入 `archive/{year-month}/`，status: completed）。
- 支持 parent/child 任务树（非依赖系统，依赖顺序写在 child 的 prd/implement 里）。
- 上下文清单 `implement.jsonl`/`check.jsonl`：每行 `{"file":"<path>","reason":"<why>"}`，由 AI 在规划期向子代理填充“该注入哪些 spec/research”，超上限降级为 index 行（见 `config.yaml` 的 `context_injection`）。
- 生命周期 hooks（`after_create/after_start/after_finish/after_archive`）可挂 shell 命令。
- 支持 `set-branch` / `set-base-branch` / `create-pr`（PR 创建，含 `--dry-run`）。

### 5.3 Workspace（项目记忆，按人隔离）
- `.trellis/workspace/<developer>/journal-N.md`：会话日志，`max_journal_lines: 2000` 自动轮转；`index.md` 记录总会话数与最后活跃。
- 开发者身份由 `init_developer.py` 初始化（写 `.trellis/.developer`，gitignored）。
- 个人日志按人分离，共享 spec/task 入仓——天然避免团队冲突（也是 FAQ 重点）。

---

## 6. 工作流引擎（4 阶段循环 + 子代理）

`workflow.md` 是一个**被脚本解析的状态机**，不是纯文档。其中 `[workflow-state:STATUS]` 块是每轮 `<workflow-state>` breadcrumb 的**唯一事实源**（v0.5.0-rc.0 起脚本不再内嵌文本），由 `inject-workflow-state.py`（Python 平台）/ `.js`（OpenCode 插件）解析，配合 `UserPromptSubmit` 类 hook 注入。

### 阶段划分
- **Phase 1 Plan**：分类请求 → 取得“建任务同意” → 写 PRD/design/implement → 配置上下文（jsonl）→ `task.py start`（in_progress）。
- **Phase 2 Execute**：`trellis-implement` 子代理写码（不自动 git commit）→ `trellis-check` 子代理审查 diff + 跑 lint/type/test 并自修。
- **Phase 3 Finish**：`trellis-update-spec` 把新认知提升回 `.trellis/spec/` → 批量 commit（work commits → archive commit → journal commit，三阶段不交错）→ `/trellis:finish-work` 归档并更新 journal。

### 子代理/skill 体系（`.trellis/agents/`）
- `trellis-brainstorm`：逐条提问写 PRD（一个好问题一次，优先研究、优先给选项）。
- `trellis-research`：研究子代理，结果持久化到 `research/`。
- `trellis-implement` / `trellis-check`：实现/审查子代理（Agent 形态优先；某些平台也作为 Skill）。
- `trellis-update-spec`：把经验写回 spec（Skill 形态）。
- `trellis-break-loop`：重复调试时做根因归类与预防。
- `plan.md`（Codex provider）：把模糊需求转成可交付计划（不写码）。

### 平台分发双模
- **sub-agent-dispatched 平台**（Claude Code、Cursor、OpenCode、Codex、Kiro、Gemini、Qoder、CodeBuddy、Copilot、Droid、Pi、ZCode、Snow、Reasonix、Trae、Grok、Kimi Code 等）：主会话派发 implement/check 子代理，jsonl 注入上下文；派发提示必须 `Active task: <path>` 开头，且子代理不得再派生子代理（self-exemption）。
- **inline 平台**（codex-inline、Kilo、Antigravity、Devin、DeepSeek Harness 等）：主会话直接改码，用 `trellis-before-dev` 加载规范，`trellis-check` 做审查，跳过 jsonl curation。

> 这与 LoopDesk 的“runtime-matrix / 多平台适配”目标一致；Trellis 已显式枚举 22 个平台并区分 inline vs sub-agent 两类派发语义。

### 门禁/护栏（Guardrails）
- 建任务同意 ≠ 实现同意；实现必须等 `task.py start` 且 artifact 评审通过。
- 轻量任务可仅 PRD；复杂任务必须 `prd.md`+`design.md`+`implement.md`。
- 规划必须落盘到 task artifact；报告完成前必须跑检查。
- commit 严格三阶段、不 amend、不 push 远端；含“未识别的脏文件”需用户确认。

---

## 7. Channel：并行多 Worker 调度（LoopDesk 当前缺失的能力维度）

`packages/cli/src/commands/channel/` + `packages/core/src/channel/` 提供一套**并行 agent worker 运行时**：

- `trellis channel spawn` 派生子 worker；`supervisor.ts` 监督；`guard.ts` 做 OOM/资源护栏。
- **Worker guard 配置**（`config.yaml` 的 `channel.worker_guard`）：
  - `idle_timeout: 5m`（空闲清理；`0` 关闭）
  - `max_live_workers: 6`（spawn 时预算检查；`0` 关闭）
  - 优先级：CLI flag > env（`TRELLIS_CHANNEL_WORKER_IDLE_TIMEOUT` / `TRELLIS_CHANNEL_MAX_LIVE_WORKERS`）> config > 内置默认。
  - `trusted_context_dirs`：扩展 `--file/--jsonl/--agent` 的 containment 检查，支持 `.trellis/tasks`/`.trellis/workspace` 为外部 symlink 的情况（`auto_trust_trellis_symlinks` 默认开）。
- 配套命令：`create` / `run` / `send` / `messages` / `threads` / `list` / `kill` / `rm` / `interrupt` / `wait` / `title`，以及 `store/`、`adapters/`（平台适配器）、`agent-loader.ts`、`context-loader.ts`、`context-trust.ts`。
- `core/src/channel` + `core/src/mem` + `core/src/task` 把“channel / mem / task”做成可被 CLI 与下游 Node 服务消费的领域 SDK（导出 `@mindfoldhq/trellis-core` 子路径）。

**意义**：Trellis 不止是“规范+记忆+任务”的静态框架，它还提供**运行时并行调度层**，可同时跑多个 agent worker 并做资源护栏。这是 LoopDesk v0.1（单工作区状态协议 + 适配器）尚未覆盖的维度。

---

## 8. 关键设计决策与可借鉴点

1. **真源 + 派生生成**：`.trellis/` 是单一真源，平台文件由 CLI 生成/同步，`update` 可 block 级受控覆盖并保留用户手动编辑（`trellis update` 保留 `.codex/agents/*.toml` 的模型 pin 编辑）。→ 与 LoopDesk 适配器思路一致，可参考其“保留用户编辑”的 update 策略。
2. **工作流即被解析的状态机**：`workflow.md` 的 `[workflow-state:*]` 块是 breadcrumb 唯一事实源，配测试（`test/regression.test.ts`）保证每个 `[required·once]` 步骤都有强制行——避免“AI 静默跳过必做步骤”（他们曾因 Phase 1 规划门、Phase 3.4 commit 缺口踩过坑）。→ LoopDesk 的 loop 状态/stop condition 可借鉴“状态机 + 回归测试守护”。
3. **作用域 spec 注入 vs 单文件**：明确反对 monolithic CLAUDE.md，spec 按 package/layer 切分并按需注入。→ 与 LoopDesk “loop 记忆层级/作用域”理念一致。
4. **记忆按人隔离、规范/task 入仓**：天然规避团队 git 冲突。→ LoopDesk memory 设计可参考。
5. **ablate/restore 可验证回滚**：做“有/无 Trellis”A/B 对比，且带 verifiable recovery transaction、路径冲突拒绝写入。→ LoopDesk 的“工作区隔离/回滚”可参考其事务化思路。
6. **commit 三阶段严格分离 + 不 push**：work commits → archive commit → journal commit，不 amend、不 push，未识别脏文件需确认。→ 可纳入 LoopDesk 的 run log / 安全控制。
7. **context_injection 字节上限 + 降级为 index 行**：防止超大上下文爆 token。→ LoopDesk 上下文管理可参考。
8. **平台 inline vs sub-agent 双派发语义**：统一管理 22 平台差异。→ LoopDesk runtime-matrix 可参考其分类法。

---

## 9. 与 LoopDesk 的对比（竞争情报视角）

| 维度 | Trellis | LoopDesk（本仓库 v0.1） |
| --- | --- | --- |
| 本质 | 项目层 agent harness（规范/任务/记忆入仓 + 平台生成） | 个人循环工作区（本地优先，跨工具记忆/状态一致） |
| 协议 | AGPL-3.0（强 copyleft） | 见本仓库许可证（需复核；建议与 Trellis 形成许可差异化） |
| 技术栈 | TS/Python CLI（pnpm monorepo）+ 大量 Python 引擎脚本 + hooks/skills | Python 为主（见 `src/loopdesk/`） |
| 核心数据 | `.trellis/{spec,tasks,workspace,agents,scripts}` | `LOOP-STATE.json` + loop_workspace |
| 平台适配 | 显式生成 22 平台配置 + inline/sub-agent 双派发 | MCP 优先、ACP 其次的适配器层（见 AGENTS.md） |
| 工作流 | 4 阶段循环（Plan/Implement/Verify/Finish）+ 子代理 + 状态机 breadcrumb | Loop Engineering（triage→maker→checker→escalation→run log→stop） |
| 并行调度 | **有 channel（多 worker + supervisor + OOM guard）** | 当前 v0.1 聚焦单工作区，未覆盖并行 worker |
| 记忆 | 按开发者 journal + 规范提升回 spec | 记忆层级 + durable local storage |
| 模板/市场 | 有 `marketplace` 子模块 + `docs-site` | 见 roadmap（skills/workflow 知识） |
| 消融对比 | `ablate`/`restore` 事务化 | 工作树隔离（worktree isolation） |
| 受众 | 个人 + 团队（强调团队共享标准） | 独立开发者优先（个人循环工作区） |

### 对 LoopDesk 的机会与威胁
- **威胁**：Trellis 已 14.6k star、AGPL 强开源、22 平台覆盖、且有并行 channel 调度，生态与心智占位快。LoopDesk 若定位重叠（同为“跨工具记忆/规范/任务”）需明确差异化。
- **机会（差异化方向）**：
  1. **许可差异化**：LoopDesk 若采用更宽松协议，可在“闭源/商业集成”场景避开 AGPL 雷区。
  2. **local-first 纯粹性**：LoopDesk 主打“不是 AI IDE、不是多渠道 agent 套件、不是团队协作平台”，可把“个人循环”做深做轻，避免 Trellis 的 22 平台生成复杂度。
  3. **MCP/ACP 优先而非文件生成**：LoopDesk 已有 MCP-first 适配器边界，可强调“运行时协议”而非“生成一堆平台配置文件”。
  4. **补 channel 维度**：评估是否在 v0.2 引入受护栏的并行 worker（借鉴 Trellis worker_guard 设计）。
  5. **状态机 + 回归测试守护**：借鉴 Trellis “workflow 状态机 + regression test 保证必做步骤不被跳过”的做法强化 Loop Engineering 门禁。

---

## 10. 待办 / 建议下一步

1. 复核 LoopDesk 当前许可证，确认与 AGPL-3.0 的差异化表述（写入 `docs/decisions/`）。
2. 评估 `channel`（并行 worker + OOM guard）是否纳入 v0.2 feature 列表（参考 `docs/features/loopdesk-v0.2-channel-adapter-feature-breakdown.md`）。
3. 借鉴 Trellis 的“工作流状态机 + regression 守护”与“ablate 事务化回滚”，补充 Loop Engineering review gates。
4. 如需更深，可继续读取：`packages/cli/src/commands/init.ts`（71KB，平台生成逻辑）、`update.ts`（93KB，模板同步）、`core/src/channel/*`（并行运行时实现）、`.trellis/spec/cli/backend/workflow-state-contract.md`（状态机运行时契约）。

---

## 11. 关键源码索引（main 分支）

| 关注点 | 路径 |
| --- | --- |
| CLI 入口/命令 | `packages/cli/src/commands/`（init/update/upgrade/uninstall/ablate/mem/workflow/channel） |
| 核心 SDK | `packages/core/src/{channel,mem,task,testing}/` |
| 项目配置 | `.trellis/config.yaml` |
| 工作流状态机 | `.trellis/workflow.md` |
| 规范体系 | `.trellis/spec/<package>/<layer>/index.md` |
| 任务引擎（Python） | `.trellis/scripts/task.py`、`add_session.py`、`get_context.py`、`init_developer.py` |
| 子代理定义 | `.trellis/agents/{plan,implement,check,research,architect}.md` |
| 并行调度 | `packages/cli/src/commands/channel/{spawn,supervisor,guard}.ts`、`packages/core/src/channel/` |
| 包元数据 | `packages/cli/package.json`（`@mindfoldhq/trellis` v0.6.16）、`packages/core/package.json` |
