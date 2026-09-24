# LoopDesk v2.0 第二阶段实施审计报告 · 第二轮（F6 ~ F10 复查）

> **审计日期**：2026-09-21（第二轮）
> **上一轮**：`docs/plans/2026-09-21-phase-2-implementation-audit.zh.md`（判定：报告不成立，全桩 + 零接线）
> **审计基准**：`docs/plans/2026-09-17-loopdesk-v2-phase-2-feature-breakdown.md`（28 个 Task）
> **本轮结论**：**有实质性进步，但「全部完成」仍不成立，且新引入 1 个「主动误导」级缺陷必须先修。**

---

## 0. 一句话结论

第一轮点名的两条最硬问题中，**「接线为零」已修复**（gateway 三组路由已注册），
**「PTY / REST 连接器是假实现」已修复**（真 `openpty`、真 HTTP 客户端）；
但 **F10.1 的五级 Gate 引擎虽已实现，却完全没接进产品路径——产品反而在伪造收据**，
且 **7 个模块行数与上轮逐一相同（零改动）**、**5 个 UI Task 仍为 0**。

---

## 1. 本轮相对上轮的真实改进（逐条已验）

| # | 上轮判定 | 本轮实测 | 物证 |
| --- | --- | --- | --- |
| 1 | ❌ F8.4「真实 PTY 托管」零实现 | ✅ **已修复** | `orchestration/pty_manager.py`（103 行）真用 `pty.openpty()` + `subprocess.Popen(preexec_fn=os.setsid)` + `select.select` 读 + `os.killpg` 终止；`is_alive()` 改为 `self._proc.poll() is None` |
| 2 | ❌ F9.1/F9.2「三连接器文件不存在」 | ✅ **已修复** | `JiraRestAdapter` / `PlaneRestAdapter` / `ConfluenceRestAdapter` 真实现：真实 REST 路径、urllib 请求、真实 payload |
| 3 | ❌ F10.1「ValidationReceipt 全仓库 0 命中」 | ⚠️ **引擎已实现，但未接线** | `governance/gates.py`（150 行）`FiveTierGateEngine.evaluate()` 五级真短路求值 + SHA-256 收据 |
| 4 | ❌ 零接线 | ✅ **gateway 已通** | `gateway/app.py:564-568` 注册 `orchestration` / `connectors` / `templates_assets` 三组路由 |
| 5 | ❌ 收据不落盘 | ✅ **已落盘** | `LoopWorkspaceService.record_gate_receipt()` 写入 `LOOP-STATE.json` 的 `gate_receipts`，并回写 `gate_status` / `receipt_digest` |
| 6 | ❌ 测试内自造被测对象 | ✅ **测试姿势已纠正** | `test_rest_clients.py` 用 `patch("urllib.request.urlopen")` 打在**边界**；`test_real_pty.py` 真写 `cat` 并读回显字节流 |

**本次相关测试集合：`63 passed / 0 failed`**（含 5 个新网关路由用例 / 2 个真实 PTY IO 用例 / 3 个 REST 客户端用例 / 6 个五级 Gate 用例 / 1 个收据落盘用例）。

复跑命令：

```bash
PYTHONPATH= TMPDIR=/tmp/loopdesk-verify env -u CODEBUDDY_BROKERED_FS_HOOK_ENABLED \
  .venv/bin/python -m pytest \
  tests/test_engine/test_template_engine.py tests/test_engine/test_flows.py \
  tests/test_engine/test_handoff_and_rewind.py tests/test_assets/ tests/test_orchestration/ \
  tests/test_connectors/ tests/test_governance/ tests/test_memory/ \
  tests/test_gateway/test_task_routes.py tests/test_gateway/test_template_and_asset_routes.py \
  tests/test_gateway/test_connector_routes.py tests/test_gateway/test_orchestration_routes.py -q
# → 63 passed, 129 warnings
```

---

## 2. ⛔ 必须先修：Gate 引擎是孤儿，产品路径在伪造收据

这是本轮**最严重**的问题，且比上轮的「不存在」更危险——它现在会**主动产出误导性的验证凭证**。

**证据一：引擎无任何生产调用方**

```bash
grep -rn -E "FiveTierGateEngine|gate_engine" --include='*.py' src/ tests/
# → 仅命中 src/loopdesk/governance/gates.py（定义）与 tests/test_governance/test_five_tier_gates.py（测试）
```

**证据二：`gateway/tasks.py:332` 手工伪造 `ValidationReceipt`**

```python
receipt = ValidationReceipt(
    task_id=task_id,
    project_id=project_id,
    timestamp=time.time(),
    validation_command=body.get("validation_command", "loopx operator-gate"),
    exit_code=0 if decision == "approved" else 1,
    stdout_hash=hashlib.sha256(comment.encode('utf-8')).hexdigest()[:16],
    sha256_digest=hashlib.sha256(f"{task_id}:{decision}:{comment}".encode('utf-8')).hexdigest(),
    operator_decision=decision,
    operator_comment=comment,
    passed_gates=body.get("passed_gates", ["health", "operator", "evidence", "focus", "quota"]),
)
```

四处硬伤：

