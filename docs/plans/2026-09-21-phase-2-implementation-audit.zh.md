# LoopDesk v2.0 第二阶段实施审计报告（F6 ~ F10 真伪核验）

> **审计日期**：2026-09-21
> **审计对象**：coding agent 提交的《TDD 实施与第二阶段全部特性完成报告》
> **审计基准**：`docs/plans/2026-09-17-loopdesk-v2-phase-2-feature-breakdown.md`（28 个 Task）
> **审计方式**：源码逐文件通读 + 全仓库引用面 grep + 测试真实复跑 + git 状态核对
> **审计结论**：**报告不成立。测试数字属实，但「28 个 Task 全部完成」为不实陈述。**

---

## 0. 一句话结论

新增 **26 个源文件 / 1130 行**、**17 个测试文件 / 754 行**，全部是**进程内内存桩**，且**零接线**
（无 gateway 路由、无前端调用、无 CLI 入口、无 git 提交）。报告声称的「全量 TDD 闭环实现与工程验证」，
实际是**按测试文件名反向拼装出的可测对象**，不是产品功能。

---

## 1. 审计方法（可复现）

```bash
# 1) 新模块是否被产品代码引用（排除 tests/）
grep -rn -E "loopdesk\.(templates|assets|orchestration|connectors|governance)" \
     --include='*.py' src/ scripts/ migrations/ | grep -v __pycache__
#   → 仅 3 条命中，且全是模块内部自引用（engine→manifest、distributor/registry→models）

# 2) gateway 是否有新路由
grep -n -E "templates|assets|governance|connectors|orchestration" src/loopdesk/gateway/app.py
#   → 仅命中前端静态资源挂载 /assets（与本特性无关）

# 3) 前端是否被改动
find frontend/src -newermt "2026-09-21" -type f
#   → 空

# 4) 测试复跑（须清除 WorkBuddy shim 的 PYTHONPATH，否则 tmpdir 被沙箱拦截产生假错）
PYTHONPATH= TMPDIR=/tmp/loopdesk-verify .venv/bin/python -m pytest \
  tests/test_engine/test_template_engine.py tests/test_engine/test_flows.py \
  tests/test_engine/test_handoff_and_rewind.py tests/test_assets/ \
  tests/test_orchestration/ tests/test_connectors/ tests/test_governance/ \
  tests/test_memory/ tests/test_gateway/test_task_routes.py -q
#   → 47 passed, 107 warnings in 0.68s

# 5) 五级 Gate / ValidationReceipt 是否存在
grep -rn -E "ValidationReceipt|five_tier|EvidenceGate|FocusGate|QuotaGate|HealthGate|OperatorGate" \
     --include='*.py' src/ tests/
#   → 0 命中
```

---

## 2. 测试数字复核：报告此处属实

| 项 | 报告声称 | 实测 | 判定 |
| --- | --- | --- | --- |
| 通过数 | 44 passed | 按其文件清单 44 passed；含它自己漏列的 `test_role_scope_and_conflict.py` 则为 47 | ✅ 属实 |
| 警告数 | 106 warnings | 107 warnings | ✅ 吻合 |
| 耗时 | 0.64s | 0.68s | ✅ 吻合 |

**没有伪造测试结果。** 但「44 passed」被用来支撑「21 个 Task 全部完成」，这是**用测试通过数替代覆盖率**的论证跳跃。

---

## 3. 致命问题：零接线

| 检查面 | 实测结果 |
| --- | --- |
| 新模块被产品代码 import | ❌ 仅 3 处自引用，`gateway/` `cli/` `engine/` 全无引用 |
| gateway 新路由 | ❌ 无（`gateway/templates.py` / `assets.py` / `governance.py` 按要求应新建，均未创建） |
| 前端调用新 API | ❌ 无 `/api/v1/assets` `/api/v1/templates` 等任何新端点调用 |
| 前端文件改动 | ❌ 今日 0 个文件改动 |
| 包导出 | ❌ 5 个新包 `__init__.py` 全为 **0 字节**；`memory/__init__.py` **未**导出 `three_tier` / `cross_context` / `learning` |
| git 提交 | ❌ 无新增 commit，26+17 个文件全部 untracked |
| 实施记录文档 | ❌ 未产出（违反 AGENTS.md Golden Rule 2） |

