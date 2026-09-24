# LoopDesk v2.0 Phase 2（F6~F10）第三轮完成度审计

- 审计时间：2026-09-21 17:00–17:20
- 审计对象：`docs/plans/2026-09-21-phase-2-remediation-report.zh.md`（整改方自述）对 `docs/plans/2026-09-21-phase-2-implementation-audit-round2.zh.md` 的修复情况
- 对照基线：`docs/plans/2026-09-17-loopdesk-v2-phase-2-feature-breakdown.md`（28 个 Task）
- 方法：源码逐行 + 可复现测试 + **真实 HTTP 实证探针** + 独立进程复验

---

## 0. 结论速览

| 维度 | 第一轮 | 第二轮 | **第三轮** |
| --- | --- | --- | --- |
| 后端真实逻辑度 | ~20% | ~45% | **~62%** |
| 接线度（gateway / 前端 / CLI） | 0% | ~35% | **~45%** |
| UI Task（F6.6 / F7.5 / F8.5 / F9.5 / F10.7） | 0/5 | 0/5 | **0/5** |
| 28 个 Task 可判真完成 | ~0 | ~6 | **~10** |
| git commit | 无 | 无 | **仍无**（HEAD 停在 F5） |

**本轮定性**：有真实进步，且**第一次出现「代码本身是真的」**——`git worktree`、`subprocess.Popen`、AST 条件求值器都是真实现。但出现两个新的系统性问题：**① 真实现被搁置为孤儿（写了不用）；② 报告用"类名虚构 + 计数器虚增 + 把 import 说成接线"的方式，把 62% 描述成 100%。**

---

## 1. 已真修（逐条实证）

| # | 项 | 物证 |
| --- | --- | --- |
| 1 | **Gate 引擎接入裁决链** | `gateway/tasks.py:19` 真 import、`:329` `FiveTierGateEngine()` 真实例化；`verdict.passed == False` → 返回 **422 GATE_REJECTED** 且不落收据；`passed_gates` 不再取自请求体；`record_gate_receipt()` 真写入 `LOOP-STATE.json` 的 `gate_receipts` |
| 2 | **连接器凭据移出 URL query** | 实测带 `?token=` 的请求返回 **400 `INSECURE_QUERY_TOKEN`**；改走 `Authorization: Bearer` / `X-Connector-Token` |
| 3 | **PTY 真实现 + 创建需鉴权** | 无凭证 `POST /orchestration/pty` → **403**；`pty.openpty()` + `Popen(preexec_fn=os.setsid)` 真实存在 |
| 4 | **PTY 白名单部分有效** | `["/usr/bin/curl", ...]` → **403 COMMAND_NOT_ALLOWED** |
| 5 | **模板流程同进程内真推进** | 实测四次 `POST /templates/step`：`step_idx` **0→1→2→3**，当前步 triage→maker→checker→gate，`is_ready_for_review` 在第 3 步转 `True`。第二轮「永远死在 triage」已修 |
| 6 | **stop_conditions 求值器真实现** | `templates/engine.py:8` `SafeConditionEvaluator`，AST 白名单算子（Eq/NotEq/Lt/LtE/Gt/GtE），非 `eval()` |
| 7 | **`AssetRegistry.discover()` 真扫盘** | 扫 `rules/` `specs/`，解析 YAML frontmatter 覆盖 id/name/roles；且经 `api_list_assets` 路由可达 |
| 8 | 三个模块**代码层真实现** | `parallel.py` 真调 `git worktree add -b` / `worktree remove --force`；`mcp_manager.py` 真 `subprocess.Popen(..., stdin=PIPE, stdout=PIPE, stderr=PIPE)` + `poll()`/`terminate()`/`kill()` + 熔断；`three_tier.py` Memory Dream 做关键词提炼（修掉 `"\n".join` 原样拼接）；`learning.py:46` `get_kb_health()` 删掉硬编码 `95.0` |
| 9 | 本轮相关测试 | **70 passed / 0 failed** |

复跑命令：

```bash
PYTHONPATH= TMPDIR=/tmp/loopdesk-verify env -u CODEBUDDY_BROKERED_FS_HOOK_ENABLED \
  .venv/bin/python -m pytest \
  tests/test_engine/test_template_engine.py tests/test_engine/test_flows.py \
  tests/test_engine/test_handoff_and_rewind.py tests/test_assets/ tests/test_orchestration/ \
  tests/test_connectors/ tests/test_governance/ tests/test_memory/ \
  tests/test_gateway/test_task_routes.py tests/test_gateway/test_template_and_asset_routes.py \
  tests/test_gateway/test_connector_routes.py tests/test_gateway/test_orchestration_routes.py \
  tests/test_p1_features.py -q
# => 70 passed
```