| 字段 | 实际来源 | 问题 |
| --- | --- | --- |
| `passed_gates` | `body.get(...)`，**默认值 = 五个 gate 全通过** | **未跑任何 gate 即宣称五级全过**；且**可由客户端传入覆盖** |
| `exit_code` | `0 if approved else 1` | 来自人工裁决，不是任何验证命令的真实退出码 |
| `validation_command` | 默认字面量 `"loopx operator-gate"` | 合成值，非真实执行命令 |
| `stdout_hash` | `sha256(comment)[:16]` | 哈希的是**审批批注**，不是 stdout |

**证据三：落盘时通过与否只看人工裁决**

```python
# src/loopdesk/loop_workspace/service.py:470
t["gate_status"] = "passed" if decision == "approved" else "blocked"
```

**影响**：「可验证交付的 Agent 研发运行时」与「独立 Verifier + Validation Receipt」是产品的第一护城河。
现在 `LOOP-STATE.json` 里会出现**声称五级校验全通过、实际一级都没跑**的收据。
这不再是「功能缺失」，而是**审计证据污染**。

**修法（强制）**：
1. `gate_decision` 路由必须构造 `GateContext`，字段取自任务真实数据（`touched_files` 从真实 diff 取、
   `validation_command` / `validation_exit_code` / `validation_stdout` 取真实执行结果、`consumed_tokens` 取真实记账）。
2. 必须调用 `FiveTierGateEngine.evaluate(ctx)`；**`verdict.passed is False` 时不得签发收据**，响应返回失败 gate 与原因。
3. `passed_gates` **严禁**来自请求体，只能来自 `verdict.receipt.passed_gates`。
4. `gate_status` 只能由 `verdict.passed` 决定，不能由 `operator_decision` 决定。

---

## 3. 五个 UI Task 仍为 0

```bash
find frontend/src -newermt "2026-09-21" -type f      # 空
grep -rn -E "/api/v1/(templates|assets|connectors|orchestration)" frontend/src/   # 空
```

| Task | 要求 | 状态 |
| --- | --- | --- |
| F6.6 | 新建任务弹窗模板选择器 + Goal 时间线 | ❌ 未开工 |
| F7.5 | TeamAssets 接 `/api/v1/assets` + 下发联动 | ❌ 未开工 |
| F8.5 | SettingsAgent 接后端 + 状态 Rollup | ❌ 未开工 |
| F9.5 | SettingsMcp 接后端 + 「测试连接」 | ❌ 未开工 |
| F10.7 | ControlCenter 真实指标 + `/llms.txt` | ❌ 未开工 |

后端已经开好了 `/api/v1/templates`、`/api/v1/assets`、`/api/v1/orchestration/*`、`/api/v1/connectors/*`，
但**没有任何前端消费者**——后端能力目前对用户不可见。

---

## 4. 完全没有改动的模块（行数与上轮逐一相同 → 零编辑）

| 模块 | 行数（上轮） | 对应 Task | 结论 |
| --- | --- | --- | --- |
| `templates/engine.py` | 119（119） | F6.1 模板市场 / 磁盘加载 | 未修。`stop_conditions=["tests_pass == True", ...]`（:38）仍是**从未被求值的字面量**；模板仍硬编码在 `register_builtin_templates()`（:19） |
| `templates/flows.py` | 112（112） | F6.2 / F6.3 / F6.4 | 未修。issue-fix 仍是 `current_step_idx += 1` 步进计数器；8 段 PR 仍是写死占位文案；**无 Proposer/Executor/Evaluator 角色轮转状态机、无 Typed Turn 枚举** |
| `memory/three_tier.py` | 45（45） | F10.4 | 未修。`"\n".join([item["content"] ...])`（:26）仍冒充 Memory Dream；非 TEAM 层检索 `return []`（:45） |
| `memory/cross_context.py` | 53（53） | F10.5 | 未修。`@project/...` 仍只回填路径占位，不拉取已注册内容 |
| `memory/learning.py` | 38（38） | F10.6 | 未修。`KBHealth(score=95.0, stale_rules_count=0)`（:38）仍是硬编码常量 |
| `orchestration/parallel.py` | 23（23） | F8.3 | 未修。仍只有 `select_winner()`；**不创建 worktree、不并行执行** |
| `connectors/mcp_manager.py` | 69（69） | F9.3 | 未修。仍**无 `subprocess` / `Popen` / stdio 客户端**，不拉起任何 MCP 进程（熔断计数逻辑真实） |

即：**第一轮点名的「桩实现」清单里，只剩 PTY 与 REST 连接器两项被修；其余七项原样保留。**

---

## 5. 本轮新引入的三个问题

### 5.1 PTY 路由 = 默认无鉴权的任意命令执行
`gateway/orchestration.py`：`command = data.get("command", ["/bin/zsh"])` 直接传给 `PTYSessionManager.create_session()` → `Popen(..., preexec_fn=os.setsid)`。
而 `AuthConfig.mode` 的默认值是 **`"none"`**（`gateway/config.py:58`），此时 `AuthMiddleware` 直接放行。

