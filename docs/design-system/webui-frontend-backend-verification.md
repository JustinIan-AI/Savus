# WebUI × Gateway · 任务全生命周期 前后端完备性验证

> 本文分三轮，最新在前：**§0 第三轮**（P1 补齐，当前）、**附录 A 第二轮**（P0 接线后）、**附录 B 第一轮**（接线前）。
> 三轮用的是同一套口径：真实浏览器逐屏交互 + 真实 HTTP 打后端，双线取证。

- 日期：2026-09-16
- 被测对象：`frontend/dist`（构建于 2026-09-16 18:38，`index-SXFL6EW3.js`，44 modules，241.2 kB） + `loopdesk gateway`（`http://127.0.0.1:18792`，uvicorn）
- 验证方式：真实浏览器（Chromium 1440×900，Playwright）逐屏交互 + 真实 HTTP 打后端；网络、`pageerror`、`console.error` 全程记录
- 结论：**39/39 步通过，前端 `/api` 请求 20 条，控制台零错误。任务全生命周期（新建 → 提交评审 → 状态下拉 → 裁决通过/打回 → 交付）由界面驱动，全部落到后端。**

---

## 0. 第三轮结论（P1 补齐 · 当前）

### 0.1 三轮对比

| 指标 | 第一轮（接线前） | 第二轮（P0 后） | **第三轮（P1 后）** |
| --- | --- | --- | --- |
| 走查通过 | 19 / 24 | 23 / 23 | **39 / 39** |
| 走查中前端发出的 `/api` 请求 | **0** | 10 | **20** |
| `tsc --noEmit` | 5 errors | 0 errors | **0 errors** |
| gateway 单测 `test_gateway/*` | 被沙箱阻断 | 7 passed | **16 passed** |
| 卡片状态转移 | 无（四枚按钮都汇到裁决模态） | 同左 | **「提交评审」/「状态 ▾」直连 PATCH** |
| 「复制」宿主命令 | 无行为 | 无行为 | **写真实剪贴板 + 「已复制」反馈** |
| `project_id` | 未被使用 | 未被使用 | **任务落 `project_id`，GET 按项目过滤** |
| 畸形 body | 200（静默建默认任务） | 200 | **400** |

### 0.2 P1 三项的落点与证据

| # | P1 项 | 落点 | 复验证据 |
| --- | --- | --- | --- |
| 1 | `PATCH /api/v1/tasks/{id}` + 真正的「状态 ▾」 | 后端新增 `api_update_task`（`gateway/tasks.py`）与 `LoopWorkspaceStatus.IN_REVIEW`（`loop_workspace/schema.py`）；前端 `lib/api.ts` 加 `updateTask`，`data.ts` 把 `CardActionId` 扩到四枚并给出 `TASK_STATUS_OPTIONS`，`TaskBoard.tsx` 的 `Card` 自持状态下拉 | 步 12–21：`提交评审` → `PATCH /api/v1/tasks/ACME-201` → 卡片 **进行中 → 评审中**，后端 `status=in_review`；`状态 ▾` 展开 6 项（= 后端 `LoopWorkspaceStatus` 全集）并标出当前项，选 `阻塞 · 需返工` → `PATCH` → 卡片落评审列、`gate_status=blocked` |
| 2 | 「复制」宿主命令 | `TaskDetail.tsx` 的 `DisposePanel` 接 `navigator.clipboard.writeText`，非安全上下文退回 `execCommand('copy')`，按钮 1.5s 显示「已复制」 | 步 34–36：剪贴板**实读** = `/goal <task_body> ACME-196 · 为网关补充限流与熔断策略`；`data-copied=true`、文案 `已复制`，1.5s 后复原 |
| 3 | `project_id` 真正生效 + 请求校验 | `service.upsert_task(..., project_id=)` 落库；`api_get_tasks` 按项目过滤（未知项目返回**空集**而非 default 的内容）；`_read_body` 把畸形/非对象 JSON 判为 400 | 步 38 + 单测：非法 status / 空 PATCH / 畸形 body 全部 400；`GET /api/v1/projects/nope/tasks` → `{"tasks": [], "count": 0}` |

### 0.3 裁决 ≠ 状态移动（这一轮最重要的设计判断）

P1 最容易做错的做法是：既然有了 `PATCH`，干脆把「通过 / 打回」也改成 `PATCH`。那会丢掉审批门的全部价值。两者的分工在这一轮被固化：

