# LoopDesk Loop 管理模块优化建议（基于 LoopX 对标）

> Status: v0.2 设计输入（draft）
> Date: 2026-09-11
> Author: design partner (WorkBuddy Intelligent Design Assistant)
> Companion: `docs/prd/personal-loop-workspace.zh.md` §8.5（Loop/Goal → UX 桥接）、`docs/design-system.md`
> Research source: 本机部署的 LoopX（`io.loopx.control-plane` 控制面 + 全套 `loopx-*` skills + `loopx` CLI）

---

## 1. 背景与目标

LoopDesk 当前 Loop 管理模型（经 PRD 重写与画布落地）为：

```
项目 Project（顶层空间，侧栏 项目切换器）
└─ 循环 Loop（1 项目 = 多 Loop，各自独立连续工作流）
   └─ 目标 Goal（每 Loop 多个；各享 worktree + Loop Engineering 六阶段）
      ↑ 新建任务 = 创建一个 Goal，自动进当前活跃 Loop
```

Workspace = 当前 Loop 的连续工作视图（隐式贯穿，无独立 Loop 页）。

本次调研 **LoopX**（同为主打长周期任务循环的本地 Agent 工作台）的真实界面与生命周期模型，目的是：
1. 校准 LoopDesk 在 Loop 管理上的**缺漏**；
2. 输出**可执行的界面优化建议**（A~H），作为 v0.2 设计输入；
3. 沉淀**画布增强清单**（A/B/C/E 优先可见项）。

---

## 2. LoopX 调研结论

### 2.1 数据模型（关键差异）

- **管理单元是 Goal，"Loop" 是执行上下文而非容器**。
  - Repo → `.loopx/registry.json` + `.codex/goals/<goal-id>/ACTIVE_GOAL_STATE.md`（每 Goal 一个状态文件）
  - 共享控制面 `~/.codex/loopx/registry.global.json` —— 跨项目仪表盘真相源
  - 一个仓库可挂多个 peer-owned Goal（如 delivery + validation 两条 lane）
- LoopX 的 "Loop" = 跨 host 的 heartbeat / agent-loop 执行上下文（隐式），**没有可见的 Loop 容器**。
- 这与 LoopDesk 把 Loop 做成一等容器正好相反 —— 见 §5 的 H 项（这是 LoopDesk 的差异化优势，保留）。

### 2.2 界面 / 面板面（从 CLI 与 skills 还原）

| 面板 | 命令 | 作用 |
| --- | --- | --- |
| 全局摘要 | `global-summary` | 跨项目进度速览 |
| 全局闸门 | `global-gates` | 列出待人工决策的门 + 阻塞范围 |
| 全局待办 | `global-todos` | 跨项目 user/agent todo 就绪度 |
| 全局风险 | `global-risks` | 陈旧 run / 边界风险 / 回滚候选 |
| 单 Goal 状态 | `status` | 当前 Goal、gate、下一步 |
| 验收包 | `review-packet` | 含「人只需判断 / Gate 草稿 / 给 Agent」三段 |
| 证据账 | `evidence-log` | 每 Agent 的 thin ledger，供 replan |
| 诊断 | `diagnose` | 紧凑证据包 |

### 2.3 生命周期控制（最值得借鉴的部分）

- `start-goal --guided` → 产出 `goal_start_contract` + `ordered_steps`（**先计划后执行**）
- `quota should-run` —— **算力闸门**：决定下一 turn 该不该跑（minute 粒度配额）
- `scheduler_hint` —— 调度策略：`stop_until_explicit_resume` / `stateful_backoff` / `recommended_rrule`（卡住自动暂停、带退避）
- `operator-gate` + `interaction_contract`（user_channel / agent_channel / cli_channel 三段 split）—— **正式的人工门**
- `pr-review` / `pr-program`（snapshot contract + diff_snapshot）—— 交付验收
- `self-repair` + `autonomous_replan_required` / `dead_monitor_repeat` —— 自愈与重规划守卫
- `human_reward` —— 每 run 的人工奖励信号

---

## 3. LoopDesk 当前 Loop 模块对照

| 维度 | LoopX | LoopDesk 当前 | 差距 |
| --- | --- | --- | --- |
| 管理单元 | Goal（Loop=执行上下文） | Project→Loop→Goal | LoopDesk 层级更清晰，但缺 Goal 契约 |
| 跨项目视图 | 有（4 个 global-* 面板） | 无，仅单项目 Workspace | **缺总览控制面** |
| 创建流 | `goal_start_contract`+`ordered_steps` | 新建任务→直接进当前 Loop | **缺计划合同** |
| 生命周期闸门 | `quota`+`scheduler_hint` 驱动暂停/恢复 | 仅"停止"阶段标签 | **缺自动暂停守卫** |
| 人工门 | `operator-gate`+`interaction_contract` | 仅"待审批"chip | **门未形式化** |
| 验收 | `review-packet`+`evidence-log`+`human_reward` | "交付物"静态文本行 | **交付物无证据链** |
| 待办血缘 | `todo succession`+priority stack+lineage | Current work 仅显阶段 | **缺 step 血缘** |
| 自愈 | `self-repair`+replan 守卫 | 仅"升级"阶段 | **缺自动重规划** |
| 显式 Loop 容器 | 无（Loop 是隐式 heartbeat） | 有 + 待加 Loop 切换器 | **LoopDesk 优势，保留** |

---

## 4. 优化建议（A~H，按优先级）

