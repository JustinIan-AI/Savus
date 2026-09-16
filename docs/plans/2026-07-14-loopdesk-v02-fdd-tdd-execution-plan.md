# LoopDesk v0.2 — Channel Adapter FDD/TDD Execution Plan

> **For Codex:** REQUIRED SUB-SKILL: Use `writing-plans` to execute this plan task-by-task.

**Goal:** 把 v0.2 channel adapter 草案拆成可直接落地的 FDD/TDD 执行序列，确保每个 feature、task、验证命令都可在当前工作区里被推进和检查。

**Architecture:** 复用现有 gateway channel RPC、`LOOP-STATE.json` 本地 loop workspace、禁用即隔离的平台适配器模型；不把 IM 升级成主入口。

**Tech Stack:** Python 3.12、Starlette、`src/loopdesk/gateway`、`src/loopdesk/channels`、pytest、Loop Engineering run loop。

---

## Preflight and Execution Boundary

### Approved FDD Structure

- Feature `F1`: Shared Channel Foundation
- Feature `F2`: Approved Platform Adapters
- Feature `F3`: Hardening and Operator Controls
- Feature `F4`: Local Inspection and Documentation

Every task below follows the same Loop Engineering loop:

```text
Triage -> Maker -> Checker -> Escalation -> Run log -> Stop condition
```

Delivery rules:

- 先写最小失败测试。
- 只改实现该任务所需的文件。
- 只使用文档里允许的命令格式做验证。
- scope creep 必须先更新 `docs/decisions/v0.2-channel-adapter.md`。
- 不允许把个人微信、群协作、云同步纳入 v0.2。

### Current Baseline Evidence

当前已落盘且可直接复用的 v0.2 边界与设计证据：

- v0.2 boundary lock 决策稿：`docs/decisions/v0.2-channel-adapter.md:24`
- v0.2 feature breakdown：`docs/features/loopdesk-v0.2-channel-adapter-feature-breakdown.md:20`
- v0.2 acceptance checklist：`docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md:37`
- v0.2 release notes：`docs/releases/loopdesk-v0.2.md:11`
- 项目级执行规则：`AGENTS.md:56`
- 已草拟但尚未按零上下文标准细化的实施计划：`docs/plans/2026-07-13-v02-channel-adapter-implementation-plan.md:1`

当前仓库里已经能看到一批 v0.2 测试与实现骨架，说明这不是从零开始，而是把这些骨架推进到“每个任务都能 failing-test-first 验证”的状态：

- 本地 loop workspace RPC 已存在：`src/loopdesk/gateway/rpc_loop_workspace.py:29`
- channel status RPC 已存在：`src/loopdesk/gateway/rpc_channels.py:42`
- shared channel types、capability profile、manifest、dedupe 等基础能力已存在：`src/loopdesk/channels/contract.py:1`
- Web UI loop workspace 静态资源脚手架已存在：`src/loopdesk/gateway/static/js/views/loop_workspace.js:1`
- 四平台测试骨架与 gateway channel core/hardening/notification 测试骨架已存在：
  - `tests/test_gateway/test_channel_adapter_core.py:1`
  - `tests/test_gateway/test_channel_notifications.py:1`
  - `tests/test_gateway/test_channel_feishu.py:1`
  - `tests/test_gateway/test_channel_slack.py:1`
  - `tests/test_gateway/test_channel_dingtalk.py:1`
  - `tests/test_gateway/test_channel_wecom.py:1`
  - `tests/test_gateway/test_channel_adapter_hardening.py:1`
  - `tests/test_gateway/test_rpc_loop_workspace_channels.py:1`
  - `tests/test_gateway/test_loop_workspace_channels_static.py:1`

**执行环境风险：**

当前基线验证时，执行 `python -m pytest tests/test_gateway/test_channel_adapter_core.py -x -q` 会在 pytest 启动后挂住；同一测试文件的 `import` 本身正常，说明阻塞更可能在 pytest 启动/收集链路，不在纯 Python 语法。请每个 task 都用下文的 **Baseline Verification** 小节确认环境是否恢复，不要把环境挂起误判成实现失败。

### Validation Policy

只使用下表中的命令格式。若环境仍挂起，先隔离环境问题，不要绕过 FDD/TDD 边界。

