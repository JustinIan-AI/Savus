# LoopDesk v0.1 实施计划（中文版）

> 状态：待评审
> 版本：v0.1
> 日期：2026-07-07
> 负责人：Product / Engineering
> 方法论锚点：`docs/research/loop-engineering.md`
> 依据：`docs/prd/personal-loop-workspace.md`、`docs/decisions/risk-handling-plan.md`、`docs/decisions/product-strategy.md`、`docs/architecture/personal-loop-workspace.md`、`docs/features/core-feature-list.md`

## 1. 目标与原则

### 1.1 产品目标

- 为独立开发者提供 **本地优先的个人 loop workspace**，让 Claude Code、Codex、Codebuddy、Trae、Gemini 和本地 CLI 的工作上下文、记忆和过程状态可以连续传递。
- 以 `LOOP-STATE.json`、memory、skills、artifacts、run log 为核心，形成可检查、可导出、可恢复、可运营的工作底座。
- 在跨工具场景里，降低重复解释上下文、搬运决策和重建任务状态的成本。
- 让 Loop 负责后台发现和分类工作，Goal 负责后台完成有边界的开发任务；两者是职责边界，不是前端两张独立页面。
- 对个人开发者呈现完整开发过程：不管是发现 bug 还是发现开发任务，一旦明确就自动进入 Goal 执行，并通过 maker/checker、budget、approval、worktree isolation 控制风险。
### 1.2 Loop / Goal 关系与成熟度模型
- 前端负责统一展示当前工作、来源、状态、run log、approval、成本和下一步建议，不要求用户手动管理 Loop/Goal 切换。
| 概念 | 作用 | v0.1 解释 |
- 人工介入仅保留在 approval、escalation、ambiguous items、denylist、高风险操作和预算/权限不足场景。
| Loop | 按计划发现工作、分类优先级、维护连续视角、生成候选 Goal | 头脑风暴、调研、竞品分析、依赖 review、daily brief 等持续性工作 |
| Goal | 完成有边界、可验证的具体任务，直到 stop condition 满足 | 代码修复、重构、review、文档修改、工具桥接验证等一次性执行任务 |
| L1 | 报告与 triage | Loop 只分类并记录到 `LOOP-STATE.json`，不自动修复 |
| L2 | 本地工具 + 人工确认 | 可执行本地 Goal，但高风险步骤需 approval |
| L3 | 更长自动化链 | 仅在被明确授权且预算/门控满足时运行 |

核心关系：
- Loop 不直接执行复杂变更，而是持续运行 triage，产出可执行问题、决策、Goal。
- **后端职责边界优先**：Loop/Goal 的切换由系统根据状态自动完成，前端只呈现统一工作流。
- **特性驱动优先**：先拆分特性，再拆任务；每个特性都要有目标、范围、验收条件、回滚条件。
- **测试驱动执行**：每个任务先写最小失败测试，再最小实现，再跑定向测试。
- **Loop Engineering 驱动交付**：按 triage -> maker -> checker -> escalation -> run log -> stop condition 推进。

### 1.3 非目标

- 不做团队协作、云房间、成员角色、企业 onboarding。
- 不做重桌面 GUI、IM 优先的产品形态。
- 不把 legacy OpenSquilla 多渠道运行时直接当成 v0.1 产品面继续扩张。
- 不照搬 GitHub/CI/PR 中心化叙事；LoopDesk 的重点是个人开发工作台与跨工具连续视角。

### 1.4 开发原则

- **特性驱动优先**：先拆分特性，再拆任务；每个特性都要有目标、范围、验收条件、回滚条件。
- **测试驱动执行**：每个任务先写最小失败测试，再最小实现，再跑定向测试。
- **Loop Engineering 驱动交付**：按 triage -> maker -> checker -> escalation -> run log -> stop condition 推进，并把每个特性都当成一个可运营 loop。
- **Loop / Goal 分层执行**：先用 Loop 收敛问题，再用 Goal 执行验证；不在模糊阶段直接进入 L3 自动化。
- 默认目录包含 memory、skills、artifacts、worktrees、personal templates 目录
- **文档即交付物**：研究、决策、风险、计划、状态变化必须先落盘，再继续实现。
- **命名一致优先**：公开面统一使用 `LoopDesk`、`loop_workspace`、`LOOP-STATE.json`、`Loop`、`Goal`；不把 legacy `session`、`workspace-state.json`、channels 术语带入 v0.1 产品表面。