---

## 2. ⛔ 未修：收据仍在"无验证即签发"（**这是本轮最重要发现**）

第二轮的问题是「硬编码 `passed_gates`」；本轮的问题**换了个位置但性质相同**——改为「请求体默认值自动满足五级」。

### 2.1 实证（真实 HTTP 请求，非模拟）

```http
POST /api/v1/tasks/PROBE-1/gate/decision
{"decision": "approved", "comment": "looks good", "root": "<tmp>"}
```

**响应：`HTTP 200`，签发收据。** `LOOP-STATE.json` 实际落盘内容：

```json
{
  "task_id": "PROBE-1",
  "validation_command": "pytest tests/ -q",        // 从未执行
  "exit_code": 0,                                   // 取自默认值 '0 if decision == approved else 1'
  "stdout_hash": "2cff4fad...9f75b2",               // = sha256("ALL TESTS PASSED") 凭空捏造的字面量
  "passed_gates": ["health","operator","evidence","focus","quota"],   // 五级全过
  "sha256_digest": "9ee34b53..."
}
```

**请求方没有提供任何执行证据，也没有任何测试被执行，收据却宣称五级校验全通过并持久化。**

### 2.2 根因：五级中至少四级在生产路径恒真

| Gate | 生产路径实际行为 |
| --- | --- |
| **Health** | `tasks.py:329` `FiveTierGateEngine()` 不传 `force_health_unhealthy` ⇒ 恒 `None` ⇒ **恒过**。无任何真实健康探针 |
| **Operator** | 唯一真正起作用的门（`decision != approved` 则拒） |
| **Evidence** | `validation_exit_code=body.get("validation_exit_code", 0 if approved else 1)`、`validation_stdout=body.get("validation_stdout", "ALL TESTS PASSED")` ⇒ **默认即通过**；`validation_command` 有默认值故非空检查也过。**引擎从不执行该命令** |
| **Focus** | `allowed_write_scopes` 默认 `[]` ⇒ `for f in touched_files` 循环空转 ⇒ **恒过** |
| **Quota** | `consumed_tokens=0`、`token_limit=1000000` 默认 ⇒ **恒过**。未接任何真实 token 计量 |

⇒ 有效门只有 1 级（Operator），却签发 5 级全过的凭证。**第二轮定的 P0 只修了"字段来源"，没修"证据真实性"。**

### 2.3 报告对应表述的核对

> "只有在五级 Gate 真实通过时，才签发 `ValidationReceipt`"

"真实通过"在本实现中等价于"客户端未显式传反例 + 用了默认值"。**该表述构成误导。**

---

## 3. ⛔ 本轮新引入：PTY 鉴权后门 + 白名单可绕

`gateway/orchestration.py` 新增的加固存在三处洞（均已实测）：

| # | 缺陷 | 实测证据 |
| --- | --- | --- |
| 1 | **硬编码鉴权旁路发布进生产代码**：`orchestration.py:35` `if request.headers.get("X-LoopDesk-Test-Auth") == "test-authorized": return True` | 仅带该头、**不带任何真实密钥** → `POST /orchestration/pty` **HTTP 200 创建成功** |
| 2 | **白名单只校验 `cmd_list[0]`，而名单含解释器** ⇒ 任意代码执行 | `["python3","-c","print('ARBITRARY-CODE-EXEC-OK')"]` → 200，读回显得到 `ARBITRARY-CODE-EXEC-OK` |
| 3 | **`write` / `read` / `terminate` 三端点完全无鉴权** | 无凭证 `POST /orchestration/pty/p2/write` → **200**；`DELETE /orchestration/pty/p2` → **200 terminated** |

补充：默认 key 兜底为公开字面量 `os.environ.get("LOOPDESK_ADMIN_KEY", "loopdesk-admin-secret")`；全局 `AuthConfig.mode` 默认 `"none"`（`config.py:58`），故其余新路由（templates / assets / connectors / gate decision）默认全部开放。

与 GOV-08/GOV-09「deny-wins / 五层安全」正面冲突。

> 报告称"无鉴权直接返回 **401** Unauthorized"——实测为 **403**，且第 3 项根本未鉴权。

---

## 4. ⛔ 前端接线是「import 摆设」，UI Task 仍 0/5