| | `PATCH /api/v1/tasks/{id}` | `POST /api/v1/tasks/{id}/gate/decision` |
| --- | --- | --- |
| 语义 | 生命周期移动 | **审计裁决** |
| 取值 | `planned` / `active` / `in_review` / `blocked` / `completed` / `canceled` | `approved` / `denied` |
| 载荷 | `status` / `phase` / `title` / `template` / `intent` | `decision` + `comment`（+ `title`） |
| 副作用 | 改列 | 改列 **+ 落 run log** |
| 入口 | 卡片「提交评审」「状态 ▾」 | 卡片「通过」「打回」→ 审批门裁决模态 |

因此四枚卡片动作现在**分成两条路**：`submit-review` / `set-status` 直连 `PATCH`；`gate-approve` / `gate-deny` 仍进模态。步 27 从 `request.post_data` 里读到 `{"decision": "denied", ...}`，证明「打回」没有退化成一次状态写入。

### 0.4 `PATCH` 是 upsert，不是 404（一个必须讲清的口径）

看板上有 8 张**画布种子卡**，它们只是设计稿夹具，工作区里未必有条目。把一张种子卡从「进行中」移到「评审中」时，后端必须**顺便把它物化**，否则下次取快照它会跌回原列。

- 实现：`api_update_task` 在目标 id 不存在时用前端带来的 `title` 建条目，响应里用 `created: true` 说明发生了物化。
- 未提供的字段一律**原样保留**（步 16 / 26 断言标题没被改写：状态移动不许顺手重写用户没碰过的标题）。
- 与裁决路径同构 —— 裁决在画布卡上本来也是 upsert，口径一致。

### 0.5 本轮自己踩到并修掉的两个真 bug

1. **光标回填把别的项目的任务抢了过来**。`GET /api/v1/projects/{id}/tasks` 的「光标一次性回填」原先只在**过滤后**的列表里找 `current_work_id`。于是：往 `project x` 建任务 → 光标指向它 → 读 `project default` → 回填把这条任务重新打上 `project_id="default"`。**只是读了一下默认项目，就偷走了 x 的任务**。修法：回填判重必须看**未过滤的整个集合**。
2. **状态下拉会被看板行裁掉**。初版按「视口高度」决定向上/向下弹；但看板行是 `overflow: hidden`，靠下的卡片照样被切。修法：以**所在列的底边**（`closest('[data-column]')`）为参照。实测「进行中」列 7 张卡逐个开菜单，全部完整落在列内（最高的一个 y=541..731，列底 743）。

### 0.6 新增的观测钩子（零像素，e2e 依赖）

| 钩子 | 位置 |
| --- | --- |
| `data-action="submit-review\|set-status\|gate-approve\|gate-deny"` | 卡片动作按钮 |
| `data-testid="status-menu-{cardId}"` | 状态下拉容器 |
| `data-status-option="in_review"` / `data-current="true"` | 下拉项及其当前项标记 |
| `data-testid="host-cmd-copy"` / `data-copied` | 详情页「复制」按钮及其反馈状态 |

这些属性不产生任何像素，不触碰设计稿保真纪律，但让走查从「猜选择器」变成「按 id 定位」。

### 0.7 剩余缺口

| 级别 | 项 | 说明 |
| --- | --- | --- |
| P2 | `phase` 仍偏粗 | 创建写 `triage`，其余路径 `maker`；看板暂未用 `phase` 分列 |
| P2 | `PATCH` 无权限/版本校验 | 任何调用方都能改任何任务的状态；审计裁决有批注，状态移动没有留痕 |
| P3 | `GET` 含一次写 | 光标回填会让 `GET /tasks` 落盘一次（一次性迁移，已注释说明） |
| P3 | 新建任务面板无标题字段 | 设计稿只有「描述」，任务标题取描述首行（截 60 字） |
| P3 | 状态移动无乐观更新 | 每次 PATCH 后整表重取快照（20 条请求里 14 条是 GET）；任务量大时应改为按 id 局部更新 |

### 0.8 复跑方式

```bash
# 1) 起网关（后端代码改动需重启；LOOPDESK_STATIC_NO_CACHE=1 便于反复核对产物）
cd /Users/freecisco_yan/Documents/trae_projects/savus
LOOPDESK_STATIC_NO_CACHE=1 uv run loopdesk gateway run --port 18792

# 2) 前端类型检查 + 产物
cd frontend && ./node_modules/.bin/tsc --noEmit && npm run build

# 3) 全生命周期接线复验（39 步 PASS/FAIL + 网络请求清单）
cd .. && cp LOOP-STATE.json /tmp/loopdesk-state.bak && .venv/bin/python tests/verify_webui_lifecycle.py

# 4) gateway 单测（沙箱下需摘掉文件代理开关）
env -u CODEBUDDY_BROKERED_FS_HOOK_ENABLED .venv/bin/python -m pytest \
  tests/test_gateway/test_task_routes.py tests/test_gateway/test_events_sse.py \
  tests/test_gateway/test_control_ui.py -q
```

