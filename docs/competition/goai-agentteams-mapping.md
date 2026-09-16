# LoopDesk × AgentTeams 映射对照表

> 配套文档：`goai-agentinfra-proposal-core.md` 第 4.4 节引用。
> 用途：说明 LoopDesk 如何作为 AgentTeams 的 Worker Runtime 接入，覆盖赛道要求评估的"角色编排、任务拆解、上下文传递、协同执行、状态追踪"五项。
> 事实基准：AgentTeams 官方仓库（agentscope-ai/AgentTeams）README，项目已于 #1065 完成 hard-cut rename（前身为 HiClaw）。
> 标记约定同方案内核：`[已实现]` 已在 LoopDesk 代码；`[增强]` 底座已有需补层；`[新建]` 复赛交付。

---

## 0. 关键事实基线（避免虚构）

| 维度 | AgentTeams 官方事实 |
| --- | --- |
| 项目定位 | 协作式多智能体**编排平面**（orchestration plane），明确声明"不与其他 Agent runtime 竞争，本身不实现 Agent 逻辑，只编排管理多个 Agent 容器" |
| 控制平面 | `agentteams-controller`，Kubernetes 原生，reconcile `Worker` / `Team` / `Manager` CR |
| CRD Kinds | `Manager`、`Team`、`Worker`、`Human`（声明式 YAML 管理） |
| Worker `spec.runtime` 现有值 | `openclaw`（默认，Node.js 通用代理）、`qwenpaw`（Python 轻量）、`copaw`（兼容别名）、`hermes`（自主编码代理 + 终端沙箱） |
| `openhuman` | **CRD 显式拒绝** `spec.runtime: openhuman`；人类 Worker 须经由 `Human` CRD / `spec.image` 显式配置 |
| 通信 | Matrix 协议（Tuwunel IM Server 自托管 + Element 客户端）；每房间含"人类 + Manager + 相关 Workers"，默认 Human-in-the-Loop |
| 凭证隔离 | Higress AI Gateway 持真实密钥；Worker 仅持 `consumer token`，看不到真实凭证 |
| 共享存储 | MinIO，Worker 设计为**无状态**，文件存于 MinIO 降低 token 消耗 |
| 完成上报 | Worker 在 Matrix 房间内自然语言回复结果（如 "Done. PR submitted: ..."），**无机制验证"done"是否真实** |
| 可观测 | 控制器 reconcile metrics + 集成 AgentLoop 提供审计 |

> **核心定位**：AgentTeams 自述不实现 runtime 层、且 Worker 完成是"自报告"的——这正是 LoopDesk 的接入点。LoopDesk 作为**新增的 `spec.runtime: loopdesk`** 值（拟贡献），补齐官方声明不做的运行时可靠性层。

---

## 1. 角色编排（角色编排 → AgentTeams CRD）

| LoopDesk Agent | 职能 | AgentTeams 映射 | 状态 |
| --- | --- | --- | --- |
| `loopdesk-planner` | 拆解与重规划 | 由 **Manager / TeamLeader** 职能延伸承载；Planner 作为 `Worker`（runtime=loopdesk）被 Manager 调度 | `[增强]` |
| `loopdesk-executor` | 代码修复执行 | **Worker**（runtime=loopdesk），在独立 worktree 内工作 | `[已实现]` worktree + `[新建]` 适配层 |
| `loopdesk-verifier` | 独立验证 | **Worker**（runtime=loopdesk，只读角色），与 Executor 同 Team 但权限隔离 | `[新建]` ★ |
| `loopdesk-curator` | 经验蒸馏 | **Worker**（runtime=loopdesk），读取 Evidence Bundle | `[增强]` |
| `loopdesk-approver` | 人工审批 | **`Human` CRD**（Human-in-the-Loop 默认机制），非 runtime | `[已实现]` human gate |

