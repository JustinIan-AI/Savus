# 产品决策 — LoopDesk Desktop/Web/IM 产品边界与 v1.0 方向

> 状态：草案待评审
> 版本：v1.0
> 最后更新：2026-07-16
> 负责人：Product / Engineering
> 输入：`docs/prd/personal-loop-workspace.md`、`docs/prd/personal-loop-workspace.zh.md`、`docs/prd/personal-loop-workspace.en.md`、`docs/architecture/personal-loop-workspace.md`、`docs/decisions/product-strategy.md`、`docs/decisions/v0.2-channel-adapter.md`、`docs/releases/loopdesk-v0.1.md`、`docs/releases/loopdesk-v0.2.md`、`docs/research/competitive-intel.md`、`docs/research/competitive-intel-stablyai-orca.md`、`docs/research/competitive-intel-proma.md`

## 1. 决策背景

### 1.1 我们要解决什么问题
独立开发者已经在多个 coding agent、终端和工具之间来回切换，但当前的竞品方案都没有把三件事同时做好：

- 以本地可持久化状态为核心的跨工具 continuity；
- 明确的 loop engineering 方法；
- 可远程继续、但不抢主运行时地位的 control surface。

若继续把 LoopDesk 描述成“轻量 Web 产品”或“终端工具包装层”，都会导致两个后果：

- 桌面 runtime 的权威性被削弱；
- Web/IM 被误当成核心执行环境，而不是分发、查看、轻控和远程继续的辅助面。

### 1.2 为什么现在要定边界
v0.1 已经验证了本地 loop workspace、`LOOP-STATE.json`、MCP、memory、skills、worktree isolation、CLI 和本地 Web UI。
v0.2 已经验证了 IM channel adapter 可作为 disabled-by-default 的远程控制面。
接下来进入 v1.0 之前，需要把“主次关系”说清楚，避免后续产品、文档、营销、落地页继续分裂。

## 2. 现状盘点

### 2.1 v0.1 已交付
- 本地优先的 personal loop workspace；
- `LOOP-STATE.json` 作为 durable source of truth；
- MCP-first、ACP-second 的适配策略；
- Loop Engine：triage、maker/checker、run log、stop condition；
- 本地 CLI 和本地 Web UI；
- memory、skills、artifacts、worktree isolation；
- cost/safety controls：budget、approval、escalation、kill switch。

### 2.2 v0.2 已交付
- 四个 approved IM channel adapters：Slack、Feishu/Lark、DingTalk、WeCom；
- 统一 command surface：read-only  inspection 与 write-gated 控制；
- disabled-by-default、allowlist、audit log、rate limit、budget alert；
- channel 故障不破坏本地 workspace state；
- 本地 Web UI 可查看 channel 状态。

### 2.3 当前缺口
- 尚无明确产品级叙述，说明 Desktop / Web / IM 谁是主 runtime、谁是辅 surface；
- 若未来继续扩张，Web 与 IM 很容易被过度承诺为“完整替代桌面”；
- 远程继续任务的授权边界还不够锋利：IM 能看什么、能继续什么、什么必须回到桌面。

## 3. 可选方案

### 方案 A：Web-first，Desktop 为辅
- 把 Web 当成主入口和主控制面；
- Desktop 仅作为后台 runtime 或文件访问代理。

优点：
- 分发成本低，跨设备访问方便。

缺点：
- 本地文件、worktree、终端、agent  fidelity 难以完整迁移到 Web；
- 与当前已验证的本地 runtime 优势冲突；
- 会放大安全、权限、沙箱、大 artifact 传输问题；
- 与 LoopDesk 的“workspace-first、local-first”定位不符。

结论：**不建议**。

### 方案 B：IM-first 远程执行
- 把 IM 当成主要 loop 控制面；
- Desktop/Web 退化为辅助查看。

优点：
- 移动端场景直觉性强；
- 适合 notification-heavy 产品。

缺点：
- IM 天然不适合大 artifact、diff、replay、长链路审批；
- 会弱化本地 runtime 权威性；
- 容易演变成 chat-first 产品，而不是 loop-first 产品；
- 与 v0.2 的“IM 是 continuation surface”边界冲突。

结论：**不建议**。

