# 企业级 Agent 平台能力清单 × LoopDesk 功能清单 — 逐条对照

> 日期：2026-10-09
> 对照左侧：外部「企业级 AI 数字员工班组底座」能力清单（14 大类，共 89 条细项）
> 对照右侧：LoopDesk 权威功能清单 —— `docs/prd/loopdesk-prd-v2.0.zh.md` §9「功能清单（Feature Inventory）」
> 定位依据：`docs/product-positioning.md`、`docs/prd/loopdesk-prd-v2.0.zh.md` §3.2/§3.3、`AGENTS.md` §1.1

---

## 0. 结论（先看这三条）

1. **两者不是同一坐标系，覆盖率天然不高，这不是缺陷。**
   左侧清单的隐含前提是「**中心化平台拥有 agent 的一切**」——租户、集群、平台内工具、平台内知识库、平台内模型渠道。
   LoopDesk 的隐含前提是「**agent 的 runtime 归别人**（claude / codex / pi），LoopDesk 只管循环状态 + 交接 + 治理」。
   LoopDesk 在 `AGENTS.md` §1 的自述是 **控制 / 编排层**，且 §3.3 明确排除「重多面 agent OS / 多租户」。

2. **逐条对照的结果（89 条细项，逐行可数）：● 完全覆盖 19 条、◐ 部分覆盖 41 条、○ 不覆盖 20 条、⊘ 明确不做 9 条。**
   重合的部分**形态都更轻**：无租户、无集群、无平台内模型渠道，但换来可移植状态与跨工具连续性。

3. **LoopDesk 有 9 项左侧清单完全没有的东西**（§3），全部集中在「跨工具/跨团队的循环连续性」这一条线上。
   其中 `LOOP-STATE.json` 可移植真源、git 原生资产分发、Validation Receipt 是**竞品也没做**的差异化（PRD §2.3）。

> ⚠️ 口径提醒：本文件「LoopDesk 功能清单」指 **PRD §9 的 119 条**（实测 `grep -cE '^\| (WS|SYS|ORCH|LOOP|CTX|ASSET|GOV|SURF|LEARN)-[0-9]+'` = 119）。
> PRD §9.10 自带统计表写「合计 117」，且其 P0/P1/P2 三列加总仅 114 —— **该统计表与表格实际行数不符，本文件以实测 119 为准**。

---

## 1. LoopDesk 的功能清单是什么（九大平面 / 119 条）

来源：PRD v2.0 §7 能力总览 + §9 功能清单。状态列口径：`✅ 已实现` / `🆕 新增设计（本轮定义，未实现）` / `🔲 待实现` / `⏳ 部分` / `🔶 预留`。

| 平面 | 职责 | 条数 | 代表条目 |
| --- | --- | --- | --- |
| **WS 工作区与状态内核** | 单一真相源 | 10 | `LOOP-STATE.json` 可移植真源、Project/Loop/Goal/Task/Run 五层模型、Handoff Packet、partial export/import |
| **SYS 系统集成与 MCP** | 外部系统接入 | 11 | MCP-first adapter、ACP-second、JIRA/Plane/Confluence/GitHub 连接器、双向同步、MCP lifecycle |
| **ORCH Agent 编排** | local-first 编排 | 13 | Agent 注册表、Task Router + human override、per-Goal worktree 隔离、并行 agent 赢家选择、真实 PTY |
| **LOOP Loop 引擎与长任务** | 长任务自动完成 | 21 | Scheduler、triage/maker/checker 六阶段、issue-fix/pr-commit/auto-research 模板、五级 Gate、typed handoff、独立验证、checkpoint/rewind |
| **CTX 上下文传递与记忆** | 上下文传递 | 13 | Context Injection Contract（7 字段）、跨会话 continuity、三层记忆、白盒可编辑记忆、compaction |
| **ASSET 团队 AI 资产** | 团队能力复用 | 14 | 资产注册表（Spec/Rule/Skill/MCP/Deliverable）、git 共享、下发 Distributor、Skill Engineering |
| **GOV 治理/成本/安全** | 治理与护栏 | 16 | Execution Trace schema、成本 rollup、预算/kill switch、审批队列 + 多端审批、沙箱、deny-wins 策略、Validation Receipt |
| **SURF 用户面与分发** | 用户面 | 13 | CLI、本地 Web 控制中心、Agent Work Feed、统一运行视图、IM 继续面、任务看板、资产市场 |
| **LEARN 学习与持续改进** | 持续改进 | 8 | Continuous Learning Loop、knowledge flush、decision 谱系、KB Health、anchor packet |
| **合计** | | **119** | |