## 2. 总体范围与边界

### 2.1 v0.1 必须交付

| 模块 | 说明 |
| --- | --- |
| Workspace State Protocol | `LOOP-STATE.json`、可序列化/反序列化、导出导入、override history |
| Loop Workspace 布局 | 标准目录结构、memory、skills、artifacts、worktrees |
| 状态服务与持久化 | 创建/查询/更新 loop state、记录 Goal run log、可恢复 |
| Git worktree 隔离 | 自动化/高风险的 Goal 在独立 worktree 中运行 |
| CLI | `loop init/show/update/resume/export` 等核心命令 |
| Gateway RPC | 为本地 Web UI 和外部客户端提供 loop workspace 接口 |
| 本地 Web UI | 查看 Loop/Goal 状态、运行记录、审批项、成本与错误 |
| Cross-tool 适配层 | MCP-first，ACP-second，以及本地 CLI bridge |
| Memory & Session 连续性 | 本地 durable memory、搜索、compaction、session resume |
| Skills & Meta-Skills | 个人工作流 skill 的查看、运行、审计 |
| Cost & Safety | 预算、审批、升级、denylist、kill switch |
| 集成测试 | 至少一个本地编码工作流 MCP 场景、自动化 Goal 场景 |

### 2.2 v0.1 明确不进入公开面

- channels、Slack/Telegram/DingTalk/WeCom 等 IM onboarding
- cron/scheduling 作为主卖点叙事
- diagnostics/replay/migration 作为主要用户旅程
- 视频、音乐、语音、论文写作、PDF/PPTX/DocX 等宽媒体 skill 矩阵
- 团队 workspace、成员管理、云房间、marketplace

### 2.3 架构边界

- `src/loopdesk` 作为 **可复用 runtime 库**
- `src/loopdesk/loop_workspace` 作为 **v0.1 产品 owned 层**
- legacy `session`、`dist/workspace_state`、`channels`、`scheduler`、broad skills 只能内部复用，不能直接暴露给 v0.1 用户
- `LOOP-STATE.json` 是个人 loop 状态唯一 source of truth；`workspace-state.json` 仅是 legacy install inventory

## 3. 特性拆分与任务拆解
Feature details and boundary notes are maintained in `docs/features/loopdesk-v0.1-feature-breakdown.md`; this plan keeps the same six features and execution boundary.

采用 FDD + TDD + Loop Engineering 方式执行。每个特性先写 feature plan，再拆成小任务；每个任务先写失败测试，再最小实现。

### 特性 1：LoopDesk 核心状态与布局

**目标**：建立可运行的最小 loop workspace 底座。

**范围**
- in：`LoopWorkspaceState`、序列化、目录布局、worktree isolation helper
- out：Web UI、RPC、MCP adapter、memory 检索

**验收条件**
- `LOOP-STATE.json` 可创建、读取、更新、导出、恢复
- 默认目录包含 memory、skills、artifacts、worktrees
- 自动化 loop 可在独立 worktree 中启动，且不会污染主分支
- 定向测试全部通过

**回滚条件**
- 状态文件格式破坏现有可恢复性
- worktree 逻辑导致主工作区误切换或误删

### 特性 2：LoopDesk 状态服务与 CLI

**目标**：让开发者可通过 CLI 管理 loop state。

**范围**
- in：state service、CLI `loop init/show/update/resume/export`
- out：Web UI、RPC、外部 adapter

**验收条件**
- CLI 可初始化 workspace、查看状态、更新状态、导出上下文
- 可查看当前工作流、Loop/Goal 状态、运行日志、审批项、成本摘要
- 集成 memory/skills/artifacts 目录展示
- 命令输出适合人类阅读，也支持 `--json`

### 特性 3：LoopDesk 本地控制面

**目标**：让开发者能在本地 Web UI 中观察 Loop 与 Goal 运行情况。

**范围**
- in：gateway RPC、local Web UI 视图、静态资源
- out：多渠道推送、团队权限、复杂 dashboard

**验收条件**
- 可查看当前工作流、状态、运行日志、审批项、成本摘要
- RPC 返回结构与 CLI 状态保持一致
- 静态资源可通过 focused tests 校验

### 特性 4：跨工具适配与本地桥接