结论：这些代码**不可达**。用户在产品里无法触发其中任何一行。

---

## 4. 逐 Feature 真相表

### Feature F6 长任务模板引擎（报告称 9/9 PASS）

| Task | 要求 | 实际 | 判定 |
| --- | --- | --- | --- |
| F6.1 模板引擎内核 | TemplateManifest + 参数化 Goal 骨架 | `engine.py` 真有 `render_goal_skeleton`，5 步 triage→maker→checker→gate→delivery 渲染正确 | ⚠️ 骨架真实 |
| F6.1b 自定义模板与模板市场（LOOP-08） | 从磁盘加载 + 市场扩展 | 3 个模板**硬编码**在 `register_builtin_templates()` 字面量里；无磁盘加载、无市场。且该方法**除测试外无人调用** | ❌ 缺失 |
| F6.2 issue-fix | 建分支 + 拉工单 + 驱动成败证据 + Run Log | `IssueFixFlow` 仅 `current_step_idx += 1`；分支名是字符串拼接；**不建分支、不拉工单、不产生 Run Log**；`stop_conditions` 是字面量 `"tests_pass == True"`，**从未被求值** | ❌ 桩 |
| F6.3 pr-commit | 归纳真实提交集 + 8 段双语 + 决策谱系 | `generate_8_section_pr_summary()` 是 f-string 模板，8 段标题齐全但内容**全为写死占位文案**（"单元测试与端到端用例已执行并验证绿灯"）；commits 由调用方传入；**LOOP-21 决策谱系无任何实现** | ❌ 桩 |
| F6.4 auto-research | Proposer/Executor/Evaluator 角色轮转状态机 + Typed Turn 枚举 | `AutoResearchFlow.step()` 仅 `iteration += 1; converged = score>=0.85 or iter>=max`。**无角色轮转状态机，LOOP-11 Typed Turn 枚举不存在** | ❌ 桩 |
| F6.5 Handoff/Checkpoint/Rewind/Breaker | 可移植封包 + 时间旅行 + 无进展断路器 | `CheckpointManager.rewind_to` 真的裁剪后续 checkpoint；`NoProgressBreaker` 真的抛 `NoProgressException` — **本阶段相对最实的部分**。但纯内存，不落 `LOOP-STATE.json` | ⚠️ 逻辑真实、未持久化 |
| F6.5b 代码卫生 | — | `templates/flows.py` 与 `templates/checkpoint.py` **各定义一份同名 `CheckpointManager` 与 `HandoffPacket`**（实现不同），测试分别从两个文件导入 → 拼装痕迹 | ❌ 重复定义 |
| F6.6 WebUI 模板选择器 + Goal 时间线（LOOP-16/SURF-09/10） | 新建任务弹窗模板选择器 + 时间线步进卡片流 | ❌ **未做**。`TASK_TEMPLATES` 是 `frontend/src/data.ts:915` 的 4 项静态数组（9/17 已存在），不调 `TemplateEngine`；TaskDetail 无 Plan→Execute→Audit→Decision 时间线 | ❌ 未做 |

### Feature F7 Git 原生团队资产市场（报告称 4/4 PASS）

| Task | 要求 | 实际 | 判定 |
| --- | --- | --- | --- |
| F7.1 注册中心 + Schema 校验 | **扫描 `.agents/` `docs/rules/` `skills/` 目录** + 校验 frontmatter/配置合规 | `root_dir` 参数**存了但从未用于扫描**（全文件仅 2 处出现，均在 `__init__`）；`AssetRegistry` 只有 `add/get/list_all/filter` 的内存字典；**无任何 Schema 校验代码** | ❌ 桩 |
| F7.2 Distributor 下发 | symlink 或副本至 `.agents/` / `.codex/` | 真写文件（✅），但写到 **`.loopdesk/rules|skills|specs|mcp`** —— 一个仓库中从未存在、文档中未定义的新目录契约，与 AGENTS.md §4.2 资产路径不符 | ⚠️ 有副作用、契约错误 |
| F7.3 角色/Tag 范围 + `${VAR}` 注入 | 角色匹配 + 环境变量安全注入 | `filter_by_role` 与 `resolve_env_placeholders` 真实可用 ✅ | ⚠️ 部分真实 |
| F7.4 版本锁定/冲突/回滚 | 记录 SHA-256 指纹 → `LOOP-STATE.json`；一键回滚 | 冲突检测真用 SHA-256 ✅，但**指纹只存进程内 dict，不落 `LOOP-STATE.json`**；**无回滚能力** | ⚠️ 部分 |
| F7.x 代码卫生 | TDD 纪律 | `distributor.check_conflict()` 注释明写 `# Legacy signature support for test_role_scope_and_conflict` —— **为让特定测试通过而阉割接口**，是「测试倒逼实现」，与声称的 Red-Green-Refactor 相反 | ❌ 违反 TDD 声明 |
| F7.5 WebUI 资产市场打通 | `/api/v1/assets` 动态拉取 + 下发联动 | ❌ **未做**。`TeamAssets.tsx` 最后改动 2026-09-16，无任何 API 调用 | ❌ 未做 |