---

## 2. 逐类对照（左侧 14 类）

判定符号：**●** 完全覆盖 ｜ **◐** 部分覆盖 ｜ **○** 不覆盖 ｜ **⊘** 明确不做（有书面排除依据）

### 一、内核调度与执行引擎

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 1.1 | 单进程主底座 + 常驻后台服务 + 后台长任务，不依赖前端保活 | 本地 gateway 常驻服务；`docs/scheduling.md` 调度任务由 gateway 执行；`loopdesk agent --timeout` | ◐ | 「单进程」是本地 gateway 与宿主 CLI 同机，不是 worker 池 |
| 1.2 | 任务自动拆解器：长任务拆子任务 DAG、父子状态联动 | 领域模型是 Project→Loop→Goal→Run 的**纵向层级**，非 DAG；GOAP plan tree = LEARN-08 P2 🆕 | ○ | 无 DAG 生成器/依赖管理 |
| 1.3 | 会话状态持久化：断点续跑，崩溃/重启后恢复上下文 | WS-01/02/04 ✅、CTX-02 ✅、LOOP-15 checkpoint/resume/rewind 🆕、ORCH-12 🆕 | ● | **LoopDesk 核心强项**，且状态是白盒文件而非 DB |
| 1.4 | 任务回放：完整执行日志可重放（prompt/工具/分支） | `docs/diagnostics-and-replay.md` 重放已记录回合；LOOP-16 Goal 时间线；GOV-01 trace | ● | 重放粒度是**已记录的 trace 事件/回合**，非 runtime 全量重演 |
| 1.5 | 三级推理分流：规则引擎 → 语义缓存 → LLM | 无对应条目（`语义缓存`/`规则引擎` 在 docs 仅出现于竞品调研） | ○ | LoopDesk 降本走**预算/配额**，不走缓存分流 |
| 1.6 | 多模型路由：多 LLM 作下属 Worker 分发子任务 | ORCH-01 Agent 注册表（provider/runtime/instructions/MCP/skills）、ORCH-03 Task Router + human override、`docs/decisions/runtime-matrix.md` | ● | 编目的是 **agent CLI（claude/codex/pi）**，不是裸 LLM 渠道 |
| 1.7 | 任务优先级队列：插队、权重、最大并发 | 有最大并发（ORCH-01）与 pause/kill（LOOP-01）；`优先级队列/插队` grep 0 命中 | ◐ | **无优先级/权重调度** |
| 1.8 | 超时隔离：单任务/单工具独立超时熔断 | `--timeout`（agent 总墙钟）、`--max-iterations`；LOOP-17 no-progress breaker P1 🆕 | ◐ | **无 per-tool-call 独立超时** |
| 1.9 | 资源配额隔离：每 Agent/租户算力、Token、内存上限 | GOV-03 预算上限/日限/max iterations/kill switch ✅；LOOP-09 `should-run`、LOOP-20 duty cycle 🆕 | ◐ | 无租户级、无内存/CPU 上限 |