**目标**：至少打通一个本地编码工作流，并预留 ACP 能力。

**范围**
- 至少一个本地 coding workflow 可经 MCP/CLI bridge 联动，且前后端呈现为连续任务流
- out：云端同步、重型 vendor 私有协议、多渠道 bridge

**验收条件**
- 至少一个本地 coding workflow 可通过 MCP 与 LoopDesk 联动
- tool 输入/输出可正确写入 `LOOP-STATE.json`
- tool 输入/输出可正确写入 `LOOP-STATE.json` 的 run log / artifacts / goal context
- 本地 bridge 能手动触发外部工具并把结果回填，供后续 Loop/Goal 使用
### 特性 5：Memory、Skills 与 Loop 连续性
- in：durable memory、搜索、compaction、session resume、skills/meta-skills 查看与运行、个人模板查看与审计
- out：marketplace、云共享 skill、team knowledge base、team template management

**范围**
- in：durable memory、搜索、compaction、session resume、skills/meta-skills 查看与运行
- out：marketplace、云共享 skill、team knowledge base

**验收条件**
- 长会话可 compact，且关键知识可检索
- loop workspace 可 resume、export、abort
- skill 可查看、运行、审计

### 特性 6：Cost、Safety 与 Worktree 隔离收口

**目标**：让 loop/goal 自动化可控、可审计、可停止，并和 `loop-engineering` 的安全运营规则对齐，但限定在个人本地工作台。

**范围**
- in：token/cost tracking、budget cap、approval queue、escalation、worktree cleanup/retain、run log、denylist、human gate、kill switch
- out：复杂企业权限、多云计费、团队审批流、team notification、cloud-first governance

**验收条件**
- 预算、审批、错误、升级路径、run log 都可在本地观察到
- 超过预算/denylist/repeated failure 时可切 report-only 或暂停 loop
- 高风险操作可阻止或升级给人
- 自动运行后的 worktree 可清理或保留快照
- 每个 Goal 结束后保留最少必要运行记录，支持复盘和后续 Loop

### 特性 7：集成验证与发布收尾

**目标**：验证 v0.1 可发布的最小可用集合。

**范围**
- 适配器结果可被 Goal 作为上下文回填，也可被 Loop 作为 run log 使用
- out：团队功能、渠道落地页、营销素材

**验收条件**
- 所有 loop workspace 定向测试通过
- 至少一个 MCP 本地编码工作流跑通
- 文档覆盖安装、连接工具、运行 loop、检查状态、失败恢复

## 4. 成熟度与工具链映射

### 4.1 Loop/Goal 成熟度与本地化约束

LoopDesk 借鉴 `docs/research/loop-engineering.md:66` 的 L1/L2/L3 渐进增强，但不照搬其 GitHub/CI 默认假设：

- **L1 report-only**：Loop 扫描工作区状态、外部工具结果、pending items，分类为 act / propose / escalate，并写入 `LOOP-STATE.json`。此时不自动修改代码、不自动发 PR、不默认通知外部渠道。
- **L2 local execution**：在人工确认或预设 approval 下，通过 MCP/local CLI bridge 执行 bounded Goal；高风险步骤需 approval；自动 worktree isolation；结果经 checker 验证后回写 state。
- **L3 extended automation**：只在预算、权限、连续成功次数、stop condition 明确满足时才允许更长自动化链；默认随时可被 kill。

### 4.2 与 `loop-engineering` 工具链的对齐方式

| 参考工具/概念 | LoopDesk 采用方式 | 排除或延后 |
| --- | --- | --- |
| durable state + run log | 采用 `LOOP-STATE.json` + run log + override history | 不强制复制 `STATE.md` / `LOOP.md` 双文件体系 |
| skills / intent debt | 采用 personal workflow templates + skills / meta-skills 运行 | 不做 team marketplace |
| scaffold patterns | 采用个人开发工作流模板、triage 模板、budget/constraints 模板 | 不做 team repo-maintenance scaffold |
| cost / budget / human gate | 本地 cost observatory + budget cap + approval queue + kill switch | 不做云计费、团队审批流 |
| failure modes | 收敛本地工作台常见失败：ambiguous goal、verifier theater、legacy coupling、scope creep | 不覆盖复杂发布流水线事故 |

## 5. 详细 Goal 分解与 TDD 步骤