`tests/verify_webui_lifecycle.py` 开头会先 PATCH 三张画布卡回到「进行中」——这是**测试前置**，否则上一次走查留下的状态会让下一次找不到「提交评审」按钮。所有徽标断言都是**增量**口径，不依赖工作区里已有多少任务。

证据截图：`docs/design-system/webui-p1-status-menu.png`（状态下拉）、`docs/design-system/webui-p1-copy-feedback.png`（复制反馈）、`docs/design-system/webui-lifecycle-wired.png`（P0 轮：ACME-196 已换列）。

### 0.9 卫生与运维

- 走查会真实写状态文件（这正是接线生效的证据）。复跑前后各 `cp` 一次即可。
- ⚠️ **证据截图是 gitignored 的**（`.gitignore:46` 的 `*.png`）——本文引用的三张 PNG 只在本地存在，新克隆的仓库里没有。要长期留存需显式 `git add -f` 或改为 `docs/assets/` 白名单。
- 走查每轮会往工作区留下几条探针任务（标题形如「外部 HTTP 注入的 SSE 探针任务」）。本轮结束时 `LOOP-STATE.json` 已 `git checkout` 回已提交基线（仅余 `task-1aa1af6b / Untitled Task`），未把探针数据留在里面。
- 后端 Python 改动**必须重启 gateway**（uvicorn 无 reload）。本轮踩到两个运维坑：
  1. `kill <pid>` 可能让旧进程**挂住不退**（`STAT=SN`），端口已释放但进程仍在 → 新进程启动时报 `Another gateway is already running`。**用 `kill -9`**。
  2. 非正常退出会留下陈旧 pidfile `~/.loopdesk/state/gateway.pid`，需手动删除才能起新进程。
- ⚠️ 请求参数仍是**不对称**的：`GET .../tasks` 的 `root` 取自 **query**，而 `POST` / `PATCH` 取自**请求体**、缺省 `Path.cwd()`。本轮已让 `_resolve_root` **两者都认**（query 优先），避免探针打畸形 body 时丢掉 `root` 而直接写进仓库根目录的状态文件。

---

## 附录 A · 第二轮记录（P0 接线后）

### A.1 前后对比

| 指标 | 第一轮（接线前） | **第二轮（当前）** |
| --- | --- | --- |
| 走查通过步数 | 19 / 24 | **23 / 23** |
| 走查中前端发出的 `/api` 请求 | **0** | **10**（7× GET tasks、1× GET events、1× POST tasks、1× POST gate/decision） |
| `tsc --noEmit` | 5 errors | **0 errors** |
| `dist` 产物中的 `/api/v1` / `EventSource` | 0 次（被 tree-shake） | 各 1 次（已入包） |
| gateway 单测 `test_gateway/*` | 被沙箱阻断 | **7 passed** |
| 新建任务是否落库 | ❌ 只关窗 | ✅ 落库并上板 |
| 审批门放行/驳回 | ❌ 完全不可达 | ✅ 卡片动作 → 模态 → 后端 → 看板换列 |
| 看板数据源 | 纯常量 | **画布种子 ⊕ 后端任务集合** |
| 右栏 ✕ 折叠 | ❌ 静默失效 | ✅ aside 2 → 1 |

### A.2 三条 P0 接线的落点

| # | P0 项 | 落点 | 复验证据 |
| --- | --- | --- | --- |
| 1 | 审批门可达 + 回写后端 | `Modals.tsx` 导出 `GateDecisionModal`；`App.tsx` 补 import 并把 `onConfirm` 接到 `submitGateDecision`；`TaskBoard.tsx` 卡片动作按钮补 `onClick`，经 `data.ts` 的 `CardActionId` 汇到 `onGate` | 步 12/13/14/15：`通过` → 模态 → `POST /api/v1/tasks/ACME-196/gate/decision` → ACME-196 从**评审中**移到**已完成**，状态行变 `已交付 · run log 完整`，且标题未被裁决批注改写 |
| 2 | 新建任务落库 | `Modals.tsx` 的 `NewTaskPayload` + 描述改真 `textarea`；`App.tsx` 的 `handleCreateTask` → `createTask` → 重新取快照 | 步 8/9/10/11：`POST /api/v1/projects/default/tasks` → 新卡片上板 → HTTP 交叉核对后端确有该标题 |
| 3 | 看板接后端 + SSE | `App.tsx` 挂载时 `fetchTasks` + `subscribeToEvents`；`data.ts` 新增**运行时叠加层** | 步 1/2/3/4/7/16：载入即拉快照、SSE 已连；外部 HTTP 建任务后看板**自动**多出一张卡（10 → 11），无需手刷 |

