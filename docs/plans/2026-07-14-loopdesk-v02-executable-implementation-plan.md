# LoopDesk v0.2 — Channel Adapter 可执行实施计划

> Status: ready to execute
> Owner: Engineering
> Inputs:
> - `docs/decisions/v0.2-channel-adapter.md:1`
> - `docs/plans/2026-07-14-loopdesk-v02-fdd-tdd-execution-plan.md:1`
> - `docs/features/loopdesk-v0.2-channel-adapter-feature-breakdown.md:1`
> - `docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md:1`

## 1. 执行原则

- 只按本计划推进 v0.2 channel adapter，不扩展团队协作、个人微信、云同步、rich-media 主路径。
- 每个 task 都按 `Triage -> Maker -> Checker -> Escalation -> Run log -> Stop condition` 执行。
- 每个 task 先补最小 failing test，再补最小实现，再做定向验证。
- 若出现 scope、边界、命名风险，先更新 `docs/decisions/v0.2-channel-adapter.md:1`，再继续实现。
- 若 `python -m pytest <task file>` 再次挂起，记录环境阻塞后继续用最小可执行验证推进，不要把环境问题误判为功能失败。

## 2. 当前基线状态

| Task | 状态 | 说明 |
| --- | --- | --- |
| F1.1 | 已完成 | 核心契约、disabled 跳过、unknown command rejection、denied write、admin/viewer scope 已落地；对应测试已通过。 |
| F1.2 | 待确认 | 已有 scope parametrize 与 viewer-blocked write 测试；需确认是否已补 viewer `/current` allow `/new` deny 测试。 |
| F2.1 | 有缺口 | Feishu 测试仍包含与现有实现不一致的断言，需同步到最小可验证行为。 |
| F2.2 | 有缺口 | Slack 测试存在导入缺失与 parse_event 行为假设不一致。 |
| F2.3 | 待补齐 | DingTalk 测试骨架存在，但覆盖较弱。 |
| F2.4 | 待补齐 | WeCom 测试骨架存在，但未覆盖 review-gate config validation。 |
| F2.5 | 有缺口 | RPC/static 测试存在路径与断言问题。 |
| F3.1 | 已完成 | 通知 formatter 已落地，通知测试已通过。 |
| F3.2 | 待补齐 | 测试为行为示例，不是 gateway hardening 的真实落地。 |
| F4.1 | 待补齐 | 文档边界已大致存在，但需逐项对照实现闭门。 |
| F4.2 | 待补齐 | acceptance checklist 已存在，但缺少 sign-off gate。 |

### 2.1 当前定向验证结果

- `python -m pytest tests/test_gateway/test_channel_adapter_core.py -q --maxfail=5`：11 passed
- `python -m pytest tests/test_gateway/test_channel_feishu.py -q --maxfail=5`：2 failed, 3 passed
  - `test_feishu_command_surface_maps_to_compact_workspace_commands`
  - `test_disabled_feishu_entry_does_not_start_transport`
- `python -m pytest tests/test_gateway/test_channel_slack.py -q --maxfail=5`：4 failed
  - `test_slack_command_surface_maps_to_compact_workspace_commands`
  - `test_slack_read_command_preserves_thread_reply_target`
  - `test_slack_approval_flow_uses_existing_approval_records`
  - `test_disabled_slack_entry_does_not_start_transport`
- `python -m pytest tests/test_gateway/test_rpc_loop_workspace_channels.py -q --maxfail=5`：2 failed
  - `test_channels_status_includes_disabled_loop_workspace_status`
  - `test_loop_workspace_channel_route_exposes_workspace_state`
- `python -m pytest tests/test_gateway/test_loop_workspace_channels_static.py -q --maxfail=5`：1 failed
  - `test_loop_workspace_view_registers_channel_status_action`

### 2.2 失败根因速查