### 二、Agent 班组编排 & 多智能体管理

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 2.1 | Agent 角色定义：岗位/职责/系统 Prompt/权限集/技能包 | ORCH-01 🆕（provider/runtime/instructions/env/MCP/skills/并发） | ● | 缺「权限集」独立字段（权限走 GOV-06 全局模式） |
| 2.2 | 班组编排：串行/并行/轮询/评审模式（执行+审核+复盘） | LOOP-02 triage/maker/**checker**/escalation 六阶段 ✅；ORCH-05 并行 agent + 赢家选择 🆕；LOOP-07 auto-research 三角色 🆕 | ◐ | 是**按 Goal 的六阶段 + 并行扇出**，不是常设班组；§3.3 明确不采纳 swarm-first 自动编排 |
| 2.3 | 角色委派：主 Agent 委派子任务、跨 Agent 传上下文与文件 | LOOP-12 typed handoff packet、CTX-01 Context Injection Contract（7 字段）、ORCH-06 子会话 | ◐ | 是**对等交接（handoff）**，不是上下级委派 |
| 2.4 | 会话隔离：各 Agent 会话独立 + 跨 Agent 消息通信/广播 | ORCH-04 per-Goal worktree 隔离 ✅；Scenario F 房间级隔离 🆕；CTX-04 Big @ 跨代理引用 🆕 | ◐ | **无消息广播/总线式通信** |
| 2.5 | Agent 启停管控：暂停/终止/冻结实例 | LOOP-01 pause/kill（调度任务级） | ◐ | **无实例级冻结** |
| 2.6 | Agent 版本管理：配置快照、回滚、A/B、灰度 | ASSET-04 是**资产**版本管理，非 Agent 配置 | ○ | 无 Agent 配置快照/灰度 |
| 2.7 | 实例扩缩容：单机多实例 / 集群横向扩容 | 单机多 agent ✅（ORCH）；集群 = **零基础设施**核心卖点 | ⊘ | §2.3 差异化护城河即「无服务器无 DB 无云账号」 |
| 2.8 | 节点接入：内网主机出站接入做执行节点 | 无节点概念（LoopDesk 跑在执行者本机，local-first） | ○ | 无中心节点池 |

### 三、记忆、上下文与会话管理

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 3.1 | 分层记忆：短时/中期/长期向量/企业知识库 | CTX-06 三层记忆 = **person / event / experience**（语义分层，非存储分层）🆕 | ◐ | **无向量库/知识库存储层** |
| 3.2 | 记忆读写权限控制：可读/可写/禁改分区 | CTX-07 白盒可编辑记忆（可查/改/删/钉住）🆕；权限模式是全局的 | ◐ | **无分区级读写权限** |
| 3.3 | 记忆检索路由：向量 / 关键词 / 静态文档自动选择 | CTX-12 本地检索：keyword + semantic + BM25 图增强重排 ✅ | ● | |
| 3.4 | 会话分支：分叉尝试多方案、对比不同 Agent 输出 | ORCH-06 子会话/平行探索（分叉不污染主上下文、一键带回、对抗性分析）🆕 | ● | |
| 3.5 | 上下文压缩：自动摘要、冗余裁剪、动态窗口 | CTX-10 compaction + superseded-read elision ✅ | ● | |
| 3.6 | 会话归档：结束自动归档、归档后只读不可改 | CTX-02 export ✅；GOV-11 hash-chain 篡改可检测 P2 🆕 | ◐ | **无只读归档锁** |

### 四、技能 / 工具系统

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 4.1 | 技能包管理：注册、版本、上下线、分组、复用 | ASSET-06 Skill Engineering（trigger/context/workflow/evaluation/feedback）✅、ASSET-07 组织级分发 🆕 | ● | |
| 4.2 | 多类型工具：API/Shell/DB/文件/RAG/SDK/MCP | SYS-01 MCP-first（stdio + HTTP）✅、`docs/tools-and-sandbox.md` | ◐ | **无 RAG 检索工具**、无 DB 查询工具 |
| 4.3 | 工具调用审批流：白名单自动放行 + 高风险人工审批 | GOV-04 审批队列 + CLI/Web/IM 多端审批同一 audit trail ✅；GOV-05 escalation ✅；`docs/approvals-and-permissions.md` | ● | **LoopDesk 核心强项** |
| 4.4 | 工具入参自动脱敏：手机号/身份证/银行卡/企业敏感字段 | 无（`脱敏` 命中均为凭证 `*****` 展示，非 PII 掩码） | ○ | GOV-10 是**凭证保护**，不是**入参脱敏** |
| 4.5 | 工具调用审计：参数、返回值、耗时、异常 | GOV-01 Execution Trace / Run Log schema（action/tool/runtime/duration/cost/decision/result/artifacts）✅、LOOP-19 ✅ | ● | |
| 4.6 | 沙箱隔离执行：限制文件读写、网络出站 | GOV-07 沙箱 worktree / bwrap / sandbox-exec / Docker ✅；GOV-08 path denylist ✅ | ◐ | **无网络出站限制**（GOV-09 五层安全语法含 network，P1 🆕） |
| 4.7 | 工具失败重试 & 降级：重试次数、退避、切备选技能 | LOOP-17 no-progress breaker P1 🆕；GOV-12 失败模式目录 + kill/降级规则 🆕 | ◐ | **无自定义退避策略**、无备选技能切换 |
| 4.8 | 技能权限矩阵：最小权限，只能调授权范围内技能 | GOV-06 权限模式 read-only/restricted/full-access ✅；GOV-08 deny-wins ✅；ASSET-08 分发范围 roles/tags/sources 🆕 | ◐ | 权限是**模式级**，非「Agent × 技能」矩阵 |