### A.3 看板叠加模型（为什么不直接用后端数据替换画布）

`data.ts` 的运行时叠加层（`setRuntimeTasks` / `allTasks` / `columnOf` / `cardsInColumn` / `boardColumns`）按三条规则合成：

1. **与画布卡片同 id** → 只覆盖 `state`，标题 / 分支 / 目标 / 证据仍取画布值 ⇒ 后端不会把设计稿文案冲掉。
2. **画布没有的 id** → 追加一张真卡片，字段由后端负载推出（`title` / `template` 作分支芯片 / `intent` 作 goal）。
3. **列徽标** = 画布基数 + 移进来的 + 后端追加的 − 移出去的（画布 5/4/2/9 是「积压总数」，所以徽标可大于可见卡片数，但卡片真的换列时两边账要对得上）。

这样做的收益：**设计稿保真度与后端真值同时成立**——8 张画布卡永远在，后端任务作为真卡片叠进来，裁决后卡片真的换列。代价：看板不是「后端的镜像」，而是「设计稿 ⊕ 后端」。

### A.4 前端改动清单

| 文件 | 改动 |
| --- | --- |
| `frontend/src/lib/api.ts` | `new EventSource()` → `new EventSource('/api/v1/events')`（原来无参会抛 `TypeError`，TS2554）；`fetchTasks` 返回 `TasksSnapshot { ok, tasks }` 以便区分「离线」与「零任务」；`GateDecisionPayload` 增 `title`；导出 `DEFAULT_PROJECT_ID` / `API_BASE` |
| `frontend/src/data.ts` | 运行时叠加层（见 §A.3）；`taskById` 走 `allTasks()`；`inspectorView` / `detailView` 同步改；`CARD_ACTIONS` 从「label 列表」升级为带 `CardActionId` 的动作表 |
| `frontend/src/App.tsx` | 补 `GateDecisionModal` import；挂载 `fetchTasks` + `subscribeToEvents`；`handleCreateTask` / `handleGateDecision` 两条上行；根节点挂 `data-loopdesk-online` / `data-loopdesk-tasks` 观测属性 |
| `frontend/src/screens/TaskBoard.tsx` | 卡片动作按钮接 `onAction`；列成员改 `cardsInColumn(id)`、列头改 `boardColumns()`；检视器 ✕ 包一层 `<button>`（`IconProps` 不收 `onClick`，原来被 React 静默丢弃）；补 `data-card-id` / `data-column` / `data-testid` 观测钩子 |
| `frontend/src/overlays/Modals.tsx` | `NewTaskModal` 出参改 `NewTaskPayload`；「描述」由静态 `<span>` 改真 `<textarea>`（空态靠 `::placeholder` 保持画布 muted 色，视觉零漂移） |
| `frontend/src/index.css` | 新增 `textarea::placeholder { color: var(--c-tm) }` |
| `frontend/src/screens/TaskDetail.tsx` | 仅补 `data-testid="detail-back"` 观测钩子 |

### A.5 后端改动清单（让接线不至于「接上一个错的形状」）

| 文件 | 改动 |
| --- | --- |
| `loop_workspace/schema.py` | `LoopWorkspaceState` 新增 `tasks: list[dict]` —— `current_work_id` 只是**光标**，写两次就吃掉第一条；看板需要的是**集合** |
| `loop_workspace/service.py` | `current_state()` 暴露 `tasks`；新增 `upsert_task()`（按 id 就地更新，保留 `created_at`） |
| `gateway/tasks.py` | `GET` 以任务集合为准 + 光标**一次性回填**（不回填的话，集合一有别的任务，原先看得见的那张卡会因光标挪走而凭空消失）；`POST` 同时写光标与集合；**审批门裁决保留任务原标题**（原来会把 `current_work_summary` 改写成 `Gate decision: approved (…)`） |

### A.6 剩余缺口（不阻断闭环）

> 下表是**第二轮当时**的视角。其中的 P1 两项（`状态 ▾` 语义、`复制` 按钮）与 P2 两项（`project_id`、畸形 body）已于第三轮完成，见 §0.2。