| 文件 | 问题 |
| --- | --- |
| `tests/test_gateway/test_channel_feishu.py:50` | 断言要求 `/current` 等完整命令都出现在 registry surface 中；当前实现表面包含其他命令，需改成最小子集/影子命令验证。 |
| `tests/test_gateway/test_channel_feishu.py:97` | helper 不接受 kwargs；需改成可覆盖 enabled/connection_mode 的 helper。 |
| `tests/test_gateway/test_channel_slack.py:48` | 缺少 `DEFAULT_REGISTRY` / `Surface` import。 |
| `tests/test_gateway/test_channel_slack.py:73` | 现有实现将 read command 解析为 `IncomingMessage`；测试却断言为 `None` 或 `OutgoingMessage`。 |
| `tests/test_gateway/test_rpc_loop_workspace_channels.py:42` | macOS `/tmp` 解析为 `/private/tmp`，硬编码根路径断言失败。 |
| `tests/test_gateway/test_loop_workspace_channels_static.py:26` | CSS 里没有 `channel` 文本；静态检查目标需改成真实 UI 信道状态文本。 |

## 3. Feature F1: Shared Channel Foundation

Stop condition: 禁用默认配置、command parser、allowlist、审计日志、unknown command rejection 都有 failing test -> 最小实现 -> 通过测试。

### Task F1.1: Wire the shared channel contract and disabled-by-default config model

- Files:
  - `src/loopdesk/channels/contract.py:1`
  - `src/loopdesk/channels/manager.py:1`
  - `src/loopdesk/channels/registry.py:1`
  - `src/loopdesk/channels/command_registry.py:1`
  - `tests/test_gateway/test_channel_adapter_core.py:1`

Step 1: 确认最小 failing test 已覆盖 disabled skip、unknown reject、denied write、admin/viewer scope。
Step 2: 运行定向测试确认 baseline：

```bash
python -m pytest tests/test_gateway/test_channel_adapter_core.py -x
```

Step 3: 只修被 failing test 要求的最小实现；不顺手重构 legacy 叙事。
Step 4: 运行定向测试确认通过。
Step 5: 记录 run log：

```text
Run log: F1.1 completed at <datetime>; tests/test_gateway/test_channel_adapter_core.py passed; risk note: ...
```

Escalation gate: 若需新增非 v0.2 安全模型，先更新 `docs/decisions/v0.2-channel-adapter.md:1`。

### Task F1.2: Lock scope table and command allowlist

- Files:
  - `src/loopdesk/gateway/scopes.py:1`
  - `src/loopdesk/channels/command_registry.py:1`
  - `tests/test_gateway/test_channel_adapter_core.py:1`

Step 1: 确认测试覆盖：
- `channels.status` -> `operator.read`
- `loop_workspace.get` -> `operator.read`
- 写类方法 -> `operator.write`
- viewer sender 调用 `/current` 能过，调用 `/new` 被拒
Step 2: 运行定向测试确认 baseline：

```bash
python -m pytest tests/test_gateway/test_channel_adapter_core.py -x
```

Step 3: 只补最小 scope table 和 channel command allowlist。
Step 4: 运行定向测试确认通过。
Step 5: 记录 run log：

```text
Run log: F1.2 completed at <datetime>; tests/test_gateway/test_channel_adapter_core.py passed; risk note: ...
```

Escalation gate: 若允许命令集与现有 `DEFAULT_REGISTRY` 冲突，先更新决策稿再改代码。

## 4. Feature F2: Approved Platform Adapters

Stop condition: Feishu/Lark、Slack、DingTalk、WeCom 都能通过各自 focused test file；禁用任一平台不影响本地 loop workspace。

### Task F2.1: Add Feishu/Lark adapter surface

- Files:
  - `src/loopdesk/channels/feishu.py:1`
  - `tests/test_gateway/test_channel_feishu.py:1`

Step 1: 把测试对齐到当前最小可验证行为：
- 验证 websocket 是 preferred transport
- 验证 read command 会保留 thread target metadata，且返回 `IncomingMessage`
- 验证 `/approve` approval-id 被标准化为 workspace command
- 验证 helper 支持 `enabled=False` 且 disabled entry 不会启动 transport
Step 2: 运行定向测试确认 baseline：

```bash
python -m pytest tests/test_gateway/test_channel_feishu.py -x
```