### 方案 C：Desktop-first，Web/IM 为辅（推荐）
- Desktop 是主 runtime、主 authority、 richest inspection surface；
- Web 是分发、guided setup、inspection、approval、diagnostics surface；
- IM 是 disabled-by-default 的 remote continuation surface，用于选 workspace、看状态、approve/reject、继续已批准 bounded work。

优点：
- 保留本地 fidelity、安全边界和状态权威；
- Web 解决 onboarding 与远程查看；
- IM 解决轻量远程继续，不抢 runtime；
- 最贴合 v0.1/v0.2 已验证能力。

缺点：
- 需要持续维护三端状态一致；
- Desktop packaging/分发需要额外投入。

结论：**推荐并采纳**。

## 4. 决策内容

### 4.1 主叙事
LoopDesk 的产品主叙事从此刻起统一为：

- **Desktop-first personal loop workspace**；
- Web 为辅：分发、setup、inspection、approval、diagnostics；
- IM 为 continuation surface：选择 workspace、查看状态、批准/拒绝、继续已批准 bounded work。

### 4.2 产品边界
- Desktop 拥有 gateway、workspace、worktree、agent、run log、memory、skills、artifacts、cost/safety 的最高权威。
- Web 可查看和轻控，但不得复刻完整本地文件系统/终端语义来替代 Desktop。
- IM 默认关闭；开启后只能做轻量 continue/approve/notify；不能跑完整 loop、不能替代 Desktop runtime。

### 4.3 状态权威
- `LOOP-STATE.json` 继续是唯一 durable source of truth；
- Desktop、Web、IM 三端都从 workspace state 读取或回写；
- IM 不维护第二套任务状态或第二套 approval 真相。

### 4.4 集成策略保持不变
- MCP-first；
- ACP-second；
- tool-specific adapters；
- IM 不是新的集成层主入口，只是现有 safe workspace RPC 的远程别名入口。

## 5. 架构与数据流

### 5.1 三端职责

| 端 | 角色 | 核心职责 | 禁止事项 |
| --- | --- | --- | --- |
| Desktop | 主 runtime / 主控制面 | 安装、gateway、workspace、agent、worktree、审批、运行日志、成本、诊断、artifact 管理 | 不得把自己降级为纯后台服务 |
| Web | 分发 + 辅助控制面 | 下载、setup、workspace 查看、approval、诊断、replay、export | 不得替代本地终端/完整文件编辑 runtime |
| IM | 远程 continuation 面 | workspace 选择、状态查看、approve/reject、compact follow-up、cost alert | 不得支持完整 loop 执行、team room、rich media 主路径 |

### 5.2 信息流原则
- 任何远端操作最终都映射到本地 workspace RPC；
- IM/web 只携带 compact command/status/approval，不携带 workspace 权威；
- Desktop 是唯一可创建/修改/恢复本地 runtime 的入口；
- 若 Desktop 离线，Web/IM 只能查看最近已知状态或排队轻量决策，不能改变安全边界。

### 5.3 远程继续的授权模型
- 默认只能继续 **bounded + approved work**；
- discovery、triage、高风险 write、denylist 路径继续回 Desktop；
- IM/web 的 approve/reject 必须回写本地 run log 和 approval history；
- 任何绕过 Desktop 安全边界的继续都视为越权。

## 6. 与现有版本的兼容策略

### 6.1 v0.1 基线不变
- 本地 loop workspace、`LOOP-STATE.json`、memory、skills、artifacts、MCP、worktree isolation、CLI、本地 Web UI 继续作为底座；
- Desktop-first 是对 v0.1 的显性化，不是推翻。

### 6.2 v0.2 边界不变并收紧
- IM channel adapter 保持 disabled-by-default；
- IM 继续是 optional remote control/notification surface；
- 不允许因为 v1.0 产品叙事而把 IM 升级为“primary control surface”。

### 6.3 升级要求
- 所有 public docs、release notes、landing/setup 文案都必须同时说明：
  - Desktop 是主 runtime；
  - Web 是辅助 surface；
  - IM 是继续 surface，不是替代。

## 7. 落地影响

### 7.1 产品
- 产品路线图以 Desktop runtime packaging、Desktop UX、loop engineering 为主；
- Web 路线图优先 guided setup、inspection、approval、operator docs；
- IM 路线图优先 workspace selection、status、approve/reject、compact follow-up。

