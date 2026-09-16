# LoopDesk MVP PRD — MCP 配一次 + 换 Agent 不丢 Context

> 版本：MVP v0.1（最小可验证版本）
> 日期：2026-07-30
> 来源：AI 刘小排 office-hours 收敛结论
> 定位：本地优先的个人 loop workspace，先只解决"配置一次、换 agent 不丢 context"这一件事

---

## 1. 一句话主张

**MCP / Skills 在一个 workspace 里配一次，自动投影到 Claude Code、Codex、Kimi、WorkBuddy 各自的原生配置里，不重复、不漂移；任务在 agent 之间转移时，相关 context 跟着走。**

不是 AI IDE，不是终端包装器，不是 IM 远程控制台。是多个 coding agent 共享的那层"状态底座"。

---

## 2. 背景 / 为什么是现在

真实痛点（来自目标用户本人的日常）：

- 同一个 `pencil mcp` 要在 Claude Code、Codex、Kimi、WorkBuddy 里各配一遍，容易漂移、漏配。
- 连续 / 长任务只能泡在 Claude Code 或 Codex；设计类任务又跑到 WorkBuddy；同一个需求 context 在几个 agent 间手动搬运。
- 套餐额度不够要换 agent 时，context 直接断，得重来。
- 额度统计要自己看，没有统一视图。

竞品调研结论（见 `docs/research/`）：Tutti 偏云协作房间，WeSight 偏桌面壳，Multica 偏团队治理，都没干净拥有"本地优先 + 单人 + 可携带状态"这一块。cc-connect 已占满 IM 远程控制（13 个平台，含微信 ilink / QQ / 钉钉 / 飞书），无需重建。

---

## 3. 目标用户（那个人）

**主 persona（即产品使用者本人）：**
独立开发者，同时跑 3–4 个 AI coding agent（Claude Code / Codex / Kimi / WorkBuddy），按任务类型路由（长任务→Claude/Codex，设计→WorkBuddy），被"同一份 MCP 配 N 次"和"换 agent 丢 context"反复折磨。

**首批 10 个同类用户：**
wesight 社群、开源社区里同样多 agent 并用的开发者。分发不靠投放，靠开源社区与同道口碑。

**非目标（明确排除）：**
团队 / 企业多人在同一 workspace 协作；只用一个 agent 的开发者；追求 GUI 控制面板的用户。

---

## 4. MVP 范围（in scope）

只做两件事：

### 4.1 配置一次，多 agent 共用（MCP / Skills 投影）
- 在 workspace 里定义一份 MCP / Skills 配置（单一事实来源）。
- 一个 projector / sync 脚本把这份配置自动生成为每个 agent 的原生配置：
  - Claude Code：`.mcp.json` / `settings.json`
  - Codex：`config.toml` 或等价
  - Kimi CLI：其原生配置位
  - WorkBuddy：其原生配置位
- 改一处，全 agent 同步；不漂移、不漏配。
- 冲突 / 不支持的 agent 配置项给出明确报错，而不是静默失败。

### 4.2 换 Agent 不丢 Context（任务 handoff）
- `LOOP-STATE.json` 作为跨 agent 的可携带状态契约：记录当前任务的目标、已做的决策、关键文件、未决问题。
- 提供 handoff 命令（CLI 优先）：`loop handoff <target-agent>`，把当前任务 context 打包进 `LOOP-STATE.json`，目标 agent 启动时可读取并续上。
- 只携带"决策与状态"，不搬运完整对话历史（避免噪声与 token 浪费）。

---

## 5. 明确不做（out of scope，砍掉的）

| 砍掉的项 | 原因 / 替代 |
|---|---|
| IM 远程控制（钉钉 / 飞书 / 微信 / QQ 指挥调度） | cc-connect 已开源占满，直接当通道接，不重建 |
| 三端控制面板（Web / Desktop / Mobile） | v0.1 只做 CLI + 本地最小控制；GUI 壳是 WeSight 的地盘 |
| 额度 / 套餐统计仪表盘 | 列为 v2；当前 MVP 不解决，避免 scope 膨胀 |
| 团队 / 多人工位、权限治理 | 个人 loop 优先；团队是 Multica 的地盘 |
| 自研调度编排引擎 | MVP 不调度，只做"状态底座 + 配置投影" |

---

## 6. 核心能力设计（最小实现）

| 能力 | MVP 实现 | 验收 |
|---|---|---|
| 单一配置源 | `loop-workspace/mcp.sources.json` + `skills/` 目录 | 一份定义，多 agent 可见 |
| 配置投影 | `loop sync` 命令生成各 agent 原生配置 | 4 个 agent 启动后都能加载同一份 MCP，无手动步骤 |
| 状态契约 | `LOOP-STATE.json`（task / decisions / files / open-questions） | 手动改或 handoff 后能落盘 |
| 任务 handoff | `loop handoff <agent>` 写入目标 agent 可读状态 | 目标 agent 续上任务，无需重贴 context |

---

## 7. 验收标准（Definition of Done）

- [ ] 一份 MCP 定义，执行 `loop sync` 后 4 个 agent 全部加载，零手动配置。
- [ ] 修改 MCP 定义一处，`loop sync` 后 4 个 agent 全部更新，无漂移。
- [ ] `loop handoff` 后，目标 agent 能读取任务决策与关键文件，继续工作。
- [ ] 开源仓库可 `git clone` 后本地跑通上述流程，README 含"我是怎么让 pencil mcp 在 4 个 agent 里只配一次"的示例。

---

## 8. MVP 落地路径（降级优先）

- **Level 1–2（本周手工验证）**：一份共享 config + 一个同步脚本 + 一篇"MCP 配一次"文档。先发给 wesight 社群 3 个人手工试用。
- **Level 4（小工具）**：沉淀为 `loop` CLI（sync / handoff），开源发布。
- **不做 Level 5+（SaaS / 面板）**：除非社区 daily-dependency 信号明确。

---

## 9. 成功度量（刘小排口径）

不是 star 数，是**第二天还打开**。

- 首批 3 个 wesight 社群开发者把 `loop sync` 接入日常，连续 7 天仍在用。
- 至少 1 人反馈"换 agent 不再重配 MCP / 丢 context"是 daily 依赖。
- 出现非作者提交的 issue / PR（说明别人真在用、在改）。

---

## 10. 风险

- **开源社区 ≠ 每天依赖**：同道中人是"一起造的人"，未必"每天靠你活"。验证看 daily-dependency，不看热闹。
- **agent 配置格式易碎**：Claude / Codex / Kimi / WorkBuddy 各自配置 schema 会变，投影逻辑需持续跟进。
- **handoff 语义模糊**："带哪些 context"难定义；MVP 只带决策与状态，不带完整历史，避免过度设计。
- **护城河在格式不在代码**：真正的 moat 是 `LOOP-STATE.json` 变成别的项目也读写的事实标准，不是这个 CLI 本身。

---

## 11. 与现有仓库的关系

- 本 MVP 是 `docs/prd/personal-loop-workspace.md` 的**最小子集**，只取"跨工具状态一致性"与"MCP 投影"两块。
- 复用现有 `LOOP-STATE.json` / `loop_workspace` 架构约定，不新建概念。
- IM 远程、三端面板、额度仪表盘在 v0.2+ 再议，且 IM 远程优先接 cc-connect。