Expected: FAIL, 且失败点集中在 Feishu transport/command/disabled 行为。
Step 3: 只补 Feishu 最小骨架缺失；优先 websocket + thread target + approval 路径，不引入复杂卡片。
Step 4: 运行定向测试确认通过。
Step 5: 记录 run log：

```text
Run log: F2.1 completed at <datetime>; tests/test_gateway/test_channel_feishu.py passed; risk note: ...
```

Escalation gate: 若需要额外 public channel 语义，先更新 `docs/decisions/v0.2-channel-adapter.md:1`。

### Task F2.2: Add Slack Socket Mode adapter surface

- Files:
  - `src/loopdesk/channels/slack.py:1`
  - `tests/test_gateway/test_channel_slack.py:1`

Step 1: 补最小 failing test：
- socket mode 是 preferred default transport
- read command 保留 thread reply target
- `/reject` approval-id 调用能进入 approval flow
- disabled entry does not start transport
Step 2: 运行定向测试确认 baseline：

```bash
python -m pytest tests/test_gateway/test_channel_slack.py -x
```

Expected: FAIL
Step 3: 只补 Slack 最小 Socket Mode / thread reply / approval 路径；不要引入复杂 card。
Step 4: 运行定向测试确认通过。
Step 5: 记录 run log：

```text
Run log: F2.2 completed at <datetime>; tests/test_gateway/test_channel_slack.py passed; risk note: ...
```

Escalation gate: 若需要超出骨架的 mention/thread 语义，先更新 `docs/decisions/v0.2-channel-adapter.md:1`。

### Task F2.3: Add DingTalk adapter surface

- Files:
  - `src/loopdesk/channels/dingtalk.py:1`
  - `tests/test_gateway/test_channel_dingtalk.py:1`

Step 1: 补最小 failing test：
- stream transport 是默认 adapter surface
- `/approve`、`/reject` 可用
- unsupported rich format fallback 到 plain text
- disabled entry does not start transport
Step 2: 运行定向测试确认 baseline：

```bash
python -m pytest tests/test_gateway/test_channel_dingtalk.py -x
```

Expected: FAIL
Step 3: 只补 DingTalk stream + plain text fallback + minimal approval 路径。
Step 4: 运行定向测试确认通过。
Step 5: 记录 run log：

```text
Run log: F2.3 completed at <datetime>; tests/test_gateway/test_channel_dingtalk.py passed; risk note: ...
```

Escalation gate: 若需要复杂卡片或 OA 消息，先更新 `docs/decisions/v0.2-channel-adapter.md:1`。

### Task F2.4: Add WeCom adapter with public-URL review gate

- Files:
  - `src/loopdesk/channels/wecom.py:1`
  - `tests/test_gateway/test_channel_wecom.py:1`

Step 1: 补最小 failing test：
- public webhook 在 `public_webhook_reviewed=False` 时不可启用
- approved review gate 在显式开启后才可启用
- 命令表映射到 compact workspace commands
- compact error template 可读且长度受控
Step 2: 运行定向测试确认 baseline：

```bash
python -m pytest tests/test_gateway/test_channel_wecom.py -x
```

Expected: FAIL
Step 3: 只补 WeCom review-gate validation 和 minimal command surface；不引入 personal WeChat 语义。
Step 4: 运行定向测试确认通过。
Step 5: 记录 run log：

```text
Run log: F2.4 completed at <datetime>; tests/test_gateway/test_channel_wecom.py passed; risk note: ...
```

Escalation gate: 若需要公开回调暴露策略，先更新 `docs/decisions/v0.2-channel-adapter.md:1`。

### Task F2.5: Add channel gateway plumbing and local Web UI status scaffold

- Files:
  - `src/loopdesk/gateway/rpc_loop_workspace.py:1`
  - `src/loopdesk/gateway/rpc_channels.py:1`
  - `src/loopdesk/gateway/control_ui.py:1`
  - `src/loopdesk/gateway/static/js/views/loop_workspace.js:1`
  - `src/loopdesk/gateway/static/css/views/loop_workspace.css:1`
  - `src/loopdesk/gateway/templates/index.html:1`
  - `tests/test_gateway/test_rpc_loop_workspace_channels.py:1`
  - `tests/test_gateway/test_loop_workspace_channels_static.py:1`