## 5.1 Goal 1：Loop workspace 状态模型与序列化

**文件**
- 新建：`src/loopdesk/loop_workspace/schema.py`
- 新建：`src/loopdesk/loop_workspace/serialization.py`
- 测试：`tests/test_loop_workspace/test_schema.py`

**Step 1：写最小失败测试**

```python
def test_default_loop_state_round_trip(tmp_path: Path) -> None:
    state = LoopWorkspaceState.create(
        workspace_root=tmp_path,
        intent="Implement loop handoff between Codex and Claude Code.",
        tags=["codex", "claude-code", "handoff"],
    )

    payload = state.to_dict()
    restored = LoopWorkspaceState.from_dict(payload)

    assert restored.schema_version == 1
    assert restored.workspace_root == tmp_path
    assert restored.status == LoopWorkspaceStatus.PLANNED
    assert restored.intent == state.intent
    assert restored.tags == state.tags
    assert restored.updated_at >= restored.created_at
```

运行：
```bash
pytest tests/test_loop_workspace/test_schema.py::test_default_loop_state_round_trip -v
```
预期：`ModuleNotFoundError`

**Step 2：最小实现**

- 定义 `LoopWorkspaceStatus`
- 定义 `LoopWorkspaceState`
- 提供 `create`、`to_dict`、`from_dict`、`record_override`

**Step 3：补状态变更测试**

```python
def test_status_change_records_override_history() -> None:
    state = LoopWorkspaceState.create(workspace_root=tmp_path, intent="Review PRD and draft plan.")
    previous = state.status
    state.status = LoopWorkspaceStatus.BLOCKED
    state.record_override(source="loop-engine", reason="Awaiting MCP adapter confirmation.", previous_status=previous)

    payload = state.to_dict()
    restored = LoopWorkspaceState.from_dict(payload)

    assert restored.status == LoopWorkspaceStatus.BLOCKED
    assert len(restored.override_history) == 1
    assert restored.override_history[0]["source"] == "loop-engine"
```

运行：
```bash
pytest tests/test_loop_workspace/test_schema.py -v
```
预期：通过

**Step 4：提交**

```bash
git add src/loopdesk/loop_workspace/schema.py src/loopdesk/loop_workspace/serialization.py tests/test_loop_workspace/test_schema.py
git commit -m "feat(loop_workspace): add portable loop state schema"
```

## 5.2 Goal 2：Loop workspace 目录布局与助手 API

**文件**
- 新建：`src/loopdesk/loop_workspace/layout.py`
- 新建：`src/loopdesk/loop_workspace/helpers.py`
- 测试：`tests/test_loop_workspace/test_layout.py`

**Step 1：写最小失败测试**

```python
def test_default_layout_creates_required_paths(tmp_path: Path) -> None:
    workspace = tmp_path / "loop"
    workspace.mkdir()

    layout = LoopWorkspaceLayout.ensure(workspace)

    assert layout.root == workspace
    assert layout.state_file.exists()
    assert layout.memory_dir.exists()
    assert layout.skills_dir.exists()
    assert layout.artifacts_dir.exists()
    assert layout.worktrees_dir.exists()
```

运行：
```bash
pytest tests/test_loop_workspace/test_layout.py::test_default_layout_creates_required_paths -v
```
预期：`ModuleNotFoundError`

**Step 2：最小实现**

- 定义 `LoopWorkspaceLayout`
- 提供 `ensure`，创建 `LOOP-STATE.json`、`memory`、`skills`、`artifacts`、`.loop-worktrees`

**Step 3：路径安全测试**

```python
def test_layout_rejects_paths_outside_workspace(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret", encoding="utf-8")

    with pytest.raises(ValueError):
        LoopWorkspaceLayout.ensure(outside)
```

运行：
```bash
pytest tests/test_loop_workspace/test_layout.py -v
```
预期：通过

**Step 4：提交**

```bash
git add src/loopdesk/loop_workspace/layout.py src/loopdesk/loop_workspace/helpers.py tests/test_loop_workspace/test_layout.py
git commit -m "feat(loop_workspace): add filesystem layout and helpers"
```

## 5.3 Goal 3：Git worktree 隔离助手

**文件**
- 新建：`src/loopdesk/loop_workspace/worktree.py`
- 测试：`tests/test_loop_workspace/test_worktree.py`