`frontend/src/lib/api.ts` 新增 8 个真实客户端函数（`createPTYSession` / `readPTYSession` / `writePTYSession` / `fetchConnectorTasks` / `fetchConnectorDoc` / `listMarketplaceAssets` / `distributeAsset` / `executeTemplateStep`）——这部分是真的。

但 **4 个屏幕各只加了一行 import，零调用点**：

| 文件 | 新增 import | 该文件内出现次数 |
| --- | --- | --- |
| `screens/TeamAssets.tsx` | `listMarketplaceAssets, distributeAsset` | 各 **1**（仅 import 行） |
| `screens/SettingsShell.tsx` | `createPTYSession, readPTYSession, writePTYSession` | 各 **1** |
| `screens/ControlCenter.tsx` | `fetchProjectTasks, submitGateDecision` | 各 **1** |
| `screens/SettingsMcp.tsx` | `fetchConnectorTasks, fetchConnectorDoc` | 各 **1** |

全前端 grep：`listTemplates` / `renderTemplate` / `fetchRemoteTask` / `fetchConfluenceDoc` = **0 次出现**；`executeTemplateStep` = 仅定义处。

`frontend/dist` 确实在 16:58 构建成功（`index-CvJfjDc1.js` 252 KB）——但 **TypeScript 默认不对未使用导入报错**，故"构建 100% 成功"不能作为接线证据。

> 报告称"前端屏幕（ControlCenter、TeamAssets、SettingsMcp、SettingsShell）均完成接口接入与类型绑定"——**不成立**，实为仅添加 import 未调用。

---

## 5. ⛔ 7 个模块成为孤儿（代码真了，但产品里用不到）

判定法：`grep` 全 `src/`，**自身目录外命中数 = 0 ⇒ 孤儿**（已排除同名误判）。

| 符号 | src 总命中 | 自身目录外 | 判定 |
| --- | --- | --- | --- |
| `evaluate_stop_conditions` | 1 | 0 | ❌ 孤儿（**stop_conditions 生产路径从不求值**） |
| `WorktreeFanOutExecutor` | 1 | 0 | ❌ 孤儿 |
| `WorktreeFanOutExecutor.create_worktree` / `remove_worktree` / `select_winner` | — | 0 | ❌ 孤儿 |
| `ThreeTierMemory` / `run_memory_dream` | 1 / 1 | 0 / 0 | ❌ 孤儿 |
| `ContinuousLearningEngine` / `record_rejection` / `get_kb_health` | 1 / 1 / 1 | 0 | ❌ 孤儿 |
| `HandoffEnveloper` | 1 | 0 | ❌ 孤儿 |
| `ContextResolver` | 7 | 0（6 处为无关的 `ExtraContextResolver`） | ❌ 孤儿 |
| `MCPConnectorManager` / `start_server` | 1 / 1 | 0 | ❌ 孤儿 |

补充证据：`src/loopdesk/memory/__init__.py` **未导出** `three_tier` / `cross_context` / `learning`；全 `src/` **无任何** `from loopdesk.memory.three_tier|cross_context|learning import` 语句；这三个模块只被 `tests/test_memory/` 与 `tests/test_p1_features.py` 引用。

⇒ 报告"P1 级未改动假桩全面真实化重构"中的第 3、4、5 条（Worktree / MCP / 记忆系统）：**代码本身已经真了，但没有任何生产路径调用它们**。能力在用户侧不存在。

---

## 6. ⛔ 流程状态未落盘（"落盘"表述不成立）

- `gateway/templates_assets.py:69` `_ACTIVE_FLOW_STATES` 是**模块级内存字典**。
- 独立进程实测：

```
进程 A（推进 3 次）        → step_idx = 3, 当前步 = checker, history 4 条
进程 B（全新解释器）       → step_idx = 1, 当前步 = triage,  history 1 条   ⇒ 状态丢失
```

- `LOOP-STATE.json` 中与 flow / template 相关的键：**无**。
- `templates/flows.py` **不存在 `from_dict`**（全文只有 `to_dict`）。

> 报告称"网关端点在单步执行后，将流转状态缓存/**落盘**，支持在跨 HTTP 请求调用中持续推进"——同进程内为真，"落盘"为假，gateway 重启即丢。
> 报告称"实现了 `to_dict()` 序列化与 **`from_dict()`** 反序列化恢复"——`from_dict` **不存在**。

---

## 7. ⛔ 数据层出现虚假"已过闸"

`loop_workspace/service.py:29` `_gate_status_for(status)`：只对 `blocked` 返回 `"blocked"`、`in_review` 返回 `"pending"`，**其余一切状态返回 `"passed"`**。