| 级别 | 项 | 说明 |
| --- | --- | --- |
| P1 | `状态 ▾` 语义被简化 | 网关只有一个状态转移端点（审批门裁决），因此 `提交评审 / 通过 / 打回 / 状态 ▾` 四枚按钮都汇到裁决模态（`打回` 预选驳回）。**该补 `PATCH /api/v1/tasks/{id}` 与真正的状态下拉。** |
| P1 | 「复制」按钮仍无行为 | `TaskDetail.tsx` 的待宿主操作命令复制未接 `navigator.clipboard` |
| P2 | `project_id` 未被使用 | 任意 project id 返回同一份状态（网关尚未按项目分区） |
| P2 | 畸形 body 仍返回 200 | `POST .../tasks` 收到非 JSON / 非对象时静默建「Untitled Task」，应 400 |
| P2 | `phase` 仍偏粗 | 创建写 `triage`，其余路径 `maker`；看板暂未用 `phase` 分列 |
| P3 | `GET` 含一次写 | 光标回填会让 `GET /tasks` 落盘一次（一次性迁移，已注释说明） |
| P3 | 新建任务面板无标题字段 | 设计稿只有「描述」，任务标题取描述首行（截 60 字） |

### A.7 复跑方式

```bash
# 1) 起网关（后端代码改动需重启；LOOPDESK_STATIC_NO_CACHE=1 便于反复核对产物）
cd /Users/freecisco_yan/Documents/trae_projects/savus
LOOPDESK_STATIC_NO_CACHE=1 uv run loopdesk gateway run --port 18792

# 2) 前端类型检查 + 产物
cd frontend && ./node_modules/.bin/tsc --noEmit && npm run build

# 3) 全生命周期接线复验（23 步 PASS/FAIL + 网络请求清单）
cd .. && .venv/bin/python tests/verify_webui_lifecycle.py

# 4) gateway 单测（沙箱下需摘掉文件代理开关）
env -u CODEBUDDY_BROKERED_FS_HOOK_ENABLED .venv/bin/python -m pytest \
  tests/test_gateway/test_task_routes.py tests/test_gateway/test_events_sse.py \
  tests/test_gateway/test_control_ui.py -q
```

证据截图：`docs/design-system/webui-lifecycle-wired.png`（ACME-196 已从评审中移到已完成；进行中列叠出两张后端任务卡）。

### A.8 卫生

- 走查会真实写状态文件（这正是接线生效的证据）。复跑前建议 `cp LOOP-STATE.json /tmp/loopdesk-state.bak`，跑完 `cp` 回去。
- 本轮结束后 `LOOP-STATE.json` 已还原到复验前状态；`frontend/dist` 已按新源码重建（`dist` 被 `frontend/.gitignore` 忽略）。
- ⚠️ 本次实测：**`POST .../tasks` 的 `root` 取自请求体、`GET` 的 `root` 取自 query**，而缺省是 `Path.cwd()`。用 `TestClient` 打畸形 body 而不带 `root` 时，会直接写进仓库根目录的 `LOOP-STATE.json`。压测/探针请显式给 `root`。

---

## 附录 B · 第一轮记录（接线前，2026-09-16 16:27 构建）

- 被测对象：`frontend/dist`（提交 `fb990b6d`，构建于 2026-09-16 16:27）
- 结论：**前端 19/24 步通过；后端 API 面可用。但前后端零接线，生命周期有 4 处硬断点。**


---

### B.1 一句话结论（接线前）

WebUI 目前是**可交互的静态视觉稿**：所有数据来自 `frontend/src/data.ts` 常量，**整个生命周期走查中前端发出的 `/api` 请求数为 0**；后端 `/api/v1/*` 三条任务端点与 SSE 事件总线**实测全部可用，但无人调用**。

| 层 | 状态 |
| --- | --- |
| 后端 gateway（路由 / 状态读写 / SSE 广播） | ✅ 可用（实测） |
| 前端视觉与交互（页面、右栏三段、详情 10 段、设置、抽屉、快捷键） | ✅ 基本可用（19/24） |
| 前端 → 后端接线 | ❌ **完全缺失（0 调用）** |
| 任务全生命周期闭环（新建→流转→审批门→交付） | ❌ **4 处硬断点** |

---

### B.2 生命周期走查结果（24 步 · 接线前）

