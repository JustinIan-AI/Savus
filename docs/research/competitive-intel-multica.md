# 竞品调研 — Multica（`multica-ai/multica`）

> 调研更新：2026-09-15（覆盖最新版 v0.4.43，2026-09-11）
> 来源：GitHub README/Releases、`multica.ai` 官网与 Changelog、中文技术解读（CSDN / 个人博客）。
> 说明：本文只读取公开仓库/官网/社区内容，未执行任何安装或初始化命令。
> 关联：`docs/prd/loopdesk-prd-v2.0.zh.md`（团队能力复用 + AI 资产管理方向）。

## 0. 元信息

| 项 | 内容 |
| --- | --- |
| 仓库 | [github.com/multica-ai/multica](https://github.com/multica-ai/multica) |
| 官网 | multica.ai · multica.ai/docs · multica.ai/changelog |
| Slogan | *"Agents that show up on the board."* / "Make humans and AI agents work as one team — open-source and self-hostable." |
| 名称含义 | **Mul**tiplexed **I**nformation and **C**omputing **A**gent（致敬 1960 年代 Multics 分时概念） |
| 成熟度 | **49.9k Stars / 6.4k Forks / 5,304 Commits** |
| 最新版本 | **v0.4.43（2026-09-11）**；`latest` 标签 |
| 发布节奏 | 2026-03 起持续高频，**几乎 1–3 天一个版本**（8/25→9/11 已发 10 个版本；Releases 共 16 页） |
| 许可证 | **Multica License** = Apache-2.0 全文 + 附加条件，覆盖 **托管服务 / 商业嵌入 / 品牌（branding）** 三类场景（署名见 `NOTICE`） |
| 技术栈 | Next.js 16（App Router）· Electron（桌面）· Expo/React Native（iOS）· Go（Chi + sqlc + gorilla/websocket）· PostgreSQL 17（`pgcrypto` + `pg_trgm`） |

## 1. 一句话定位

**把人（同事）与 AI coding agent 放进同一个工作空间，让 agent 像队友一样被指派 issue、自行领取、在你自己的机器上执行、边做边评论、完成后交回评审**——开源、可自托管。

它要解决的痛点是：你已在使用 Claude Code、Codex 等多个 agent，但它们各自待在终端标签页里、会话结束就丢上下文。Multica 用"**任务看板 + 队友模型 + 自带 runtime**"把这些 agent 组织成团队。

## 2. 最新版（v0.4.43）与近期演进

**v0.4.43（2026-09-11）重点**：评论/描述批注、桌面端前进后退历史菜单、Issue 看板新默认视图（聚焦最新工作）、运行记录标注"工具输出未完整保留"、运行历史显示取消人、CLI 设置/清空 agent 开场建议、GPT-6 Astra（含公开价格）、自托管支持 Redis 集群/Serverless。

**近期主线（v0.4.34→v0.4.43）**：
- **评论线程内跑 agent**：排队/运行状态、步骤与日志直接显示在评论线程；同线程追加指令并入当前运行；不同线程各自排队（v0.4.42）。
- **侧边栏重构**：分为「工作」「AI 团队」；设置页按个人/工作区/Issue 配置/连接与扩展/桌面应用分组（v0.4.41）。
- **MCP 一等化**：MCP server 改名不丢连接配置与已分配 agent；替换连接成独立操作（v0.4.40）；Oh My Pi 支持 MCP（v0.4.36）。
- **自定义 Issue 属性**：按文本/数字/日期/URL 筛选，数字/日期支持区间；自定义 Issue 状态正式开放（v0.4.34/0.4.36/0.4.38）。
- **技能本地导入**：从本地文件夹 / `.skill` / `.zip` 导入，导入前预览、冲突提示（v0.4.36）。
- **运行时扩容**：华为云 CodeArts 成为内置 agent runtime（v0.4.37）；iPad 原生安装。
- **多渠道**：`/new`、`/clear` 覆盖钉钉、飞书、Slack、Telegram、企业微信（v0.4.35）。

> 演进信号：Multica 正从"issue 看板 + agent 指派"快速扩张为**完整的团队 agent 协作平台**（评论线程执行、自定义字段、自托管弹性、多端、CLI/API 全面可脚本化）。

## 3. 核心能力（README 归纳）

### 3.1 组队（Build the team）
- **26 种 Agent CLI**：Claude Code、OpenAI Codex、Cursor Agent、GitHub Copilot CLI、OpenCode、OpenClaw、Hermes、Pi、Antigravity、CodeBuddy、DevEco Code、Grok、Kimi、Kiro CLI、Qoder CLI / Qoder CN、Qwen Code、QwenPaw、Reasonix、Trae CLI、DeepSeek Harness、Oh-My-Pi、MiniMax Code、Dim、Huawei Cloud CodeArts 等。
- **Agents as teammates**：每个 agent 起名、选 provider 与 runtime，像真人一样出现在看板上。
- **Squads**：agent 与人混编成队，由 leader 分发工作。
- **Skills**：把已解决的问题沉淀成 playbook，供所有 agent 复用。
- **自带 runtime（daemon）**：agent 的"工位"是你自己的机器（笔记本/云主机），**代码不离开该机器**。

### 3.2 派活（Hand off the work）
- **指派 issue**：把 agent 当同事一样设为 assignee。
- **Autopilots**：cron 驱动站会、审计、报告（`create_issue` / `run_only`；`skip`/`queue`/`replace` 并发策略）。
- **Chat**：直接向工作空间提问，或不建 issue 直接开工。
- **Projects**：归组工作，并挂载 agent 需要的**仓库与文档作为上下文**。

### 3.3 过程可视（Stay in the loop）
- **Execution log**：带时间戳回放每次工具调用、命令与报错。
- **Token usage**：按 agent、按 issue 查看每次运行成本。
- **Review gates**：成果进入 review 而非直接进 main，由人决定是否合入。
- **Inbox**：只在 agent 需要决策时通知。
- **Retries and timeouts**：失败运行自动重试，或停下并说明原因。

### 3.4 可定制与团队/企业特性（Make it yours）
- **完全自托管**：Docker Compose 或 Helm；v0.4.43 起支持 **Redis 集群 / Serverless**。
- **任意 Git 托管**：GitHub、GitLab、Gitea、Forgejo（含自托管）。
- **Workspaces**：按团队隔离 agent、issue 与设置。
- **角色与访问范围**：`owner` / `admin` / `member`，可精确控制每个成员能运行哪些 agent。
- **Security model**：明确 agent 能触及与不能触及的边界。
- **聊天渠道**：Slack、Lark、DingTalk、WeCom、Telegram（后三者社区维护）。
- **多端**：Web、桌面（macOS/Windows/Linux）、移动（iOS，需从源码构建）。
- **CLI 与 API**：所有界面皆可脚本化；agent 通过与你相同的 CLI 驱动 Multica。
- **审计轨迹**：包含机器人（agent）在内的完整审计记录。

## 4. 架构

```
        Web  ·  Desktop (macOS/Windows/Linux)  ·  iOS
                          │
                          ▼
   ┌──────────────┐   ┌──────────────┐   ┌────────────────────┐
   │   Next.js    │──>│  Go backend  │──>│   PostgreSQL 17    │
   │   frontend   │<──│  (Chi + WS)  │<──│ (pgcrypto+pg_trgm) │
   └──────────────┘   └──────┬───────┘   └────────────────────┘
                             │  tasks over WebSocket
                      ┌──────┴───────┐
                      │ Agent daemon │  跑在你的机器上，紧邻你的代码
                      └──────┬───────┘
                             │  spawns
                      ┌──────┴─────────────────────────┐
                      │ Claude Code · Codex · Cursor · …│
                      │ (上述 26 种 runtime 任意一种)   │
                      └─────────────────────────────────┘
```

**开发环境**：Node.js 22、pnpm 10.28.2、Go 1.26.6、Docker；`make dev` 一键起全部服务；iOS 位于 `apps/mobile/`。

## 5. 相对上一版调研（2026-07-07）的关键变化

| 维度 | 上一版结论 | 最新版（2026-09-15） |
| --- | --- | --- |
| 成熟度 | 未记录 | **49.9k★ / 6.4k fork / 5,304 commits** |
| 版本 | 未记录 | **v0.4.43**，1–3 天一版 |
| Agent runtime 数 | "自动发现多个 coding CLI" | **明确 26 种**（含 CodeArts、DeepSeek Harness、Oh-My-Pi 等） |
| 许可证 | 未确认 | **Multica License**（Apache-2.0 + 托管/商业嵌入/品牌条件） |
| MCP | 列为 agent 配置项 | **MCP 一等化**：server 改名迁移、连接替换、Oh My Pi MCP |
| 团队模型 | workspace/member/role | 增加 **Squads（人机混编 + leader）** |
| 技能 | 可复用 skill | 增加**本地导入**（folder/.skill/.zip + 预览/冲突提示） |
| Issue 模型 | 固定状态机 | **自定义状态 + 自定义属性（文本/数字/日期/URL + 区间筛选）** |
| 执行可视 | issue/task 实时事件 | **评论线程内执行**、Execution log、token 用量、Review gates、Inbox |
| 部署 | Docker/自托管 | 增加 **Helm + Redis 集群/Serverless** |
| 端 | Web + 桌面 | 增加 **iOS/iPad** |

## 6. 与 LoopDesk 的关系

### 6.1 关系判定
- **相邻竞品（团队 agent 协作/任务编排）**，非个人 loop 连续性的直接克隆。
- 对 LoopDesk v2.0「团队能力复用 + AI 资产管理」方向，是**强参照**：其 **Skills（团队 playbook 复用）+ Projects（挂载仓库/文档上下文）+ Autopilots + Review gates** 与 LoopDesk 的团队资产/长任务模板高度同构。

### 6.2 可借鉴功能（对 LoopDesk 的价值）

| Multica 能力 | 机制要点 | LoopDesk 落地建议 |
| --- | --- | --- |
| Agents as teammates | agent 具名、出现在看板、可被指派 | 任务看板允许 agent 作为 assignee；agent 注册表可视化 |
| Squads | 人机混编 + leader 分发 | 团队能力复用的编排拓扑（对应 LoopDesk 团队层） |
| **Skills（playbook 复用）** | 已解决问题固化为可复用 skill | 对齐 LoopDesk 团队 AI 资产（Skill 下发）；补充"本地导入 + 预览 + 冲突提示" |
| Projects（挂载上下文） | 项目挂载仓库/文档供 agent 消费 | 对应 LoopDesk 的 JIRA/Plane/Confluence 连接器 + 项目上下文 |
| Autopilots | cron/webhook/手动；create_issue/run_only；skip/queue/replace | 对应 LoopDesk 长任务调度与并发策略（可直接对齐其并发语义） |
| Execution log + Token usage | 时间戳回放 + 按 agent/issue 成本 | 对齐 LoopDesk run log / cost rollup（GOV-01/02） |
| Review gates | 成果进 review，人决定合入 | 对齐 LoopDesk maker/checker + 独立验证 + 审批门 |
| 自带 runtime（daemon） | 代码不离开本机 | 与 LoopDesk local-first 编排同向；安全叙事可复用 |
| 角色 + agent 运行范围控制 | 精确控制成员能跑哪些 agent | 对应 LoopDesk 分发范围控制（roles/tags/sources） |
| 多端 + CLI/API 全可脚本化 | 所有界面 CLI 驱动 | 对齐 LoopDesk CLI-first 与机器可读面 |

### 6.3 明确不借鉴
- **team-first issue 看板作为核心**：LoopDesk 保持"任务为中心但 local-first"的轻量形态，不做重型 issue 治理。
- **强制 Postgres + Docker + Redis 的重基础设施**：LoopDesk 坚持文件驱动、零基础设施。
- **Cloud/web+desktop 同步依赖**：LoopDesk 以 git 异步资产为底座，不强制云。
- **Multica License 的托管/品牌限制**：LoopDesk 若自开源，倾向纯 Apache-2.0/MIT 以最大化采用（见 PRD 关于许可证的取舍）。
- **26 种 runtime 全量覆盖的广度**：LoopDesk 按 runtime matrix 选深度适配，不追求数量堆积。

## 7. 结论

- Multica 已从"agent 当队友的任务平台"演进为**完整的团队 agent 协作/编排平台**（v0.4.43，49.9k★，26 runtime，Squads，自定义字段，自托管弹性，多端）。
- 它对 LoopDesk 的价值主要在**团队能力复用 + AI 资产管理 + 长任务自动化**三个方向的实现范式：Skills/playbook、Projects 上下文挂载、Autopilots 并发语义、Execution log/token 用量、Review gates。
- LoopDesk 的差异化仍清晰：**local-first、零基础设施、可移植 loop state、git 原生资产分发、跨外部工具 continuity**——Multica 在这些点上恰恰是"重平台"路线。

## 8. Open Questions

- Multica 的 Skills 是否支持**跨团队分发与版本治理**（还是工作区内部复用）？需查 docs。
- Squads 的 leader 是否为**持久 leader**，还是 claim/lease 式对等（决定团队复用拓扑）？
- 个人（solo）模式是否被明确支持，还是产品默认团队？
- 自托管是否可完全离线、无云依赖？
- Multica License 对"二次开发后再商业化"的具体限制边界？
