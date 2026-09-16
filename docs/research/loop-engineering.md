# LoopDesk 竞品/方法论调研 — loop-engineering

> 状态：已完成
> 日期：2026-07-07
> 来源：`https://github.com/cobusgreyling/loop-engineering`
> 说明：以下结论基于该仓库的公开 README、docs、patterns、templates、release notes 与参考状态文件整理。

## 1. 核心定位

`loop-engineering` 不是一个代码框架，而是一套 **“设计能自动提示 agents 的 loop，而不是继续手动写 prompt”** 的方法论。

- 核心口号：Stop prompting. Design the loop. Get a score.
- 目标用户：Grok、Claude Code、Codex、OpenClaw、Opencode、Cursor、Windsurf、Hermes 等 AI coding agent 使用者
- 关键转变：从“ Craft 单次 prompt”转向“设计持续运行的控制系统”

对 LoopDesk 的意义：
- 它验证了“Loop 作为第一公民”的方向是对的
- 但它更偏向 **repo maintenance / CI/PR 维护 loop**
- LoopDesk 如果要借鉴，应提取其“个人开发工作台”版本，而不是照搬其 GitHub-centric 流程

## 2. 关键概念

### 2.1 Loop Engineering

- 定义：你不再只是 prompt agent，而是设计一个系统去发现工作、分配工作、验证结果、持久化状态
- 一句话：Loop = recursive goal；agent 持续迭代，直到完成或升级给人

### 2.2 相关概念

| 概念 | 含义 | 对 LoopDesk 的启示 |
| --- | --- | --- |
| Agent Harness Engineering | 单个 agent 运行环境：工具、上下文、权限、规则 | LoopDesk 的 runtime / adapter / permission 层 |
| Factory Model | 软件建造系统：pipeline、agents、checks、handoffs | LoopDesk 可把自己定位成个人版 factory floor |
| Intent Debt | 每次 session 冷启动导致的目标缺失 | 用 skills / LOOP-STATE.json / memory 偿还 |
| Comprehension Debt | 代码写得快，但人理解跟不上 | LoopDesk 需要强化 review / artifacts / memory |
| Cognitive Surrender | 让 loop 运行，但人停止思考 | LoopDesk 必须保留 human gate / approval |
| Orchestration Tax | 多 agent 协调成本 | LoopDesk 用 worktree + run log + budget 降低税负 |
| Code Agent Orchestra | explore / implement / verify 分离 | LoopDesk 的 Goal 很适合 adopt maker/checker |

### 2.3 六类原语 + Memory

1. Automations / Scheduling
2. Worktrees
3. Skills
4. Plugins & Connectors (MCP)
5. Sub-agents (maker / checker)
6. Memory / State

该仓库把 durable state 视为 loop 的脊柱，这与 LoopDesk 的 `LOOP-STATE.json` 方向一致。

## 3. 工作方式与模板

### 3.1 Loop 与 Goal 的关系

- Loop：持续发现工作、分类优先级、维护状态、按节奏运行
- Goal：完成有边界、可验证的具体任务，直到 verifier 通过
- 明确 handoff 模式：Loop 发现可修复项 -> 转成 Goal 执行

这与我们之前对齐的 LoopDesk 语义完全一致。

### 3.2 成熟度分级

| 等级 | 含义 | 典型行为 |
| --- | --- | --- |
| L0 | 只写意图 | 文档化 purpose/non-goals |
| L1 | 报告为主 | triage -> state，不自动修复 |
| L2 | 辅助执行 | 小修复 + verifier + worktree |
| L3 | 无人值守 | 只在预算/denylist/gate 明确后开放 |

对 LoopDesk 的价值：
- v0.1 应该默认 L1/L2
- 避免把用户直接推入 L3

### 3.3 典型 Patterns

该仓库提供 7 个 production patterns：

- Daily Triage
- PR Babysitter
- CI Sweeper
- Dependency Sweeper
- Changelog Drafter
- Post-Merge Cleanup
- Issue Triage

每个 pattern 都包含：
- cadence
- starter
- week-one recommendation
- token cost
- safety level

对 LoopDesk 的启示：
- 不要一开始就做“全功能自动化平台”
- 先做 **高信噪比、低风险 pattern**
- 个人开发者最可能受益的是：
  - Daily Triage 类 Loop
  - Issue/Feature Triage 类 Loop
  - Dependency Review Loop
  - Release Note / Docs Draft Loop

## 4. 关键机制

### 4.1 State / Memory

- 强调 `STATE.md` / `LOOP-STATE.json` 是 loop 最重要的产物
- state 应回答：
  - 现在在做什么
  - 上次尝试了什么、结果如何
  - 什么在等人处理
- 每次 run 都应：
  - 读取 prior state
  - 写入 outcome / timestamp / last action
  - prune closed/merged 项

与 LoopDesk 对齐：
- `LOOP-STATE.json` 应成为核心事实来源
- memory/skills/artifacts 是 state 的延伸

### 4.2 Worktree Isolation

- 每个 fix attempt 建议一个独立 worktree
- 成功后合并，失败/升级后清理
- 避免多 loop/多 agent 同时污染主工作区