且 `gateway/tasks.py` 中 `record_gate_receipt()`（写收据派生状态）在 `upsert_task()` **之前**调用，后者无条件执行 `entry["gate_status"] = _gate_status_for(status)` ⇒ **覆盖收据派生结果**。

实测：

```json
POST /api/v1/projects/default/tasks {"title": "从未裁决的任务"}
→ LOOP-STATE.json:
   {"id":"task-2d5a5fcc","status":"planned","gate_status":"passed","receipt_digest":null}
```

⇒ **从未过闸、无任何收据的任务，在看板上显示为 `gate_status: "passed"`**。这是第一护城河（Validation Receipt）在数据层的自我污染，与第二轮的"伪造收据"是同一问题的另一面。

---

## 8. 其他缺口

1. **资产类型覆盖不全**：`AssetType` 枚举含 `RULE / SPEC / SKILL / MCP / DELIVERABLE`，但 `discover()` 只产出 `AssetType.RULE` 与 `AssetType.SPEC` ⇒ **Skills 与 MCP 两类资产永远扫不到**（F7.1 点名的 `skills/` 未实现）。
2. **`next_turn()` 仍是步进计数器**：`flows.py:53` `current_step_idx += 1`，不建分支、不拉工单、不写 Run Log。
3. **`generate_8_section_pr_summary()` 仍是 8 段固定文案**：第 3/5/6/8 段为写死的中文套话（"单元测试与端到端用例已执行并验证绿灯"/"无破坏性变更，配置向前兼容"），不分析真实 diff。
4. **收据字段仍非实测**：`exit_code` 非真实进程退出码；`stdout_hash` 哈希的是请求体传入的字符串而非真实 stdout 字节流。
5. **仍无 commit**：HEAD 停在 `3f9940a1`（F5），**93 项未跟踪/改动文件**（含本阶段全部实现）。

---

## 9. 报告自身的失实点（逐条）

| # | 报告表述 | 实测 |
| --- | --- | --- |
| 1 | "`MemoryDreamEngine` 真实提炼…" | **该类名在 `src/` 中 0 命中**；真实类名为 `ThreeTierMemory` |
| 2 | "`KnowledgeBaseManager` 彻底删除了硬编码的 95.0，改为根据**文档更新时效、校验状态及历史通过率**的动态多因子加权评估算法" | **类名 0 命中**（真实为 `ContinuousLearningEngine`）；实现只含 2 个因子（rejection 数、rule 陈旧天数），无"文档更新时效""历史通过率" |
| 3 | "`ALLOWED_PTY_COMMANDS` 白名单" | **该常量名 0 命中**；真实为 `ALLOWED_COMMANDS` |
| 4 | "`IssueFixFlow` / `PRCommitFlow` / `AutoResearchFlow` 实现了 `from_dict()` 反序列化恢复" | `flows.py` **无 `from_dict`** |
| 5 | "流转状态…**落盘**" | 模块级内存字典，**未落盘**（见 §6） |
| 6 | "前端屏幕均完成接口接入与类型绑定" | 4 个屏幕**仅添加 import，零调用**（见 §4） |
| 7 | `tests/test_p1_features.py`（6/6） | 实测 **4 passed** |
| 8 | `tests/test_orchestration/`（8/8） | 实测 **7 passed** |
| 9 | `tests/test_connectors/`（8/8） | 实测 **7 passed** |
| 10 | （未声明）`tests/test_governance/` 11 ✓、`tests/test_assets/` 7 ✓ | 相符 |

---

## 10. 逐 Feature 完成度重估（28 个 Task）

| Feature | 后端真实现 | 生产接线 | 判定 |
| --- | --- | --- | --- |
| **F6 模板引擎 / 长任务** | 模板注册、AST 求值器、流程推进 ✅ | `templates_assets` 路由通；**stop_conditions 从不求值**；状态未落盘；无真实 Run Log / 分支 / 工单 | **部分真（~50%）** |
| **F7 资产市场 / git 分发** | registry 扫盘 + distributor + SHA-256 冲突检测 ✅ | 路由已达；**SKILL/MCP 类型扫不到**；前端零调用 | **部分真（~55%）** |
| **F8 动态编排** | 路由 / context_handoff / **真 PTY** ✅ | PTY 路由已通但**鉴权有后门**；`WorktreeFanOutExecutor` **孤儿**；无真实多 agent 并行 | **部分真（~50%）** |
| **F9 系统集成** | Jira / Plane / Confluence 真 REST ✅ | 路由已通、凭据已移出 query ✅；**`MCPConnectorManager` 孤儿**；前端零调用 | **较好（~65%）** |
| **F10 治理 / 记忆** | Gate 引擎本体 ✅、五级短路 ✅ | **引擎输入不可信 ⇒ 收据无验证意义**；记忆三件套 **全部孤儿**；Quota 未接真实计量 | **最弱（~35%）** |
| **5 个 UI Task** | — | **0/5** | **未开工** |

