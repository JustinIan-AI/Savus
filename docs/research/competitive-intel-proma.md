# 竞品调研：proma-ai/Proma（Proma）

> 调研时间：2026-09-09（更新）
> 调研对象：https://github.com/proma-ai/Proma（社区版 AGPL-3.0，作者 Erlich Liu / erlichliu@gmail.com）
> 定位：本地优先的开源通用桌面 Agent 工作台（local-first AI desktop workbench）
> 关联项目：LoopDesk（本仓库 v0.1 个人循环工作区）
> 说明：本版为中文重写并整合最新 README（约 2026-09-08 更新，2.2k Stars / 282 Forks / 2050 Commits）；重点补充**企业版功能**、**团队能力复用**与**AI 资产管理**，并关联 LoopDesk 后续将新增的“团队能力复用 + 配套 AI 资产管理”产品方向。

---

## 1. 调研方法

- 读取公开仓库 `proma-ai/Proma` README（中文 + `README.en.md`），交叉核验官方站 `proma.cool`、下载页 `proma.cool/download` 与 App Store 元数据。
- 检索社区生态信号：`Proma-Easy` 发布说明（企业版 Skills 分发）、`CLIMASHSCAPE/PROMA-MANAGER-MCP`（跨工作区 Skill 同步/配置审计 MCP）、版本演进（v0.9.8 agent teams → v0.16.8 企业版 Skills 分发 → v0.17.0 proactive memory）。
- 全部结论对照 LoopDesk 定位（`docs/product-positioning.md`）、PRD（`docs/prd/personal-loop-workspace.md`）、架构（`docs/architecture/personal-loop-workspace.md`）与既有竞品研究。
- 无法在当前环境完整渲染的官网正文、英文 README 细节，已如实标注。

---

## 2. 产品身份

### 2.1 定位
- **一句话**：本地优先的开源通用桌面 Agent 工作台，把多模型 Chat、通用 Agent、计划模式、工作区、Skills、MCP、远程机器人、记忆放在同一客户端。
- **核心理念**：简单问题走 Chat，复杂任务交 Agent，数据与配置尽量留在本地；面向“100× 专业人士”与 proactive Agent 时代。
- **双版本并行**：社区开源版（AGPL-3.0）+ 商业/企业版（独立下载、可覆盖安装、数据继承）。

### 2.2 目标用户
- 想要“一个本地桌面客户端同时搞定聊天与 Agentic 工作”的专业用户。
- 重视工作区隔离、可复用 Skills、MCP 扩展与本地数据所有权的个人/团队用户。
- 并非以“跨工具循环规划器 / 持久状态协议方 / 多工具编排器（跨 Claude Code、Codex、CodeBuddy、Trae、Gemini）”为主定位。

### 2.3 差异点声明
- 单客户端整合 Chat + Agent + Skills + MCP + 远程机器人 + 记忆。
- 本地优先、文件型存储（`~/.proma/` 下 JSON/JSONL，而非本地数据库）。
- 工作区级 Skills/MCP 配置；远程机器人桥接飞书/Lark（含钉钉、微信入口）。
- **商业/企业版与开源版并行**（这是与 Trellis AGPL / TeamAI MIT 不同的“双版本商业化”路径）。

---

## 3. 架构总览

### 3.1 系统形态
- 以 Electron 风格桌面应用为核心（设置、附件、工作区、Agent 运行时）。
- 仓库含 docs、tutorial、思考笔记、assets，以及开源/商业下载引用。
- README 主题强聚焦：桌面应用、本地存储、Chat、Agent、Skills、MCP、远程机器人、记忆、多模型。

### 3.2 运行时模型
- 主运行时为本地桌面：工作区数据、对话、Agent 会话、附件、Skills、设置均本地存储。
- Agent 模式基于 Claude Agent SDK（本地编排而非纯云端执行）。
- 商业版通过 Proma Cloud 提供托管模型渠道，与开源版独立分发。
- 公开仓库无证据表明存在跨外部编码 CLI 的持久工作区状态协议（类似 LoopDesk `LOOP-STATE.json`）。

### 3.3 协议/传输
- **MCP 为一等公民**：工作区级 stdio/HTTP MCP Server 配置，可启停。
- **远程机器人**：飞书/Lark 桥接，含钉钉、微信桥接入口；支持私聊/群组，结合工作区 Skill/MCP 远程使用 Agent。
- 无公开证据表明存在跨外部工具的统一状态同步协议。

### 3.4 可观测性
- UX 向可观测：Agent 工具调用过程与结果展示在消息流中（子会话/主会话结构）。
- 无公开证据表明具备 LoopDesk 式 run log、成本观测、L1/L2/L3 成熟度门禁或 maker/checker 拆分。