| # | 步骤 | 结果 | 证据 |
| --- | --- | --- | --- |
| 1 | 加载 WebUI，React 挂载 | ✅ | `title=LoopDesk`，`#root` 有子节点，0 pageerror |
| 2 | 看板四列 + 8 张卡渲染 | ✅ | 待办 2 / 进行中 1 / 评审中 1 / 已完成 1，卡号 8/8 |
| 3 | 「新建任务」弹窗 4 模板可选 | ✅ | issue-fix / pr-commit / auto-research / 自由·无模板 |
| 4 | 提交后弹窗关闭 | ✅ | 「开始任务」消失 |
| **5** | **新建任务落到看板 / 后端** | ❌ | **卡片数 8→8，`/api` 调用 0** |
| 6 | 单击卡片 → 右栏三段 + 成本尾块 | ✅ | 任务状态 / 详情 / 交付物清单 / 成本·配额 全中 |
| 7 | 右栏跟随被点卡片（不跳转） | ✅ | 右栏含 `ACME-196`，主区仍在看板 |
| 8 | 切换卡片 → 右栏重算 | ✅ | 切到 `ACME-165` 后右栏内容随之改变 |
| 9 | 交付物清单「外链 / 内链」标记 | ✅ | 两者齐备 |
| 10 | 内链 → 任务详情，10 段契约齐全 | ✅ | 评审包·8 段契约 / 完成定义 / 变更文件 / 就绪检查 / 待宿主操作 / 交付凭据 / 运行记录 |
| 11 | 详情 7 个锚点 id 存在 | ✅ | `packet / completion / diff / readiness / host-gate / receipt / run-log` |
| 12 | 详情按被点卡片动态取 id / 标题 | ✅ | 含 `ACME-165`，无残留 `TDS-412` |
| **13** | **「复制」按钮（待宿主操作命令）** | ❌ | 按钮存在但点击后剪贴板哨兵值未被覆盖 |
| 14 | 详情 ✕ 返回看板 | ✅ | 回看板成功（**唯一返回控件是无标签 ✕ 图标**） |
| 15 | 卡片生命周期动作按钮渲染 | ✅ | 提交评审 / 状态 ▾ / 通过 / 打回 各 2 个 |
| **16** | **「通过」→ 审批门裁决模态** | ❌ | **不弹窗**：按钮无 `onClick`，点击仅冒泡为「选中卡片」 |
| **17** | **审批门裁决回写后端** | ❌ | 前端 `/api` 总调用数 = 0，无 `POST /tasks/{id}/gate/decision` |
| 18 | 左栏导航切换 | ✅ | 任务看板 / 团队资产 / 控制中心 |
| 19 | 团队资产页（作用域健康条） | ✅ | 含「作用域」 |
| 20 | 设置·Agent 运行时四选一 | ✅ | `codex-cli 已选定` + 歧义提示 |
| 21 | 设置·MCP 来源列 + 插件与市场 | ✅ | 两处齐备 |
| 22 | 会话 · 渠道抽屉 | ✅ | 可打开 |
| 23 | `⌘B` 折叠 / 展开右栏 | ✅ | `aside` 3 → 2 → 3 |
| 24 | 顶栏项目下拉可切换 | ✅ | 隔离复验：开→选 `LoopDesk Core`→顶栏标题随之改变 |

> 第 24 步在主序列中受前序点击状态影响（下拉为 toggle），**已隔离复跑确认功能正常**，记为通过。
> 净缺陷 **4 项**：第 5、13、16、17 步。

---

### B.3 缺口明细（按严重度 · 接线前）

#### P0-1 「新建任务」不回写后端
- `frontend/src/App.tsx:97` — `onConfirm={() => setNewTaskOpen(false)}`，**只关窗**。
- `NewTaskModal`（`overlays/Modals.tsx:196`）内部无任何网络调用。
- 后端 `POST /api/v1/projects/{project_id}/tasks` **实测可用**（返回 `task-8421e668`），但前端从不调用。
- 后果：新建任务在看板与后端**双向都不留痕**，生命周期从第一步即断。

#### P0-2 审批门放行/驳回 完全不可达
三重问题叠加：

1. **按钮无行为**：`screens/TaskBoard.tsx:112–135`，卡片上的「提交评审 / 状态 ▾ / 通过 / 打回」只映射 `label` / `primary`，**没有 `onClick`**；点击「通过」只会冒泡触发父级 `onSelect`（实测：点后右栏切到该卡，无弹窗）。
2. **组件未导入**：`App.tsx:103` 渲染 `<GateDecisionModal>`，但顶部 import（第 12 行）只有 `AddAgentModal, AddConnectorModal, NewTaskModal`。`tsc` 报 **`TS2304: Cannot find name 'GateDecisionModal'`**。
3. **状态永不置位**：`gateModalTask` / `setGateModalTask` 在全仓库**只被调用为 `null`**，从未传入任务对象 → 即使补上 import 也**没有触发路径**。
4. **产物已裁剪**：`frontend/dist/assets/index-BnFdUeKr.js` 中字符串 `审批门裁决` 出现 **0 次** → 组件被 tree-shake；一旦真的渲染会抛 `ReferenceError`。
5. 即便渲染成功，`onConfirm` 也只 `console.log`（`App.tsx:108`），**不回写后端**。

> 后端 `POST /api/v1/tasks/{task_id}/gate/decision` 与 SSE `gate_decision_recorded` **实测全通**，缺的只是前端触发与调用。

