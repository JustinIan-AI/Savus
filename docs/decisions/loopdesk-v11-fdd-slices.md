# Feature Decomposition — LoopDesk v1.1 FDD Slices

> 状态：已分解
> 版本：v1.1
> 最后更新：2026-07-28
> 负责人：Product / Engineering
> 输入：`docs/prd/personal-loop-workspace-v1.1.zh.md`、`docs/decisions/prd-v1.1-review-checklist.md`、`docs/plans/2026-07-28-loopdesk-v11-fdd-tdd-execution-plan.md`、`docs/decisions/runtime-matrix.md`

## 1. 为什么这样拆

LoopDesk v1.1 的 PRD 已经覆盖 workspace、runtime、intent/router、planner、desktop/handoff、human model 等多个能力；如果直接按模块线头开发，很容易出现“每个文件都有改动，但没有一个可独立验收的 feature stop condition”。

因此，v1.1 FDD 采用 **capability slice + failing-test-first** 的交付方式：

- 每个 Feature 有独立 stop condition；
- 每个 Task 先写最小失败测试；
- 每个 Feature 结束后，只保留最小实现 + 测试证据 + docs evidence。

## 2. Feature Slices

| Feature | Slice | 一句话价值 | Stop condition | 证据位置 |
| --- | --- | --- | --- | --- |
| F1 | Workspace Context and Type Model | 让 `LOOP-STATE.json` 明确表达 project/personal/business 三类 workspace，以及 `user/project/task` 三类 context。 | schema、layout、service 都通过 workspace type / context subdir 测试。 | `tests/test_loop_workspace/test_schema.py`、`tests/test_loop_workspace/test_layout.py`、`docs/prd/personal-loop-workspace-v1.1.zh.md` |
| F2 | Agent Runtime and Execution Trace Contracts | 把 runtime、execution trace、run log 从隐含约定变成显式类型契约。 | `AgentRuntime` 接口、trace schema、run log consumer 字段都有锚点测试。 | `src/loopdesk/engine/types.py`、`tests/test_engine/test_router_decision.py`、`src/loopdesk/loop_workspace/schema.py` |
| F3 | Intent Engine and Router Surface | 明确 intent classification、runtime/skill/MCP tool 决策、human override 路径。 | intent 分类、router 输入输出、人工可干预点都有测试。 | `src/loopdesk/engine/router_decision.py`、`tests/test_engine/test_router_decision.py` |
| F4 | Task Planner and Continuous Learning Loop | 支持 task graph / DAG / depends_on，以及 completed goal 向 memory/skills 的 compact flush。 | task graph、learning loop flush、goal+worktree 创建都有测试。 | `src/loopdesk/loop_workspace/schema.py`、`src/loopdesk/loop_workspace/service.py`、`tests/test_engine/test_v11_intent_planner.py` |
| F5 | OpenCode Adapter and v1.1 Runtime Matrix | 将 OpenCode 纳入官方支持矩阵，并保持 capability profile 与 docs 一致。 | OpenCode 出现在官方矩阵，runtime profile 可被测试读取。 | `src/loopdesk/loop_workspace/runtime_matrix.py`、`docs/decisions/runtime-matrix.md`、`tests/test_loop_workspace/test_runtime_matrix.py` |
| F6 | Desktop Launcher and Local Runtime Distribution | 明确桌面端只是 local runtime + system launcher，不替代 gateway authority。 | desktop boundary 文档和最小 smoke test 存在且通过。 | `docs/decisions/desktop-web-im-product-boundary.md`、`tests/test_packaging/test_desktop_launcher.py` |
| F7 | Project/Loop Switching CLI Surface | 给外部工具一个明确的 handoff entrypoint，而不是靠猜 `current_work_id`。 | `workspace project set` / `workspace loop set` 存在，状态可读，且不改 loop engine。 | `docs/decisions/handoff-cli-surface.md`、`tests/test_cli/test_loop_workspace_handoff_commands.py` |
| F8 | Guided Handoff and Anti-Room Guardrails | 把“如何第一次 handoff”说清楚，并防止 team-room / cloud-sync / IM-first 泄漏到公共叙事。 | guided handoff doc 存在；guardrail test 通过。 | `docs/guides/guided-handoff.md`、`tests/test_docs_guardrails.py` |
| F9 | Human Model Surface | 在 workspace state 中保留极简 human profile，用于偏好、decision pattern、review standard 演进。 | human profile schema / service / gateway RPC 都有读写测试。 | `tests/test_loop_workspace/test_human_model.py`、`tests/test_gateway/test_rpc_loop_workspace_human_model.py` |
| F10 | v1.1 Release and Acceptance Evidence | 让 v1.1 不是“代码写完了”，而是有 release notes、acceptance checklist、launch gate。 | release/acceptance artifacts 存在；focused test commands 可被引用。 | `docs/releases/loopdesk-v1.1.md`、`docs/acceptance/loopdesk-v1.1-acceptance-checklist.md`、`tests/test_release_acceptance.py` |

## 3. 交付节奏

### Phase A：Capability Skeleton
- F1 + F2 + F3 + F4
- 目标：把 PRD 里“被讨论很多但没有类型锚点”的 runtime、trace、intent、task graph、learning loop 做成可测试骨架。

### Phase B：Surface and Distribution
- F5 + F6 + F7
- 目标：锁定 runtime 支持范围、桌面边界、handoff CLI，不让产品边界继续漂移。

### Phase C：Narrative and Launch
- F8 + F9 + F10
- 目标：补齐 docs guardrail、human model、release/acceptance 证据，形成可 review 的 v1.1 launch 包。

## 4. 每个 Feature 的 TDD 模板

每个 Feature 必须按以下模板执行：

```text
1. 写最小失败测试
2. 运行单 Feature 测试并确认 FAIL
3. 写最小实现
4. 运行单 Feature 测试并确认 PASS
5. 运行相邻回归测试
6. 更新 run log
7. 检查 docs/decisions 是否需要回填
```

## 5. 与 v1.2 Backlog 的关系

- 若某个 capability 在 v1.1 只需要“契约存在”，就只保留 schema + tests，不展开复杂 UI/automation；
- 若某个能力需要更重的 runtime/scheduler/team semantics，直接进入 `docs/plans/prd-v1.2-gap-backlog.md`；
- v1.1 不接受 scope creep；发现新需求时，先判断属于 F1-F10 还是 v1.2。