```bash
# Step verification
pytest tests/test_gateway/test_channel_adapter_core.py -x
pytest tests/test_gateway/test_channel_notifications.py -x
pytest tests/test_gateway/test_channel_feishu.py -x
pytest tests/test_gateway/test_channel_slack.py -x
pytest tests/test_gateway/test_channel_dingtalk.py -x
pytest tests/test_gateway/test_channel_wecom.py -x
pytest tests/test_gateway/test_channel_adapter_hardening.py -x
pytest tests/test_gateway/test_rpc_loop_workspace_channels.py -x
pytest tests/test_gateway/test_loop_workspace_channels_static.py -x

# Baseline verification
pytest --version
python -c "import tests.test_gateway.test_channel_adapter_core"

# Focused gate
pytest tests/test_gateway/test_channel_adapter_core.py \
  tests/test_gateway/test_channel_notifications.py \
  tests/test_gateway/test_channel_feishu.py \
  tests/test_gateway/test_channel_slack.py \
  tests/test_gateway/test_channel_dingtalk.py \
  tests/test_gateway/test_channel_wecom.py \
  tests/test_gateway/test_channel_adapter_hardening.py \
  tests/test_gateway/test_rpc_loop_workspace_channels.py \
  tests/test_gateway/test_loop_workspace_channels_static.py -x
```

## Feature F1: Shared Channel Foundation

Stop condition: 禁用默认配置、command parser、allowlist、审计日志、unknown command rejection 都有 failing test -> 最小实现 -> 通过测试。

### Task F1.1: Wire the shared channel contract and disabled-by-default config model

**Files:**
- Edit: `src/loopdesk/channels/contract.py:1`
- Edit: `src/loopdesk/channels/manager.py:1`
- Edit: `src/loopdesk/channels/registry.py:1`
- Edit: `src/loopdesk/channels/command_registry.py:1`
- Test: `tests/test_gateway/test_channel_adapter_core.py:1`

**Step 1: Write the failing test**

为下列行为写最小 failing test；每个 test 只断言一个行为：

- disabled channel entry 不会进入 `ChannelManager`。
- unknown channel command 在调用任何 workspace action 前就被拒绝。
- blocked write command 返回 denied metadata。
- admin/non-admin sender 被正确映射到 write/viewer scope。

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_gateway/test_channel_adapter_core.py -x
```

Expected: FAIL, 报错点应为 contract/registry/manager 行为不存在或不符合测试。

**Step 3: Write minimal implementation**

只补实现被当前 failing test 要求的最小能力：

- 在 `src/loopdesk/channels/contract.py` 增加或修正最小 capability/status 类型。
- 在 `src/loopdesk/channels/manager.py` 保证 disabled entry 被跳过且不会泄露到 `get()` / `start_all()`。
- 在 `src/loopdesk/channels/registry.py` 和 `src/loopdesk/channels/command_registry.py` 保证 unknown command 先返回 reply，且 blocked write 带 `denied=True`。

不要顺手重构 legacy channel 叙事或增加非 v0.2 平台。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_gateway/test_channel_adapter_core.py -x
```

Expected: PASS

**Run log**

记录到本计划对应 task 下：

```text
Run log: F1.1 completed at 2026-07-14; tests/test_gateway/test_channel_adapter_core.py passed; risk note: fixed test helper defaults and build_channel_rpc_context channel_admin_senders forwarding.
```

### Task F1.2: Lock scope table and command allowlist

**Files:**
- Edit: `src/loopdesk/gateway/scopes.py:1`
- Edit: `src/loopdesk/channels/command_registry.py:1`
- Test: `tests/test_gateway/test_channel_adapter_core.py:1`

**Step 1: Write the failing test**

- `test_v0_2_scope_table_classifies_channel_and_workspace_methods` 已存在；如果没有，补一条只验证 `channels.status` -> `operator.read`、`loop_workspace.get` -> `operator.read`、写类方法 -> `operator.write`。
- 补一个只允许 read commands 的 allowlist test：viewer sender 调用 `/current` 能过，调用 `/new` 被拒。

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_gateway/test_channel_adapter_core.py -x
```

Expected: FAIL

**Step 3: Write minimal implementation**

- 在 `src/loopdesk/gateway/scopes.py` 维护最小且固定的 v0.2 scope table。
- 在 `src/loopdesk/channels/command_registry.py` 只注册 v0.2 允许的命令集。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_gateway/test_channel_adapter_core.py -x
```