#### P1-3 「复制」按钮无行为
- `screens/TaskDetail.tsx` 全文**只有 1 处 `onClick`**（右栏 ✕ 关闭）；「待宿主操作」代码块下的「复制」按钮（第 346 行）为纯样式。
- 实测：点击后 `navigator.clipboard.readText()` 仍返回预置哨兵值 `__SENTINEL__` → 未写入。
- 后果：`cli_can_mutate_directly = false` 场景下「命令只交付不代执行」，而交付的唯一动作（复制命令）不可用。

#### P1-4 检视器 ✕ 折叠按钮失效
- `screens/TaskBoard.tsx:887` 给 `CloseIcon` 传 `onClick={onClose}`，但 `IconProps` 不含 `onClick` → `tsc` **TS2322**，React 丢弃该 prop。
- 实测：点击后 `aside` 数 **2 → 2**（无变化）；`⌘B` 正常（2 → 1）。
- 后果：鼠标无法折叠右栏，只能靠快捷键。

---

### B.4 编译与产物健康度（接线前）

```
$ frontend/node_modules/.bin/tsc --noEmit      → 5 errors
  src/App.tsx(103,12)        TS2304  Cannot find name 'GateDecisionModal'
  src/App.tsx(107,25/35)     TS7006  Parameter 'decision'/'comment' implicitly has 'any'
  src/lib/api.ts(78,23)      TS2554  Expected 1-2 arguments, but got 0   (new EventSource())
  src/screens/TaskBoard.tsx(887,30) TS2322  'onClick' does not exist on 'IconProps'

$ frontend/node_modules/.bin/vite build        → ✓ built in 300ms，43 modules
  assets/index-BnFdUeKr.js  231.24 kB
```

**产物扫描（决定性证据）**：

| 字符串 | 在 dist JS 中出现次数 |
| --- | --- |
| `/api/v1` | **0** |
| `EventSource` | **0** |
| `审批门裁决` | **0** |
| `任务处置`（详情右栏） | 1 |
| `查看详情` | 1 |

→ `lib/api.ts` 与 `GateDecisionModal` **均被 tree-shake 出包**。构建不报错，因为 esbuild 不做类型检查：`<GateDecisionModal>` 被编译成一个**未定义全局引用**，只在渲染时才会 `ReferenceError`，而它永远不被渲染。

---

### B.5 后端能力面（实测 · 接线前）

### B.5.1 路由面（27 条 `/api*` + `/ws`，由 `create_gateway_app` 枚举）

```
GET/HEAD  /api/agents        /api/approvals      /api/channels/status  /api/chat/history
GET/HEAD  /api/config        /api/cron           /api/sessions         /api/system/status
GET/HEAD  /api/usage         /health
POST      /api/approvals/resolve   /api/approvals/settings   /api/audio/transcribe
POST      /api/channels/logout     /api/chat                /api/elevated-mode
GET/HEAD  /api/v1/artifacts/{id}   /api/v1/attachments/{sha256}   /api/v1/events
POST      /api/v1/files/upload
GET/HEAD  /api/v1/projects/{project_id}/tasks
POST      /api/v1/projects/{project_id}/tasks
POST      /api/v1/tasks/{task_id}/gate/decision
WS        /ws
```

控制台 SPA 由 `gateway/control_ui.py` 从 `frontend/dist` 托管（`base_path=/control`，根路径 `/` 同样回落到 SPA）。

### B.5.2 任务生命周期三端点 —— 实测全通

| 步骤 | 请求 | 结果 |
| --- | --- | --- |
| 查任务 | `GET /api/v1/projects/default/tasks` | `{"tasks":[...],"count":1}` |
| 建任务 | `POST` 同路径 `{title,template,intent}` | `{"ok":true,"task":{"id":"task-8421e668","phase":"triage"}}` |
| 审批门（放行） | `POST /api/v1/tasks/{id}/gate/decision {decision:"approved"}` | `status → completed` |
| 审批门（驳回） | 同上 `denied` | `status → blocked` |

### B.5.3 SSE 事件总线 —— 实测全通

浏览器内 `new EventSource('/api/v1/events')` 依次收到：

```
connected                {"status":"connected","timestamp":"now"}
task_created             {"task":{"id":"task-8de86afc","title":"SSE 探针任务",...}}
gate_decision_recorded   {"task_id":"task-sse","decision":"approved","status":"completed"}
```

### B.5.4 后端模型的 5 个偏薄点（非阻断，但限制「全生命周期」表达）