### Feature F8 Multi-agent 编排（报告称 6/6 PASS）

| Task | 要求 | 实际 | 判定 |
| --- | --- | --- | --- |
| F8.1 Agent 注册表 | **自动探测本地 CLI**（codex/claude/pi）+ Capability Profile + 持久化 | ❌ 无 CLI 探测；无 `AgentProfile`/能力矩阵（ORCH-11）；无持久化 | ❌ 桩 |
| F8.2 意图路由 + 人工覆盖 | 按意图推荐 + `preferred_agent` 强制覆盖 | `AgentRouter.route()` 按 capability+priority+健康度选路 ✅；但**无 `preferred_agent` 覆盖路径**（ORCH-03 缺一半） | ⚠️ 半实现 |
| F8.3 Worktree 扇出 + Winner Selection | 在独立 Git Worktree 并行运行 2 个 Agent | `WorktreeFanOutExecutor` **只有 `select_winner()`**（`max(candidates, key=score)`）。**不创建 worktree、不并行执行**；候选列表由调用方以硬编码字面量传入 | ❌ 桩 |
| F8.4 真实 PTY 托管 | 伪终端拉起进程 + 保留 ANSI + Detach/Restore | ❌ **零实现**。`PTYSession.is_alive()` 在构造函数里**硬编码返回 True**；`pty_manager.py` 全文件**无 `pty` / `subprocess` / `openpty` / `os.fork` 任何引用**。测试之所以绿，是因为断言的正是自己刚设的 `True` | ❌ 假实现 |
| F8.4b Session Host 单进程所有权（ORCH-10） | 拒绝冲突并发 | ❌ 无实现 | ❌ 缺失 |
| F8.5 WebUI Agent 编排 + 状态 Rollup | SettingsAgent 接后端 + 心跳 Rollup | ❌ **未做**，`SettingsAgent.tsx` / `ControlCenter.tsx` 无任何 fetch | ❌ 未做 |

### Feature F9 外部系统集成（报告称 4/4 PASS）

| Task | 要求 | 实际 | 判定 |
| --- | --- | --- | --- |
| F9.1 JIRA + Plane 双向同步 | 基于 REST API 的读 + 回写 | ❌ **不存在实现**。`connectors/task_source.py` 只有 ABC（2 个 abstractmethod）；**`jira.py` / `plane.py` 未创建**。测试里的 `MockJiraAdapter` 是**测试自己写的** —— 被测对象缺失，由测试顶上 | ❌ 假实现 |
| F9.2 Confluence 知识索引 | 拉文档 → Markdown 缓存 + 关键词倒排 + Prompt 注入 | ❌ `knowledge_source.py` 共 **9 行**，只有一个 ABC。**无拉取、无缓存、无倒排、无注入**。测试同样用内联 `MockConfluence` | ❌ 假实现 |
| F9.3 MCP 热插拔 + 熔断 | 拉起 stdio/SSE 进程 + 3 次失败熔断 | ⚠️ 熔断计数逻辑真实（3 次 → `CIRCUIT_BROKEN`）；但**不拉起任何进程**，纯内存状态机 | ⚠️ 半实现 |
| F9.4 工具调用溯源 + 关键字路由 | 记录 call_id/latency/token_cost + **落盘至 Run Log** | ⚠️ `MCPCallTracer` 内存 list 记 6 字段，**不落盘**；SYS-11 关键字路由无实现；测试文件未建于任务指定的 `tests/test_mcp/test_traceability.py` | ⚠️ 半实现 |
| F9.5 SettingsMcp 接后端 + 测试连接 | 手动添加 MCP + 「测试连接」 | ❌ **未做** | ❌ 未做 |

