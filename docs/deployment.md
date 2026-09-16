# LoopDesk v0.1 发布、打包与部署说明

> 状态：draft for review
> 版本：v0.1
> 日期：2026-07-08
> 负责人：Product / Engineering / QA
> 依据：`docs/prd/personal-loop-workspace.md`、`docs/releases/loopdesk-v0.1.md`、`docs/acceptance/loopdesk-v0.1-acceptance-checklist.md`、`docs/plans/2026-07-07-loopdesk-implementation-plan.md`

## 1. 发布边界

LoopDesk v0.1 的发布口径是 **本地优先的个人开发工作台**，不是 OpenSquilla 全量运行时。

- 公开发布面：`LoopDesk` / `loop_workspace` / `LOOP-STATE.json`
- 核心交付：本地 workspace 状态、memory、skills、artifacts、worktree、MCP-first 集成、CLI、本地 Web UI
- 明确不在 v0.1 发布面：团队协作、云房间、channel-first 叙事、重型 GUI、broad media/skill marketplace
- 包名仍使用 `loopdesk`，但产品文档、README、release notes、CLI 帮助以 `LoopDesk` 口径呈现

## 2. 前置要求

| 要求 | 推荐版本/说明 |
| --- | --- |
| Python | 3.12+ |
| 包管理 | `uv`（推荐）或 `pip` |
| Git | 仅 source install 需要 |
| Git LFS | 仅 source install / 开发构建需要 |
| 操作系统 | macOS / Linux / Windows（PowerShell 安装路径可参考 `install.ps1`） |
| 网络 | 发布安装需要访问 GitHub release；本地部署可离线 |

## 3. 打包方式

### 3.1 本地 wheel 构建

```bash
python -m build
```

输出文件通常位于：

```bash
dist/loopdesk-*.whl
```

### 3.2 推荐 extras

| extras | 适用场景 |
| --- | --- |
| `mcp` | MCP stdio server / MCP bridge |
| `memory` | memory / search / compaction 依赖 |
| `recommended` | 默认本地体验 |
| `dev` | 本地开发与测试 |

示例：

```bash
pip install "dist/loopdesk-*.whl[mcp,memory]"
```

### 3.3 发布命名建议

- 发布包名保持 `loopdesk-<version>-py3-none-any.whl`
- 产品 README / release notes 明确写成 **LoopDesk v0.1**
- 避免在 v0.1 发布口径中使用 `LoopDesk` 作为主产品名

## 4. 安装方式

### 4.1 推荐终端安装（release wheel）

```bash
uv tool install --python 3.12 "loopdesk[recommended,mcp] @ https://github.com/loopdesk/loopdesk/releases/download/v0.3.1/loopdesk-0.3.1-py3-none-any.whl"
```

安装后若命令未生效：

```bash
uv tool update-shell
```

### 4.2 pip 安装

```bash
pip install --upgrade "loopdesk[recommended,mcp] @ dist/loopdesk-*.whl"
```

### 4.3 源码安装

```bash
git lfs install
git clone https://github.com/loopdesk/loopdesk.git
cd loopdesk
git lfs pull --include="src/loopdesk/squilla_router/models/**"
bash scripts/install_source.sh
```

### 4.4 开发环境安装

```bash
uv sync --extra recommended --extra dev --extra mcp
uv run loopdesk --help
```

## 5. 验证命令

### 5.1 定向功能 gate

```bash
pytest tests/test_loop_workspace tests/test_cli/test_loop_workspace_cmd.py tests/test_gateway/test_rpc_loop_workspace.py tests/test_gateway/test_loop_workspace_view_static.py tests/test_loop_workspace_integration/test_developer_scenarios.py
```

预期结果：
- `31 passed`
- `2 deselected`
- `0 failed`

说明：`tests/test_loop_workspace/test_mcp_stdio.py` 当前在 pytest/FastMCP stdio harness 下存在 hang 风险，已由 `tests/test_loop_workspace/test_mcp_stdio_process.py` 覆盖，发布前需明确处理策略。

### 5.2 核心 CLI 验证

```bash
uv run loopdesk loop --help
```

应能看到 workspace 子命令：`init`、`show`、`list`、`update`、`resume`、`export`

### 5.3 工作区初始化验证

```bash
uv run loopdesk loop init /tmp/loopdesk-demo --json
```

预期输出包含：
- `status`
- `project_name`
- `current_work_id`
- `state_file`

### 5.4 本地 gateway 验证

```bash
uv run loopdesk gateway run
```