### 五、成本、预算与熔断管控

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 5.1 | 多级 Token 预算：租户/项目/单 Agent/单任务 | GOV-02 成本 rollup（session/agent/skill/loop/team）✅、GOV-03 预算上限/日限 ✅ | ◐ | **无租户级**预算 |
| 5.2 | 自动熔断：达阈值停任务/暂停 LLM/告警 | GOV-03 kill switch ✅、LOOP-09 quota `should-run` 🆕、GOV-12 降级 🆕 | ● | 告警仅落 run log，无通知通道 |
| 5.3 | 成本计量：in/out token、缓存命中、分模型/Agent | GOV-02 ✅、`docs/usage-and-cost.md`（按模型分组、JSON 输出） | ◐ | **无缓存命中统计**（无缓存体系） |
| 5.4 | 缓存命中率统计 | 无 | ○ | |
| 5.5 | 模型计费标签：按业务线统计 LLM 成本 | 维度是 session/agent/skill/loop/team，**无自定义业务标签** | ○ | |
| 5.6 | 流量限流：单分钟最大 LLM 请求数 | 无 | ○ | |

### 六、安全、权限、租户体系

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 6.1 | 多租户隔离：数据/配置/记忆/日志租户级隔离 | 无。§3.3「重多面 agent OS / 多租户」列为**不采纳**（来源 Octos / PilotDeck） | ⊘ | 定位冲突：零基础设施 vs 租户体系 |
| 6.2 | RBAC：管理员/运维/开发者/审批人/审计员 | 无角色体系（`RBAC` grep 0 命中）；有权限模式 + 审批人语义 | ⊘ | 同上 |
| 6.3 | 数据访问权限：知识库/文件/DB 细粒度 | GOV-08 path denylist ✅、GOV-06 权限模式 ✅、WS-08 公私边界 🆕 | ◐ | 路径级，非资源级 |
| 6.4 | Prompt 输入输出内容安全：拦截违规请求与输出 | 无 | ○ | |
| 6.5 | 密钥托管：加密存储，Agent 不能明文读取 | GOV-10 secrets 保护（不进 prompt/state/logs，OS keychain）✅ | ● | |
| 6.6 | 出站网络管控：节点出站白名单 | 无（GOV-09 network 维度 P1 🆕，且无白名单配置项） | ○ | |
| 6.7 | 水印与溯源：输出文档携带溯源水印 | 无文档水印；有 run log 可溯源到 workspace/Goal/run（SYS-09 🆕） | ○ | |
| 6.8 | 操作防篡改：审计日志不可篡改、只追加 | GOV-11 hash-chain / ledger P2 🆕，**未实现** | ○ | 来源：Block/Buzz（`docs/research/competitive-intel-block-buzz.md`） |

### 七、可观测、监控、审计 & 复盘

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 7.1 | 全链路日志：每步思考/工具/模型 IO/决策分支落盘 | GOV-01 trace ✅、LOOP-19 Run log（started/found/acted/escalated/cost）✅ | ● | |
| 7.2 | 实时监控大盘：agent 状态、token、成功率、审批待办 | SURF-02 本地 Web 控制中心 ✅、SURF-04 统一运行视图（所有会话/审批门/运行任务/资产/长任务进度）✅、ORCH-07 状态 rollup 🆕 | ◐ | **无聚合指标大盘**（消耗率/成功率/超时率） |
| 7.3 | 告警体系：预算/失败/卡死/异常工具/安全事件 | GOV-03 预算 ✅、GOV-12 失败模式 🆕、LOOP-17 卡死熔断 🆕 | ◐ | **无告警通道/通知中心** |
| 7.4 | 审计检索：按时间/Agent/任务 ID/用户/关键词 | CTX-12 本地检索 ✅、run log；**无专门审计检索界面** | ◐ | |
| 7.5 | 任务复盘工作台：可视化 DAG、每步输入输出/理由/根因 | SURF-10 goal 时间线（六阶段 stepper + trace 事件 + resume/rewind）🆕、LOOP-16 Plan→Execute→Audit→Decision 卡片流 🆕 | ◐ | **无 DAG 可视化** |
| 7.6 | 指标报表：日报/周报、CSV 导出 | WS-07 partial export/import ✅（按 Goal/Loop/time range） | ◐ | **无报表生成** |
| 7.7 | 事件导出：对接企业 SIEM / 日志系统 | 无 | ○ | |