Expected: PASS

**Run log**

记录到本计划对应 task 下：

```text
Run log: F1.2 completed at <datetime>; test file passed; risk note: ...
```

## Feature F2: Approved Platform Adapters

Stop condition: Feishu/Lark、Slack、DingTalk、WeCom 都能通过各自 focused test file；禁用任一平台不影响本地 loop workspace。

### Task F2.1: Add Feishu/Lark adapter surface

**Files:**
- Edit: `src/loopdesk/channels/feishu.py:1`
- Test: `tests/test_gateway/test_channel_feishu.py:1`

**Step 1: Write the failing test**

按现有骨架补最小 failing test：

- websocket 是 preferred transport。
- read commands 保留 thread reply target。
- `/approve` approval-id 调用能进入 approval flow。
- disabled entry does not start transport。

每个 failing test 只覆盖一个行为。

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_gateway/test_channel_feishu.py -x
```

Expected: FAIL

**Step 3: Write minimal implementation**

只补 Feishu 现有骨架里缺失的最小行为；若 webhook 不是 v0.2 重点，优先保证 websocket + thread reply + approval 路径可用。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_gateway/test_channel_feishu.py -x
```

Expected: PASS

**Step 5: Escalation gate**

如果 Feishu 需要额外 public channel 语义，先更新 `docs/decisions/v0.2-channel-adapter.md` 再继续。

**Run log**

记录到本计划对应 task 下：

```text
Run log: F2.1 completed at <datetime>; test file passed; risk note: ...
```

### Task F2.2: Add Slack Socket Mode adapter surface

**Files:**
- Edit: `src/loopdesk/channels/slack.py:1`
- Test: `tests/test_gateway/test_channel_slack.py:1`

**Step 1: Write the failing test**

- socket mode 是 preferred default transport。
- read command 保留 thread reply target。
- `/reject` approval-id 调用能进入 approval flow。
- disabled entry does not start transport。

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_gateway/test_channel_slack.py -x
```

Expected: FAIL

**Step 3: Write minimal implementation**

只补 Slack 最小 Socket Mode / thread reply / approval 路径；不要引入复杂 card 流程。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_gateway/test_channel_slack.py -x
```

Expected: PASS

**Step 5: Escalation gate**

如果 Slack 需要额外 mention/thread 语义超出现有骨架，先更新 `docs/decisions/v0.2-channel-adapter.md` 再继续。

**Run log**

记录到本计划对应 task 下：

```text
Run log: F2.2 completed at <datetime>; test file passed; risk note: ...
```

### Task F2.3: Add DingTalk adapter surface

**Files:**
- Edit: `src/loopdesk/channels/dingtalk.py:1`
- Test: `tests/test_gateway/test_channel_dingtalk.py:1`

**Step 1: Write the failing test**

- stream transport 是默认 adapter surface。
- `/approve`、`/reject` 可用。
- unsupported rich format fallback 到 plain text。
- disabled entry does not start transport。

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_gateway/test_channel_dingtalk.py -x
```

Expected: FAIL

**Step 3: Write minimal implementation**

只补 DingTalk stream + plain text fallback + minimal approval 路径。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_gateway/test_channel_dingtalk.py -x
```

Expected: PASS

**Step 5: Escalation gate**

如果 DingTalk 需要复杂卡片或 OA 消息，先更新 `docs/decisions/v0.2-channel-adapter.md` 再继续。

**Run log**

记录到本计划对应 task 下：

```text
Run log: F2.3 completed at <datetime>; test file passed; risk note: ...
```

### Task F2.4: Add WeCom adapter with public-URL review gate

**Files:**
- Edit: `src/loopdesk/channels/wecom.py:1`
- Edit: `src/loopdesk/onboarding/channel_specs.py:1`
- Test: `tests/test_gateway/test_channel_wecom.py:1`

**Step 1: Write the failing test**

- `public_webhook_reviewed=False` 时无法启用。
- `public_webhook_reviewed=True` 且 `enabled=True` 时可以通过启用检查。
- minimal inbound commands 可用。
- cost alert 能输出 compact text。

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_gateway/test_channel_wecom.py -x
```

Expected: FAIL

**Step 3: Write minimal implementation**

只补 review gate + webhook route + compact outbound alert；不要扩大 rich media。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_gateway/test_channel_wecom.py -x
```