```python
# src/loopdesk/gateway/config.py:58
mode: str = "none"  # none | token | password | trusted-proxy
```

后果：默认配置下，`POST /api/v1/orchestration/pty {"command": ["任意二进制"]}` 可执行任意命令。
与 GOV-08（deny-wins 工具策略）、GOV-09（五层安全语法）直接冲突。
**修法**：该路由强制鉴权（不受 `mode="none"` 影响）+ 命令白名单（只允许已注册 Agent runtime）。

### 5.2 连接器路由把密钥放 URL query
`GET /api/v1/connectors/tasks?...&token=<API_TOKEN>` —— `base_url` 与 `token` 都从 query 取。
密钥会进访问日志、浏览器历史、Referer。**修法**：改为请求头或加密配置读取。

### 5.3 `api_execute_template_step` 每次请求新建 flow 对象 → 状态不成立
`gateway/templates_assets.py` 内联执行 `IssueFixFlow(...)` 后立即丢弃对象，
`current_step_idx` 随对象消失 → 每次调用都返回 `step="triage"`。
所谓「9 步时序流转 / 状态断点保存」在 HTTP 层**不可用**（且 `flows.py` 未改，本也无持久化）。
**修法**：flow 状态须按 task_id 落到 `LOOP-STATE.json` 并与模板引擎对接。

---

## 6. 交付纪律（仍未改善）

| 项 | 状态 |
| --- | --- |
| git commit | ❌ 仍为 0，43+ 文件全部 untracked → **无法审计红-绿过程** |
| 本轮实施记录文档 | ❌ `docs/` 下无新增（仅上一轮我写的审计报告）→ 违反 AGENTS.md Golden Rule 2 |
| 资产下发目录契约 | ❌ 仍是 `.loopdesk/rules|skills|specs|mcp`（仓库中不存在的路径），与 AGENTS.md §4.2 不符 |
| 包导出 | ❌ `templates/` `assets/` `orchestration/` `connectors/` `governance/` 五个 `__init__.py` 仍均为 **0 字节** |
| CLI 入口 | ❌ 无（新能力只能通过 HTTP 触发，无 `loopdesk` 子命令） |

---

## 7. 测试面口径澄清（避免误判为回归）

- 若整目录跑 `tests/test_engine/`，会得到 **`501 failed, 455 passed, 9 errors`**。
- 经查根因是 venv **缺 `pytest_asyncio`**（`ModuleNotFoundError: No module named 'pytest_asyncio'`，
  且报 `PytestUnknownMarkWarning: Unknown pytest.mark.asyncio`）→ 异步用例体根本不执行。
- 抽查的失败用例（`test_engine/turn_runner/test_turn_finalizer_stage_unit.py`）对本次新模块**引用数为 0**。
- **结论：这批失败是 pre-existing 环境性问题，与本次改动无关，不计入本次回归。**

---

## 8. 完成度重估（对比上轮）

| 维度 | 上轮 | 本轮 |
| --- | --- | --- |
| 后端真实逻辑度 | ~20% | **~45%** |
| 接线度（gateway / 前端 / CLI / 持久化） | 0% | **~35%**（gateway 已通；前端 0；CLI 0；持久化仅 `gate_receipts`） |
| UI Task | 0 / 5 | **0 / 5** |
| 28 个 Task 中可判「真实完成」 | ~0 | **约 6 个**（F8.4、F9.1、F9.2 部分、F10.1 引擎本体、F10.3 部分、收据落盘） |
| 新增缺陷 | — | **3 个**（PTY 无白名单、密钥入 query、模板 step 无状态） |

---

## 9. 处置建议（按优先级）

| 优先级 | 动作 |
| --- | --- |
| **P0** | 把 `FiveTierGateEngine` 接进 `gate_decision` 路由；`passed_gates` 禁止来自请求体；`gate_status` 由 `verdict.passed` 决定；**引擎未通过则拒绝签发收据**。修完前 `ValidationReceipt` 不具备审计可信度。 |
| **P0** | PTY 路由加命令白名单 + 强制鉴权（不受 `auth.mode="none"` 影响）。 |
| **P1** | 连接器路由的 `token` 改走请求头 / 加密配置，禁止 URL query。 |
| **P1** | `templates/flows.py` + `memory/*` + `parallel.py` + `mcp_manager.py` 七个模块的桩实现重做（含 `stop_conditions` 真实求值、模板市场、角色轮转状态机、Memory Dream 真提炼、worktree 扇出、MCP 进程托管）。 |
| **P1** | 模板 step 状态持久化到 `LOOP-STATE.json`。 |
| **P2** | 补 F6.6 / F7.5 / F8.5 / F9.5 / F10.7 五个 UI Task（后端路由已就绪，可直接接）。 |
| **P2** | 落 commit；补本轮实施记录文档；统一资产下发的目录契约（`.loopdesk/` vs `.agents/`）；补包导出与 CLI 入口。 |
| **流程** | 验收报告必须附 ① 可复现测试命令与输出 ② **调用链证据**（gateway 路由 / 前端 fetch / CLI）③ **持久化前后 diff** ④ commit hash。本轮已具备 ①③，缺 ②（前端）与 ④。 |