Step 1: 修正测试为最小可执行验证：
- RPC status 使用 `tmp_path` 创建本地 workspace root，避免 macOS `/tmp` 路径差异
- Web UI 静态检查改成真实 channel status 文本/样式标记，而不是任意 `channel` 子串
Step 2: 运行定向测试确认 baseline：

```bash
python -m pytest tests/test_gateway/test_rpc_loop_workspace_channels.py tests/test_gateway/test_loop_workspace_channels_static.py -x
```

Expected: FAIL
Step 3: 只补最小 channel status RPC 和 local Web UI scaffold；不把 IM 写成主入口。
Step 4: 运行定向测试确认通过。
Step 5: 记录 run log：

```text
Run log: F2.5 completed at <datetime>; test files passed; risk note: ...
```

Escalation gate: 若需要额外 public URL 暴露，先更新 `docs/decisions/v0.2-channel-adapter.md:1`。

## 5. Feature F3: Hardening and Operator Controls

Stop condition: rate limiting、cost alert、compact error template、disable without data loss 都有 failing test -> 最小实现 -> 通过测试。

### Task F3.1: Add channel notification formatter behavior

- Files:
  - `src/loopdesk/channels/types.py:1`
  - `tests/test_gateway/test_channel_notifications.py:1`

Step 1: 确认通知行为测试已覆盖 status、approval、cost alert、error、run summary 五类最小输出。
Step 2: 运行定向测试确认 baseline：

```bash
python -m pytest tests/test_gateway/test_channel_notifications.py -x
```

Step 3: 只补通知 formatter 和 compact output 能力；不引入复杂卡片。
Step 4: 运行定向测试确认通过。
Step 5: 记录 run log：

```text
Run log: F3.1 completed at <datetime>; tests/test_gateway/test_channel_notifications.py passed; risk note: ...
```

### Task F3.2: Add hardening primitives for channel commands

- Files:
  - `src/loopdesk/channels/command_registry.py:1`
  - `src/loopdesk/channels/manager.py:1`
  - `tests/test_gateway/test_channel_adapter_hardening.py:1`

Step 1: 把测试从假 service 改成真实最小 gateway hardening 验证：
- 重复错误命令被 throttle 并记录
- budget-cap exceeded 在 enabled channel 中生成 compact cost alert
- `/cancel` 立即返回状态，不阻塞 IM session
- disabled adapter 不会删除或修改 `LOOP-STATE.json`、memory、skills、artifacts、worktrees
Step 2: 运行定向测试确认 baseline：

```bash
python -m pytest tests/test_gateway/test_channel_adapter_hardening.py -x
```

Expected: FAIL
Step 3: 只补 hardening 最小原语；不新增团队审批队列或云同步。
Step 4: 运行定向测试确认通过。
Step 5: 记录 run log：

```text
Run log: F3.2 completed at <datetime>; tests/test_gateway/test_channel_adapter_hardening.py passed; risk note: ...
```

Escalation gate: 若 hardening 需要新 RPC 方法，先更新 `docs/decisions/v0.2-channel-adapter.md:1`。

## 6. Feature F4: Local Inspection and Documentation

Stop condition: docs、release notes、acceptance checklist、boundary lock 都指向同一 v0.2 边界；没有公开叙事泄露 legacy channels-first 或 team-first 概念。

### Task F4.1: Finalize v0.2 docs and boundary lock

- Files:
  - `docs/decisions/product-strategy.md:1`
  - `docs/prd/personal-loop-workspace.md:1`
  - `docs/releases/loopdesk-v0.2.md:1`
  - `docs/README.md:1`
  - `docs/project/loopdesk-project-initialization.md:1`
  - `AGENTS.md:1`

Step 1: 制造最小 doc gate，确认当前状态仍为 incomplete。
Step 2: 验证 doc gate 开放：