---

## 4. 核心能力（截至最新 README）

### 4.1 模式与项目管理
- **三种模式**：Chat 模式、Agent 模式、计划模式（plan mode）。
- **项目分区**：按项目隔离 Skills/MCP/记忆，避免上下文膨胀。
- **记忆系统**：项目级 `AGENTS.md` 约束 Agent 表现，个人 `MEMORY.md` 作为记忆索引（v0.17.0 强化“主动记忆”）。

### 4.2 内嵌环境与任务
- **内嵌浏览器**：Agent 可主动调用，用于自动化/对照研究。
- **内嵌终端**：可见且 Agent 可直接登录使用。
- **定时任务**：单次/间隔/复杂工作日周期。
- **Todo**：与 macOS 提醒事项同步，可引用继续工作。
- **日程**：与 macOS 日历同步，Agent 协助创建管理。
- **Obsidian 深度集成**：更好的 Markdown 编辑体验。

### 4.3 探索与并行（Agent 结构）
- **Agent 平行探索**：分叉不污染主上下文，可一键带回主线。
- **子会话 & 主会话**：类似 SubAgent 但上下文更干净、可持续迭代；可并行深度研究、对抗性分析、主会话修复 + 子会话持续审核。
- **自动 worktree 工作**：开发者基于 worktree 快速开发，Agent 主动选对应 worktree。

### 4.4 文件与扩展
- 多格式预览编辑（Live Markdown、PDF、Docx、PPT、Excel），文件改动按轮次/Diff 显示。
- Skills / MCP / CLI 三者均支持，分项目配置。
- 远程链接：微信、飞书、钉钉、Slack。

### 4.5 模型/供应商覆盖
- Chat 支持 OpenAI、Anthropic、Google 及 OpenAI 兼容端点。
- Agent 模式需 Anthropic 或兼容协议；已验证兼容：Anthropic、DeepSeek、Kimi API、Kimi Coding Plan、Google、智谱 AI、MiniMax、豆包、通义千问、自定义端点。
- 商业版支持配置 Codex、Kimi Coding Plan 等数十种 Coding Plan。

### 4.6 本地数据与桌面体验
- 本地优先存储于 `~/.proma/`（conversations、agent sessions、workspaces、attachments、settings、profile、channels、SDK config）。
- API Key 经 Electron `safeStorage` 加密。
- 桌面特性：自动更新、代理设置、文件预览、全局快捷键、快捷任务窗、语音输入、主题。

---

## 5. 企业版 / 商业版功能（重点）

> 商业版下载：`proma.cool/download`；开源版可直接覆盖安装，数据保留继承。闭源集成或 SaaS 商用需邮件联系获取商业授权。

### 5.1 开源版 vs 商业版

| 对比项 | 开源版 | 商业/企业版 |
| --- | --- | --- |
| 核心桌面能力 | 完整体验、自由配置 | 同左 |
| 模型渠道 | 自行添加管理 API Key | 内置 Proma Cloud 官方渠道 + 自配第三方 |
| 模型价格 | 按供应商规则 | Proma Cloud 专属优惠，部分低至官方价 **1 折** |
| 安全稳定 | 自担风险 | Proma Cloud 官方托管，统一监控兼容 |
| 联网/内嵌 AI | 自配搜索/生图 | 完整 Cloud 能力（WebSearch、GPT Image 2 等） |
| 对外 API | 自配供应商 API | 可建 Proma Cloud API Key（设额度上限） |
| 团队额度 | 自行搭建 | 团队管理员分配/回收共享额度，月自动分配，查用量 |
| Skills 分发 | 工作区本地 | **组织级分发、版本统一管理**（企业版） |
| 订阅用量 | 自管供应商账号 | 应用内订阅余额 + 模型/Agent/工具用量明细 |

### 5.2 企业版核心增强（要点）
1. 稳定安全的 **Proma Cloud 官方托管模型渠道**（亦支持自配第三方）。
2. 精选模型 **Proma Cloud 专属优惠**（部分低至官方价 1 折）。
3. 完整联网与内嵌 AI（WebSearch、GPT Image 2 生图/编辑）。
4. 可创建**独立、设额度上限的 Proma Cloud API Key**。
5. 应用内订阅与用量管理。

### 5.3 团队能力（仅商业/企业版）
- **团队额度管理**：管理员向成员分配/回收共享团队额度，支持按月自动分配，查看成员用量与额度流水。
- **Skills 组织级分发**：管理员一键下发团队 Skills 至成员，免安装直接使用；统一版本管理、更新与使用范围。
- **对外 API 服务**：成员可获独立 Proma Cloud API Key，将 LLM/工具/多模态能力接入自有应用。
- **集中订阅与用量**：团队内应用内管理订阅与余额，查看模型/Agent/工具用量明细。