**Step 1：写最小失败测试**

```python
def test_create_loop_worktree_creates_branch_and_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    git_init(repo)
    layout = LoopWorkspaceLayout.ensure(tmp_path / "ws")

    worktree = create_loop_worktree(layout, loop_id="loop-1", repo_root=repo)

    assert worktree.path.exists()
    assert worktree.branch == "loopdesk/loop-1"
```

运行：
```bash
pytest tests/test_loop_workspace/test_worktree.py::test_create_loop_worktree_creates_branch_and_path -v
```
预期：`ModuleNotFoundError`

**Step 2：最小实现**

- 提供 `create_loop_worktree`
- 提供 `remove_loop_worktree`
- 提供 `list_loop_worktrees`
- 避免在非 git 仓库误用；保留现有工作区不被意外删除

**Step 3：清理测试**

```python
def test_remove_loop_worktree_cleans_branch_and_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    git_init(repo)
    layout = LoopWorkspaceLayout.ensure(tmp_path / "ws")
    worktree = create_loop_worktree(layout, loop_id="loop-1", repo_root=repo)

    remove_loop_worktree(worktree)

    assert not worktree.path.exists()
```

运行：
```bash
pytest tests/test_loop_workspace/test_worktree.py -v
```
预期：通过

**Step 4：提交**

```bash
git add src/loopdesk/loop_workspace/worktree.py tests/test_loop_workspace/test_worktree.py
git commit -m "feat(loop_workspace): add git worktree isolation helpers"
```

## 5.4 Goal 4：状态服务、持久化与导出

**文件**
- 新建：`src/loopdesk/loop_workspace/repository.py`
- 新建：`src/loopdesk/loop_workspace/service.py`
- 测试：`tests/test_loop_workspace/test_service.py`

**Step 1：写最小失败测试**

```python
def test_service_persists_and_exports_state(tmp_path: Path) -> None:
    layout = LoopWorkspaceLayout.ensure(tmp_path)
    service = LoopWorkspaceService(layout)

    state = await service.create_state(intent="Daily dependency review.", tags=["automation", "review"])
    await service.update_state(
        state.loop_id,
        status=LoopWorkspaceStatus.COMPLETED,
        last_tool="loop-engine",
        last_result="Reviewed 12 dependencies; 2 updates proposed.",
        lessons=[{"lesson": "Prefer patch-only automation for review loops."}],
    )

    payload = json.loads(layout.state_file.read_text(encoding="utf-8"))
    assert payload["status"] == "completed"
    assert payload["last_tool"] == "loop-engine"
    assert payload["lessons"][0]["lesson"] == "Prefer patch-only automation for review loops."
```

运行：
```bash
pytest tests/test_loop_workspace/test_service.py::test_service_persists_and_exports_state -v
```
预期：`ModuleNotFoundError`

**Step 2：最小实现**

- repository 负责读写 `LOOP-STATE.json`
- service 负责状态机、更新校验、导出上下文包

**Step 3：服务测试**

```bash
pytest tests/test_loop_workspace/test_service.py -v
```
预期：通过

**Step 4：提交**

```bash
git add src/loopdesk/loop_workspace/repository.py src/loopdesk/loop_workspace/service.py tests/test_loop_workspace/test_service.py
git commit -m "feat(loop_workspace): add state service, persistence, and context export"
```

## 5.5 Goal 5：Loop workspace CLI 命令

**文件**
- 新建：`src/loopdesk/cli/loop_workspace_cmd.py`
- 修改：`src/loopdesk/cli/main.py`
- 测试：`tests/test_cli/test_loop_workspace_cmd.py`

**Step 1：写最小失败测试**

```python
def test_loop_workspace_init_creates_state_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["loop", "init", "--intent", "Review PRD."])

    assert result.exit_code == 0
    assert (tmp_path / "LOOP-STATE.json").exists()
```

运行：
```bash
pytest tests/test_cli/test_loop_workspace_cmd.py::test_loop_workspace_init_creates_state_file -v
```
预期：`ModuleNotFoundError` 或 attribute error

**Step 2：最小实现**

- 注册 `loop` 子命令
- 支持 `init`、`show`、`update`、`resume`、`export`
- 默认 human-readable；高风险/批量信息支持 `--json`

**Step 3：CLI 测试**