```bash
python -c "from pathlib import Path; text=Path('docs/releases/loopdesk-v0.2.md').read_text(); print('open' if 'Status: draft' in text else 'closed')"
```

Expected: `open`
Step 3: 只更新以下边界文档：
- IM 是 optional remote control/notification surface
- v0.2 只覆盖 DingTalk、Feishu/Lark、Slack、WeCom
- 禁用 channel 不会删除本地 loop workspace 数据
- 公开文档不会把 channels 写成主入口
- 更新 project initialization 和 `AGENTS.md` 中的 v0.2 status/plan 引用
Step 4: 验证 doc gate 关闭：

```bash
python -c "from pathlib import Path; text=Path('docs/releases/loopdesk-v0.2.md').read_text(); print('open' if 'Status: draft' in text else 'closed')"
```

Expected: `closed`
Step 5: 记录 run log：

```text
Run log: F4.1 completed at 2026-07-15T09:35+08:00; doc gate closed; added local channel inspection panel docs and boundary-lock references; risk note: none
```

### Task F4.2: Complete acceptance checklist and release gate

- Files:
  - `docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md:1`

Step 1: 制造最小 acceptance gate。
Step 2: 验证 acceptance gate 开放：

```bash
python -c "from pathlib import Path; text=Path('docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md').read_text(); print('open' if 'Approved by Product:' in text and 'Approved by Engineering:' in text and 'Approved by QA:' in text else 'closed')"
```

Expected: `closed`
Step 3: 只补充：
- 每项 checklist 对应的测试命令
- disable rollback evidence 要求
- sign-off 栏位
Step 4: 验证 acceptance gate 关闭：

```bash
python -c "from pathlib import Path; text=Path('docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md').read_text(); print('open' if 'Approved by Product:' in text and 'Approved by Engineering:' in text and 'Approved by QA:' in text else 'closed')"
```

Expected: `open`
Step 5: 记录 run log：

```text
Run log: F4.2 completed at 2026-07-15T09:35+08:00; acceptance gate open; local channel inspection surface and rollback evidence fields added; risk note: none
```

## 7. Release Gate and Completion Criteria

完成本实施计划时，必须同时满足：

- `F1` -> `F2` -> `F3` -> `F4` 按 task-by-task 通过。
- focused gate 通过：

```bash
python -m pytest tests/test_gateway/test_channel_adapter_core.py \
  tests/test_gateway/test_channel_notifications.py \
  tests/test_gateway/test_channel_feishu.py \
  tests/test_gateway/test_channel_slack.py \
  tests/test_gateway/test_channel_dingtalk.py \
  tests/test_gateway/test_channel_wecom.py \
  tests/test_gateway/test_channel_adapter_hardening.py \
  tests/test_gateway/test_rpc_loop_workspace_channels.py \
  tests/test_gateway/test_loop_workspace_channels_static.py -x
```

- 所有 channel 默认禁用；本地 loop workspace 在 disable 状态下行为不变。
- `docs/README.md`、`docs/releases/loopdesk-v0.2.md`、`AGENTS.md` 都不再泄露 IM-first / team-first / personal-WeChat 叙事。
- 每项 task 的 run log 已记录在本计划中。

## 8. Rollback Criteria

若任意 task 出现以下情况，立即停止并回滚该 task：

- 某个 platform adapter 开始依赖未批准的 IM 能力。
- 本地 `LOOP-STATE.json`、memory、skills、artifacts、worktrees 被 channel 代码直接改写。
- focused test 无法在 3 次尝试内恢复 green。
- 公开 docs/README 开始把 channels 放在 loop workspace 前面。

回滚方法：

```bash
git checkout -- <affected files>
python -m pytest tests/test_gateway/<last green focused test file>.py -x
```

## 9. 推荐的直接执行顺序

```text
F1.2 -> F2.1 -> F2.2 -> F2.3 -> F2.4 -> F2.5 -> F3.2 -> F4.1 -> F4.2 -> focused gate
```

每个 task 只改当前需要的文件，避免跨 task 并行冲突。