### 八、知识库 & RAG 能力

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 8.1 | 多格式文档接入：PDF/Word/Excel/MD/网页/DB | SYS-05 Confluence 连接器（页面/空间 → 项目知识）🆕；附件摄取 `attachment_ingest.py`、音频转写 | ◐ | **无 PDF/Word/Excel 解析管线产品面** |
| 8.2 | 文档版本管理：更新快照，可指定版本知识库 | ASSET-04 是资产版本管理（Specs/Rules/Skills），非知识库文档 | ◐ | |
| 8.3 | 权限绑定知识库：不同 Agent 只能访问授权知识库 | 无（无角色/权限体系） | ⊘ | |
| 8.4 | 引用溯源：回答附原文片段与来源链接 | SYS-09 MCP 调用溯源 🆕、GOV-01 artifacts 字段 ✅ | ◐ | **无文档级引用溯源** |
| 8.5 | 增量索引 / 定时同步业务数据源 | SYS-07 双向同步 🆕、LOOP-01 Scheduler ✅ | ◐ | |

### 九、文件与数据交互

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 9.1 | 会话内文件上传下载 + Agent 读写隔离存储 | `uploads.py` / `attachments.py` / `artifacts.py`；ORCH-04 worktree 隔离 ✅ | ● | |
| 9.2 | 文件类型校验、病毒扫描 | 类型/大小校验有（`input_normalization.py`）；**病毒扫描无** | ◐ | |
| 9.3 | 文件权限：上传者/Agent/审批人访问控制 | GOV-08 path denylist + WS-08 公私边界 | ◐ | 无主体级权限 |
| 9.4 | 批量文件处理：批量读取/解析/生成 | 能力来自宿主 agent runtime，**无批量处理产品面** | ◐ | |

### 十、API、集成与外部对接

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 10.1 | 平台 REST API：创建 Agent/提交任务/查状态/取日志/触发审批 | 本地 HTTP 面：`src/loopdesk/gateway/` 下 30+ `rpc_*.py` 模块 + `docs/gateway.md` | ◐ | **本地单机 API，非多租户平台 API** |
| 10.2 | WebHook 回调：任务完成/待审批/告警推送到内部系统 | `docs/scheduling.md`：`--webhook-url` / `--webhook-token-env`（任务结果出站投递） | ● | 单向出站，无入站回调注册 |
| 10.3 | SSO 单点登录（OIDC/SAML） | 无（`OIDC`/`SAML` 词边界检索 0 命中；SSO 无独立条目） | ⊘ | 无账号体系（零账号默认） |
| 10.4 | 事件总线：内部事件推送，对接监控/工单 | `gateway/events.py`、`session_events.py`、`websocket.py`、`event_bridge.py` | ◐ | 进程内/本地 WS，非企业总线 |
| 10.5 | MCP 协议支持：兼容 MCP 工具生态 | SYS-01 MCP-first ✅、`docs/mcp-server.md`、`src/loopdesk/mcp` + `mcp_server` | ● | **核心能力** |

### 十一、前端控制台

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 11.1 | Agent 管理面板：新建/编辑/启停/配置 Prompt/绑技能 | ORCH-01 注册表 🆕 + `loopdesk-webui/` 静态交付面 | ◐ | |
| 11.2 | 任务工作台：查看运行任务、手动干预、终止、提交审批 | SURF-04 ✅、SURF-12 任务看板（默认落地页，Codex 三栏）🆕 | ● | |
| 11.3 | 回放调试界面：可视化回放，看每步思考与决策 | SURF-10 goal 时间线 🆕 | ◐ | 无独立回放 UI |
| 11.4 | 缓存管理面板 | 无 | ○ | |
| 11.5 | 审计查询页面、报表导出界面 | SURF-02 控制中心含 inspection/diagnostics/export ✅ | ◐ | 无审计检索页、无报表页 |
| 11.6 | 节点管理面板：内网节点在线状态、资源负载 | 无 | ⊘ | 无节点 |