```bash
pytest tests/test_cli/test_loop_workspace_cmd.py -v
```
预期：通过

**Step 4：提交**

```bash
git add src/loopdesk/cli/loop_workspace_cmd.py src/loopdesk/cli/main.py tests/test_cli/test_loop_workspace_cmd.py
git commit -m "feat(cli): add loop workspace init and show commands"
```

## 5.6 Goal 6：Gateway RPC 接口

**文件**
- 新建：`src/loopdesk/gateway/rpc_loop_workspace.py`
- 测试：`tests/test_gateway/test_rpc_loop_workspace.py`

**Step 1：写最小失败测试**

```python
def test_rpc_loop_workspace_create_and_get(tmp_path: Path) -> None:
    ...
```

运行：
```bash
pytest tests/test_gateway/test_rpc_loop_workspace.py::test_rpc_loop_workspace_create_and_get -v
```
预期：`ModuleNotFoundError`

**Step 2：最小实现**

- RPC methods：create/get/list/update/export/resume
- 返回结构与 CLI/state service 对齐

**Step 3：RPC 测试**

```bash
pytest tests/test_gateway/test_rpc_loop_workspace.py -v
```
预期：通过

**Step 4：提交**

```bash
git add src/loopdesk/gateway/rpc_loop_workspace.py tests/test_gateway/test_rpc_loop_workspace.py
git commit -m "feat(gateway): add loop workspace RPC methods"
```

## 5.7 Goal 7：本地 Web UI 视图

**文件**
- 新建：`src/loopdesk/gateway/static/js/views/loop_workspace.js`
- 新建：`src/loopdesk/gateway/static/css/views/loop_workspace.css`
- 修改：`src/loopdesk/gateway/control_ui.py`
- 测试：`tests/test_gateway/test_loop_workspace_view_static.py`

**Step 1：写最小失败测试**

- 校验 JS/CSS 路由存在、视图可访问、静态资源返回 200

**Step 2：最小实现**

- 展示 loop state 列表
- 展示单 loop 状态、run log、approval、cost
- 展示单 loop 状态、Goal 执行结果、run log、approval、cost，以及 workflow template 预览
**Step 3：静态测试**

```bash
pytest tests/test_gateway/test_loop_workspace_view_static.py -v
```
预期：通过

**Step 4：提交**

```bash
git add src/loopdesk/gateway/static/js/views/loop_workspace.js src/loopdesk/gateway/static/css/views/loop_workspace.css src/loopdesk/gateway/control_ui.py tests/test_gateway/test_loop_workspace_view_static.py
git commit -m "feat(ui): add loop workspace control view"
```

## 5.8 Goal 8：跨工具适配器与本地桥接

**文件**
- 新建：`src/loopdesk/loop_workspace/adapters.py`
- 新建：`src/loopdesk/loop_workspace/cli_bridge.py`
- 测试：`tests/test_loop_workspace/test_adapters.py`
- 测试：`tests/test_loop_workspace/test_cli_bridge.py`

**Step 1：写最小失败测试**

- adapter 能把 tool event 写入 `LOOP-STATE.json`
- CLI bridge 能把本地工具输出回填到 loop workspace

**Step 2：最小实现**

- MCP-first adapter interface
- ACP-second interface placeholder
- CLI bridge：codex / claude / trae / gemini 手工触发入口

**Step 3：适配测试**

```bash
pytest tests/test_loop_workspace/test_adapters.py tests/test_loop_workspace/test_cli_bridge.py -v
```
预期：通过

**Step 4：提交**

```bash
git add src/loopdesk/loop_workspace/adapters.py src/loopdesk/loop_workspace/cli_bridge.py tests/test_loop_workspace/test_adapters.py tests/test_loop_workspace/test_cli_bridge.py
git commit -m "feat(loop_workspace): add cross-tool adapter interface and CLI bridge"
```

## 5.9 Goal 9：开发者场景集成测试

**文件**
- 新建：`tests/test_loop_workspace_integration/test_developer_scenarios.py`

**Step 1：写最小失败测试**

- 场景 A：Codex -> Claude Code Goal 交接
- 场景 B：每日 dependency review Loop
- 场景 C：长会话 compact + memory flush
- 场景 D：通过个人开发 template 触发 Loop，并在收敛后生成 Goal

```bash
pytest tests/test_loop_workspace_integration/test_developer_scenarios.py -v
```
预期：通过