**编排拓扑**：一个 `Team` 容纳 planner / executor / verifier / curator 四个 loopdesk Worker + 一个 Human；Manager 负责把 Issue 路由进 Team Room 并做心跳监控。

**为什么是 Worker 而非另造编排**：AgentTeams 已提供声明式 CRD、Matrix 审计时间线、Higress 凭证隔离、MinIO 共享存储。LoopDesk 不重造这些，只作为 `spec.runtime` 的一个可插拔实现——符合赛道"以 AgentTeams 为协同设计基点"的强制要求。

---

## 2. 任务拆解（任务拆解 → Manager/TeamLeader + TaskDecompose Skill）

| 环节 | AgentTeams 原生 | LoopDesk 增强 |
| --- | --- | --- |
| 任务进入 | 用户向 Manager 发指令，Manager 在 Room 内回应并建 Worker | Issue / 错误日志 / 工单进入 Team Room，Planner 接管 |
| 拆解动作 | Manager / TeamLeader 做任务分配（v1.2.1 强化原子化 Matrix + TeamHarness 分配） | `TaskDecompose` Skill 把任务拆为带**可执行验收标准**的任务图（超出原生分配粒度） |
| 验收标准 | 原生无结构化验收标准概念 | 每个子任务含 `acceptance_criteria`（如"原测试 X 由红转绿"），可被 Verifier 机器消费 |
| 重规划 | 原生靠 Manager 重新分配 | FAIL 时 Receipt 回打 Planner 触发自动重规划（闭环回环） |

**状态标记**：Manager/TeamLeader 分配 `[已实现]`；`TaskDecompose` 产出有界任务图 `[增强]`（Loop Engine + 契约）。

---

## 3. 上下文传递（上下文传递 → Matrix Room + LOOP-STATE.json + MinIO）

| 维度 | AgentTeams 原生机制 | LoopDesk 映射与增强 |
| --- | --- | --- |
| 实时通信 | Matrix Room（人/Manager/Workers 同房间，默认可见可干预） | 复用 Matrix Room 作为协同通道 |
| 大产物 | MinIO 共享存储，Worker 无状态 | 大产物（diff、trace、receipt）走 MinIO / 本地存储，引用进 Evidence Bundle |
| 结构化状态 | 原生以对话/声明为主 | `LOOP-STATE.json` 承载有界任务契约与状态引用，**只传契约不传原始对话全文**，降低 token 消耗（与 MinIO 设计理念一致） |
| 隔离隔离 | 原生 Worker 无状态共享 | 每个 loopdesk Worker 在独立 **git worktree** 内工作（`[已实现]`），物理隔离避免并行冲突 |

> 关键差异：原生上下文以自然语言对话流动，LoopDesk 额外提供**结构化状态契约 + 工作区物理隔离**，这正是"并行 Agent 改同一代码库"场景缺的能力。

---

## 4. 协同执行（协同执行 → Worker 协作 + Skill→MCP 双层）

| 环节 | AgentTeams 原生 | LoopDesk 增强 |
| --- | --- | --- |
| 工具调用 | Worker 经 Higress 网关调 LLM / GitHub / MCP，凭证经 consumer token 隔离 | Skill 作能力抽象层 → MCP 作工具连接层（`[已实现]` 双向），Agent 不裸调工具 |
| 多 runtime 共存 | OpenClaw / QwenPaw / Hermes 可同房间协作 | loopdesk 作为第四种 runtime 加入同一 Team Room |
| 执行隔离 | 原生 Worker 无状态、共享 MinIO | Executor 在隔离 worktree 执行，Verifier 只读挂载该 worktree（**上下文 + 权限双隔离**） |
| Skill 下发 | v1.2.2 支持 Manager 向 Worker 自定义 Skill 交付（带校验 + `Worker.spec.skills` + 热刷新） | LoopDesk 的 7 个新 Skill 与 62 个 bundled Skill 通过该机制注入 Worker |

**凭证链路对齐**：LoopDesk Worker 同样只持 Higress `consumer token`，真实密钥留在网关——与 AgentTeams 企业级安全模型天然一致。

