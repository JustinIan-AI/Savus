# 竞品调研：Tencent/teamai-cli

> 调研时间：2026-09-09
> 调研对象：https://github.com/Tencent/teamai-cli（MIT，Tencent / jeffyxu）
> 定位：让每个团队都成为 AI 原生团队（Make Every Team AI Native）的团队级 AI 资产分发 + 知识库 CLI
> 关联项目：LoopDesk（本仓库 v0.1 个人循环工作区）
> 调研口径：基于 main 分支公开源码、README/README.zh-CN、docs/usage-guide、src/ 实现清单

---

## 1. 一句话结论

TeamAI CLI 是一个**“团队级 AI 资产分发 + 共享知识库 + 团队改进度量”**工具，由腾讯开源（MIT 许可）。它的核心不是个人工作流 harness，而是**把团队的 skills / rules / agents / hooks / MCP / env 放进一个共享 Git 仓库，用 `push → MR → review → pull` 的协作流把资源同步到每个成员本地的各种 AI 编程工具目录（如 `~/.claude/skills`）**；并额外提供 BM25 + 代码图增强检索的团队知识库、基于“摩擦信号”的自动经验沉淀、以及周报/dashboard 的团队改进度量。

与 Trellis（项目层个人/团队 harness）和 LoopDesk（local-first 个人循环工作区）相比，TeamAI 的重心更偏 **“跨成员分发”与“团队知识/度量”**，且许可为宽松 MIT，对商业/闭源集成更友好。

---

## 2. 基本信息

| 项 | 值 |
| --- | --- |
| 仓库 | `Tencent/teamai-cli`（Public） |
| 口号 | "Make Every Team AI Native" |
| 协议 | **MIT**（宽松，商业闭源友好——对比 Trellis 的 AGPL-3.0 是显著差异化） |
| 热度 | ⭐ ~2.5k Stars ｜ 🍴 162 Forks ｜ 671 Commits |
| 包形态 | npm 全局 CLI `teamai-cli`（bin: `teamai`），tsup 打包，TypeScript |
| 版本 | `0.22.0`（standard-version 发版） |
| 运行时 | Node.js（npm 全局安装） |
| 文档 | 英文 + 简体中文双语（`README.zh-CN.md`、`docs/usage-guide.zh-CN.md`）；`docs/designs/` 含设计文档 |
| 作者 | jeffyxu <jeffyxu@tencent.com> |
| 关联组织 | `teamai-hub`（提供预置 skills/rules/review agents 的模板仓库） |

---

## 3. 解决的痛点（与 LoopDesk 部分重合，但更偏团队）

1. 团队的 AI 使用经验（skills、rules、编码规范、自动化脚本、领域知识）散落在个人，无法一致地作用于每个代理。
2. 每个 AI 工具（Claude Code / Codex / Cursor / CodeBuddy …）配置各写一份，难以统一与版本化。
3. 团队缺乏“上下文共享”与“持续改进”闭环：经验不被沉淀、AI 执行不被度量。

TeamAI 用三层架构对应这三个目标：**Team Execution（让每个代理按团队方式工作）× Team Context（让每个代理理解团队）× Team Improvement（让每次执行改进团队）**。

---

## 4. 架构总览

### 4.1 三层产品架构

| Layer | Job | CLI 实现 |
| --- | --- | --- |
| **Team Execution** | 让每个代理按团队方式工作 | `init` / `pull` / `push`，skills、rules、agents、hooks、MCP、env |
| **Team Context** | 让每个代理理解团队 | recall（召回）、learnings（经验）、codebase graph（代码图）、teamwiki |
| **Team Improvement** | 让每次执行改进团队 | 基于摩擦的 share-learnings、sessions、digest、dashboard |

### 4.2 分发数据流（核心机制）

```
teamai push → 创建分支 + MR → 审阅者批准并合并
                                 ↓
         SessionStart hook → teamai pull → 同步到本地 AI 工具（如 ~/.claude/skills）
```

- 资源（skills/rules/docs/agents/hooks/mcp）存放在**团队共享 Git 仓库**（支持 GitHub / GitLab / GitCode / CNB / TGit / 私有 Git）。
- 管理员 `teamai push` 开 MR，成员审阅合并；合并后 `teamai pull` 在**会话启动钩子（SessionStart hook）**自动触发，把最新资源写入各工具的本地目录（如 `~/.claude/skills/`、`~/.codex/skills/`、`~/.cursor/skills/`、`~/.codebuddy/skills/`）。
- 同一资源仍在未合并 PR 中时再次 `push` 会**原地更新该 PR**而非重复开 PR。
- 项目级（project-scope）init 默认把资源装到项目目录；`--scope user` 装到 `~/`。project-scope 下 SessionStart 会先创建该工具的 project root 再 pull。