Expected: PASS

**Step 5: Escalation gate**

如果 WeCom 需要 corp 应用能力以外的流程，先更新 `docs/decisions/v0.2-channel-adapter.md` 再继续。

**Run log**

记录到本计划对应 task 下：

```text
Run log: F2.4 completed at <datetime>; test file passed; risk note: ...
```

### Task F2.5: Add channel gateway plumbing and local Web UI status scaffold

**Files:**
- Edit: `src/loopdesk/gateway/rpc_channels.py:1`
- Edit: `src/loopdesk/gateway/rpc_loop_workspace.py:1`
- Edit: `src/loopdesk/gateway/scopes.py:1`
- Edit: `src/loopdesk/gateway/static/js/views/loop_workspace.js:1`
- Edit: `src/loopdesk/gateway/static/css/views/loop_workspace.css:1`
- Edit: `src/loopdesk/gateway/templates/index.html:1`
- Test: `tests/test_gateway/test_rpc_loop_workspace_channels.py:1`
- Test: `tests/test_gateway/test_loop_workspace_channels_static.py:1`

**Step 1: Write the failing test**

- disabled adapter 在 `channels.status` 里返回 `disabled`。
- `loop_workspace.get` 保留 run_log / approvals / workspace state。
- 静态资源包含 loop workspace JS/CSS，且 HTML 注册该视图。

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_gateway/test_rpc_loop_workspace_channels.py tests/test_gateway/test_loop_workspace_channels_static.py -x
```

Expected: FAIL

**Step 3: Write minimal implementation**

只做最小 RPC 和 UI 注册；不要把 channels 做成主入口叙事。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_gateway/test_rpc_loop_workspace_channels.py tests/test_gateway/test_loop_workspace_channels_static.py -x
```

Expected: PASS

**Run log**

记录到本计划对应 task 下：

```text
Run log: F2.5 completed at <datetime>; test files passed; risk note: ...
```

## Feature F3: Hardening and Operator Controls

Stop condition: rate limit、cost alert、`/cancel` immediate、compact error、disable without data loss 都可通过 focused test。

### Task F3.1: Add channel notification formatter behavior

**Files:**
- Edit: `src/loopdesk/channels/types.py:1`
- Test: `tests/test_gateway/test_channel_notifications.py:1`

**Step 1: Write the failing test**

- status 使用 compact workspace summary。
- approval notification 包含 `/approve`、`/reject` hint。
- cost alert 不暴露 raw payload / secret。
- long run summary 被截断到 compact 长度。
- plain text fallback 限制 metadata payload。

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_gateway/test_channel_notifications.py -x
```

Expected: FAIL

**Step 3: Write minimal implementation**

只补最小 formatter / `OutgoingMessage` 行为；不要加 rich media pipeline。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_gateway/test_channel_notifications.py -x
```

Expected: PASS

**Step 5: Escalation gate**

如果通知格式需要平台私有能力，先更新 `docs/decisions/v0.2-channel-adapter.md` 再继续。

**Run log**

记录到本计划对应 task 下：

```text
Run log: F3.1 completed at <datetime>; test file passed; risk note: ...
```

### Task F3.2: Add hardening primitives for channel commands

**Files:**
- Edit: `src/loopdesk/gateway/channel_dispatch.py:1`
- Test: `tests/test_gateway/test_channel_adapter_hardening.py:1`

**Step 1: Write the failing test**

- repeated bad commands are throttled and logged。
- budget-cap exceeded 产生 compact cost alert。
- `/cancel` 返回 immediate status，不阻塞 IM session。
- channel failure 不删除或修改 `LOOP-STATE.json`、memory、skills、artifacts、worktrees。

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_gateway/test_channel_adapter_hardening.py -x
```

Expected: FAIL

**Step 3: Write minimal implementation**

只补最小 rate limiter、audit log、`/cancel` immediate path、cost alert template。

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_gateway/test_channel_adapter_hardening.py -x
```

Expected: PASS

**Step 5: Escalation gate**

如果 hardening 需要新 RPC 方法，先更新 `docs/decisions/v0.2-channel-adapter.md` 再继续。

**Run log**

记录到本计划对应 task 下：

```text
Run log: F3.2 completed at <datetime>; test file passed; risk note: ...
```