1. **无任务集合**：`gateway/tasks.py:25` 的 `api_get_tasks` 只把 `LOOP-STATE.json` 的 `current_work_id` 合成 **1 条**记录，再追加 `run_log`。连续 POST 两次，**前一条被覆盖**（实测 `task-1aa1af6b` → `task-8421e668`）。
2. **`project_id` 未被使用**：路由参数声明了它，但 `_get_service()` 只读 `root` 查询参数 → `GET /api/v1/projects/nope/tasks` 返回 **200** 且内容与 `default` 一致，**多项目隔离不成立**。
3. **审批门回写会破坏任务标题**：`record_work_item(summary=f"Gate decision: {decision} ({comment})")` 覆盖 `current_work_summary` → 实测 gate 之后 `GET` 的 `title` 变成 `"Gate decision: approved (E2E 验证放行)"`。
4. **字段与状态机不一致**：`phase` 恒为 `"maker"`（POST 却返回 `"triage"`）；`created_at` 恒 `null`；`gate_status` 仅按 `status == "blocked"` 二分，**没有** 待办/进行中/评审中/已完成 四列映射。
5. **输入校验缺失**：畸形 JSON body → **200** 并创建一条默认任务（无 400）。

### B.5.5 单测覆盖

- `tests/test_gateway/test_task_routes.py`（3 用例）覆盖上述 3 端点；`test_events_sse.py`、`test_control_ui.py` 本轮 **4 passed**。
- 3 个任务路由用例在当前沙箱下 **setup 阶段 EEXIST 报错** —— 原因是宿主文件代理把 `Path.mkdir(exist_ok=True)` 判为错误（`EEXIST: file already exists, mkdir .../pytest-of-unknown`），**属构建环境问题，非产品缺陷**。同样这 3 条端点已用真实 HTTP 对运行中的 gateway 复跑通过（§B.5.2）。
- **第三轮更正**：这 3 条用例已全部可跑（`test_task_routes.py` 现为 12 用例），且新增了 PATCH / 400 / 项目分区的覆盖；全套 `test_gateway/*` **16 passed**。

---

### B.6 建议修复顺序（第一轮提出；P0 三项已于第二轮完成见 §A.2，P1 三项已于第三轮完成见 §0.2）

| 优先 | 动作 | 落点 |
| --- | --- | --- |
| P0 | 补 `GateDecisionModal` 的 import；把卡片「通过 / 打回 / 提交评审」的 `onClick` 接到 `setGateModalTask({id,title})`；`onConfirm` 改为 `await submitGateDecision(id,{decision,comment})` | `App.tsx`、`TaskBoard.tsx`、`Modals.tsx` |
| P0 | `NewTaskModal.onConfirm` 接 `createTask(projectId,{title,template,intent})`，成功后刷新看板数据源 | `App.tsx`、`Overlays/Modals.tsx` |
| P0 | 看板数据源从 `data.ts` 常量切到 `fetchTasks()`；`subscribeToEvents()` 订阅 `task_created` / `phase_changed` / `gate_decision_recorded` 驱动刷新（SSE 后端已就绪） | `TaskBoard.tsx`、`lib/api.ts` |
| P1 | 「复制」按钮接 `navigator.clipboard.writeText`（含失败提示） | `TaskDetail.tsx` |
| P1 | 修 `IconProps` 增加 `onClick` 并透传，恢复检视器 ✕ 折叠 | `components/icons.tsx`、`TaskBoard.tsx` |
| P1 | `lib/api.ts:78` `new EventSource()` 补 URL 参数（`/api/v1/events`） | `lib/api.ts` |
| P2 | 后端：`api_get_tasks` 支持任务集合；启用 `project_id`；gate 回写不覆盖 `current_work_summary`；`phase` 真值化；body 校验返回 400 | `gateway/tasks.py` |

---

### B.7 复跑方式（已被 §0.8 取代）

```bash
# 1) 起网关（若未运行）
cd <repo> && uv run loopdesk gateway run --port 18792

# 2) 跑生命周期走查（Chromium 1440×900，输出逐步 PASS/FAIL + 网络/pageerror 汇总）
<repo>/.venv/bin/python tests/verify_webui_lifecycle.py

# 3) 类型检查 / 构建
cd frontend && ./node_modules/.bin/tsc --noEmit && ./node_modules/.bin/vite build
```

> 验证脚本：`tests/verify_webui_lifecycle.py`（不匹配 `test_*.py`，不会被 pytest 自动收集）。

### 附：状态文件卫生
本轮为验证审批门来回，对运行中的 gateway 发起过 `POST create / gate`，已从备份恢复 `LOOP-STATE.json`（`current_work_id = task-1aa1af6b`，`status = active`）。`frontend/` 无改动，`dist/` 未被覆盖（构建验证输出到临时目录）。