### 4.3 仓库形态与实现

- **纯 TypeScript CLI**（tsup 打包，bin `teamai`）。核心代码全在 `src/`（~120 个 `.ts` 文件），含完整 `test/`、`src/__tests__/` 与 e2e（`vitest.e2e.config.ts`）。
- 仓库自带 `skills/`（内置 `teamai-share-learnings`、`team-wiki-codebase`）、`agents/`（内置 `teamai-recall` 子代理）、`docs/`、`examples/ci/`。
- 关键模块（按 README + src 清单推断职责）：
  - 分发：`init.ts`(54KB)、`pull.ts`(70KB)、`push.ts`(36KB)、`team-push.ts`、`hooks.ts`(44KB)、`mcp-reconcile.ts`、`source.ts`、`roles.ts`、`tags.ts`。
  - 知识：`codebase-extract.ts`(32KB)、`code-knowledge-recall.ts`、`recall.ts`、`wiki-engine/`、`deep-enrich.ts`、`import-*.ts`（repo/org/mr/local/iwiki）。
  - 改进：`dashboard-collector.ts`(48KB)、`dashboard-html.ts`、`digest.ts`、`save-session.ts`、`contribute.ts`、`session-analytics.ts`、`usage-tracker.ts`。
  - 平台适配器：`local-agent.ts`(132KB)、`known-agents.ts`、`hook-dispatch*.ts`、`opencode-hooks.ts`、`openclaw-hooks.ts`、`hermes-*.ts`、`project-agent-root.ts`。
  - 配置/类型：`config.ts`、`types.ts`(74KB)、`agent-version.ts`、`bootstrap.ts`、`migrate.ts`、`uninstall.ts`(35KB)。

### 4.4 技术栈与关键依赖

- 语言/打包：TypeScript + tsup；测试 Vitest（含 coverage、e2e）。
- 配置：YAML（`teamai.yaml` / `hooks.yaml` / `mcp.yaml`）、Markdown、TOML（`smol-toml`）；front-matter 解析用 `gray-matter`。
- Git 操作：`simple-git`（clone/push/PR 流程）、`semver`。
- 校验：`zod`（^3.24）。
- 代码图解析：**WASM tree-sitter**（`web-tree-sitter` + `tree-sitter-wasms`）用于 TS/JS/Python/Go 的 AST 精确边；Java/Rust 等用正则启发式（heuristic）兜底。WASM 为纯 JS 依赖，无需原生工具链；失败回退启发式并记 `AST_UNAVAILABLE`；`TEAMAI_SKIP_AST=1` 强制启发式。
- 检索：BM25 全文检索 + 图增强重排序（graph-boost re-ranking）（见 `code-knowledge-recall.ts` / `recall.ts`）。
- 其他：`fs-extra`、`cross-spawn`、`fflate`、`listr2`、`ora`、`chalk`、`commander`。

---

## 5. 核心能力详解

### 5.1 Team Execution（团队执行 / 资源分发）
- 同步对象：skills、rules、docs、env、agents、hooks、mcp，跨 Claude Code / Codex / Cursor / CodeBuddy / WorkBuddy / OpenCode / OpenClaw / Hermes / DeepSeek Harness / Qoder 等。
- **团队 Hooks**：在 `hooks/hooks.yaml` 声明式定义（`event: PreToolUse`、`matcher: Bash`、`command: ...`、`tools: [claude, cursor]`），`pull` 注入到每个工具；`teamai hooks list/inject/remove` 管理。
- **团队 MCP**：在 `mcp/mcp.yaml` 声明一次（`transport: stdio|http|sse`，`${VAR}` 注入密钥），`pull` 写各工具原生配置；`teamai mcp list/inject/remove`。
- **团队包（Team Packages）**：`teamai packages install <npm|claude-plugin>`，声明并恢复团队的 npm 包与 Claude 插件。
- **分发控制（精细订阅）**：
  - **Roles**：`teamai roles` 定义 role→namespace 映射，成员只同步自己角色对应的 skills。
  - **Tags**：`teamai tags` 给 skill/rule 打标签，成员按标签订阅。
  - **Sources**：`teamai source add <其他团队/组织公共仓库>`，订阅的外部 skills 在下次 pull 自动同步。
- `teamai status` 显示本地与团队仓库 diff；`teamai skill exclude` 管理本地排除；`teamai remove` 删资源并开 MR。