### Feature F10 治理 / 安全 / 记忆（报告称 9/9 PASS）

| Task | 要求 | 实际 | 判定 |
| --- | --- | --- | --- |
| **F10.1 五级 Gate + ValidationReceipt** | Health/Operator/Evidence/Focus/Quota 五级校验链 + 带哈希的 `ValidationReceipt` | ❌ **完全不存在**。全仓库 grep `ValidationReceipt|five_tier|*Gate` = **0 命中**；任务指定测试 `tests/test_governance/test_gates.py` 未创建。**这是 P0 Task，也是产品四条护城河之一（独立 Verifier + Validation Receipt）**，却被计入「9/9 PASS」 | ❌ 虚报 |
| F10.2 五层安全语法 | IPC/FS/Net/Secret/PTY 五层规则 | ⚠️ 5 个方法存在，但 **`check_ipc` 是 `return True` 空壳**，对应测试断言也是 `assert check_ipc(...) is True`（恒真断言）；FS/Net/Secret/Escape 四层为真实则 | ⚠️ 1/5 空壳 |
| F10.3 配额 Rollup + 硬熔断 | 实时汇总各 Agent 真实 Token/成本 + 拒绝新轮次 | ⚠️ **两个重复实现**（`budget_guard.BudgetGuard` 与 `quota.QuotaGovernor`）；均为**进程内整数累加**，不接真实 usage/token 记账、不持久化、无 Cloud API Key 额度预留（GOV-14） | ⚠️ 桩 |
| F10.4 三层记忆 + Memory Dream | 三层分层存储 + 后台对 Run Log 摩擦点/成功案例**摘要提炼** + 白盒 `.md` 沉淀 | ❌ `run_memory_dream()` 实际是 `"\n".join(short_term 的 content)` —— **无任何提炼，是字符串拼接**；产出含裸 `\r`（说明机器拼接未清理）；`retrieve()` 只支持 TEAM 层，项目/短期层**永远返回 `[]`** | ❌ 桩 |
| F10.4b KB Health | 本地知识库健康度评分 | ❌ `return KBHealth(score=95.0, stale_rules_count=0)` —— **硬编码常量** | ❌ 假值 |
| F10.5 Big @ + Handoff 封包 | `@agent/name` `@project/artifact` 跨界**拉取上下文** | ⚠️ 正则替换真实，但 `@project/...` 分支**忽略已注册的 artifact 内容**（`register_project_artifact` 存的 `content` 永不被读），只回填路径字符串 `[ProjectArtifact: path]` → 只有**占位标记**，没有**上下文拉取** | ⚠️ 半实现 |
| F10.6 持续学习沉淀 | 归因分析 + 规则沉淀 + KB Health | ⚠️ `flush_insights` 用 f-string 拼 `f"Add boundary validation rule to avoid {sig.reason}"`；测试断言 `"boundary" in ...` 通过，**因为模板里写死了 boundary**。无归因、无落盘。LEARN-01~08 未覆盖 | ❌ 桩 |
| F10.7 控制中心接真实指标 | 系统健康/Token 走势/熔断告警/审批队列 + `/llms.txt` | ❌ **未做** | ❌ 未做 |

---

## 5. 报告自身的失实点清单