### 十二、部署模式

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 12.1 | 私有化单机部署：单进程部署内网服务器，免公网 | `docs/deployment.md` §6.1「本地单开发者部署（推荐）」+ §6.2 后台 gateway 部署 | ● | |
| 12.2 | 私有化集群部署：多节点分布式执行 | 无。「零基础设施 local-first（无服务器、无 DB、无云账号）」是 PRD §2.3 四条护城河之一 | ⊘ | |
| 12.3 | 混合云模式：管理面在内网、节点跨机房接入 | 无 | ⊘ | |
| 12.4 | 容器镜像交付：Docker 镜像、K8s 编排 | 仓库根有 `Dockerfile` + `compose.yaml`（开发/运行环境）；**无企业镜像交付矩阵与 K8s 编排** | ◐ | |
| 12.5 | 离线包版本：无互联网环境部署、本地模型对接 | pip/wheel 本地安装可离线；多 provider（`docs/providers-and-models.md`）。**无企业离线包交付流程** | ◐ | |

### 十三、高级企业增值模块

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 13.1 | Agent 评估模块：批量评测准确率/幻觉率、生成报告 | LEARN-03 reward 模型（输出量/质量/token 保守评估）P2 🆕，语义不同 | ○ | 无批量评测 |
| 13.2 | 合规模块：GDPR/等保、留存周期清理、脱敏导出 | 无（`GDPR`/`等保` grep 0 命中） | ○ | |
| 13.3 | 工单联动：Agent 自动创建/处理工单、同步状态 | SYS-03 JIRA 连接器、SYS-04 Plane 连接器（任务拉取 + 进度/结果/链接回写）🆕、SYS-07 双向同步 🆕 | ◐ | 同构但目标是 JIRA/Plane，非企业 ITSM |
| 13.4 | 人工介入 HITL：中途接管、下发干预指令 | GOV-04 审批队列 + 多端审批 ✅、ORCH-03 human override ✅、SURF-05 IM 继续面 ⏳ | ● | **核心强项**（审批而非「接管」） |
| 13.5 | 模型网关集成：统一多模型、负载均衡、故障切换 | 多 provider 支持 + `docs/decisions/runtime-matrix.md`；**无负载均衡/自动故障切换** | ◐ | |
| 13.6 | SLA 管理：超时告警、SLA 达成率 | 无 | ○ | |
| 13.7 | 定制化运维/技术支持/现场实施 | 组织能力，非产品能力 | ○ | |

### 十四、底层运维能力

| # | 左侧要求 | LoopDesk | 判定 | 差异说明 |
| --- | --- | --- | --- | --- |
| 14.1 | 节点健康检查、自动下线故障节点 | 无（无节点） | ⊘ | |
| 14.2 | 日志轮转、存储容量告警 | 无 | ○ | |
| 14.3 | 备份与恢复：配置/记忆库/审计日志定时备份 | WS-07 partial export/import（按 Goal/Loop/time range，无云账号）✅；**无定时备份** | ◐ | |
| 14.4 | 灰度升级：平台与 Agent 配置灰度发布、回滚 | ASSET-04 资产可回滚 ✅；**无平台灰度升级** | ◐ | |
| 14.5 | 资源监控：节点 CPU/内存/磁盘 | 无 | ○ | |

---

## 3. 反向：LoopDesk 有、企业清单没有的（护城河）