预期：
- 默认地址：`http://127.0.0.1:18791/control/`
- 若本机已有旧服务占用 `18791`，可改用 `18792` 做人工验证；示例：
  - `uv run loopdesk gateway run --port 18792`
  - 访问 `http://127.0.0.1:18792/control/`
- 本地 Web UI 可访问
- loop workspace 静态视图可访问

### 5.5 MCP stdio 验证

```bash
LOOPDESK_WORKSPACE=/tmp/loopdesk-manual-demo uv run python -m loopdesk.loop_workspace.mcp
```

实际验证结果
- 可用工具：`loopdesk.list_templates`、`loopdesk.read_template`、`loopdesk.get_context_pack`、`loopdesk.run_local_command`
- 额外验证：用 `work_id=work-1` 调用 `loopdesk.run_local_command` 可收到参数校验错误，说明 tool contract 正常；业务输入已按工作项绑定。
- 时间：2026-07-08

可用工具：
- `loopdesk.get_context_pack`
- `loopdesk.list_templates`
- `loopdesk.read_template`
- `loopdesk.run_local_command`

## 6. 部署方式

### 6.1 本地单开发者部署（推荐）

```bash
# 1. 安装
uv tool install --python 3.12 "loopdesk[recommended,mcp] @ <wheel or release url>"

# 2. 初始化工作区
uv run loopdesk loop init /path/to/project/workspace --selected-template backend-engineer

# 3. 启动 gateway
uv run loopdesk gateway run

# 4. 打开本地控制面
# http://127.0.0.1:18791/control/
```

### 6.2 后台 gateway 部署

```bash
uv run loopdesk gateway start --json
uv run loopdesk gateway status
```

停止：

```bash
uv run loopdesk gateway stop
```

### 6.3 端口与主机配置

```bash
uv run loopdesk gateway run --listen 127.0.0.1 --port 18791
```

公网暴露需显式 opt-in：

```bash
uv run loopdesk gateway run --listen 0.0.0.0 --port 18791
```

安全要求：
- 仅本地 loopback 为默认安全边界
- 公网暴露需配合额外鉴权与网络边界

### 6.4 工作区导入/导出

```bash
uv run loopdesk loop export /path/to/project/workspace --output /path/to/export.json
```

可用于：
- 迁移
- 备份
-  handed off 给其他本地工具

## 7. 环境变量

| 变量 | 说明 |
| --- | --- |
| `LOOPDESK_WORKSPACE` | MCP stdio server 的工作区根目录 |
| `LOOPDESK_GATEWAY_CONFIG_PATH` | gateway 配置文件路径 |
| `OPENROUTER_API_KEY` / provider 环境变量 | provider 接入 |
| `UV_TOOL_LOOPDESK` | uv tool 安装时的项目目录 |
| `LOOPDESK_INSTALL_PROFILE` | 安装 profile：`core` / `recommended` |

## 8. 发布检查清单

- [ ] release wheel 构建完成
- [ ] 定向 gate 通过：`31 passed, 2 deselected`
- [ ] `docs/releases/loopdesk-v0.1.md` 已更新
- [ ] `docs/acceptance/loopdesk-v0.1-acceptance-checklist.md` 已逐项打勾
- [ ] `docs/acceptance/loopdesk-v0.1-signoff-report.md` 已生成
- [ ] README / product docs 口径已切到 `LoopDesk`
- [ ] 已知 issue：legacy stdio test hang 已记录并进入跟踪
- [ ] 发布说明包含 boundary / limitation / next steps

## 9. 回滚与恢复

- 工作区数据本地化，可直接回滚到上一份 `LOOP-STATE.json` 备份
- gateway 配置变更失败时，优先使用：
  ```bash
  uv run loopdesk gateway restart
  uv run loopdesk doctor
  ```
- 工作区损坏时，优先：
  ```bash
  uv run loopdesk loop show /path/to/workspace
  uv run loopdesk loop export /path/to/workspace --output /tmp/backup.json
  ```

## 10. 已知限制与发布注意事项

- v0.1 以 MCP-first 为主，ACP 仍为第二路径
- 团队/云同步/marketplace 不在 v0.1 发布面
- legacy `tests/test_loop_workspace/test_mcp_stdio.py` 需作为已知 harness 跟踪项处理
- 建议首次发布只面向个人开发者本地使用场景

## 11. 下一步

- Product / Engineering / QA 完成签核
- 发布冻结前统一 README / docs 口径
- 发布后收集模板、cross-tool handoff、cost observability 反馈，用于 v0.2