### 7.2 工程
- Gateway、Loop Engine、State Plane 的权威继续留在本地 runtime；
- Web 和 IM 通过 existing gateway RPC 控制，不新建第二套执行平面；
- Channel adapter 继续复用 v0.2 shared foundation，不引入 chat-first execution 语义。

### 7.3 运营
- Desktop install 包作为主要分发资产；
- Web 作为官网/下载/setup 主入口，但不暗示 SaaS runtime；
- IM onboarding 必须强调“先启用本地 Desktop runtime，再做远程继续”；
- 所有平台材料避免 team room、cloud-first、multi-user 叙事。

## 8. 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 用户仍把 Web/IM 当主产品 | 所有 docs、release notes、setup、UI 文案持续锁定 Desktop-first 叙事 |
| Desktop packaging 周期长 | Web 承担 onboarding/setup，但明确标注 full fidelity 需要 Desktop runtime |
| IM 继续膨胀成执行面 | disabled-by-default、allowlist、budget/kill-switch、command allowlist、audit log |
| 多端状态不一致 | 唯一 durable source of truth 仍是本地 `LOOP-STATE.json`；三端只读或回写 |
| 远端继续引发高风险执行 | 仅 approved bounded work 可继续；高风险工作继续 approval-gated + desktop-oriented |
| 文档口径分裂 | 本决策作为后续 PRD、release notes、docs、landing page 的上层边界依据 |

## 9. 验证方式

- 评审此决策后，以 `docs/prd/personal-loop-workspace-v1.0.zh.md` 和 `docs/prd/personal-loop-workspace.en.md` 作为 v1.0 正式 PRD 的上层边界依据；
- 更新 `docs/releases/loopdesk-v0.1.md`、`docs/releases/loopdesk-v0.2.md`、`docs/README.md`、`README.product.md` 的对外口径；
- 保留 v0.1 + v0.2 现有 acceptance checklist 作为兼容性证据；
- 参考 `docs/research/proma-inspiration.md` 时，只采纳 workspace-scoped Skills/MCP 与 bounded remote bot 信号，不复制 Chat/Agent shell 叙事；
- 新增 v1.0 的 launch criteria 时，必须检查：
  - Desktop 仍是默认安装和默认 runtime；
  - Web 不得替代本地 gateway authority；
  - IM 不得启用 unbounded execution 或 team semantics。

## 10. 未决问题

- Desktop 是 Electron shell，还是“本地 runtime + 系统 launcher”更合适？
- Web 是否需要 future 的多设备只读查看能力，以及本地 trust boundary 如何定义？
- IM 后续是否扩大平台集合；扩大前需要哪些 operator controls？
- Desktop 是否支持自动更新；若支持，更新边界和 rollback 流程如何定义？

## 11. 决策结论

**采纳方案 C：Desktop-first，Web 为辅，IM 为 continuation surface。**

桌面分发边界已在 v1.1 中锁定：

- 采用 **local runtime + system launcher**，不做 Electron shell。
- Desktop 负责启动本地 gateway、提供 inspection shortcut，并在升级/回滚时保留本地 workspace 数据。
- 所有 durable state 继续归属本地 workspace；Web/IM 不得替代本地 gateway authority。

LoopDesk 的后续产品、工程、文档、运营口径统一按以下优先级组织：

1. Desktop runtime 是第一优先级；
2. Web surface 是第二优先级；
3. IM surface 是第三优先级，且保持 optional、disabled-by-default、approval-gated、workspace-first。

官方 runtime 矩阵与能力边界见 `docs/decisions/runtime-matrix.md`；实现锚点见 `src/loopdesk/loop_workspace/runtime_matrix.py`。

此决策应作为后续 PRD、release notes、docs、landing page、marketing 文案的共同上层边界。

> 权威 PRD 锚点：`docs/prd/personal-loop-workspace-v1.0.zh.md`、`docs/prd/personal-loop-workspace.en.md`。

## 12. 批准

| Role | Name | Status |
| --- | --- | --- |
| Product | | Pending |
| Engineering | | Pending |
| Design | | Pending |
| QA | | Pending |
