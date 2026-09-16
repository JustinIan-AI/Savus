# Competitive Intelligence: huangruiteng/LoopX

> 调研更新：2026-09-11（补充最新 README / 官方文档站 / 中文技术解读信号）
> 关联：LoopDesk（本仓库）个人循环工作区；后续规划新增「团队能力复用 + 配套 AI 资产管理」

- **Repo**: [github.com/huangruiteng/loopx](https://github.com/huangruiteng/loopx)（文档站：https://huangruiteng.github.io/loopx/）
- **Author**: huangruiteng（黄瑞腾）
- **License**: **Apache-2.0（v0.4.8 起）**；v0.4.7 及之前保留 MIT（仓库同时含 `LICENSE` 与 `LICENSE-MIT`）
- **Language**: Python 3.11+（CLI/安装/demo）；Node.js 22.6+（推荐 24 LTS）运行托管式 TypeScript Effect 控制面核心
- **Maturity**: 约 5,923 Commits / 2.5k Stars，已宣称 200+ 小时真实长程 loop 运行证据（非早期玩具）
- **Dependencies**: 零 runtime 依赖（标准库即可运行）；纯文件系统 + JSON/Markdown，无 Postgres/Redis/S3
- **Tagline**: "The local control plane for long-running AI agent work" / "Long-horizon agent control plane"
- **Slogan**: **Keep the loop moving. Keep the judgment human.**（让循环持续运转，让判断权留给人）
- **中文定位**: 给 AI Agent 团队装一个「项目管理部」——一层薄薄的控制面，负责记住目标、分配工作、控制预算、记录证据、交接任务

## 1. What Is LoopX

LoopX 是一个 **轻量级本地控制面 (local control plane)** 和 **state kernel**，专为 **长程 AI agent 工作** 设计。它不替代 agent runtime（Codex、Claude Code、Cursor 等），而是在这些 runtime 之上提供一层持久控制状态，使跨轮次、跨工具、跨 agent 的工作变得可审阅、可恢复、可接力。

核心理念：**Keep the loop moving. Keep the judgment human.**（让 Loop 持续向前，让关键判断留在人手里。）

## 2. 架构

### 六层持久控制面

| Layer | 职责 |
|-------|------|
| **Registry** | 已知 goal 列表，repo 绑定，adapter 状态，authority source，guards |
| **Goal State** | 单个 goal 的活跃状态文件 (`ACTIVE_GOAL_STATE.md`) |
| **Run Log** | JSON + Markdown 报告，按 goal 保存 |
| **Run History** | 紧凑索引，供 agent、heartbeat、UI 消费 |
| **Status / Attention Queue** | 首屏摘要：谁需要下一步执行 |
| **Compute Quota** | 每个 goal 的本地算力配额策略 |

可选探针层 (Probe Surface): 支持注册 `next_probe` 命令用于只读观测。

### 四角色运行时模型

| 角色 | 拥有 | 不拥有 |
|------|------|--------|
| **Agent** | 规划、分析、工具使用、一次有界执行 | 持久 goal 生命周期或无范围的 effect authority |
| **Provider** | 外部调用和有界观测、effect 结果 | 领域转移策略或 LoopX todo 状态 |
| **Capability** | 调用方结果契约、领域策略、观测归一化、验证、typed transition proposal | 持久调度、claim、gate 或直接生命周期写入 |
| **LoopX Kernel** | goal、todo、claim、gate、monitor、quota、writeback、recovery、scheduling | 领域特定推理或 provider 实现细节 |

### 请求/结果路径

```text
Agent → Capability → Provider → external system
external observation / effect readback → Provider → Capability
typed transition proposal → LoopX Kernel → next todo / gate / monitor / turn
```

### Turn Decision 词汇

两个核心枚举：

- **LoopXTurnRoute** (执行前): `ready_for_host`, `repair_required`, `replan_required`, `user_action_required`, `wait`, `blocked`, `contract_error`
- **LoopXTurnResultKind** (执行后): `validated_progress`, `validated_completion`, `repair_required`, `replan_required`, `user_action_required`, `wait`, `host_failure`, `validation_failed`, `writeback_failed`, `quota_spend_failed`

### 状态存储

```text
.loopx/registry.json                          # 项目级 registry
.codex/goals/<goal-id>/ACTIVE_GOAL_STATE.md    # 活跃 goal 状态
```

零外部依赖：无 Postgres、无 Redis、无 S3。纯文件系统 + JSON/Markdown。

## 3. 核心概念

### Loop Agent

LoopX 定义的 Loop Agent 是：一个 **always-running 的数字员工**，具有：
- 相对稳定的职责
- 相对一致的工作目标
- 监听或接收外部信号
- 匹配职责的工作产出
- 结构化的已做已证据
- 通过轻量级 performance-review loop 接收人类反馈
- 明确的 focus 和 cost 控制

### Quota 模型

简洁的 compute quota：

```json
{
  "quota": {
    "compute": 0.5,
    "window_hours": 24,
    "slot_minutes": 1,
    "allowed_slots": 720,
    "spent_slots": 240,
    "state": "eligible"
  }
}
```

- `1.0` = 全占空比（24h 全可执行）
- `0.5` = 半占空比（约 12h/天）
- `0` = 暂停计算

优先级：health gate → operator gate → evidence wait → focus wait → compute quota

### Gate 模型

Gate 是 LoopX 的核心治理机制：
- **Health gate**: registry 损坏、contract 失败
- **Operator gate**: 读写控制、reward 判断、生产操作
- **Evidence wait**: 等待外部指标或目标控制器响应
- **Focus wait**: 当前 delivery lane 饱和或等待新证据
- **Compute quota**: 计算配额

### Peer Agent 模型

注册 agent 彼此平级：
- 通过 claim、lease、task boundary、capability gate 和 typed continuation 决定谁执行
- 不需要长期 leader agent
- 支持 peer 之间的 handoff

## 4. 集成与工具支持

### 支持的 Host/Runtime

| Host | 入口 | Loop driver |
|------|------|-------------|
| **Codex App** | 在项目中连接 LoopX，运行 `loopx doctor` | Codex App heartbeat |
| **Codex CLI** | 在项目中启动 codex，连接并诊断 | 可见 `/goal <task>` |
| **Claude Code** | 安装 opt-in adapter，`/loopx <任务>` | LoopX gate 的 Claude Code `/loop` |
| **OpenCode** | 静态 command facade | OpenCode command facade |
| **Cursor** | 使用同一 installer | 手动或 runner 调用 |

### 核心 CLI tick

```bash
loopx quota should-run      # 当前 agent 是否应该执行？
loopx todo claim             # 谁拥有这个 slice？
loopx todo update            # 发生了什么？
loopx refresh-state          # 下一轮应该看到什么？
loopx quota spend-slot       # 为完成并验证的 slice 记账
```

### 扩展

- **Lark/飞书 Kanban Adapter**: 看板投射
- **OpenViking Semantic Preference**: 开源贡献偏好
- **Auto Research**: proposer → executor → evaluator/promoter 多角色迭代
- **Issue-Fix Capability**: rolling repo context + 带版本的修复知识

## 5. 产品愿景

### 目标用户

**Loop Agent 的 maintainer/operator** — 需要管理 always-running 数字员工的人。

### First-Screen Promise

用户打开 LoopX 应该能立即看到：
- agent 已经做了什么
- agent 正在做什么
- 哪里被阻塞了
- 下一步会是什么
- agent 需要用户什么
- 用户反馈如何改变计划

### Agent Work Feed

推荐式而非仪表盘式——每个 agent work card 包含：
- agent 产出了什么
- 现在为什么值得关注
- 什么证据支撑
- 花了多少 quota/注意力
- agent 建议的下一步
- 有哪些一键反馈选项

### 四条产品化赛道

1. **Maintainer 管理面**: signal inbox, anchor, lane, gate, evidence, performance review
2. **非技术 operator 状态模型**: plain language 投射
3. **开源 anchor packet**: issue/PR → candidate with evidence boundary
4. **Office operations connector**: connector → signal → feedback loop

### 更远的愿景

- **Creator-Operator Case**: 自媒体/创作运营用户，LoopX 作为创作助手的控制面
- 从开发者工具扩展到非工程操作者

## 6. 公私边界

LoopX 对公开/私有数据有严格边界：

**公开**: schema、目录约定、通用 CLI 代码、adapter 规则、脱敏示例
**私有**: 本地路径、内部仓库名、原始日志、凭证、人名、活跃 goal 状态

实践规则：
- 公开仓库回答："LoopX 如何工作？"
- 项目仓库回答："这个具体 goal 当前在做什么？"
- 运行时根目录回答："最近的 goal tick 发生了什么？"

## 7. 真实轨迹证据

LoopX 声称有超过 200 小时的真实长程 loop 运行证据：

- **OpenViking Issue-Fix**: 200+ 小时的公开贡献轨迹（PR 交付 + 可复用修复知识积累）
- **Auto ML Experiment**: 200+ 小时的 owner-run 实验轨迹（假设 → matched evidence → 无效谱系 → promote/stop gate）
- **Auto Research**: proposer/executor/evaluator 多 agent 并行迭代

## 8. 企业/团队特性与 AI 资产管理

> LoopX 未直接使用「企业版 / AI 资产管理」命名，但以供应商中立的控制面，实质覆盖了团队能力复用与 AI 资产治理两大方向，与 LoopDesk 后续规划高度同频。

### 8.1 对等智能体团队（Peer Agent Teams）
- 注册 agent 彼此平级，通过 **claim（声明）/ lease（租约）/ task boundary / capability gate / typed continuation** 决定下一行动者，无需持久 leader 身份。
- 跨主机协调方向：为显式共享 goal 提供供应商中立协调（NoKV 为候选 provider，非新控制权威）。
- IM/操作员集成：操作员工作区、会话记录、Lark/飞书边界协作面（方向跟踪中）。

### 8.2 采用与治理（Adoption & Governance）
- `ADOPTERS.md` 自愿采用目录；合作伙伴 **OpenViking**（自进化上下文 DB）、**NoKV**（AI 原生分布式文件系统）。
- 治理文件：`GOVERNANCE.md`、`CONTRIBUTING.md`、`CODE_OF_CONDUCT.md`。
- 项目级 **reward 模型**：跨输出量、质量、token 成本、用户注意力成本做保守评估。

### 8.3 AI 资产管理（AI Asset Management）
LoopX 把下列对象纳入「智能体循环操作资产」的治理与留存：
- **证据（Evidence）**：紧凑运行历史、验证状态、阻塞项、已接受 writeback，跨 200+ 小时可查。
- **奖励记忆（Reward Memory）**：实验性上下文学习，默认关闭；命名注册 agent 可试用供应商中立记忆（OpenViking 为可选 provider）。
- **决策上下文（Decision Context）**：基于当前证据与已验证结果重定基决策，保留决策谱系。
- **探索（Explore）能力**：保留假设、发现、基线/处理/守护边界，不替代生产审批。
- **anchor packet（开源锚定包）**：issue/PR → 带证据边界的 candidate，可复用、可审计。
- **公私边界**：`docs/public-private-boundary.md` 确保不提交凭证、私有日志、活跃 goal 状态——是 AI 资产治理的隐私/合规底座。
- **状态内核**即持久化「AI 工作资产」（goal、todo、gate、quota、handoff），跨工具/跨重启不丢失。

### 8.4 与 LoopDesk 路线图（团队能力复用 + AI 资产管理）的关联
LoopDesk 后续规划在个人循环工作区之上新增「团队能力复用 + 配套 AI 资产管理」。LoopX 已在该方向有实质积累，可作首要对标：
- **团队能力复用**：peer agent teams + claim/lease + typed handoff，已是「多 agent 协作」产品化雏形；LoopDesk 可从「单人跨工具」平滑演进到「多人/多 agent 协作」。
- **AI 资产治理**：evidence / reward memory / decision context / anchor packet + 严格公私边界，构成可审计、可复用的资产底座；LoopDesk 的 memory/skills/artifacts 可借其「证据链 + 决策谱系」思路增强复用可信度。
- **成本治理**：reward 模型把输出量/质量/token 成本/注意力成本纳入评估，是 LoopDesk 做 AI 资产成本治理的可借鉴范式。

## 9. 与 LoopDesk 的关系分析

### ⚠️ 极高相关性

LoopX 与 LoopDesk 在理念和设计上有非常显著的重叠：

| 维度 | LoopX | LoopDesk |
|------|-------|----------|
| **定位** | 长程 AI agent 工作的本地控制面 | 个人 loop 工作空间，跨工具保持上下文一致 |
| **本地优先** | ✅ 纯文件系统，零依赖 | ✅ LOOP-STATE.json，本地优先 |
| **状态存储** | `.loopx/registry.json` + `ACTIVE_GOAL_STATE.md` | `LOOP-STATE.json` |
| **跨工具** | Codex、Claude Code、Cursor 等 | Claude Code、Codex、Trae、Gemini 等 |
| **不替代 runtime** | ✅ 控制层，不是 agent runtime | ✅ 协调层，不是 AI IDE |
| **Loop 工程** | Loop Engineering 是核心方法论 | Loop Engineering 是操作方法 |
| **Quota/Cost** | compute quota (duty cycle, slot-based) | cost/safety controls |
| **Gate/Stop** | typed gate model (health, operator, evidence, focus, quota) | stop conditions |
| **Maker/Checker** | 无显式 maker/checker；peer claim 模型 | 显式 maker/checker split |
| **Triage** | 通过 quota should-run + gate 决策 | 显式 triage 步骤 |
| **Memory** | run history + evidence + authority source | durable local memory |
| **Handoff** | typed handoff packet | session continuity |
| **目标用户** | Loop Agent maintainer / operator | 独立开发者 |

### 关键差异

1. **LoopX 更重控制面，LoopDesk 更重工作空间。** LoopX 是一个严格的 state kernel (quota/gate/claim/writeback)；LoopDesk 是一个工作空间 (memory/skills/artifacts + loop engine)。
2. **LoopX 的 goal 模型更成熟。** 六层架构 + 四角色模型 + 两个 turn decision 枚举 + quota 模型 + gate 体系，形成完整治理闭环。LoopDesk 的 loop engine 设计相对简约。
3. **LoopX 面向团队 agent 治理，LoopDesk 面向个人开发者效率。** LoopX 的 peer agent model、lease、claim 机制针对多 agent 场景；LoopDesk 更侧重单人使用多工具的连贯性。
4. **LoopX 已有 200+ 小时真实运行证据。** 这是 LoopDesk 目前缺乏的。
5. **LoopX 有更完善的文档体系。** architecture, state interaction model, integration guide, quota allocation, public/private boundary, control plane course（9 节中文课程）。

### 直接竞争风险

**LoopX 是 LoopDesk 当前最直接的竞品。** 两者在以下维度几乎完全重叠：
- 本地优先的文件系统状态
- 跨 AI coding tool 的控制/协调层
- Loop Engineering 方法论
- 不替代 agent runtime 的定位
- Python 实现（LoopX 也是 Python）

### 可借鉴的设计

1. **Quota 模型**: duty cycle + slot-based 计算配额，比简单的 cost control 更精细。可以参考其 `compute` 占空比、`window_hours` 窗口、`spent_slots` 记账思路。
2. **Gate 体系**: 五级 gate 优先级（health → operator → evidence → focus → quota）是很好的决策链设计。LoopDesk 的 stop conditions 可以演进为类似的分层 gate。
3. **Turn Decision 枚举**: `LoopXTurnRoute` 和 `LoopXTurnResultKind` 提供了 typed 的 turn 前/后决策词汇。比自由文本的 run log 更结构化。
4. **公私边界设计**: 明确区分公开/私有状态，对 local-first 工具而言是重要的产品考量。
5. **控制面 Kanban 心智模型**: 把 control plane 解释为 "面向长程 Agent 的可执行看板" 是很好的用户沟通方式。
6. **Agent Work Feed 设计**: 推荐式 card 而非仪表盘，每张 card 带 evidence + cost + next step + 一键反馈，值得 LoopDesk Web UI 参考。
7. **Zero runtime dependency**: 标准库即可运行，install 一条命令完成。LoopDesk 也应保持这种极简安装体验。

### LoopDesk 的差异化方向

1. **MCP/ACP Adapter 层**: LoopX 通过 CLI 命令集成工具；LoopDesk 通过 MCP-first 的 adapter 层直接嵌入工具。这是更深层的集成。
2. **Memory/Skills/Artifacts 三位一体**: LoopX 靠 run history + evidence；LoopDesk 设计了独立的 memory、skills、artifacts 层，更适合知识积累和复用。
3. **Worktree Isolation**: 文件系统级隔离是 LoopX 没有的能力。
4. **Maker/Checker Split**: 显式的 maker/checker 分工比 LoopX 的 peer claim 模型更适合单人场景的质量保证。
5. **Web UI**: LoopDesk 规划了本地 Web UI；LoopX 的 frontstage 更偏 dashboard/status 展示。
