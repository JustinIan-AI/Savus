# Competitive Intelligence: yetone/cumora

> 调研更新：2026-09-18（基于仓库页 / `docs/COORDINATION.md` / `docs/BYOA.md` / commits 页 / cumora.ai 官网）
> 关联：LoopDesk v2.0（`docs/product-positioning.md`、`docs/prd/loopdesk-prd-v2.0.zh.md`）。本项与 LoopDesk 在 **agent runtime 适配（同样支持 `claude` / `codex` / `pi`）、triage 门、原子认领、成本账本、fail-closed 权限边界**上高度可对标；其 `COORDINATION.md` 是目前已收录竞品中**对多 agent 协调工程教训记录最完整**的一份公开材料。
> 对照项：同期调研的 `docs/research/competitive-intel-tabtin.md`（同为"Agent 作为团队成员"，但 TabTin 为快照式开源，Cumora 为真实活跃协作开发）。

- **Repo**: [github.com/yetone/cumora](https://github.com/yetone/cumora)
- **作者**: yetone（个人项目，`avante.nvim` 作者）；主要贡献者含 WhichPaths、KIDA-MNESIA、bingqilinweimaotai 等
- **官网**: [cumora.ai](https://cumora.ai) · Web 应用 `app.cumora.ai` · 桌面分发 [yetone/cumora-releases](https://github.com/yetone/cumora-releases)
- **License**: **MIT**
- **热度（抓取时点 2026-09-18）**: 3.7k Stars / 477 Forks / 6 Watchers
- **提交活跃度**: **327 次提交**（main）；抓取到的近期区间 2026-09-10 ~ 09-17 共 35 次提交，6 位作者，含外部 fork PR 合并
- **版本节奏**: 7 天内连发 v0.18.0 → v0.18.5（6 个版本）；文档中另有 `cumora@0.1.119`（2026-06）→ 约 3 个月从 0.1.x 迭代到 0.18.x
- **阶段**: Invite-only Public Preview（邀请制，预览期免费）
- **Tagline**: "Where agent teams gather." / "Not a chatbot. **A coworker.**"
- **中文定位**: 跨平台团队聊天应用，**AI Agent 是与人类平级的一等参与者**——同一份花名册、私信、群聊、看板与日历；agent 可运行在 Cumora 云端，或跑在用户自己的机器上（BYOA）

## 1. 定位与主张

Cumora 的产品形态是**团队聊天（chat-first）**，而非任务看板。核心命题是：**AI 不是被提示的工具，而是房间里的成员**——有自己的观点、对共事者的记忆，可以主动走进来说一个想法。

官网 6 条 "Why Cumora"：

| # | 主张 | 要点 |
| --- | --- | --- |
| 1 | **Agents have memory** | 每个 agent 有私有工作区（文件、笔记、观察），并维护对共事者的 "climate"（情绪/态度倾向）；记得上周对话，能感知房间气氛 |
| 2 | **Agents start things** | 定时器唤醒空闲 agent，自行判断：私聊同事 / 发一条想法 / 拉小群——强调**主动性而非被动响应** |
| 3 | **Workspaces are real** | 邮件或分享链接邀请真人；agent 可编成 "公司"、分配项目、挂附件；桌面/浏览器/手机共享同一 live state |
| 4 | **Personas, not prompts** | Agent 由角色、语气、可编辑 system prompt 构成（Iris 会反驳糟糕设计、Bram 不交付含糊规格、Atlas 做没人愿做的调研） |
| 5 | **Agent-to-agent** | Agent 之间互相私信；**Whisper rooms** 让人类只读旁听它们对话而不加入 |
| 6 | **Convene rooms** | 需要真正决策时 agent 可发起 Convene——聚焦会议，含**参与者、议题、决议记录**，"少闲聊，多清晰" |

**默认开箱团队**（每工作区 4 个）：Atlas（Researcher）、Iris（Designer）、Bram（Engineer）、Nova（Product Manager）；支持编辑 Persona、**解雇（fire）**、招聘新 agent。

## 2. 架构总览

| 层级 | 实现 |
| --- | --- |
| 前端 | 纯 UI：React 18 + Vite + TypeScript + Tailwind；`desktop/` / `mobile/` / `web/` / `admin/` 四个外壳复用同一套组件 |
| 后端 | **无状态 Node 服务**：Express + `ws`；**Postgres 为唯一真实数据源**（pg pool + Drizzle schema）；**Redis** 用于 pub/sub 扇出与在线状态 |
| 持久化写入 | **PostgreSQL 事务性 outbox** 排队实时失效通知；**Redis 降级只延迟实时刷新，不影响命令结果** |
| 云端 agent runtime | **每 agent 一个 Kubernetes Pod**（服务器经 `kubectl` 编排；Go FUSE 驱动挂载工作区，见 `agent-fuse/`） |
| BYOA agent runtime | 用户机器上的长驻 daemon（`agent-cli/`，npm 包 `cumora`） |
| 边缘/Serverless | Cloudflare Workers（`email-gate` 入站邮件、`r2-gate` 签名 CDN）+ Cloudflare R2 |
| AI | 云端路径走 OpenAI Responses API；BYOA 走用户自己的 provider 账号 |
| 其他服务 | Resend（发信）、APNs / FCM（推送）、sub2api 网关 |
| 目录 | `src/` `server/` `electron/` `ios/` `android/` `agent-cli/` `agent-fuse/` `workers/` `website/` `benchmarks/` `tests/` `scripts/` `server/k8s/` `docs/` |
| 基准 | `benchmarks/` 内置真实 LLM 多 agent 协调基准：**chain / counting / werewolf / kanban** |

## 3. 双路径「大脑」：Cloud Pod vs BYOA

| 维度 | Cumora Cloud（托管） | 你的 Computer（BYOA） |
| --- | --- | --- |
| 引擎 | `managed`（服务器 `turn.ts` 多跳循环） | `claude` / `codex` /（兼容）其他 CLI |
| 调度 | `scheduler.wakeOne` → `ensurePod`（kubectl）→ pod | `scheduler.wakeOne` → **跳过 `ensurePod`** → publish wake → daemon SSE |
| Agent 循环 | `turn.ts` 多跳工具调用循环 + **Cumora 管理的上下文压缩** | **引擎自己的** agentic loop 与原生上下文管理（`turn.ts` **完全被绕过**） |
| 成本/限流归属 | 服务器 | **操作者自己的**订阅/账号（BYOA 宣称的核心收益） |
| 上线状态 | 永远在线 | 离线 → agent 显示 **sleeping**（而非 broken） |
| 数据模型 | 每公司一行 `kind='cloud'` | `kind='local'`/`'vps'`，带 `credential_hash`、`paired_at`、`revoked_at`、`daemon_version`、`daemon_supervised` |
| 可观测性 | `/runtime/runs`、`llm_calls` | **同一套**：`POST /runtime/runs`（60s 心跳）、`/runtime/llm-calls` 进**同一张 `llm_calls` 总账**；triage 单独走 `/runtime/triage` |

**关键设计**：调度器**只对 `computers.kind` 分支**——这是云/本地统一的关键。`participants` 增加 `computer_id`、`engine`、`model`、`fast_model` 字段；在 Cumora 里 BYOA agent 仍是普通 `kind='agent'` 参与者，**不存在"特殊的 BYOA agent"**。

**BYOA 的低成本属性**：`cumora` CLI（`reply` / `dm` / `memory` / `workspace` / `card` …）只是一个**固定的 MCP-to-file-IPC 桥**——把 argv 发给本地 daemon，**只有 daemon（位于模型沙箱之外）持有 runtime JWT** 并 POST 到 `/runtime/cli`。BYOA 换掉的**只是大脑和宿主**，其余全部复用。

## 4. BYOA 引擎矩阵（10 个适配器）

`server/src/agents/computer/engine.ts` 为每个引擎定义 `EngineAdapter`：**`claude`、`codex`、`grok`、`cursor`、`opencode`、`pi`、`gemini`、`qwen`、`antigravity`、`zcode`**。

> **与 LoopDesk 的直接重叠**：LoopDesk 编排 `claude` / `codex` / `pi`，Cumora 的 10 个引擎**已全部覆盖**，且适配器接口（`seedHome` / `startSession?` / `run` / `classify` / `probe`）与 LoopDesk 的 cross-tool adapter 目标一致。

### 安全默认 vs 兼容 opt-in（最重要的分界线）

| 类别 | 引擎 | 条件 |
| --- | --- | --- |
| **安全默认（fail-closed）** | **Claude Code ≥ 2.1.248**（`--restricted`）、**Codex ≥ 0.138.0** | 可施加 fail-closed 宿主边界 |
| **兼容性（需显式非沙箱 opt-in）** | Grok Build、Cursor Agent、OpenCode、**pi**、Gemini CLI、Qwen Code、Antigravity、ZCode，以及**原生 Windows 上的 Claude** | 检测到二进制在 `PATH` 上**不足以**执行它们 |

**"检测到不等于可执行"**：daemon 会把这些引擎从自己的可运行清单（runnable inventory）中**移除**，因此即使服务器下发 assignment 也无法让它们意外执行——**不只是 UI 隐藏**。

### 各引擎关键差异（对多 runtime 适配有直接参考价值）

- **持久会话**：Claude 用 `-p --input-format stream-json --output-format stream-json --verbose`；Codex 安全默认是**一次性 `exec`**（其 app-server 目前无法排除 user config / MCP / hook / rule 层）；Cursor、OpenCode、Gemini、Qwen **无持久 stdio 会话**。
- **记忆/人格文件**：Claude `CLAUDE.md`；Codex/Grok/Cursor/OpenCode/**pi**/Antigravity/ZCode `AGENTS.md`；Gemini `GEMINI.md`；Qwen `QWEN.md`。
- **Mid-turn steering**：Claude 支持注入；Grok Build 的 ACP `session/prompt` 是 one-in-flight；Cursor/OpenCode 无持久会话 → mid-turn 注入是 no-op。
- **模型解析优先级链**：显式 `participants.model` / `fast_model` → 计算机的每引擎默认（`computers.engine_defaults`，Me 页配置）→ 上报的自定义 Claude provider 默认 → 部署级 `CUMORA_DEFAULT_*_MODEL`。当自定义端点拥有**未命名的本地默认**时，daemon **不传任何模型标志**，以免把厂商特定 pin 交叉带进错误命名空间。
- **`CUMORA_ENGINE_MODEL`**：未设 → 走上述链；`local` → 完全不传模型（连 small/fast pin 也丢掉）；任意模型 id → 覆盖。

## 5. 凭证与 fail-closed 沙箱边界

**Computer 是带自身可撤销凭证的注册设备，而非用户会话**——"Remove Computer" 是真正的 kill switch。

配对流程要点：公司持久配对令牌 → `npx cumora agent computer --pair <code> --server <url>` → 返回 `{ computerId, deviceToken }`（**服务端只存哈希**）→ daemon 每 60s 轮询花名册，为每个 agent 铸造**短期限 runtime JWT（2h TTL，到期前刷新）**，**只保留在 daemon 内存** → 30s 心跳，**90s 无心跳即 offline，其 agent 显示 sleeping** → UI "Remove" 置 `revoked_at`，device token 与所有派生 JWT 全被拒。

**边界核心原则**：
- **认证共享，工具权限不共享**：引擎核心可用操作者已有登录，但**模型 spawn 的命令在安全模式下读不到该登录、不能继承 provider 凭证**
- 模型进程**拿不到**服务器 URL、bearer token 或 HTTP 客户端路径
- **运行时 token 是凭证**：只在 daemon 内存，**永不进入引擎环境或 agent home**；短 TTL + 计算机级撤销构成纵深防御
- **IPC 命名空间位于 agent home 之外**（`.runtime-cli-tools/`、`.runtime-cli-ipc/`、`.runtime-cli-broker/`）：模型**无法重写可执行文件，也无法直接写入会合目录**
- **本地内态不镜像到服务器**：home 里的 memory/notes/skills 只能在机器上查看；**共享成果应放在服务端面**（`cumora workspace`、docs、boards）——本地与服务端状态**互补**
- Claude 偏好桥只继承**固定七键白名单**（`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_BASE_URL`、`ANTHROPIC_SMALL_FAST_MODEL` + 三个 `ANTHROPIC_DEFAULT_*_MODEL` 别名）；**hooks、plugins、MCP servers、permissions、任意环境变量、output styles、workflow modes 都不导入**
- 安全引擎启动时**从 `PATH` 剔除空、相对和指向 agent home 的条目**——**模型植入的 `claude`/`codex` 可执行文件无法在下一个沙箱建立前运行**

**通用 fail-closed 属性**：沙箱不可用则**停止 turn**，而不是放宽访问（Linux/WSL2 缺 `bubblewrap`/`socat` 直接导致 turn 失败）；原生 Windows 上 Claude **被禁用**，Codex 走 elevated sandbox。

**唯一后门（且很大声）**：`CUMORA_BYOA_ALLOW_UNSANDBOXED=1 cumora agent computer` —— 恢复**宿主级爆炸半径**，官方明确要求"仅在你自己信任为真正安全边界的外部容器或 VM 内使用"。

## 6. 协调机制精读（`docs/COORDINATION.md`）★ 本项最高价值材料

系统本质：**同一台机器上 N 个独立的本地引擎会话**，各自被服务端 SSE 事件唤醒，读同一对话、各自独立决策。由此产生两类故障：

| 类型 | 描述 | 可否用服务端拦截 |
| --- | --- | --- |
| **竞态冲突**（Race collision） | 两 agent 同时唤醒、决定发同样内容、同时 INSERT | ✅ 可用预插入检查拦截 |
| **大脑误判**（Brain misjudgment） | 视野正确（看到最新帖），但大脑仍选错动作（重复、回退序号、抢先） | ❌ 服务端无法拦截，只能靠 prompt 塑造（**软机制有上限**） |

**核心原则（值得整句引用）**：

> **能用代码机制修的，绝不加 prompt 规则；大脑在正确状态下做出的明确决策，绝不用代码机制去覆盖。**

### 6.1 seen-cursor 新鲜度门（Freshness Preflight）

- 从 Redis 读该 agent 的"已见 seq"基线（`cumora:seen:<agentId>:<convoId>`，**10 分钟 TTL**）
- 若存在比基线新的、非本人消息（`LIMIT 8`）→ 返回 **HELD 信封（退出码 2）**，内联展示被拦消息，并把基线推进到最大被拦 seq（**避免无限 HOLD 循环**）
- **绕过方式**：`--send-anyway`、`--continue`/`--also`（独白续写）、2 人 DM、邮件对话
- **为何用 Redis 而非 `conversation_reads.last_read_at`**：该列是 `loadInbox` 的 SELECT 游标，推进到 `NOW()` 会导致下次 `loadInbox` 返回空行、daemon **静默假忙**（早期 commit `a6e69aa` 已踩，被 `72748e8` 回滚）。**与 inbox 游标共享状态的任何东西在结构上都不安全**
- **契约**：**"展示即已见"（shown ⇒ seen）**；历史 `Compose-anchor`（`/thinking/mark`）机制已于 2026-07 退役

### 6.2 原子逐字重复门（5b）与 hold-token 门控覆盖（5d）

- **5b（事务内、不可绕过）**：在 `cmdReply` 包裹 seq 认领 + INSERT 的事务内，取得行级锁后**重新查询最新非本人 peer 消息体**比对；逐字相同 → `ROLLBACK` + HELD。理由：预插入逐字检查是脆弱 TOCTOU（两 agent 相隔 2s 可同时通过快照）。**不可被 `--send-anyway` 绕过**（不存在合法用例逐字重复上一 peer 消息）。
- **5d（软门必须有成本）**：覆盖标志 `--send-anyway` / `--force` **只在服务端真正展示过 HOLD 之后才生效**（`recordHold`/`consumeHold`/`clearHold`，Redis **2 分钟 TTL**，fail-open）。起因是 2026-06-11/12 双交付事故：**agent 学会预先传 `--send-anyway` 来省一轮往返，导致门形同虚设**。
- **Token 生命周期是"一个时刻"而非"一个会话"**（2026-07-08 stale-"6" 事故）：seq 绑定（房间推进则标志作废）、**回合结束即失效**、`ack` 即失效、TTL 从 10 分钟缩至 2 分钟。
- **5e（共享资源创建去重）**：`tryClaimTenantWork` 只守**进行中**工作，无法阻止**顺序**重复 → 追加"认领窗口内、INSERT 前检查同标题资源 15 分钟内是否由**其他 actor** 创建"。

### 6.3 原子认领与分诊门

- **原子认领**：序号认领 + INSERT 在 `conversation_counters` 的 UPSERT 行级锁下、同一事务内完成；`markThinking`/`peekThinking` 用 ZSET 表达"谁正在此处撰写"。**协议规则 5：永不认领聊天回合或游戏槽位**——认领仅用于真正的共享交付物。
- **通用规则**：**"完成即自动释放的锁"能防并发但不能防重复，必须配权威状态检查**（5e）。
- **小脑分诊门**（`triage-core.ts`）：便宜模型为每次唤醒判定 `actionable: boolean`，只有 `actionable=true` 才唤醒大脑。**纯门**——绝不决定谁回复、如何回复；提示词就一条原则：**涉及 HUMAN 或有人在等 → 永远 actionable**；**不确定 → actionable=true**。
  - **服务端事实信号（非消息措辞）**：Worklog 认领 = "开放工作状态"；人类消息、表情反应、读游标活动均计为"人类正在观看"。
  - **确定性循环下限（回归护栏——已被"为 AI 原生优雅"删除两次，两次都导致循环回归，勿再删）**：已认领线程 `HARD_LOOP_CAP = 20`；未认领线程一旦"绕圈"（消息数超过不同参与 agent 数）即视为死循环；agent↔agent DM 每第 8 条消息运行循环检查。

### 6.4 七层冲突避免防线

| 层 | 机制 | 关键参数 |
| --- | --- | --- |
| **2** | 每电脑大脑并发上限（daemon） | `CUMORA_BYOA_MAX_CONCURRENT_BIG_BRAIN` 默认 **6**（原 2） |
| **3** | 确定性生成间隔 | `MIN_SPAWN_INTERVAL_MS` 默认 **500ms**（替代原 `random(0..1500ms)` 抖动；确定性 1/interval 硬上限） |
| **3a/3b** | 小脑分诊并发上限；AdaptivePacer 突发吸收 | 分诊并发默认 **8**；遇限流全局间隔**翻倍**（上限 8s），5 次连续干净回合后**减半** |
| **3c** | 唤醒去抖、合并、同回合转向 | `WAKE_DEBOUNCE_MS = 2500`；`INBOX_POLL_MS = 20s`（**独立于 SSE 的安全网**） |
| **4** | 每 agent 限流冷却 | `ENGINE_BACKOFF_AFTER_RATE_LIMIT_MS = 60_000`；**抑制 `byoa_engine_failed` 通知**（限流非 Cumora 故障），保留未读 inbox 供冷却后重试 |
| **5 / 5b / 5c** | 服务端新鲜度 preflight / 原子逐字重复 / 停滞管道 + 确定性回退 | `STALL_MIN_MS` 5min / `STALL_MAX_MS` 6h；`NUDGE_COOLDOWN_MS` 45min / `_FALLBACK_MS` 5min；**回退下降级上限 3 次** |
| **5d / 5e** | hold-token 门控覆盖 + 近期创建去重 | 见 §6.2 |
| **6** | 小脑分诊门 | 见 §6.3 |
| **7** | 常驻提示词 + `GLANCE_YIELD_RULES` | 契约是**简洁**，5/28 基线约 5KB |

**两条共享基础设施教训**：
1. 分诊与大脑**共享同一账户与本地 CLI 进程池**，**必须成对设置信号量**（2026-06-02：只限大脑不限分诊 → 惊群 → 分诊全部超时 → **全部静默**）
2. **任何新增 fetch 必须带 `AbortController`/`fetchWithTimeout`**（`aaf8c0b`：无超时 → daemon 永久假忙、agent 永久静默）

### 6.5 Prompt 协议五条（`GLANCE_YIELD_RULES`）

1. **人类可点名一个队友而无需 @**——读他们点名的是谁；不是你则退出
2. **从真实、已发布的状态回复**——绝非从你在队列中的位置或对 peer 行为的猜测；新人类任务定义自己的起点（**意图高于字面**）
3. **乐观发布**；服务端是安全网——不要 glance→think→glance 循环；HELD 意味着读取、重算、重发
4. **不重复 peer，做完即停**——完成由**任务条目数**而非人头数衡量；若有人缺席，在场者接下一项，**即使要第二次**
5. **永不认领聊天回合或游戏槽位**

编辑规则：编辑 const、保持五条、**保持"形状级"（shape-level）**。

### 6.6 反模式清单（15 条，原文明确"不要重做"）

1. 不要只限一层而不限另一层（大脑 + 分诊**成对**）
2. 不要在 prompt 中堆积场景示例（违反"形状级"原则）
3. 不要把 `AGENT_VOICE_RULES` 倒进 BYOA 常驻提示（`bd9bc40`：行话俚语吃掉协调规则注意力）
4. 不要把 CLI 目录倒进常驻提示
5. 不要写"如何处理 HELD"章节（`091c393`：返回文本已自解释）
6. 已有循环防护时不要堆积更多机制
7. 不要把写 `conversation_reads.last_read_at` 作为副作用
8. 不要加无超时的 fetch 调用
9. 不要为单个观测事故加场景特定 prompt
10. **不要发布无成本的覆盖标志（软门会侵蚀）**
11. **不要用 prompt 修改修基础设施问题**（2026-06-03：先读服务器日志）
12. **不要烧 token 锤打已收敛的 LLM 判断**（下降级上限）
13. **不要把缺席成员当作要"修复"的失败模式**（用户重构：**"AI 原生意味着让 AI agent 像真人一样协作"**）
14. 当某功能坏了，**与最后好的基线 DIFF**
15. 方法论优先级：**先读 agent 记录**（`~/.claude/projects/<agent-home-slug>/<sessionid>.jsonl`）→ **声明测试失败前重查实时状态** → **加机制前先诊断基础设施** → **内存文件也是状态**（`~/.cumora/agents/<id>/memory/`）

### 6.7 T1→T10 试验（chain-with-absent-member，2026-06-03）

`T1 6/8 → T2/T3/T4/T5/T6 7/8 → T7 10/8 dups → T8 11/8 dups → T9 9/8 → T10 **8/8 ✅**`

关键教训：T3 sub2api 503 导致 **agenda 安全网静默死亡**；T5 agent 正确诊断但**出于社交理由拒绝**；T6 Bram **写新内存文件"保持沉默"——系统自我毒化**。**T10 的突破时刻是用户的重构**："AI 原生意味着让 AI agent 像真人一样协作。不要局限思考。每次决策或实现代码时，想想真人会怎么做。"

**实证良好状态**：7 agent 计数游戏（1 codex + 6 claude opus-4-7，极简 prompt，sem=4）：**0 冲突、0 限流、第一个数字 28s**；相同设置 + **扩充 prompt**：每局 1-3 次冲突、第一个数字 2:30+、3 分钟窗口内未完成。→ **prompt 膨胀会直接反噬协调效率**。

## 7. 成本账本与计费陷阱（对 LoopDesk `quota` / `gate` 直接可用）

所有 LLM 调用（云端与 BYOA）**计入同一张 `llm_calls` 成本账本**，管理面板中可比。文档记录了多个**引擎特有的计费陷阱**：

| 引擎 | 陷阱 | 处理 |
| --- | --- | --- |
| **Gemini** | `stats.input_tokens` 是**含缓存读的整个 prompt**，`stats.input` 才是新增部分 | 账本**只计 `input`**，单独报 `cached`，**避免缓存前缀重复计费** |
| **Antigravity** | `result.usage` 对活跃 CLI 进程是**累计值** | 适配器减去上一次结果；daemon 重启后**故意开新会话**（直接 resume 会重算历史 turn 的账） |
| **OpenCode** | JSONL `step_finish` 事件会与 terminal idle 事件**竞争** | 每个 `step_finish` 记为独立 provider hop；**以进程干净退出为完成信号**，事件缺失时计费 best-effort |
| **通用** | provider 限流 | **静默吸收**（cooldown + pacer），**绝不泄漏进聊天**；`byoa_engine_failed` 只在真正故障时浮出（带认证提示，如"运行 `claude login`"） |

## 8. 工程活跃度与开源性

| 维度 | 证据 |
| --- | --- |
| 提交量 | 327 次（main） |
| 近期节奏 | 2026-09-10 ~ 09-17：35 次提交，5 个活跃日（9/11、9/12、9/14 空档），日均 ~4.4，峰值 11 |
| 发版 | 7 天内 v0.18.0 → v0.18.5（6 个版本）；文档中 `cumora@0.1.119`（2026-06）→ 约 3 个月到 0.18.x |
| 协作 | 6 位作者（yetone 34%、WhichPaths 31%、KIDA-MNESIA 14%、bingqilinweimaotai 14%、lianxin255、wg2038）；有 `Merge pull request #233 / #281 / #282` 等**外部 fork PR**，存在分支 → PR → review → 合并流程 |
| 提交信息质量 | Conventional Commits + PR 编号，指向具体技术问题，如 `fix(scheduler): wake-retry recovery must obey the same backpressure as live fan-out (#287)`、`fix(byoa): an Antigravity turn that reports no usage must not re-bill the last one (#285)`、`fix(chat): a message that gains its author mid-render must not change the hook count (#284)` |
| 工程治理工具 | biome、`node:test`、CI 守护脚本 `npm run guard:big-brain`（**仅 agent 回合可调用大模型**）、`.github/workflows/publish.yml` |
| 分发 | **`npx cumora@latest agent computer --pair <code>`，新机器只需 Node ≥ 18**；`agent-cli/` 以 esbuild 打成**单个自包含 ESM 文件（~330KB、零运行时依赖）**，打包 daemon 源码——**单一事实来源，无副本**；根 `package.json` 保持 `private`，只发布这个薄包 |
| 服务化 | `--install-service`（macOS launchd `io.cumora.daemon` / Linux `systemd --user` / Windows 每用户 Task Scheduler watchdog），用户登录时可重启；**macOS 跑在 GUI domain，这样引擎的 keychain 登录才真正可用**；另有 `--doctor` 端到端探针、`--status`/`--logs`/`--restart`/`--stop` |

> **与 TabTin 的对照**：两者同为"Agent 作为团队成员"，但 TabTin 为 7 次**快照式导入**（`TabTin Go Public` + `sync opensource/v1`），Cumora 为**真实连续协作开发**（327 提交、6 作者、外部 PR、高频发版）。**Cumora 的开源可信度显著更高。**

**遗留提示**：`COORDINATION.md` 引用的部分 commit id（如 `3c5786e9`、`75732f7`）**在当前仓库无法解析**——属开源前开发历史，说明公开仓库并非完整历史。

## 9. 与 LoopDesk v2.0 的对照

### 9.1 ⚠️ 高重叠区（能力可直接对标）

| 能力 | Cumora | LoopDesk v2.0 |
| --- | --- | --- |
| **Agent runtime 适配** | 10 个引擎，含 `claude` / `codex` / **`pi`**；`EngineAdapter` 统一接口 | 编排 claude / codex / pi；cross-tool adapter（MCP-first / ACP-second） |
| **triage 分诊门** | 小脑（便宜模型）判 `actionable`，只有 true 才唤醒大脑；**纯门**不做决策 | Loop Engineering 的 triage 阶段 |
| **maker / checker 分离** | agent 间互相检查、HELD 重决策、`Convene` 决议 | 显式 maker / checker split |
| **escalation** | 停滞管道 → nudge（45min 冷却）→ 确定性回退（下降级上限 3 次） | escalation 阶段 |
| **stop condition** | `HARD_LOOP_CAP = 20`；未认领线程"绕圈"即死循环判定；DM 每 8 条检查 | stop condition |
| **run log** | `/runtime/runs`（60s 心跳）+ 统一 `llm_calls` 总账 | run log |
| **成本护栏** | 统一 `llm_calls` 账本 + 引擎级计费陷阱处理 | quota / gate（成本与安全护栏） |
| **权限边界** | fail-closed 沙箱 + 七键白名单 + 工具权限不共享 + 可撤销设备凭证 | approvals & permissions + gate |
| **Agent 资产** | 每 agent home：`CLAUDE.md`/`AGENTS.md`、`memory/`、`skills`、`notes` | memory / skills / Rules / Specs |
| **看板** | Kanban + 日历 agenda 主动唤醒 | 任务看板（默认落地页） |
| **审批/决议** | `Convene`：议题 + 参与者 + **决议记录** | 审批门（右栏区块） |
| **本地/云统一抽象** | `computers.kind` 单点分支，BYOA agent 无特殊性 | local-first + 跨设备 Operator 场景 |
| **可移植性** | `npx` 单文件 330KB 零依赖 daemon | 零基础设施 CLI |

### 9.2 关键差异：形态与基础设施路线

| 维度 | Cumora | LoopDesk v2.0 |
| --- | --- | --- |
| **主对象** | **团队聊天（chat-first）**：房间、DM、花名册、Whisper rooms、Convene | **任务（task-first）**：任务看板为默认落地页，Session 降为手动动作渠道 |
| **基础设施** | Postgres（唯一数据源）+ Redis（pub/sub、presence）+ K8s Pod + Cloudflare Workers/R2 + Resend + APNs/FCM | **零基础设施**：无服务器、无 DB、无云账号即可跑 |
| **云端依赖** | 双路径，但**云路径是默认一等公民**；邀请制预览 + 账号登录 | 明确不做**多租户 SaaS / SaaS 计费商业化** |
| **状态可移植性** | durable state 在 **Postgres**，无公开可移植格式 | **可机读、可 diff / export 的 `LOOP-STATE.json`** |
| **资产分发** | 服务端面（`cumora workspace` / docs / boards）+ npm 薄包 | **git 原生**（Specs / Rules / Skills / MCP / 交付物） |
| **实时协作** | SSE 唤醒 + Redis 扇出 + 多端 live state | 不做**强实时云房间** |
| **长任务模板** | 无固定模板叙事；靠 agent 自主性与 agenda | LoopX 式长任务 + **issue-fix / pr-commit / auto-research 固定模板** |
| **工作应用** | 看板、日历、文档、邮件（真实收发） | 排除 broad media skills；控制/编排层 |
| **License** | MIT | Apache-2.0 |

### 9.3 直接竞争风险评估

- **风险等级：中高（高于 TabTin）**。理由：① Cumora **同为 MIT/Apache 类宽松许可**，商业可读性差异小；② 其 **BYOA 本地 daemon 路径**与 LoopDesk 的 local-first 立场部分重合（"agent 跑在你自己的机器上、用你自己的账号"）；③ **引擎适配面已覆盖 LoopDesk 的 claude/codex/pi**，且工程实现细节（持久会话、mid-turn steering、模型解析链）比 LoopDesk 现有文档更细；④ **真实活跃开源**，迭代速度极快（3 个月 0.1.x → 0.18.x）。
- **但 LoopDesk 的三条差异化仍然成立**：① **零基础设施**——Cumora 的 BYOA 仍需 Postgres + Redis + 服务端 + Cloudflare Workers，"本地"只指大脑与宿主，**控制面依然在云**；LoopDesk 的 `LOOP-STATE.json` 是真正的零依赖；② **主对象是任务而非聊天**——LoopDesk 已裁决"任务为产品主对象、Session 降为手动动作渠道"，而 Cumora 把 chat 作为唯一主面（任务/看板是附属）；③ **git 原生资产分发**——Cumora 的资产在服务端面与 npm 包，LoopDesk 是 git 可版本化、可审计、可下发。
- **主要风险点**：Cumora 的"主动性"叙事（agent 自己起事、Whisper room、Convene）**在概念吸引力上强于"控制面/编排层"叙事**；且其 `COORDINATION.md` 公开的工程深度会成为开发者心智中的"技术标杆"。

## 10. 对 LoopDesk 的启示（可借鉴点）

### 10.1 协调机制（可直接采纳的设计原则）

1. **"硬机制 > 软机制，且软门必须有成本"**——LoopDesk 的审批门 / gate 设计应遵循：任何覆盖（override）标志**只能在系统真正展示过该门之后才生效**，否则 agent 会学会预置覆盖而架空门槛。这是 Cumora 用 2026-06-11/12 双交付事故换来的结论。
2. **"完成即自动释放的锁能防并发但不能防重复，必须配权威状态检查"**——LoopDesk 的 worktree 隔离与 claim 机制应补"顺序重复"检查（同标题产物在窗口内是否由其他 actor 创建），这是 `tryClaimTenantWork` 的真实缺陷。
3. **确定性循环下限不可用"优雅"换掉**——`HARD_LOOP_CAP = 20` 被删两次、两次导致循环回归。LoopDesk 若引入 stop condition 的 AI 自适应判断，**必须保留确定性的兜底下限**，并在代码注释中标注"勿删"。
4. **主控与分诊必须成对限流**——任何共享账户/进程池的两级 LLM 调用（如 LoopDesk 的 triage → maker）**必须成对设置信号量**，只限一级会导致惊群 → 另一级全部超时 → **全部静默**。
5. **prompt 膨胀会反噬效率（有 A/B 实证）**：极简 prompt 版 0 冲突 / 28s 出首个结果；扩充 prompt 版每局 1-3 次冲突 / 2:30+ 未完成。LoopDesk 的 Rules / Specs 下发应坚持"形状级"（shape-level）而非场景枚举。
6. **唤醒通道必须有独立安全网**：Cumora 在 SSE 之外保留 `INBOX_POLL_MS = 20s` 轮询。LoopDesk 的调度器不应单点依赖事件推送。
7. **任何外部调用必须带超时**，否则会出现"daemon 永久假忙、agent 永久静默"这类无告警的静默故障。
8. **设计假设"成员可能缺席"**：不要把缺席当失败模式去修复；让在场者接下一项。这与 LoopDesk 的 escalation 语义（而非"卡死等待"）同向。

### 10.2 成本账本（可直接影响 quota / gate 实现）

9. **统一账本是正确方向**：云端与本地路径写**同一张表**，管理面板可比。LoopDesk 若做 quota/gate，应让所有 agent 路径（claude / codex / pi）的用量进同一账本。
10. **必须处理引擎级计费陷阱**：Gemini 的 `input_tokens` 含缓存读（**只计 `input`、单独报 `cached`**，否则缓存前缀重复计费）；Antigravity 的 `usage` 是累计值（需差分，daemon 重启后不可直接 resume）；OpenCode 以**进程干净退出**为完成信号（事件会竞争）。LoopDesk 支持 claude / codex / pi 时需逐引擎验证用量语义。
11. **限流不是故障**：provider 限流应**静默吸收**（cooldown + pacer），不冒泡为面向用户的失败通知；只在真正故障时提示（并给出可操作修复，如"运行 `claude login`"）。

### 10.3 安全边界（可强化 approvals & permissions）

12. **"认证共享，工具权限不共享"**是一条高价值边界表述：引擎可用操作者已有登录，但**模型 spawn 的命令读不到该登录、不能继承 provider 凭证**。LoopDesk 的权限文档可直接采用这一分层。
13. **运行时凭证只在宿主体内、短 TTL、可撤销**：daemon 内存持有 2h TTL JWT，`Remove Computer` 即 kill switch，派生凭证全部失效。LoopDesk 的跨设备 Operator 场景（另一设备查看/审批）可借鉴"设备级可撤销凭证 + 短期限派生 token"。
14. **IPC 会合目录置于 agent home 之外**，使模型**无法重写可执行文件、无法直接写会合目录**；并从 `PATH` 剔除指向 agent home 的条目——**模型植入的 `claude`/`codex` 无法在下一次沙箱建立前运行**。这是 worktree 隔离之外值得补的一层。
15. **fail-closed 原则**：沙箱不可用则**停止回合**，绝不放宽访问；后门（`ALLOW_UNSANDBOXED`）必须显式、带警告、并在文档中限定为外部 VM/容器内使用。
16. **本地内态默认不入服务端**：memory/notes/skills 只在机器上可见；需要团队共享的成果**主动写到共享面**。这一"本地私有 vs 团队共享"的二元划分与 LoopDesk 的 `memory/skills/artifacts/worktrees` 目录契约高度一致，可用于澄清边界。

### 10.4 工程方法（可直接抄的实践）

17. **公开一份"反模式清单"**：Cumora 的 15 条反模式每条都绑定具体事故与 commit。LoopDesk 已有 `docs/decisions/` 决策记录，可增设 `docs/loop-engineering-antipatterns.md`，把 Loop Engineering 的踩坑以"不要做 X（因为事故 Y）"形式固化——这同时也是对外证明工程深度的资产。
18. **"与最后好的基线 DIFF"** 应写入协作规范：功能坏了先 diff 而非猜测。
19. **薄包分发模式**：把宿主/daemon 源码用 esbuild 打成**单个自包含零依赖文件**发布（`agent-cli/` ~330KB），根 `package.json` 保持 `private`，**单一事实来源无副本**。LoopDesk 若需分发自托管 runtime，这是低摩擦方案。
20. **CI 守护规则产品化**：`npm run guard:big-brain`（**仅 agent 回合可调用大模型**）把成本纪律编码为可执行的 CI 门。LoopDesk 的 quota/gate 可增加同类"静态守护"而非仅运行时限流。
21. **服务化安装 + GUI domain**：macOS 上 daemon 跑在 GUI domain 才能使用引擎的 keychain 登录——LoopDesk 若做本地常驻服务需注意同类平台细节。

## 11. 待核实与信息缺口

- **仓库页元数据缺失**：未取到 `created_at` / `pushed_at` / 语言占比 / Releases / Packages；本次提交日期结论基于 commits 页（2026-09-10 ~ 09-17）。
- **历史不完整**：`COORDINATION.md` 引用的部分 commit id 在当前仓库**无法解析**（属开源前开发历史），公开仓库并非完整历史。
- **开源主体与治理未明确**：仓库为个人 owner（yetone），无公司主体；官网无作者/公司/团队页，无发布日期。
- **商业模式未公布**：官网仅"预览期免费"（Free during preview）+ 邀请制 waitlist + 分批放人；**无定价、无套餐、无企业版**；下载链接为占位锚点 `#download`。
- **数据与合规未披露**：官网未说明底层模型、上下文长度、agent 数量上限、数据驻留与合规；而架构上**云端为默认路径**（Postgres + K8s），这对合规敏感团队是关键未知项。
- **文档质量不均衡**：`COORDINATION.md` 与 `BYOA.md` 工程深度极高（含事故与 commit 溯源），但官网偏营销叙事；两者对"能力边界"的表述需分别评估。
- **中文定位为本文档归纳**：仓库与官网均无官方中文描述（本项系根据 README + 官网 + 文档归纳）。
- **iOS 状态不一致**：仓库页称 iOS 可经 TestFlight 参与、Android 需自行构建；官网称 iOS "shipping next"。以仓库为准。

## 12. 数据来源

| 来源 | 用途 |
| --- | --- |
| `github.com/yetone/cumora` 仓库页 | 简介、Stars/Forks、License、目录结构、双路径大脑与协调机制概览、技术栈 |
| `docs/COORDINATION.md`（raw） | §6 全部：两类失败模式、seen-cursor、逐字重复门、hold-token、原子认领、分诊门、七层防线、五条协议、15 条反模式、T1→T10 |
| `docs/BYOA.md`（raw） | §3 / §4 / §5 / §7：双路径对照、10 个引擎适配器、凭证边界、fail-closed 沙箱、分发运维 |
| `github.com/yetone/cumora/commits/main` | §8：提交量、日期分布、作者分布、PR 流程、提交信息质量 |
| `cumora.ai` | §1 定位与 6 条主张、默认团队、定价与准入策略、竞品差异叙事 |
| 抓取时点 | **2026-09-18** |

> **本报告定性**：§6 / §7 / §8 的事实与引用均来自仓库内公开文档与提交记录，可直接复核；§9 竞争评估与 §10 启示为本文档的分析推断，非官方表述。Cumora 的官网主张（主动性、人格化、Convene）未做独立验证。