> 社区侧佐证：`Proma-Easy` 发布说明（v0.16.8）明确“企业版新增 Skills 的组织级分发与团队协作”；`PROMA-MANAGER-MCP` 提供 Skill 跨工作区同步/溯源（check/diff/sync/bootstrap/info）、MCP 配置一致性审计、AI 自动分组归类、会话批量管理——说明“团队级 Skill 同步与配置审计”已是真实需求与生态实践。

---

## 6. 团队能力复用与 AI 资产管理（对标重点）

### 6.1 团队能力复用（Capability Reuse）
- **Skills 即团队资产**：Proma 主张“最佳 Skills 来自用户真实场景”，带 Agent 实操后沉淀为 Skills 并迭代；企业版把这种个人沉淀升级为**组织级分发**——管理员一键下发、免安装、版本统一。
- **Agent 协作结构**：子会话/主会话、平行探索、对抗性分析，使“多人/多 Agent 协同处理复杂任务”成为产品能力（社区称 agent teams，可提升 5–20% 效果）。
- **项目分区 + 记忆资产**：`AGENTS.md`（项目级约束）+ `MEMORY.md`（记忆索引）构成可复用、可移植的项目级能力资产。

### 6.2 AI 资产管理（AI Asset Management）
Proma 把下列对象纳入“资产”统一治理：
- **模型渠道与密钥**：开源版自管供应商 Key；商业版 Cloud 内置渠道或自配；可建带上限的 Cloud API Key。
- **配额与额度**：团队额度池分配与监控；Cloud API Key 额度上限。
- **订阅与余额**：应用内用量明细（模型/Agent/工具）。
- **知识资产**：`AGENTS.md`、`MEMORY.md`、会话文件、Skills、MCP/CLI 配置，按项目/会话隔离，避免上下文膨胀。
- **文件与预览资产**：项目文件、会话引用文件、拖拽引用，构成 Agent 可消费资产。

### 6.3 与 LoopDesk 后续方向的关联
> **LoopDesk 产品设计的后续规划：在个人循环工作区之上，新增“团队能力复用”与“配套的 AI 资产管理”功能。**

Proma 企业版已将上述两项产品化，是 LoopDesk 该方向的**强对标参考**：
- LoopDesk 的 skills / artifacts / memory 若进化为“可跨成员复用、可分发、可审计”的团队资产，Proma 的**组织级 Skills 分发 + 版本统一管理**是直接竞品范式。
- LoopDesk 若引入团队/额度/用量层，Proma 的**团队额度管理 + Cloud API Key 额度上限 + 用量明细**是可借鉴的计费/治理模型。
- LoopDesk 的“AI 资产管理”可对标 Proma 对模型渠道、密钥、配额、知识资产、文件资产的统一治理边界。

> 战略含义：LoopDesk 当前 v0.1 以个人 local-first 为主，但路线图已指向团队能力复用 + AI 资产管理；这意味着它与 Proma 企业版的**直接竞争点将前移**——需提前在“能力复用粒度、资产治理模型、跨成员分发机制”上建立差异化。

---

## 7. 功能对比矩阵（Proma vs LoopDesk，含团队/资产维度）

| 维度 | Proma | LoopDesk（v0.1，路线图含团队/资产） |
| --- | --- | --- |
| 主隐喻 | 本地优先 Chat + Agent 桌面工作台 | 个人循环工作区（后续扩展团队能力复用 + AI 资产管理） |
| 目标用户 | 个人桌面专业用户 + 企业团队 | 独立开发者为主；后续面向团队能力复用 |
| 本地优先 | 强（本地桌面存储 + JSON/JSONL） | 强（local-first 运行时、`LOOP-STATE.json`、memory、skills、artifacts） |
| 跨工具上下文 | Agent 用工作区文件/MCP；非持久跨工具连续层 | 持久 `LOOP-STATE.json`、适配器层、跨工具交接 |
| 工作树隔离 | 自动 worktree（开发者向） | 一等公民 per-loop worktree/scratch 隔离 |
| 界面 | 重桌面 GUI：Chat/Agent 工作区、Skills/MCP 配置、文件预览 | 轻量 CLI + 本地 Web UI |
| 远程/移动 | 飞书/Lark 桥接，钉钉/微信入口，App Store  listing | 受批准工作区的可选 IM 远程控制 |
| 循环工程 | 非一等产品支柱 | triage、maker/checker、run log、预算、升级、stop condition |
| 安全/可观测 | Agent 权限模式、本地存储、基础桌面 UX | 成本可观测、审批、预算上限、升级、诊断/回放 |
| MCP/ACP | 一等公民工作区 MCP；Agent SDK 执行 | MCP 优先适配器、ACP 次之适配器 |
| 执行模型 | Electron 桌面承载 chat/agent/workspace/memory/bridge | 网关 + 循环引擎 + 运行时平面 + 适配器平面 |
| 商业模型 | **开源版(AGPL-3.0) + 商业/企业版并行** | 当前文档未围绕核心工作流做 SaaS 商业化包装 |
| 企业/团队 | **团队额度管理、Skills 组织级分发、Cloud API Key 额度、用量明细** | 后续规划：团队能力复用 + AI 资产管理 |
| AI 资产治理 | 模型渠道/密钥/配额/知识资产/文件资产统一治理 | 后续规划：配套 AI 资产管理 |
| 许可 | AGPL-3.0（商业需授权） | 见本仓库许可证（建议与 AGPL/MIT 形成差异化表述） |