**Step 3：提交**

```bash
git add tests/test_loop_workspace_integration/test_developer_scenarios.py
git commit -m "test(loop_workspace): add cross-tool and automation scenario tests"
```

## 5.10 Goal 10：定向验证与文档收尾

**Step 1：定向验证**

```bash
pytest tests/test_loop_workspace tests/test_cli/test_loop_workspace_cmd.py tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_loop_workspace_view_static.py tests/test_loop_workspace_integration/test_developer_scenarios.py
```

```bash
pytest -m "not llm and not llm_smoke and not llm_costly and not llm_tools and not llm_embedding and not llm_reasoning"
```

预期：loop workspace 定向测试通过，现有非 live 测试不回归

**Step 2：文档 checklist**

- 在 `docs/features/core-feature-list.md` 增加 LoopDesk v0.1 CLI/RPC/UI 条目
- 在 `docs/architecture/personal-loop-workspace.md` 补充 loop workspace 边界说明
- 在 `docs/prd/personal-loop-workspace.md` 补充实际交付约束
- 在 `README.product.md` 确保首屏是 `LoopDesk`，不是 legacy multi-channel runtime 叙事

**Step 3：最终边界检查**

```bash
rg "loop workspace|LOOP-STATE|loopWorkspace|LoopDesk" docs src tests
```

预期：只出现预期 v0.1 公开面，不出现 channel-first、team-first、media-skill-first 的泄露

**Step 4：提交**

```bash
git add docs/features/core-feature-list.md docs/architecture/personal-loop-workspace.md docs/prd/personal-loop-workspace.md README.product.md
git commit -m "docs: align product docs with LoopDesk v0.1"
```

- `工作台`：统一展示当前任务/Goal、来源 Loop、run log、approval、cost、模板建议、下一步操作
- `运行中心`：Goal 运行历史、maker/checker 结果、escalation 记录、错误与重试、session 操作
- `模板`：个人开发 workflow 模板浏览、选用、运行与审计
- `上下文`：memory 搜索与查看、skills 查看与运行、artifacts 列表与下载、决策/约定
- `适配器`：MCP 连接、ACP 连接、本地工具桥接状态、工具事件日志
- `成本与安全`：成本总览、预算限制、审批队列、升级策略、kill switch
- `工作区`：loop workspace 列表、创建/恢复、worktree 创建/清理/保留、隔离快照
- `设置`：本地路径、权限模式、通知偏好、诊断与日志导出

审批后，后续 Task 7 的 UI 原型、静态资源和 RPC 结构都应保持该菜单边界。
## 7. 每个特性的 Loop Engineering 运行方式

每个特性按以下 loop 执行：

1. **Triage**
   - 确认该特性是否属于 v0.1 公开面
   - 检查是否触碰 legacy channels / broad skills / team features
   - 选最小可验证任务作为下一个 maker 输入

2. **Maker**
   - 按 Goal 1-10 的顺序，一次只做一个最小 Goal
   - 先写失败测试，再写最小实现
   - 保持 diff 最小，不顺手重构无关 legacy 代码

3. **Checker**
   - 运行该任务定向测试
   - 运行命名/边界 grep 检查
   - 检查是否把 legacy `session`、`workspace-state.json`、channel 术语泄露到公开面

4. **Escalation**
   - 若发现范围膨胀、命名混乱、legacy coupling，立刻停止编码
   - 更新 `docs/decisions/risk-handling-plan.md` 或 feature plan
   - 不经过评审不继续

5. **Run Log**
   - 记录当前 Goal、结果、遗留风险、下一步
   - 必要信息写入 docs plan 或 `LOOP-STATE.json`

6. **Stop Condition**
   - 该 Goal/特性的 acceptance criteria 全部满足
   - 定向测试通过
   - 风险门控仍然满足

## 8. 验证方案

### 8.1 测试策略

- **单元测试**：schema、layout、worktree、service、adapters
- **CLI 测试**：`loop init/show/update/resume/export` 行为
- **Gateway RPC 测试**：接口结构与状态一致性
- **静态资源测试**：Web UI JS/CSS/路由可用性
- **集成测试**：至少一个 MCP 本地编码工作流 + 一个自动化 loop 场景
- **回归测试**：非 live 的现有测试套件保持通过

### 8.2 定向测试命令