### 5.2 Team Context（团队上下文 / 知识）
- **自动经验分享（friction-based）**：会话结束的 Stop hook 按“摩擦信号”打分——你打断/纠正了 AI、拒绝了工具调用、或 AI 反复重试失败的工具。长但例行的会话不触发；真正“啃过问题”的会话才触发。高分时建议运行 `/teamai-share-learnings` 把会话摘要推到团队仓库。提示可整体关闭（`sharing.contributeHint.enabled: false`）。
- **团队知识召回（recall，默认关闭需显式开启）**：`teamai recall enable` 部署内置 `teamai-recall` 子代理（`agents/teamai-recall.md`）并注入引导规则；任务前子代理先跑 `teamai recall --check` 相关性预检，无关则跳过检索，否则抽取关键词→BM25 检索→读命中源文件→返回结构化摘要。`teamai recall promote` 把高置信 learning 提升为正式 skills/rules/docs；`teamai recall maintenance` 维护 KB 健康（剪枝低置信、回写分数、标陈旧）。
- **代码库知识图谱（codebase graph / teamwiki）**：`teamai import --from-repo/--from-org` 或 `teamai codebase --extract` 把源码解析为 `teamwiki/` 下的结构化图，存组件/接口/配置与跨仓库 `DEPENDS_ON`/`REFERENCES`/`IMPLEMENTS` 边（AST 轨道优先，启发式轨道补充）。`teamai recall` 用图做 boost 重排；命中附 `Sources:` 列出源文件路径，给 agent 直接的改动起点。`teamai codebase --lint` / `teamai ci extract-mr` 做图健康与 CI 知识抽取。

### 5.3 Team Improvement（团队改进 / 度量）
- **Usage digest**：`teamai digest` 生成周报——token 用量、对话量、干预率（intervention rate）。
- **Sessions**：`teamai session save` 记录脱敏（privacy-scrubbed）的每会话摘要（工具序列、prompt 轮次、干预），`--push` 喂给 digest 的 Session Highlights。
- **Dashboard**：`teamai dashboard` 启动 Web 仪表盘，显示成员实时会话状态、干预次数、token 用量；含 **KB Health** 页（按类型覆盖率、Top 召回、静默条目、召回趋势、作者贡献、维护控制台）。由 `dashboard-collector.ts` / `dashboard-html.ts` 实现。
- **Votes / review**：`votes.ts`、`review-cmd.ts`、`review-store.ts` 支持对知识/资源的投票与评审。

---

## 6. 与 LoopDesk 的对比（竞争情报视角）

| 维度 | TeamAI CLI | LoopDesk（本仓库 v0.1） |
| --- | --- | --- |
| 本质 | 团队级 AI 资产分发 + 共享知识库 + 改进度量 | 个人循环工作区（本地优先，跨工具记忆/状态一致） |
| 协议 | **MIT**（宽松） | 见本仓库许可证（建议与 MIT/AGPL 形成差异化表述） |
| 技术栈 | TypeScript CLI（tsup），tree-sitter WASM，zod，simple-git | Python 为主（见 `src/loopdesk/`） |
| 核心机制 | `push→MR→review→pull` 同步到各工具本地目录 | `LOOP-STATE.json` + loop_workspace + MCP/ACP 适配器 |
| 主要对象 | skills / rules / agents / hooks / MCP / env | 规范、记忆、loop 状态、skills/artifacts |
| 知识管理 | BM25 + 代码图增强检索（`teamwiki/`）、friction 沉淀 | 记忆层级 + durable local storage |
| 多工具支持 | 10+ 平台 + 多 Git 提供商 | MCP 优先、ACP 其次的适配器层（AGENTS.md） |
| 改进度量 | digest / sessions / dashboard（含 KB Health） | cost/safety 控制、run log（v0.1） |
| 受众 | 团队（强调跨成员一致分发）+ 可 solo | 独立开发者优先 |
| 许可友好度 | 高（MIT，可闭源集成） | 取决于本仓库许可证 |

### 对 LoopDesk 的机会与威胁
- **威胁**：腾讯背书 + MIT 宽松许可，在“团队 AI 资产分发/知识沉淀/度量”场景心智占位快；LoopDesk 若仅做个人循环工作区，团队维度会被 TeamAI 抢先。
- **机会（差异化方向）**：
  1. **local-first 纯粹性 + 个人闭环**：LoopDesk 主打“不是团队平台”，把个人记忆/状态/loop 做深做轻，避开 TeamAI 的 Git 仓库托管与 MR 协作复杂度。
  2. **许可差异化**：若 LoopDesk 采用与 MIT 不同但同样宽松或更明确的协议，可针对“不想引入 Git 协作依赖”的个人/小团队定位。
  3. **运行时协议而非文件分发**：LoopDesk 的 MCP/ACP 适配器更偏“运行时协议”，TeamAI 偏“把文件写进各工具目录”——前者在动态上下文注入上更灵活。
  4. **可借鉴能力**：
     - **friction-based 经验沉淀**：用“打断/纠正/重试”信号触发经验总结，比“每次都总结”更省噪声（可在 LoopDesk 的 loop 日志/run log 中借鉴）。
     - **代码图增强检索（teamwiki）**：tree-sitter WASM + 启发式双轨、BM25 + 图 boost 重排，是 LoopDesk 记忆/上下文检索可参考的实现路径。
     - **分发控制（roles/tags/sources）**：若 LoopDesk 未来做团队层，可参考 namespace + 标签订阅的精细分发。
     - **KB Health 维护**：置信度剪枝、陈旧标记、回写分数，是知识库“持续演进”的关键运维能力。
     - **隐私脱敏 session 摘要**：`session save` 的脱敏做法可作 LoopDesk 会话记录的安全参考。