### A. 跨项目「All Loops / 总览」控制面【高】
- **借鉴**：LoopX 的 `global-summary / gates / todos / risks` 四个跨项目面板。
- **落地**：在控制组加"总览"页，跨所有项目的 Loop 聚合（活跃数 / 卡住数 / 待审批数 / 风险数）。
- **理由**：当前只有单项目 Workspace，多项目一多就失控。
- **画布映射**：新增"跨项目总览"页（§5-1）。

### B. 新建任务显式化 Goal 契约【高】
- **借鉴**：`start-goal --guided` → `goal_start_contract` + `ordered_steps`（先计划后执行）。
- **落地**：创建 Goal 时先出契约卡：目标 / 范围 / 验收标准 / `ordered_steps`（计划先于执行）。
- **理由**：当前"新建任务"直接进当前 Loop，没有计划可见性 —— 这正是 LoopX 刻意强化的环节。
- **画布映射**：新增"新建任务"弹窗（含 Goal 契约 + 步骤列表）（§5-2）。

### C. 把「升级 / 停止」做成真 gate【高】
- **借鉴**：`operator-gate` + `interaction_contract`（user/agent/cli 三段 split）。
- **落地**：Loop Engineering 的"升级""停止"从阶段标签升级为**带人工确认的形式化门**：触发时弹"人只需判断"的确认卡，记录决策与理由。
- **理由**：当前只有"待审批"chip，没有决策流。
- **画布映射**：新增"升级 / 停止 gate"确认卡（§5-3）。

### D. Loop 停止条件接 quota/scheduler 守卫【中】
- **借鉴**：`scheduler_hint`（`stop_until_explicit_resume` / `stateful_backoff`）。
- **落地**：当 Goal 连续 N turn 无进展、或成本触预算上限时，Loop 自动暂停 + 退避提示，而非空转。
- **理由**：补 LoopDesk"停止"阶段的执行语义。
- **画布映射**：状态 chip 增加"自动暂停"态（非独立页）。

### E. 交付物升级为 evidence-backed 验收包【高】
- **借鉴**：`review-packet` + `evidence-log` + `human_reward`。
- **落地**：把当前静态"交付物"行改成验收包结构：spec/test/PR 作为**带证据链**的验收项，每项可点开看产物 + 人工 reward。
- **理由**：这是 LoopDesk "交付物随 Goal 沉淀"理念的最佳落地形。
- **画布映射**：改造"交付物"面板为验收包（§5-4）。

### F. Goal 级 step 血缘 + priority stack【中】
- **借鉴**：`todo succession` + priority stack + lineage。
- **落地**：Current work 面板从"显阶段"升级为可追踪的 step 列表，带优先级栈与 successor 血缘（A 完成后自动激活 B）。
- **画布映射**：改造 Current work 面板（v0.2）。

### G. 升级 → 自主 replan 守卫【中】
- **借鉴**：`self-repair` + `autonomous_replan_required` / `dead_monitor_repeat`。
- **落地**：当 Loop 卡住 / 检查反复失败时，自动进入 replan（重拟 `ordered_steps`），而非停在人手里等拍板。
- **画布映射**：非独立页，融入升级门逻辑。

### H. 保留 LoopDesk 的显式 Loop 容器 + Loop 切换器【关键】
- **立场**：LoopX 没有可见的 Loop 容器；LoopDesk 的"项目→多 Loop→Goal"显式层级 + 侧栏 Loop 切换器是**差异化优势**，不要因借鉴 LoopX 而弱化。
- **落地**：A~G 全部叠加在现有 Loop 容器模型之上。
- **画布映射**：侧栏已在 PRD 中规划 Loop 切换器（待画布落地）。

---

## 5. 本次画布增强范围（A / B / C / E）

> 注：原 Ardot 画布（fileId `704108281339017`）在调研时 Ardot 服务可用；本轮 Ardot MCP 未连接，故以下四块以**等价 HTML 原型稿**交付（配色对齐 `design-system.md`），待 Ardot 重连后并入画布。

| 增强块 | 对应建议 | 原型内容 |
| --- | --- | --- |
| 跨项目总览页 | A | 跨项目 Loop 聚合卡片 + 阻塞/风险列表 |
| 新建任务弹窗 | B | Goal 契约（目标/范围/验收/ordered_steps） |
| 升级/停止 gate 卡 | C | 人工确认卡（人只需判断 / 给 Agent / 理由） |
| 交付物验收包 | E | evidence-backed 验收项（产物 + human_reward） |

---

## 6. 开放问题 / 下一步

1. **Ardot 服务重连**后，把 §5 四块并入 `704108281339017`，并补侧栏 Loop 切换器（建议 H）。
2. **跨项目总览的数据源**：LoopDesk 当前是单项目本地优先，跨项目聚合需要统一的 `~/.loopdesk/registry.global.json` 类真相源（参考 LoopX 的 `registry.global.json`）—— 是否纳入 v0.2？
3. **Goal 契约与 worktree 的绑定**：`ordered_steps` 每一步是否各开一个 worktree，还是共享一个 Goal worktree？需与 Loop Engineering 执行层对齐。
4. **human_reward 信号如何沉淀**：是否进项目记忆（`memory/`），供下次同类 Goal 复用？

---

## 7. 结论

LoopX 在**跨项目控制面、计划合同、形式化门、证据化验收、自动守卫**五个维度领先；LoopDesk 在**显式 Loop 容器层级**上领先。采纳 A~E（高优先级）即可让 LoopDesk 的 Loop 管理从"阶段标签展示"升级为"可计划、可门控、可验收、可守护"的闭环。