| # | 能力 | PRD 条目 | 为什么企业清单里没有 |
| --- | --- | --- | --- |
| R1 | **可移植 durable `LOOP-STATE.json` 单一真源**（可机读、可 diff、可 export，跨工具消费） | WS-01 ★ | 企业清单的状态全在平台内部，无跨平台可移植诉求 |
| R2 | **git 原生团队 AI 资产分发**（Specs/Rules/Skills/MCP/交付物，一键下发、版本化、可回滚） | ASSET-01~14 | 企业清单把资产锁在平台里，不分发给成员工作区 |
| R3 | **跨工具 / 跨会话 / 跨团队成员 handoff packet** | WS-06、LOOP-12、CTX-01 | 企业清单是「单平台内多 Agent」，不跨工具 |
| R4 | **独立验证 + 机器可读 Validation Receipt**（checker fresh context / 只读 / 快照哈希） | LOOP-13、GOV-15 | 企业清单只有「审核 Agent」概念，无机器可读验证凭证 |
| R5 | **五级 Gate**（health → operator → evidence → focus → compute quota） | LOOP-10 | 无对应 |
| R6 | **Loop Engineering 六阶段 + L1/L2/L3 成熟度分级**（报告 → 辅助 → 无人值守渐进） | LOOP-02、LOOP-03 | 企业清单无成熟度模型 |
| R7 | **零基础设施 local-first**（无服务器/无 DB/无云账号） | PRD §2.3 | 企业清单恰好相反 |
| R8 | **长任务固定模板**（issue-fix / pr-commit / auto-research，参数化生成 Goal 骨架） | LOOP-05~07 | 企业清单只提「任务模板」泛概念 |
| R9 | **公私边界**（public schema / private 路径·日志·凭证·活跃 goal 不提交） | WS-08 | 无对应 |

---

## 4. 若要向企业版延伸：缺口清单（按补齐代价从低到高）

| 序 | 缺口 | 为什么 LoopDesk 现在没有 | 补齐代价 |
| --- | --- | --- | --- |
| G1 | hash-chain 防篡改审计（GOV-11） | 已设计为 P2，未实现 | **低** —— 纯本地文件层，不动架构 |
| G2 | PII 入参脱敏 | 与凭证保护是两件事 | **低** —— 工具调用前的中间件 |
| G3 | 指标大盘 / 报表 / 审计检索页 | 有 run log 与导出，缺聚合与展示 | **中** —— 前端 + 聚合查询 |
| G4 | 工具调用级超时 + 退避重试 + 备选技能 | 当前只有 agent 级 `--timeout` | **中** —— 执行器改造 |
| G5 | 网络出站白名单 | GOV-09 五层安全语法的 network 维度 | **中** —— 依赖沙箱后端能力 |
| G6 | 会话只读归档锁 | 无归档状态机 | **中** |
| G7 | 平台内知识库 / RAG 解析管线 | Confluence 连接器是入口，无解析与索引 | **高** —— 需引入向量存储，与零基础设施冲突 |
| G8 | 多租户 + RBAC | §3.3 明确不采纳 | **极高** —— 等于换产品定位 |
| G9 | 集群 / 节点池 / 混合云 | 与「零基础设施」护城河直接冲突 | **极高** —— 放弃核心差异化 |
| G10 | SLA / 合规（GDPR·等保）/ SIEM 对接 | 无 | **高** —— 需要合规体系而非单点功能 |

---

## 5. 一句话回答

**LoopDesk 的功能清单是「循环控制层」的 119 条（九大平面：工作区状态 / 系统集成 / Agent 编排 / Loop 引擎 / 上下文记忆 / 团队资产 / 治理成本安全 / 用户面 / 学习改进）；企业清单里它以 19 条完全覆盖、41 条部分覆盖落在编排·循环·审批·成本·审计五条线上；不包含的是平台化那一整套 —— 多租户 / RBAC / 集群节点 / 平台内 RAG / PII 脱敏 / 指标大盘 / SLA 合规 / SIEM，其中多租户、集群、SSO、节点管理是被书面明确排除的。**

---

## 附：核对命令（可复跑）

```bash
cd <repo>
# 1) PRD §9 各平面条目实数
grep -oE '^\| (WS|SYS|ORCH|LOOP|CTX|ASSET|GOV|SURF|LEARN)-[0-9]+' docs/prd/loopdesk-prd-v2.0.zh.md \
  | sed 's/^| //' | cut -d- -f1 | sort | uniq -c
grep -cE '^\| (WS|SYS|ORCH|LOOP|CTX|ASSET|GOV|SURF|LEARN)-[0-9]+' docs/prd/loopdesk-prd-v2.0.zh.md   # → 119

# 2) 企业级特性在 LoopDesk 文档/源码中的存在性
for kw in 多租户 RBAC 租户 SLA 集群 OIDC SAML 水印 病毒 GDPR 等保 SIEM 语义缓存 优先级队列; do
  printf '%s: ' "$kw"; grep -rl "$kw" docs --include="*.md" 2>/dev/null | wc -l
done

# 3) 网关 API 面
ls src/loopdesk/gateway/rpc_*.py | wc -l
```