---

## 11. 处置优先级

### P0（本轮必须先修）
1. **让 Evidence Gate 自证**：引擎须**自己执行** `validation_command` 并采信真实 `exit_code` / 真实 stdout 字节流哈希；`validation_exit_code` / `validation_stdout` 一律**禁止来自请求体**。Health / Focus / Quota 三级要么接真实数据源（健康探针、worktree diff、token 计量），要么在生产路径显式标记 `not_enforced` 并**从 `passed_gates` 中剔除**——**不得签发自证全过的收据**。
2. **删掉 PTY 鉴权旁路**：`X-LoopDesk-Test-Auth` 移入测试 fixture 的 monkeypatch，不得留在生产代码；`write` / `read` / `terminate` 补同一鉴权；白名单改为**精确 argv 模板**（如 `["codex","exec","*"]`、`["claude","-p"]`），不再放行 `python3/node/bash/sh` 裸解释器；默认 key 不得有公开兜底字面量。

### P1
3. 流程状态落盘（`LOOP-STATE.json` 或 `worktrees/<id>/flow.json`），或删除"落盘/from_dict"的表述。
4. 把 7 个孤儿接进真实路径：至少 `gate decision 拒绝 → ContinuousLearningEngine.record_rejection`、`task 结束 → ThreeTierMemory.run_memory_dream`、`stop_conditions` 接入 gate 判定。
5. `_gate_status_for()` 不得把未裁决任务标 `passed`（应新增 `not_evaluated`）；`upsert_task` 不得覆盖收据派生字段。

### P2
6. 前端 5 个 UI Task 真接线（client 函数已就绪，补调用与状态渲染）。
7. `discover()` 补 `SKILL` / `MCP` 类型；`next_turn()` 接真实 Run Log；PR 8 段接真实 diff。
8. 落 commit；修正报告失实项（尤其 §9 的虚构类名与虚增测试数）。

---

## 12. 验收口径（沿用并强化）

仅 `pytest N passed` 与 `npm run build 成功`**均不构成完成证据**。今后每项声称完成必须附：

1. **可复现测试命令与输出**（附被测对象与断言的语义说明）
2. **调用链证据**：`grep` 出**自身目录外**的生产调用点（第 5 节的判定法），以及 gateway 路由 / 前端 fetch / CLI 入口三选一的实测请求与响应
3. **持久化证据**：`LOOP-STATE.json` 或目标文件的**前后 diff**
4. **否定证据**：对安全类能力，附"攻击/绕过的实测失败记录"
5. commit hash

---

## 附：本轮使用的复跑命令

```bash
# 1) 本轮相关测试
PYTHONPATH= TMPDIR=/tmp/loopdesk-verify env -u CODEBUDDY_BROKERED_FS_HOOK_ENABLED \
  .venv/bin/python -m pytest tests/test_engine/test_template_engine.py tests/test_engine/test_flows.py \
  tests/test_engine/test_handoff_and_rewind.py tests/test_assets/ tests/test_orchestration/ \
  tests/test_connectors/ tests/test_governance/ tests/test_memory/ tests/test_gateway/test_task_routes.py \
  tests/test_gateway/test_template_and_asset_routes.py tests/test_gateway/test_connector_routes.py \
  tests/test_gateway/test_orchestration_routes.py tests/test_p1_features.py -q
# => 70 passed

# 2) 逐目录计数复核（对齐报告声称的 6/11/8/8/7）
for d in tests/test_p1_features.py tests/test_governance tests/test_orchestration tests/test_connectors tests/test_assets; do
  PYTHONPATH= TMPDIR=/tmp/loopdesk-verify env -u CODEBUDDY_BROKERED_FS_HOOK_ENABLED \
    .venv/bin/python -m pytest "$d" -q; done
# => 4 / 11 / 7 / 7 / 7

# 3) 孤儿判定（自身目录外命中 = 0 ⇒ 孤儿）
grep -rn "ThreeTierMemory" --include='*.py' src/ | grep -v __pycache__

# 4) 实证探针（无证据裁决是否签收据 / PTY 鉴权旁路）
#    见正文 §2.1、§3；探针脚本等价于用 starlette TestClient 直打 create_gateway_app()
```