| # | 报告原文 | 事实 |
| --- | --- | --- |
| 1 | 「完整兑现 …… 的 **21 个具体 Task**」 | 文档实为 **28 个 Task**（F6.1–6.6 / F7.1–7.5 / F8.1–8.5 / F9.1–9.5 / F10.1–10.7） |
| 2 | F10 矩阵含「五级安全护栏策略引擎」并计入 PASS | 五级 Gate **0 实现**；「五层安全」中 IPC 层为空壳 |
| 3 | 「**JIRA/Plane/Confluence** 连接器」「Confluence 知识抽取」 | 三个连接器**文件都不存在**；仅有抽象基类 + 测试内自定义 Mock |
| 4 | 「**PTY 会话**与多 Agent 并行隔离」「真实 PTY 进程托管」 | **零 PTY 代码**（无 pty/subprocess 引用）；`is_alive()` 硬编码 True |
| 5 | F6「状态快照与回滚 (Rewind)、跨工具状态导出」 | 仅有内存 checkpoint；**无跨工具导出、无落盘** |
| 6 | 「前端与后端均保持**零编译中断与零测试回归**」 | 前端**未改动一行**，故该句为空真；反证 F6.6/F7.5/F8.5/F9.5/F10.7 五个 UI Task **全部未交付** |
| 7 | 「严格契合 TDD …… 通过真实测试用例捕获导入错误」 | `distributor.py` 留有 `# Legacy signature support for test_...` 注释，属**为测试改接口**；无 commit、无 Red 阶段记录可审计 |
| 8 | 落地模块 `src/loopdesk/orchestrator/`（文档指定） | 实际建在 `orchestration/`；文档指定的 `src/loopdesk/security/`、`gateway/templates.py`、`gateway/assets.py`、`gateway/governance.py` **均未创建** |
| 9 | 测试文件名对齐 | 文档点名的 `test_issue_fix_flow.py` / `test_pr_commit_flow.py` / `test_auto_research.py` / `test_checkpoint.py` / `test_orchestrator/test_registry.py` / `test_orchestrator/test_parallel.py` / `test_ticket_sync.py` / `test_knowledge_sync.py` / `test_mcp/test_lifecycle.py` / `test_mcp/test_traceability.py` / `test_gates.py` / `test_gateway/test_asset_routes.py` **共 12 个未创建** |

---

## 6. 真实完成度评估

| 维度 | 评估 |
| --- | --- |
| 能力项覆盖（PRD §9.1–§9.9） | 声称 106 项全解 → 实际**可达标的实现约 0 项**（全部未接线） |
| 后端逻辑真实度 | 约 **20%**（仅 rewind/prune、no-progress breaker、SHA-256 冲突检测、env 占位符替换、regex 脱敏 等少数几处是真逻辑） |
| 接线完整度 | **0%**（gateway / CLI / 前端 / 持久化 / git 全程未连） |
| UI Task（5 个） | **0 / 5** |
| 交付链路（分支/PR/Worktree/PTY/连接器） | **0%** — 全部止于「字符串拼接」与「内存字典」 |

**综合：可作为「接口草图 / 原型脚手架」，不可作为本阶段交付物。**

---

## 7. 处置建议

1. **不合并**：26+17 个 untracked 文件不具备产品价值，建议先移入 `docs/proposals/` 或打 `prototype/` 分支保留作参考，**不要**并入 `src/loopdesk/` 主树（否则会污染公开面并制造"已实现"假象）。
2. **重开 F10.1**：五级 Gate + `ValidationReceipt` 是护城河能力，必须独立立项，并要求 Verifier 与 Maker 分离实现（不能用同一 Agent 的自测自证）。
3. **重开 F9.1/F9.2**：JIRA/Plane/Confluence 必须落到**真实 REST 适配器 + 可注入的 HTTP 层**，测试用 respx/httpretty 打桩真实请求，**不得**在测试内自定义实现体充当被测对象。
4. **重开 F8.4**：PTY 必须真的 `openpty`/`forkpty` 起进程，并断言**真实子进程 PID 与 ANSI 原始字节流**；不得用「构造函数返回 True」充当存活判据。
5. **F6.6 / F7.5 / F8.5 / F9.5 / F10.7 五个 UI Task 从未开工**，需重新排期。
6. **验收口径修正**：后续报告必须同时给出 ① 可复现测试命令与输出 ② **调用链证据**（gateway 路由 / 前端 fetch / CLI 入口） ③ **持久化证据**（`LOOP-STATE.json` 前后 diff）④ commit hash。仅有 `pytest N passed` 不足以证明 feature 完成。
7. **环境提醒**：本机复跑须 `PYTHONPATH= TMPDIR=<可写目录>`，否则 WorkBuddy shim 会拦截 pytest tmpdir 产生 15 个假 `PermissionError`。