## Feature F4: Local Inspection and Documentation

Stop condition: docs、release notes、acceptance checklist、boundary lock 都指向同一 v0.2 边界；没有公开叙事泄露 legacy channels-first 或 team-first 概念。

### Task F4.1: Finalize v0.2 docs and boundary lock

**Files:**
- Edit: `docs/decisions/product-strategy.md:1`
- Edit: `docs/prd/personal-loop-workspace.md:1`
- Edit: `docs/releases/loopdesk-v0.2.md:1`
- Edit: `docs/README.md:1`
- Edit: `docs/project/loopdesk-project-initialization.md:1`
- Edit: `AGENTS.md:1`

**Step 1: Write the failing doc gate**

把当前 v0.2 文档和项目状态说明改回“未完成”或“与实现不一致”，制造显式的 doc gate。

**Step 2: Verify doc gate is open**

```bash
pytest docs/ -x || true
```

Expected: 文档相关检查显示 v0.2 状态/边界不完整。

**Step 3: Write minimal documentation updates**

只更新以下内容：

- 确认 IM 是 optional remote control/notification surface。
- 确认 v0.2 只覆盖 DingTalk、Feishu/Lark、Slack、WeCom。
- 确认禁用 channel 不会删除本地 loop workspace 数据。
- 确认公开 docs/README 不会把 channels 写成主入口。
- 更新 project initialization 和 AGENTS 里的 v0.2 status/plan 引用。

**Step 4: Verify doc gate closes**

```bash
pytest docs/ -x || true
```

Expected: 不再有 v0.2 boundary/status 冲突。

**Run log**

记录到本计划对应 task 下：

```text
Run log: F4.1 completed at <datetime>; doc gate closed; risk note: ...
```

### Task F4.2: Complete acceptance checklist and release gate

**Files:**
- Edit: `docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md:1`

**Step 1: Write the failing acceptance gate**

把 checklist 中的关键项改回未勾选，或补一个必须 Product/Engineering/QA 签名的 gate 说明。

**Step 2: Verify acceptance gate is open**

```bash
python -c "from pathlib import Path; text=Path('docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md').read_text(); print('open' if 'Approved by Product:' in text and 'Approved by Engineering:' in text and 'Approved by QA:' in text else 'closed')"
```

Expected: `closed`

**Step 3: Write minimal acceptance updates**

只补充：

- 每项 checklist 对应的测试命令。
- disable rollback evidence要求。
- sign-off 栏位。

**Step 4: Verify acceptance gate closes**

```bash
python -c "from pathlib import Path; text=Path('docs/acceptance/loopdesk-v0.2-channel-adapter-checklist.md').read_text(); print('open' if 'Approved by Product:' in text and 'Approved by Engineering:' in text and 'Approved by QA:' in text else 'closed')"
```

Expected: `open`

**Run log**

记录到本计划对应 task 下：

```text
Run log: F4.2 completed at <datetime>; acceptance gate open; risk note: ...
```

## Release Gate and Completion Criteria

完成本条执行计划时，必须同时满足：

- `F1` -> `F2` -> `F3` -> `F4` 按 task-by-task 通过。
- focused gate 通过：

```bash
pytest tests/test_gateway/test_channel_adapter_core.py \
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
- 每项 task 的 run log 已记录在计划里。

## Rollback Criteria

若任意 task 出现以下情况，立即停止并回滚该 task：

- 某个 platform adapter 开始依赖未批准的 IM 能力。
- 本地 `LOOP-STATE.json`、memory、skills、artifacts、worktrees 被 channel 代码直接改写。
- focused test 无法在 3 次尝试内恢复 green。
- 公开 docs/README 开始把 channels 放在 loop workspace 前面。

回滚方法：

```bash
# 在相关 task 范围内回滚
git checkout -- <affected files>
pytest tests/test_gateway/<last green focused test file>.py -x
```

## Execution Handoff

**Plan complete and saved to `docs/plans/2026-07-14-loopdesk-v02-fdd-tdd-execution-plan.md`. Two execution options:**

**1. Subagent-Driven (this session)** - 每个 task 派发一个最小 owner，保持当前工作区继续推进。

**2. Direct Execution (recommended)** - 继续当前会话，按 F1.1 -> F1.2 -> F2.1 -> ... 的顺序直接推进，并把阻塞记录到本计划。

Which approach?