```bash
pytest tests/test_loop_workspace tests/test_cli/test_loop_workspace_cmd.py tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_loop_workspace_view_static.py tests/test_loop_workspace_integration/test_developer_scenarios.py
```

```bash
pytest -m "not llm and not llm_smoke and not llm_costly and not llm_tools and not llm_embedding and not llm_reasoning"
```

### 8.3 边界 grep 检查

```bash
rg "loop workspace|LOOP-STATE|loopWorkspace" docs src tests
```

预期结果：
- 仅出现 v0.1 预期公开面
- 不出现 channels-first onboarding
- 不出现 broad media skills 作为核心卖点
- 不出现 team collaboration 作为默认叙事

## 9. 里程碑与完成标准

### 9.1 M1：核心状态与隔离就绪

- Task 1-3 完成
- `LOOP-STATE.json` 可创建、恢复、导出
- worktree isolation 可创建/清理
- 定向测试通过

### 9.2 M2：可操作本地控制面

- Task 4-7 完成
- CLI、RPC、Web UI 可查看和操作 loop state
- 至少一个本地视图可展示 approvals/cost/logs
- 至少一个本地视图可展示 approvals/cost/logs/template 入口

### 9.3 M3：跨工具与记忆连续性

- Task 8-9 完成
- 至少一个本地编码 workflow 可经 MCP/CLI bridge 联动
- memory/loop workspace compaction/resume 可用
- 至少一个个人 workflow template 可从 Loop 选用并继承上下文到 Goal

- Task 10 完成
- 集成测试、文档 checklist、边界检查全部通过
- 无未解决的高优先级 scope/naming/legacy-coupling 风险

## 10. 风险管理与执行门控

执行前必须先满足：

1. **G1 范围确认**
   - `docs/decisions/risk-handling-plan.md` 已评审通过
   - legacy channels / broad media skills / team features 不进入 v0.1 公开面

2. **G2 命名基线**
   - 统一 `LoopDesk` / `loop_workspace` / `LOOP-STATE.json` / `loop` CLI 命名
   - 不在 v0.1 公开面混用 `session`、`workspace-state.json`、channel-first 文案

3. **G3 边界模块**
   - 新代码优先放在 `src/loopdesk/loop_workspace`
   - 复用 legacy runtime 时通过 adapter/facade，而不是直接把 legacy 包暴露出去

4. **G4 发布前检查**
   - 定向测试通过
   - 非 live 回归测试通过
   - 公开 docs/CLI/Web UI 口径一致

常见风险与即时处置：
- **范围膨胀**：停止编码，更新 docs 后再继续
- **命名漂移**：回到 `docs/decisions/risk-handling-plan.md:4.4` 的命名契约
- **legacy 污染**：新增 `loop_workspace` 不允许直接 import `loopdesk.channels`、`loopdesk.scheduler`、broad skills catalog
- **文档滞后**：任何实现变更都需同步 docs，不允许“先写完代码再补文档”

## 11. 交付清单

- 代码：
  - `src/loopdesk/loop_workspace/*`
  - `src/loopdesk/cli/loop_workspace_cmd.py`
  - `src/loopdesk/gateway/rpc_loop_workspace.py`
  - gateway static loop workspace 视图
- 测试：
  - `tests/test_loop_workspace/*`
  - `tests/test_cli/test_loop_workspace_cmd.py`
  - `tests/test_gateway/test_rpc_loop_workspace.py`
  - `tests/test_gateway/test_loop_workspace_view_static.py`
  - `tests/test_loop_workspace_integration/test_developer_scenarios.py`
- 文档：
  - 特性计划、风险方案、PRD、架构、CLI/Web UI 使用说明
  - README/product docs 统一成 `LoopDesk` 口径
  - 发布说明与失败恢复说明

## 12. 评审与批准

| 角色 | 名称 | 状态 |
| --- | --- | --- |
| Product | | 待评审 |
| Engineering | | 待评审 |
| QA/测试 | | 待评审 |

## 13. 执行交接

本计划完成后，建议采用以下两种方式之一继续：

1. **Subagent-Driven**：本会话按 Task 1-10 逐个分派执行，每 Task 结束后做代码和风险评审。
2. **Parallel Session**：开新会话，基于本计划和 `AGENTS.md` 执行；保持特性驱动、TDD、Loop Engineering 不变。