---

## 5. 状态追踪（状态追踪 → reconcile metrics + Trace/Evidence）

| 维度 | AgentTeams 原生 | LoopDesk 增强 |
| --- | --- | --- |
| 心跳/状态 | Manager 心跳、控制器 reconcile metrics | 复用；额外 Loop Engine 任务状态机（maker/checker/stop） |
| 审计时间线 | 集成 AgentLoop 提供全栈审计 | Trace JSONL（`[已实现]`）按 `TraceId` 串联决策/工具调用/审批/验证，与 Matrix 审计时间线对齐 |
| 完成判定 | **Worker 自报告 "Done"**，**无验证机制** | `IndependentVerify` 产出 `Validation Receipt`（PASS/FAIL + 退出码 + 产物哈希）作为**唯一通过凭证** |
| 证据留痕 | 原生无统一证据包 | `EvidenceDeposit` 聚合 Evidence Bundle（trace + diff + receipt）落 MinIO / 本地 |
| 可复现 | 依赖各 Worker 自行记录 | 自举回归集（真实 bug commit 为 ground truth）+ Trace 回放，满足复现要求 |

> **这是本方案相对原生的最关键补足**：AgentTeams 能发现 Worker "卡住"（心跳），但发现不了 Worker "错误地认为自己成功"（自报告）。LoopDesk 的 Receipt 让"完成"变成可机器验证的事实。

---

## 6. 拟贡献给 AgentTeams 生态的接口契约

| 契约 | 形态 | 开放价值 |
| --- | --- | --- |
| `spec.runtime: loopdesk` | Worker 适配层（镜像 + CRD 映射） | 任意 AgentTeams 团队可声明式调度 LoopDesk 作为研发 Worker |
| Validation Receipt JSON Schema | 机器可读验证回执 | 可被其他 runtime 直接采用，统一"完成"语义 |
| 7 个新 Skill 包 | 符合 Agent Skills 开放规范 | 跨团队复用，补运行时可靠性能力 |

---

## 7. 需向 AgentTeams 侧澄清/协商的点（诚实标注）

1. **`loopdesk` 是拟新增的 runtime 值**：需在 Worker CRD 注册（或在社区提交 runtime 适配），复赛落地。属 `[新建]`。
2. **Worker 无状态 vs LoopDesk 有状态 worktree**：AgentTeams 设计 Worker 无状态、文件存 MinIO；LoopDesk 的 worktree 属于 LoopDesk 内部管理的状态，需明确"无状态"指 Worker 容器而非其内部子工作区。建议在适配层用 MinIO 持久化 worktree 引用。
3. **Human CRD 的接入细节**：`openhuman` 被 CRD 拒绝，Human 须走 `Human` CRD；Approver 按此映射，不宣称 runtime。
4. **Receipt 与原生完成语义的桥接**：需定义"Manager 何时采信 Receipt 而非 Worker 自报告"——建议在 Team 级策略中把 Verifier 的 Receipt 设为合并前置条件。

---

## 8. 一键对照速查

| 赛道评估项 | 原生 AgentTeams | + LoopDesk 后 |
| --- | --- | --- |
| 角色编排 | Manager/Team/Worker/Human CRD | + 4 个 loopdesk Worker + Human 审批 |
| 任务拆解 | Manager 分配 | + 结构化验收标准任务图 |
| 上下文传递 | Matrix + MinIO + 对话 | + LOOP-STATE 契约 + worktree 隔离 |
| 协同执行 | 多 runtime 协作 + Higress 凭证隔离 | + Skill→MCP 双层 + 执行/验证双隔离 |
| 状态追踪 | 心跳 + reconcile + AgentLoop 审计 | + Validation Receipt + Evidence Bundle + 自举回归复现 |
| 完成可信度 | ⚠️ 自报告，不可验证 | ✅ 独立验证，机器可校验 |