与 LoopDesk 对齐：
- worktree isolation 是 v0.1 必须项
- 每个 Goal 的自动化执行应尽量隔离

### 4.3 Skills

- skill = 持久化的意图与项目约定
- 解决 intent debt：build、test、lint、review、domain knowledge
- 是 reuse 的最小单元

与 LoopDesk 对齐：
- v0.1 应该支持 personal workflow templates/skills
- 但不该做成 team marketplace

### 4.4 MCP Connectors

- MCP 被视为通用连接层
- connectors 用于 ticket、Slack、GitHub、DB、deploy
- 原则：先 read-only，再逐步扩展写权限

与 LoopDesk 对齐：
- MCP-first 是正确的
- v0.1 至少要先打通一个本地 coding workflow

### 4.5 Maker / Checker Split

- implementer 不能给自己打分
- verifier 必须在隔离环境运行测试
- `/goal` 经常用 fresh model 判断 stop condition

与 LoopDesk 对齐：
- Goal 执行天然适合 maker/checker
- 个人工作台也应默认保留 verifier / approval

## 5. 安全与运营

### 5.1 Safety

- path denylist：`.env`、secrets、payments、auth、production infra
- auto-merge 默认关闭
- human gate：安全、支付、PII、依赖升级、超过 N 文件变更、第三次失败
- secrets 不能进 prompt/state/logs
- flaky test 不能靠“继续修代码”掩盖

### 5.2 Failure Modes

常见失败模式包括：
- Infinite Fix Loop
- State Rot
- Verifier Theater
- Notification Fatigue
- Token Burn
- Over-Reach

每个失败模式都给了 severity 和 mitigation。

### 5.3 运营规则

- 每次 run 都要有 run log
- 预算超 80% 应切 report-only
- CI red / 发布期 / 关键 reviewer 不在时应暂停
- 连续 2 周 cost > value 时应 kill loop
- kill checklist：停 scheduler、归档 state、写 post-mortem

## 6. 工具链

该仓库已发布/正在推进的 CLI 与工具：

- `loop-init`：scaffold pattern、skills、state、budget
- `loop-audit`：给项目打 Loop Ready 分数
- `loop-cost`：按 pattern / cadence / level 估算 token 成本
- `loop-sync`：检测 `STATE.md`、`LOOP.md`、skill 版本漂移
- `loop-context`：stateful memory manager + circuit breaker
- `loop-mcp-server`：MCP runtime lookup for patterns/skills/state
- `loop-worktree`：mechanical worktree manifest + cleanup

最新 release notes 显示：
- v1.5.0 新增 `loop-sync`、`loop-constraints`、`loop-mcp-server`
- `loop-audit` 会基于约束文件加分
- 社区采用者/案例已形成一定规模

## 7. 与 LoopDesk 的差距与可借鉴点

### 7.1 可直接借鉴

- Loop/Goal 分层模型
- L1/L2/L3 渐进增强
- durable state 作为 source of truth
- maker/checker 分离
- worktree isolation
- skills 作为 intent 的持久化
- run log / budget / kill switch / human gate
- pattern-picker 思路：先给用户最小可用 loop

### 7.2 需要本地化/差异化

| loop-engineering 特点 | LoopDesk 需要调整 |
| --- | --- |
| GitHub/CI/PR 为主场景 | 改成个人开发者跨工具工作台 |
| STATE.md / LOOP.md 文件为主 | 保留 `LOOP-STATE.json` + memory/skills/artifacts 作为 personal loop workspace |
| npm/CLI scaffold 工具 | LoopDesk 应以本地 runtime/CLI/WebUI 为主 |
| 强 repo maintenance 导向 | 增加头脑风暴、产品调研、竞品分析、架构 sweep 类 Loop |
| 偏向单一 repo | 增加跨工具、跨 session、跨 IDE 的连续性 |
| team notification 较多 | v0.1 保持个人本地优先，不做 team Slack/notification-first |

### 7.3 是否建议 LoopDesk 直接照搬

- 不建议全盘照搬
- 建议只借鉴其 **方法论层**
- 产品层要做明显裁剪：
  - 保留 Loop/Goal、skills、state、worktree、MCP、cost/safety
  - 去掉过度 GitHub/CI/PR 中心化叙事
  - 强化个人开发者的头脑风暴、调研、跨工具 handoff

## 8. 结论

`loop-engineering` 是当前对 LoopDesk 最有价值的外部参考之一，尤其体现在：

- 把 Loop 当成可设计、可审计、可运营的系统
- 明确区分 Loop 与 Goal
- 用 state/skills/worktree/verifier 降低人工 prompting 成本
- 用 budget、run log、human gate、failure modes 控制风险

但对 LoopDesk 来说，它只是方法论语境，不是产品模板。LoopDesk 应该在此基础上长出更个人化、更跨工具、更本地优先的产品形态。

## 9. 建议下一步

1. 把 `loop-engineering` 的 L1/L2/L3 成熟度模型写进 LoopDesk PRD
2. 在 `docs/features/core-feature-list.md` 增加“Loop/Goal 最佳实践模板”说明
3. 在实施计划里保留一组“个人开发 workflow templates”作为 v0.1 卖点
4. 在架构中保留 durable state + run log + worktree isolation 作为第一层实现