---

## 8. 竞争分析

### 8.1 与“个人循环工作区”的直接相关性
- Proma 是**相邻竞品**，非 LoopDesk 的直接产品克隆。
- 作为参考更强的是：本地优先桌面工作台 UX、Chat vs Agent 模式拆分、工作区级 Skills/MCP 配置、远程机器人作为次级延续面。
- 作为参考更弱的是：跨独立编码 Agent 的持久跨工具状态协议、循环工程方法论、显式成本/安全纪律、工具无关的跨 Claude Code/Codex/CodeBuddy/Trae/Gemini 交接。

### 8.2 与企业版/团队方向的相关性
- Proma 已把“团队能力复用 + AI 资产管理”产品化（组织级 Skills 分发、团队额度、Cloud API Key、用量明细），**这正是 LoopDesk 路线图要进入的战场**。
- 值得重点监控：Proma 是否把企业版能力下沉到更小团队/个人；是否开放跨工具状态导出；远程机器人覆盖是否扩张。

### 8.3 战略差异化（LoopDesk 应坚持）
- 不去做又一个 Chat + Agent 桌面壳。
- 赢在：可移植跨工具循环状态、明确 adapter-first 集成、带 stop condition / maker-checker / 预算护栏的循环工程、轻量 CLI + 本地 Web UI。
- 但需为路线图“团队能力复用 + AI 资产管理”预留架构：能力（skills/artifacts/memory）的**可分发、可审计、可版本化、可配额**边界。

---

## 9. 对 LoopDesk 的启示 / 路线图关联

- 把 Proma 企业版当作**团队能力复用 + AI 资产管理**方向的**首要对标**：
  - 能力复用粒度：skills 作为团队资产，组织级分发 + 版本统一管理（可参考 `PROMA-MANAGER-MCP` 的同步/审计思路）。
  - 资产治理：模型渠道、密钥、配额、知识资产、文件资产统一治理边界。
  - 计费/治理：团队额度池分配回收、Cloud API Key 额度上限、用量明细。
- 不建议把 LoopDesk 变成重桌面运行时；保持轻量、可移植、adapter-first。
- 推荐监控主题：
  - Proma 是否新增持久跨工具状态导出或 adapter 策略（超出 Claude Agent SDK）。
  - 商业版是否改变 local-first 叙事或隐私姿态。
  - 远程机器人覆盖是否超出飞书/Lark、钉钉、微信、Slack。
  - 企业版 Skills 分发/团队额度是否下探到小团队/个人。

---

## 10. 待办 / 开放问题

1. 复核 LoopDesk 当前许可证，明确与 Proma（AGPL-3.0）、Trellis（AGPL-3.0）、TeamAI（MIT）的差异化定位（写入 `docs/decisions/`）。
2. 评估 v0.2+ 引入“团队能力复用 + AI 资产管理”的架构边界：能力（skills/artifacts/memory）的可分发/可审计/可版本化/可配额模型（参考 `docs/features/` 下相关 feature breakdown）。
3. 评估是否借鉴 Proma 的“组织级 Skills 分发 + 版本统一管理”范式，及 `PROMA-MANAGER-MCP` 的跨工作区同步/配置审计思路。
4. 确认 `proma-ai/Proma` 与 `ErlichLiu/Proma`、`Proma-Easy` 之间的仓库权威/分支关系（README 交叉引用暗示相关但非同一信号）。
5. 若需更深，可继续读取：`proma-ai/Proma` 完整 README/英文版、`docs/`、`release-notes/`、`CLIMASHSCAPE/PROMA-MANAGER-MCP`。