---

## 7. 关键设计决策与可借鉴点

1. **Git 即分发通道**：团队共享仓库 + MR 评审 + SessionStart 自动 pull，天然复用代码评审文化，资源可审查、可版本化。→ LoopDesk 若做团队层可借鉴“以 Git 为事实源 + hook 自动同步”。
2. **声明式团队配置（YAML）**：hooks/mcp 用 YAML 一次声明、`${VAR}` 注入密钥，pull 时翻译为各工具原生格式。→ 与 LoopDesk 适配器“一处定义多端生成”理念一致。
3. **recall 默认关闭、显式开启 + 相关性预检**：避免无脑检索污染上下文；子代理先做 `--check` 再决定是否检索。→ LoopDesk 上下文注入的“按需/门控”参考。
4. **AST + 启发式双轨 + WASM 无原生依赖**：最大化语言覆盖且不引入构建复杂度；失败优雅降级。→ LoopDesk 若做代码理解可参考。
5. **friction 信号驱动经验分享**：只在“真正遇到问题”的会话提示沉淀，降低噪音。→ LoopDesk run log / 经验抽取参考。
6. **改进度量闭环（digest/dashboard/KB Health）**：把“AI 使用”可视化，形成持续改进。→ LoopDesk cost/safety 控制可扩展为团队级度量。
7. **精细分发（roles/tags/sources）**：namespace + 标签订阅 + 外部源订阅，平衡“统一”与“个性化”。→ 团队层设计参考。

---

## 8. 待办 / 建议下一步

1. 复核 LoopDesk 当前许可证，明确与 TeamAI（MIT）/ Trellis（AGPL-3.0）的差异化定位（写入 `docs/decisions/`）。
2. 评估是否在 v0.2 引入“团队/共享层”：可直接借鉴 TeamAI 的 roles/tags/sources 分发模型与 Git-as-distribution 思路（参考 `docs/features/loopdesk-v0.2-channel-adapter-feature-breakdown.md`）。
3. 评估代码图检索（teamwiki）+ BM25 重排是否纳入 LoopDesk 记忆/上下文检索路线；重点读 `src/codebase-extract.ts`、`src/wiki-engine/`、`src/code-knowledge-recall.ts`。
4. 借鉴 friction-based 经验沉淀与 KB Health 维护，强化 Loop Engineering 的“经验反哺 spec/记忆”闭环（呼应 Trellis 的 `trellis-update-spec`）。
5. 如需更深，可继续读取：`src/pull.ts`（70KB，多工具注入逻辑）、`src/local-agent.ts`（132KB，平台抽象）、`docs/usage-guide.md`（81KB，完整用法）、`docs/designs/`（设计文档）。

---

## 9. 关键源码索引（main 分支）

| 关注点 | 路径 |
| --- | --- |
| CLI 入口 | `src/index.ts`（132KB command 注册） |
| 初始化/分发 | `src/init.ts`、`src/pull.ts`、`src/push.ts`、`src/team-push.ts`、`src/hooks.ts`、`src/mcp-reconcile.ts` |
| 分发控制 | `src/roles.ts`、`src/tags.ts`、`src/source.ts` |
| 知识库 | `src/codebase-extract.ts`、`src/code-knowledge-recall.ts`、`src/recall.ts`、`src/wiki-engine/`、`src/import-*.ts` |
| 改进度量 | `src/dashboard-collector.ts`、`src/dashboard-html.ts`、`src/digest.ts`、`src/save-session.ts`、`src/contribute.ts` |
| 平台适配 | `src/local-agent.ts`、`src/known-agents.ts`、`src/hook-dispatch*.ts`、`src/opencode-hooks.ts`、`src/openclaw-hooks.ts`、`src/hermes-*.ts` |
| 内置 agent/skill | `agents/teamai-recall.md`、`skills/teamai-share-learnings/`、`skills/team-wiki-codebase/` |
| 类型/配置 | `src/types.ts`、`src/config.ts` |
| 文档 | `docs/usage-guide.md`（中英）、`docs/providers.md`、`docs/designs/` |
| 包元数据 | `package.json`（`teamai-cli` v0.22.0，MIT） |
