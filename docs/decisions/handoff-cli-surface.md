# 产品决策 — LoopDesk v1.1 Handoff CLI Surface

> 状态：已决策
> 版本：v1.1
> 最后更新：2026-07-28
> 负责人：Product / Engineering
> 输入：`docs/prd/personal-loop-workspace-v1.1.zh.md`、`docs/decisions/desktop-web-im-product-boundary.md`、`docs/decisions/runtime-matrix.md`、`docs/plans/2026-07-28-loopdesk-v11-launch-completion-fdd-tdd.md`

## 1. 决策背景

PRD v1.1 已明确：Project 是顶层空间容器，Loop 是项目内的连续工作流，Goal 是 Loop 内的工作单元；切换 Project / Loop 必须只改变 handoff 上下文，而不是执行工作流本身。

当前本地 workspace 已有 durable state、run log、worktree isolation，但 CLI 缺少显式 project / loop 选择器。这导致用户在工具之间切换时，只能靠 `current_work_id` 或外部记忆重建 handoff context。

## 2. 决策结论

LoopDesk v1.1 在 workspace CLI 中新增最小 handoff surface：

- `workspace project set <root> --name <project_name> [--json]`
- `workspace loop set <root> <loop_id> [--json]`

实现约束：

- project / loop 切换只写 handoff 状态，不迁移 workspace 数据，不复制 memory/skills/artifacts。
- `project set` 同时设置 `project_name` 和 `active_loop_id` 默认值；`loop set` 只修改 handoff 上下文。
- `loop set` 允许把 `current_work_id` 切到活跃 Loop，但不改写 `loop_engine` 的 goal / phase / iteration / stop condition。
- CLI 必须暴露 `loop_engine` 只读快照，让外部工具判断是否有正在进行的 engine state，但 handoff 命令本身不启动或停止 loop engine。

## 3. 边界说明

- 不做 workspace migration、project template import、team project sharing。
- 不得以 cloud sync 为主路径；v1.1 公共叙事不得暗示 team room、remote project authority、IM-first project selector。
- Web / Desktop 的 project / loop 选择器可复用同一 state 字段；v1.1 先锁定 CLI 实现面和 state schema。
- 若未来需要 multi-project workspace，应进入 v1.2 backlog，而不是在本决策中扩展目录结构。

## 4. 验证方式

- CLI handoff tests：`tests/test_cli/test_loop_workspace_handoff_commands.py`
- State schema / service 回归：`tests/test_cli/test_loop_workspace_cmd.py`
- Gateway engine regression：`tests/test_gateway/test_rpc_loop_workspace_engine.py`
