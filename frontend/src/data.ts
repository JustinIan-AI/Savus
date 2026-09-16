/* ============================================================
   LoopDesk v0.2 — domain data
   Every string here is copied verbatim from the Ardot canvas.
   ============================================================ */

export type NavKey = 'board' | 'assets' | 'control' | 'settings-agent' | 'settings-mcp' | 'settings-other'

export type TaskColumnId = 'todo' | 'doing' | 'review' | 'done'

/** A card's trailing status line — colour is driven by the state itself. */
export type CardState = 'handoff' | 'gate' | 'delivered'

export interface TaskCard {
  id: string
  title: string
  branch: string
  agent: string
  state: CardState
  /** 详情 · Goal —— 这条任务要达成什么，展开「Goal · 目标」时读到 */
  goal: string
  /** 交接清单的「目标」行必须单行，因此另存一句短语版 */
  goalBrief: string
  /** 证据 —— 手上已有什么能证明当前进展；右栏「详情」段直接读它 */
  evidence: string
}

export interface TaskColumn {
  id: TaskColumnId
  title: string
  count: number
  /** only 进行中 renders in the emerald "active" treatment */
  active?: boolean
}

export const KANBAN_COLUMNS: TaskColumn[] = [
  { id: 'todo', title: '待办', count: 5 },
  { id: 'doing', title: '进行中', count: 4, active: true },
  { id: 'review', title: '评审中', count: 2 },
  { id: 'done', title: '已完成', count: 9 },
]

export const TASKS: TaskCard[] = [
  {
    id: 'ACME-218',
    title: '为登录接口补充 OAuth2 设备码流程',
    agent: 'codex',
    branch: 'feat/oauth-device',
    state: 'handoff',
    goal: '让 CLI 与无浏览器环境能通过设备码完成 OAuth2 授权，不再依赖回调地址。',
    goalBrief: '设备码授权流程落地',
    evidence: '设备码轮询单测 18 / 18',
  },
  {
    id: 'ACME-224',
    title: '重构配置加载器以支持热重载',
    agent: 'claude',
    branch: 'feat/config-hotreload',
    state: 'handoff',
    goal: '把配置加载从启动期一次性读取改成可订阅的热重载，改配置不必重启进程。',
    goalBrief: '配置热重载可订阅',
    evidence: '热重载集成测试 9 / 9',
  },
  {
    id: 'ACME-201',
    title: '实现跨会话 handoff 上下文传递',
    agent: 'claude',
    branch: 'feat/handoff-ctx',
    state: 'handoff',
    goal:
      '在 claude 完成首轮实现后，将目标、决策、证据与交接清单封装为 handoff packet，供 codex 在隔离 worktree 中续跑，无需重复解释需求。',
    goalBrief: '实现跨会话上下文续跑',
    evidence: '单测通过 23 / 23',
  },
  {
    id: 'ACME-209',
    title: '并行运行 issue-fix 模板修复内存泄漏',
    agent: 'pi',
    branch: 'fix/mem-leak',
    state: 'handoff',
    goal: '用 issue-fix 模板并行跑三条修复线，定位长驻进程的内存泄漏并锁死回归。',
    goalBrief: '定位并锁死内存泄漏',
    evidence: '堆快照对比 · 常驻内存回落 41%',
  },
  {
    id: 'ACME-196',
    title: '为网关补充限流与熔断策略',
    agent: 'codex',
    branch: 'feat/ratelimit',
    state: 'gate',
    goal: '为网关补上按租户的限流与熔断，避免单租户突发流量把下游打满。',
    goalBrief: '按租户限流与熔断',
    evidence: '压测 2 000 QPS 无 5xx',
  },
  {
    id: 'ACME-188',
    title: '生成 PR 并打磨提交信息',
    agent: 'claude',
    branch: 'chore/pr-commit',
    state: 'gate',
    goal: '用 pr-commit 模板生成 PR 描述、打磨提交信息并触发 CI，评审包须 8 段齐全。',
    goalBrief: 'PR 与提交信息成稿',
    evidence: 'CI 全绿 · 变更 3 个文件',
  },
  {
    id: 'ACME-172',
    title: '接入 JIRA 双向同步连接器',
    agent: 'claude',
    branch: 'feat/jira-sync',
    state: 'delivered',
    goal: '把 JIRA issue 与看板任务双向对齐，进度自动回写，不再靠手工搬运。',
    goalBrief: 'JIRA 双向同步打通',
    evidence: '双向同步 e2e 16 / 16',
  },
  {
    id: 'ACME-165',
    title: 'auto-research 调研向量存储选型',
    agent: 'pi',
    branch: 'research/vecstore',
    state: 'delivered',
    goal: '用 auto-research 模板横向调研向量存储选型，沉淀一份可复核的决策依据。',
    goalBrief: '向量存储选型结论',
    evidence: '12 篇来源 · 决策表 1 份',
  },
]

/* ============================================================
   运行时任务叠加层

   画布上的 8 张卡片是**设计事实源**，永远留在看板上；网关返回的
   loop 任务作为**运行时叠加**合进来：

   - 与画布卡片同 id  → 只覆盖 state（于是卡片换列、换状态词），
     标题 / 分支 / 目标 / 证据仍取画布值，后端不会把画布文案冲掉。
   - 画布没有的 id    → 追加一张真卡片，字段由后端负载推出。

   列成员与计数都是「种子 ⊕ 叠加」的结果，因此看板几何不变，但内容
   真的跟着后端走。
   ============================================================ */

/** 网关 `GET .../tasks` 返回的最小负载形状（与 lib/api 的 ApiTask 结构兼容）。 */
export interface RuntimeTaskInput {
  id: string
  title?: string
  status?: string
  template?: string
  intent?: string
}

/** 后端 status → 卡片状态词。未知状态一律按 handoff 处理。 */
const STATE_BY_STATUS: Record<string, CardState> = {
  planned: 'handoff',
  active: 'handoff',
  blocked: 'gate',
  completed: 'delivered',
  canceled: 'delivered',
}

/** 卡片状态词 → 看板列。仅用于**被后端状态改写过**的卡片。 */
const COLUMN_BY_STATE: Record<CardState, TaskColumnId> = {
  handoff: 'doing',
  gate: 'review',
  delivered: 'done',
}

export const cardStateOfStatus = (status?: string): CardState => STATE_BY_STATUS[status ?? ''] ?? 'handoff'

let RUNTIME: TaskCard[] = []
/** 画布种子卡片里，被后端 status 改写过状态的那些：id → state。 */
let OVERRIDDEN: Record<string, CardState> = {}

/** 把一次 `fetchTasks` 的结果灌进叠加层。必须在触发渲染前调用。 */
export function setRuntimeTasks(inputs: RuntimeTaskInput[]): void {
  const seedIds = new Set(TASKS.map((t) => t.id))
  const overridden: Record<string, CardState> = {}
  const appended: TaskCard[] = []

  for (const t of inputs) {
    if (!t || !t.id) continue
    const state = cardStateOfStatus(t.status)
    if (seedIds.has(t.id)) {
      overridden[t.id] = state
      continue
    }
    appended.push({
      id: t.id,
      title: t.title || t.id,
      branch: t.template || 'issue-fix',
      agent: 'codex',
      state,
      goal: t.intent || t.title || t.id,
      goalBrief: t.title || t.id,
      evidence: `网关 loop 任务 · status=${t.status ?? 'active'}`,
    })
  }

  OVERRIDDEN = overridden
  RUNTIME = appended
}

/** 画布种子 + 后端追加，按 id 查询时叠加层优先（同 id 已在灌入时折叠为覆盖）。 */
export const allTasks = (): TaskCard[] => [...TASKS, ...RUNTIME]

export const taskById = (id: string): TaskCard =>
  (allTasks().find((t) => t.id === id) ?? TASKS.find((t) => t.id === DEFAULT_TASK_ID) ?? TASKS[0]) as TaskCard

/** 某张卡片当前落在哪一列：画布位置为准，被后端改写过状态才按状态列算。 */
export function columnOf(id: string): TaskColumnId {
  const override = OVERRIDDEN[id]
  if (override) return COLUMN_BY_STATE[override]
  const seeded = BOARD.find((b) => b.cards.includes(id))?.column
  if (seeded) return seeded
  const appended = RUNTIME.find((t) => t.id === id)
  return appended ? COLUMN_BY_STATE[appended.state] : 'todo'
}

/** 某一列的卡片 id 列表：留在原列的种子 + 被移进来的种子 + 后端追加的卡片。 */
export function cardsInColumn(id: TaskColumnId): string[] {
  const seed = BOARD.find((b) => b.column === id)?.cards ?? []
  const stayed = seed.filter((cid) => !OVERRIDDEN[cid])
  const arrived = Object.keys(OVERRIDDEN).filter((cid) => COLUMN_BY_STATE[OVERRIDDEN[cid]] === id)
  const appended = RUNTIME.filter((t) => t.id && COLUMN_BY_STATE[t.state] === id).map((t) => t.id)
  return [...stayed, ...arrived, ...appended]
}

/** 列头徽标 = 画布基数 + 从别列移进来的 + 后端追加的 − 移出去的。
 *  画布画的是「积压总数」，所以徽标可以大于可见卡片数；但卡片真的
 *  换了列时，两边的账都要对得上。 */
export function boardColumns(): TaskColumn[] {
  const arrived: Partial<Record<TaskColumnId, number>> = {}
  const left: Partial<Record<TaskColumnId, number>> = {}
  const appended: Partial<Record<TaskColumnId, number>> = {}

  for (const [id, state] of Object.entries(OVERRIDDEN)) {
    const from = BOARD.find((b) => b.cards.includes(id))?.column
    const to = COLUMN_BY_STATE[state]
    if (from === to) continue
    if (from) left[from] = (left[from] ?? 0) + 1
    arrived[to] = (arrived[to] ?? 0) + 1
  }
  for (const t of RUNTIME) {
    const col = COLUMN_BY_STATE[t.state]
    appended[col] = (appended[col] ?? 0) + 1
  }

  return KANBAN_COLUMNS.map((c) => ({
    ...c,
    count: Math.max(0, c.count + (arrived[c.id] ?? 0) + (appended[c.id] ?? 0) - (left[c.id] ?? 0)),
  }))
}

/** Column membership, declared explicitly to mirror the canvas exactly
 *  (each column shows 2 cards while its badge counts the full backlog). */
export const BOARD: { column: TaskColumnId; cards: string[] }[] = [
  { column: 'todo', cards: ['ACME-218', 'ACME-224'] },
  { column: 'doing', cards: ['ACME-201', 'ACME-209'] },
  { column: 'review', cards: ['ACME-196', 'ACME-188'] },
  { column: 'done', cards: ['ACME-172', 'ACME-165'] },
]

/* The 3rd column is 评审中 — the approval gate lives *inside* it as the
   inspector's 审批门 block, so the card line must not read "待审批". */
export const CARD_STATE_TEXT: Record<CardState, string> = {
  handoff: 'handoff 可续跑',
  gate: '评审中 · 等待确认',
  delivered: '已交付 · run log 完整',
}

export const CARD_STATE_COLOR: Record<CardState, string> = {
  handoff: 'var(--c-emerald)',
  gate: 'var(--c-amber)',
  delivered: 'var(--c-ts)',
}

/** Agent name colours, per the canvas row-1 treatment. */
export const AGENT_COLOR: Record<string, string> = {
  claude: 'var(--c-emerald)',
  codex: 'var(--c-blue)',
  pi: 'var(--c-amber)',
}

/* ============================================================
   Screen 1 · 任务检视器（右栏）

   右栏不持有自己的文案。整块内容按**被选中的卡片**生成，规则是三段：

     ① 任务状态   ← card.state    状态芯片 / 六阶段进度 / 处置路由 / 两段式验证
     ② 详情       ← card 字段     Goal / Handoff 上下文包 / Agent 执行
     ③ 交付物清单 ← card.state    产出物 + 链接（外链，或跳详情页的内链）

   末尾的 成本 / 配额 不属于三段之一 —— 它是这次运行的资源消耗，常驻面板尾部。
   ============================================================ */

export type StageState = 'done' | 'current' | 'todo'

/** 画布帧 01 的样例任务。默认选中它，右栏因此与画布逐字一致。 */
export const DEFAULT_TASK_ID = 'ACME-201'

/** 右栏状态芯片 —— 比看板卡片那句话更短，22px 芯片只放得下一个词。 */
export const INSPECTOR_STATUS_TEXT: Record<CardState, string> = {
  handoff: 'handoff',
  gate: '评审中',
  delivered: '已交付',
}

/** 三段的生成依据，标注在分组标题右侧 —— 与 pr_contract / run_log 同一种标注语言。 */
export const INSPECTOR_GROUP_RULES = {
  status: 'card.state',
  detail: 'card.detail',
  deliverables: 'card.state',
}

/* ---------- ① 任务状态 ---------- */

/** 六阶段进度按 state 推进；画布样例（handoff）就是第一档。 */
const STAGE_BY_STATE: Record<CardState, { stages: { label: string; state: StageState }[]; summary: string }> = {
  handoff: {
    stages: [
      { label: '分诊', state: 'done' },
      { label: '制作', state: 'done' },
      { label: '检查', state: 'current' },
      { label: '升级', state: 'todo' },
      { label: '日志', state: 'todo' },
      { label: '停止', state: 'todo' },
    ],
    summary: 'checker 运行中 · run #3 · 2 / 6 阶段 · triage ✓ maker ✓ checker ▸',
  },
  gate: {
    stages: [
      { label: '分诊', state: 'done' },
      { label: '制作', state: 'done' },
      { label: '检查', state: 'done' },
      { label: '升级', state: 'current' },
      { label: '日志', state: 'todo' },
      { label: '停止', state: 'todo' },
    ],
    summary: 'operator gate 待确认 · run #4 · 3 / 6 阶段 · checker ✓ escalator ▸',
  },
  delivered: {
    stages: [
      { label: '分诊', state: 'done' },
      { label: '制作', state: 'done' },
      { label: '检查', state: 'done' },
      { label: '升级', state: 'done' },
      { label: '日志', state: 'done' },
      { label: '停止', state: 'done' },
    ],
    summary: 'loop 已关闭 · run #5 · 6 / 6 阶段 · 全部通过',
  },
}

/** 分诊路由 —— 三选一。只有已交付的任务才落到「仅记录」。 */
export const DISPOSITION_ROUTES = [
  { key: 'fix_pr', label: '备修复 · fix_pr' },
  { key: 'comment', label: '仅评论' },
  { key: 'log', label: '仅记录' },
] as const

export type DispositionRouteKey = (typeof DISPOSITION_ROUTES)[number]['key']

const ROUTE_BY_STATE: Record<CardState, DispositionRouteKey> = {
  handoff: 'fix_pr',
  gate: 'fix_pr',
  delivered: 'log',
}

const DISPOSITION_RUN: Record<CardState, string> = {
  handoff: 'run #3 · 候选预检',
  gate: 'run #4 · 待 operator 确认',
  delivered: 'run #5 · 已归档',
}

/** 两段式验证 —— ✗ 与 ✓ 必须成对出现：只看结果无法判断修复是否真的生效。 */
export const DISPOSITION_VERIFY = {
  key: '验证',
  repro: '✗ 复现失败',
  validated: '✓ 修复通过',
  cmd: 'npm test',
}

/* ---------- ② 详情 ---------- */

const DECISION_BY_STATE: Record<CardState, string> = {
  handoff: 'worktree 隔离 + 预算上限',
  gate: '改动冻结 · 只读评审包',
  delivered: 'worktree 已清理 · 分支已合并',
}

const TODO_BY_STATE: Record<CardState, string> = {
  handoff: '补充 operator gate 审批',
  gate: '等待 operator 确认',
  delivered: '无 · loop 已关闭',
}

const EXEC_BY_STATE: Record<CardState, { status: string; step: string; pct: number }> = {
  handoff: { status: '· 运行中', step: '第 3 / 5 步', pct: 0.6 },
  gate: { status: '· 已暂停', step: '第 5 / 5 步', pct: 1 },
  delivered: { status: '· 已完成', step: '5 / 5 步', pct: 1 },
}

const GATE_BY_STATE: Record<CardState, { text: string; action: string; pending: number }> = {
  handoff: { text: 'health → operator 待审批', action: '待你审批', pending: 1 },
  gate: { text: 'health → operator 待审批', action: '待你审批', pending: 1 },
  delivered: { text: 'gate 已放行 · receipt 已归档', action: '已放行', pending: 0 },
}

const GOAL_SUMMARY_BY_STATE: Record<CardState, string> = {
  handoff: '2 决策 · 1 待确认',
  gate: '3 决策 · 0 待确认',
  delivered: '3 决策 · 已归档',
}

const RUNLOG_SUMMARY_BY_STATE: Record<CardState, string> = {
  handoff: '12 条事件',
  gate: '18 条事件',
  delivered: '24 条事件',
}

/* ---------- ③ 交付物清单 ---------- */

/** 详情页里可被锚定的区块 —— 内链跳这里。 */
export type DetailAnchor = 'packet' | 'completion' | 'diff' | 'readiness' | 'host-gate' | 'receipt' | 'run-log'

export interface Deliverable {
  name: string
  /** 链接目标的一句话说明：外链写域名，内链写详情页的区块 */
  target: string
  kind: 'external' | 'internal'
  href?: string
  anchor?: DetailAnchor
}

const REPO = 'https://github.com/acme-platform'
const CI = 'https://ci.acme.com'
const slugOf = (branch: string) => branch.split('/')[1] ?? 'platform'
const noOf = (id: string) => id.replace(/\D/g, '')

/** 清单构成由 state 决定：在跑的任务只交出分支与状态文件，待审的交出评审包与 PR，
 *  已交付的交出凭据与运行记录。卡片自身不携带清单，避免同一任务两处维护。 */
export function deliverablesFor(card: TaskCard): Deliverable[] {
  const repo = `${REPO}/${slugOf(card.branch)}`
  const n = noOf(card.id)
  switch (card.state) {
    case 'handoff':
      return [
        { name: card.branch, target: 'github.com/acme-platform', kind: 'external', href: repo },
        { name: 'LOOP-STATE.json', target: `本地 · .loopdesk/${card.id}`, kind: 'internal', anchor: 'run-log' },
        { name: 'Handoff 上下文包', target: '详情 · 评审包 ②', kind: 'internal', anchor: 'packet' },
      ]
    case 'gate':
      return [
        { name: `PR #${n}`, target: 'github.com/acme-platform', kind: 'external', href: `${repo}/pull/${n}` },
        { name: '评审包 · 8 段契约', target: '详情 · 评审包', kind: 'internal', anchor: 'packet' },
        { name: '变更文件 · 3 个', target: '详情 · diff --stat', kind: 'internal', anchor: 'diff' },
        { name: 'validation_receipt.json', target: 'ci.acme.com/receipts', kind: 'external', href: `${CI}/receipts/${card.id}` },
      ]
    case 'delivered':
      return [
        { name: 'validation_receipt.json', target: 'ci.acme.com/receipts', kind: 'external', href: `${CI}/receipts/${card.id}` },
        { name: `CI 运行 #${n}`, target: 'ci.acme.com/runs', kind: 'external', href: `${CI}/runs/${n}` },
        { name: '变更文件 · 3 个', target: '详情 · diff --stat', kind: 'internal', anchor: 'diff' },
        { name: '运行记录', target: '详情 · run_log', kind: 'internal', anchor: 'run-log' },
      ]
  }
}

/* ---------- 尾部 · 成本 / 配额（不属三段） ---------- */

const COST_BY_STATE: Record<CardState, { value: string; pct: number; note: string }> = {
  handoff: { value: '$0.42 / $1.00', pct: 0.586, note: 'quota 决策: should-run = true · kill switch 就绪' },
  gate: { value: '$0.78 / $1.00', pct: 0.78, note: 'quota 决策: should-run = false · 改动已冻结' },
  delivered: { value: '$0.91 / $1.00', pct: 0.91, note: 'quota 决策: loop 已关闭 · 结算完成' },
}

const RUNLOG_BY_STATE: Record<CardState, { text: string; tone: 'ts' | 'amber' | 'blue' }[]> = {
  handoff: [
    { text: '[ok]   evidence: %EVIDENCE%', tone: 'ts' },
    { text: '[gate] operator approval pending', tone: 'amber' },
    { text: '[info] handoff packet written → %AGENT%', tone: 'blue' },
  ],
  gate: [
    { text: '[ok]   pr_contract 8/8 · 评审包齐全', tone: 'ts' },
    { text: '[gate] operator approval pending', tone: 'amber' },
    { text: '[info] change frozen · diff 已封存', tone: 'blue' },
  ],
  delivered: [
    { text: '[ok]   evidence: %EVIDENCE%', tone: 'ts' },
    { text: '[info] worktree cleaned · 分支已合并', tone: 'blue' },
    { text: '[info] loop closed by operator', tone: 'blue' },
  ],
}

/** 右栏的单一入口：给一个任务 id，换回三段内容加尾部。 */
export function inspectorView(id: string) {
  const card = allTasks().find((c) => c.id === id) ?? taskById(DEFAULT_TASK_ID)
  const stage = STAGE_BY_STATE[card.state]
  const exec = EXEC_BY_STATE[card.state]
  const gate = GATE_BY_STATE[card.state]
  const cost = COST_BY_STATE[card.state]
  const fill = (s: string) => s.replace(/%EVIDENCE%/g, card.evidence).replace(/%AGENT%/g, card.agent)

  return {
    card,
    status: {
      label: INSPECTOR_STATUS_TEXT[card.state],
      tone: CARD_STATE_COLOR[card.state],
      stages: stage.stages,
      stageSummary: stage.summary,
      disposition: {
        label: '处置 · 路由 / 验证',
        run: DISPOSITION_RUN[card.state],
        routes: DISPOSITION_ROUTES.map((r) => ({
          key: r.key,
          label: r.label,
          active: r.key === ROUTE_BY_STATE[card.state],
        })),
        ...DISPOSITION_VERIFY,
      },
    },
    detail: {
      goal: card.goal,
      goalSummary: GOAL_SUMMARY_BY_STATE[card.state],
      handoff: [
        { k: '目标', v: card.goalBrief },
        { k: '决策', v: DECISION_BY_STATE[card.state] },
        { k: '证据', v: card.evidence },
        { k: '待办', v: TODO_BY_STATE[card.state] },
        { k: '交接', v: `转交 ${card.agent} · ${card.branch}` },
      ],
      exec: {
        agent: card.agent,
        tone: CARD_STATE_COLOR[card.state],
        status: exec.status,
        step: exec.step,
        pct: exec.pct,
      },
      gate: {
        text: gate.text,
        action: gate.action,
        summary: `${gate.pending} 待处理`,
        pending: gate.pending > 0,
        tone: gate.pending > 0 ? 'var(--c-amber)' : 'var(--c-ts)',
      },
      runLogSummary: RUNLOG_SUMMARY_BY_STATE[card.state],
      runLog: RUNLOG_BY_STATE[card.state].map((l) => ({ ...l, text: fill(l.text) })),
    },
    deliverables: deliverablesFor(card),
    cost: { label: 'Token 预算', ...cost },
  }
}

/* ---------- Screen 2 · team assets ---------- */

export const ASSET_TABS = ['Rules · 12', 'Commands · 8', 'Skills · 34', 'MCP · 5'] as const

export type AssetKind = 'Rule' | 'Skill' | 'Command' | 'MCP'

export interface AssetCard {
  id: string
  kind: AssetKind
  name: string
  desc: string
  version: string
  usage: string
  height: number
  /** control-plane delivered but unhealthy — usage renders in the amber treatment */
  blocked?: boolean
}

export const ASSETS: AssetCard[] = [
  { id: 'py-style', kind: 'Rule', name: 'Python 代码风格 Rule', desc: '缩进 4 空格、类型注解、无 print 调试。', version: 'Acme · v2.1', usage: 'used 47', height: 130 },
  { id: 'issue-fix', kind: 'Skill', name: 'issue-fix 长任务模板', desc: '自动修复 issue 的标准骨架，含 evidence 收集与 quota gate。', version: '控制面投递 · v0.5.0', usage: '阻塞', blocked: true, height: 148 },
  { id: 'run-tests', kind: 'Command', name: 'run-tests Command', desc: '在隔离 worktree 中运行 pytest 并回写结果。', version: 'Acme · v1.3', usage: 'used 89', height: 148 },
  { id: 'pr-commit', kind: 'Skill', name: 'pr-commit 模板', desc: '生成 PR 描述、打磨提交信息、触发 CI。', version: 'Acme · v1.2', usage: 'used 72', height: 130 },
  { id: 'jira', kind: 'MCP', name: 'JIRA MCP 连接器', desc: '同步 issue、回写进度、索引项目知识。', version: 'Acme · v0.9', usage: 'used 56', height: 130 },
  { id: 'api-rule', kind: 'Rule', name: 'API 错误处理 Rule', desc: '统一 4xx/5xx 响应、trace_id 透传。', version: 'Atlas · v1.0', usage: 'used 33', height: 130 },
]

export const ASSET_KIND_STYLE: Record<AssetKind, { fg: string; bg: string; edge: string }> = {
  Rule: { fg: 'var(--c-amber)', bg: 'var(--c-warn-well)', edge: 'var(--c-amber)' },
  Skill: { fg: 'var(--c-emerald)', bg: 'var(--c-selected)', edge: 'var(--c-emerald-edge)' },
  Command: { fg: 'var(--c-blue)', bg: 'var(--c-cmd-well)', edge: 'var(--c-blue)' },
  MCP: { fg: 'var(--c-teal)', bg: 'var(--c-mcp-well)', edge: 'var(--c-teal)' },
}

export const ASSET_PREVIEW = {
  kind: 'Skill' as AssetKind,
  version: 'Acme · v1.2',
  name: 'pr-commit 模板',
  desc: '生成 PR 描述、打磨提交信息、触发 CI。',
  code: [
    'name: pr-commit',
    'runtime: loopdesk',
    'agents:',
    '  - claude',
    '  - codex',
    'stop_condition: evidence > 0.9',
  ],
  notice: '个人用户 · 仅可查看',
  action: '下发到团队（无权限）',
}

/* ---------- Screens 3 & 4 · settings tables ---------- */

export interface AgentRow {
  name: string
  provider: string
  runtime: string
  concurrency: string
  status: string
  statusTone: 'ok' | 'idle' | 'off' | 'warn'
  action: string
}

export const AGENT_COLUMNS = [
  { key: 'name', label: 'Agent', width: 200 },
  { key: 'provider', label: 'Provider', width: 160 },
  { key: 'runtime', label: '运行时', width: 160 },
  { key: 'concurrency', label: '最大并发', width: 120 },
  { key: 'status', label: '状态', width: 140 },
  { key: 'action', label: '操作', width: 120 },
]

export const AGENTS: AgentRow[] = [
  { name: 'claude', provider: 'Anthropic', runtime: 'claude-cli', concurrency: '4', status: '已连接', statusTone: 'ok', action: '配置' },
  { name: 'codex', provider: 'OpenAI', runtime: 'codex-cli', concurrency: '2', status: '已连接', statusTone: 'ok', action: '配置' },
  { name: 'pi', provider: '本地 Local', runtime: 'pi-runtime', concurrency: '1', status: '未配置', statusTone: 'warn', action: '去配置' },
]

export interface ConnectorRow {
  name: string
  type: string
  endpoint: string
  /** where the connector comes from — 配置直配 vs 插件携带 vs HTTP 接入 */
  source: string
  status: string
  statusTone: 'ok' | 'warn'
  action: string
}

/* Column widths re-cut to make room for 来源 — mirrors the canvas exactly. */
export const CONNECTOR_COLUMNS = [
  { key: 'name', label: '连接器', width: 170 },
  { key: 'type', label: '类型', width: 120 },
  { key: 'endpoint', label: '端点', width: 180 },
  { key: 'source', label: '来源', width: 150 },
  { key: 'status', label: '状态', width: 130 },
  { key: 'action', label: '操作', width: 120 },
]

export const CONNECTORS: ConnectorRow[] = [
  { name: 'JIRA', type: '项目管理', endpoint: 'https://jira.acme.com', source: '配置直配', status: '已连接', statusTone: 'ok', action: '配置' },
  { name: 'Plane', type: '项目管理', endpoint: 'https://plane.acme.com', source: '配置直配', status: '连接异常', statusTone: 'warn', action: '去重连' },
  { name: 'Confluence', type: '文档协作', endpoint: 'https://wiki.acme.com', source: '配置直配', status: '已连接', statusTone: 'ok', action: '配置' },
]

/** 3 条配置直配之外还有 2 条，它们不在同一张表里，用一行注脚说明 */
export const CONNECTOR_SOURCE_NOTE =
  '另 1 条经插件携带（随插件升级变动，不可单独删除）· 1 条为 HTTP 接入，凭据走 Bearer Token 环境变量'

/* ---------- Screen 5 · other config ---------- */

export interface ConfigRow {
  label: string
  value?: string
  /** values that read as paths, amounts or numbers use the mono face */
  mono?: boolean
  toggle?: string
}

export const CONFIG_CARDS: { title: string; rows: ConfigRow[] }[] = [
  {
    title: '成本与配额闸门',
    rows: [
      { label: '月度预算上限', value: '¥500.00', mono: true },
      { label: '单次任务成本上限', value: '¥20.00', mono: true },
      { label: '成本熔断阈值', value: '80%', mono: true },
    ],
  },
  {
    title: '安全策略闸门',
    rows: [
      { label: '危险命令拦截', toggle: '开启' },
      { label: '文件沙箱目录', value: '/sandbox/loopdesk', mono: true },
      { label: '网络访问策略', value: '仅白名单' },
    ],
  },
  {
    title: 'Worktree 隔离',
    rows: [
      { label: '每任务独立分支', toggle: '开启' },
      { label: '隔离根目录', value: '~/loopdesk/worktrees', mono: true },
      { label: '任务结束自动清理', toggle: '开启' },
    ],
  },
]

/* ---------- Screen 6 · session drawer ---------- */

export interface SessionRow {
  title: string
  meta: string
  time: string
  active?: boolean
}

export const SESSIONS: SessionRow[] = [
  { title: '修复 ACME-218 鉴权 401 问题', meta: 'claude · opus-4 · Acme', time: '2 小时前', active: true },
  { title: 'PRD 澄清：v0.2 渠道边界', meta: '模型澄清 · Nimbus', time: '昨天' },
  { title: '调研 Qdrant vs pgvector', meta: 'codex · gpt-4o · Atlas', time: '3 天前' },
  { title: '生成周报并归档到 Confluence', meta: 'claude · sonnet · Acme', time: '上周' },
  { title: 'pi 本地脚本调试 loop engine', meta: 'pi · local · Acme', time: '上周' },
]

/* ---------- Screens 7 & 8 · modal field specs ---------- */

export interface FieldSpec {
  label: string
  value?: string
  caret?: boolean
  hint?: string
  textarea?: boolean
  mono?: boolean
  muted?: boolean
}

export const ADD_AGENT_FIELDS: FieldSpec[] = [
  { label: 'Agent 标识', value: 'claude', hint: '全局唯一标识符，如 claude / codex', mono: true },
  { label: 'Provider', value: 'Anthropic', caret: true },
  { label: '运行时', value: 'claude-cli', caret: true, mono: true },
  { label: '最大并发', value: '4', hint: '并发上限 1–16，超出将排队', mono: true },
  { label: '描述（可选）', value: '可选：描述该 Agent 的用途与约束…', textarea: true, muted: true },
]

export const ADD_CONNECTOR_FIELDS: FieldSpec[] = [
  { label: '连接器名称', value: 'jira-prod', hint: '用于在工作台中标识该连接', mono: true },
  { label: '类型', value: '项目管理', caret: true },
  { label: '端点 URL', value: 'https://jira.acme.com', hint: '需以 https:// 开头，支持子路径', mono: true },
  { label: '认证方式', value: 'Bearer Token', caret: true },
  { label: 'Token', value: '••••••••••••', hint: '保存在本地加密存储，不会明文上传', mono: true, muted: true },
]

/* ---------- left rail ---------- */

export interface ProjectRow {
  name: string
  dot: 'blue' | 'amber' | 'emerald'
  count: string
  active?: boolean
}

export const PROJECTS: ProjectRow[] = [
  { name: 'Nimbus CLI', dot: 'blue', count: '4' },
  { name: 'Atlas Gateway', dot: 'amber', count: '3' },
  { name: 'Acme Platform', dot: 'emerald', count: '5', active: true },
]

export const DOT_COLOR: Record<string, string> = {
  blue: 'var(--c-blue)',
  amber: 'var(--c-amber)',
  emerald: 'var(--c-emerald)',
}

export const NAV_ITEMS: { key: NavKey; label: string; badge?: string }[] = [
  { key: 'board', label: '任务看板', badge: '12' },
  { key: 'assets', label: '团队资产' },
  { key: 'control', label: '控制中心' },
  { key: 'settings-agent', label: '设置' },
]

/* ============================================================
   Task-centric model
   Task is the first-class object; 会话 narrowed to a *channel*
   that carries the four manual actions below.
   ============================================================ */

/** 会话渠道 — the four manual actions a session can carry. */
export const CHANNEL_SCOPES = ['需求澄清', '背景查找', '任务澄清', '任务实施'] as const
export const CHANNEL_SCOPE_HINT = CHANNEL_SCOPES.join(' · ')

/* 右栏的六阶段 / 折叠区块文案已并入上方的 inspectorView 模型 ——
   它们现在按卡片生成，不再是页面级常量。 */

/* ---------- task-management form actions ---------- */

/** Per-column card actions: a task in flight is submitted for review;
 *  a task under review is approved or sent back. */
/* 卡片动作 —— 每枚按钮带一个动作 id，接线处据此决定落到哪个后端契约。
   网关目前只暴露**一个**任务状态转移端点（审批门裁决），所以四枚按钮
   都汇到它：通过 / 提交评审 / 状态 ▾ 预选「放行」，打回 预选「驳回」。
   模态窗里可以随时改选，因此实际裁决仍由用户决定。
   P1：`状态 ▾` 该换成真正的状态下拉，并配一个 `PATCH /tasks/{id}` 端点。 */
export type CardActionId = 'gate-approve' | 'gate-deny'

export const CARD_ACTIONS: Partial<Record<TaskColumnId, { id: CardActionId; label: string; primary?: boolean }[]>> = {
  doing: [
    { id: 'gate-approve', label: '提交评审', primary: true },
    { id: 'gate-approve', label: '状态 ▾' },
  ],
  review: [
    { id: 'gate-approve', label: '通过', primary: true },
    { id: 'gate-deny', label: '打回' },
  ],
}

/* ---------- C4 · 新建任务面板 ---------- */

export interface TaskTemplate {
  id: string
  name: string
  desc: string
}

export const TASK_TEMPLATES: TaskTemplate[] = [
  { id: 'issue-fix', name: 'issue-fix', desc: '从 issue 出发修复并验证' },
  { id: 'pr-commit', name: 'pr-commit', desc: '生成 PR 并打磨提交信息' },
  { id: 'auto-research', name: 'auto-research', desc: '自主检索并沉淀结论' },
  { id: 'free', name: '自由 · 无模板', desc: '纯意图描述，不套用工作流' },
]

export const NEW_TASK_DEFAULTS = {
  project: 'Acme Platform',
  issue: 'issue 链接，如 ACME-201',
  budget: '预算 $5.00',
  desc: '一句话描述要达成的目标与验收标准…',
  agent: 'claude · claude-cli',
  hint: '模板将预置 Loop 六阶段与停止条件',
}

/* ============================================================
   L1 任务控制面 (LoopX) × L2 能力供给面 (Codex) — 处置视图

   The two layers only ever touch at one place: the capability
   contract. L1 states what it needs (`required_capability`), L2
   declares what it can supply (`available_capability`), and the
   UI's job is to surface the gap between them — never to paper
   over it.  Every string below is copied verbatim from the canvas
   (frames 01 / 02 / 03 / 04 / 10).
   ============================================================ */

/* 看板右栏 · 处置（画布 34:1）已并入 inspectorView —— 路由与验证文案
   随 card.state 变化，因此不再有页面级常量。 */

/* ---------- 屏幕 10 · 任务详情（画布 34:132） ---------- */

export interface DetailTask {
  id: string
  title: string
  /** 由卡片的 state 推出，而不是照抄画布样例 */
  status: string
  statusTone: string
  /** 画布帧 10 是**模板**：这四项卡片本身不携带，对所有任务保持画布取值。 */
  priority: string
  owner: string
  assignee: string
  created: string
}

/** 卡片 state → 详情页状态标签。画布样例本身是一条 handoff 态任务，
 *  因此该档沿用画布措辞（修复中）；另两档复用看板自己的词表。 */
export const DETAIL_STATUS: Record<CardState, string> = {
  handoff: '修复中',
  gate: '评审中',
  delivered: '已交付',
}

export const DETAIL_TEMPLATE_META = {
  priority: 'P1',
  owner: '归属 Acme Platform',
  assignee: '负责人 FY',
  created: '创建 09-15 14:20',
}

/** 详情页只认"被点的那张卡"。`%ID%` / `%TITLE%` 在渲染前替换为卡片自己的
 *  id 与标题，详情页因此永远不会指向另一条任务 —— 这是画布帧 10 里
 *  TDS-412 与看板 ACME-* 两套编号并存问题的修复点。 */
export function detailView(id: string) {
  const card = allTasks().find((c) => c.id === id) ?? taskById(DEFAULT_TASK_ID)
  const task: DetailTask = {
    id: card.id,
    title: card.title,
    status: DETAIL_STATUS[card.state],
    statusTone: CARD_STATE_COLOR[card.state],
    ...DETAIL_TEMPLATE_META,
  }
  const fill = (s: string) => s.replace(/%ID%/g, task.id).replace(/%TITLE%/g, task.title)
  return {
    task,
    packet: PR_PACKET.map((r) => ({ ...r, v: fill(r.v) })),
    completionDef: COMPLETION_DEF,
    diffstat: DIFFSTAT,
    readiness: READINESS,
    hostGate: { ...HOST_GATE, arg: fill(HOST_GATE.arg) },
    receipt: RECEIPT,
    runLog: RUN_LOG_ROWS,
  }
}

export interface PackRow {
  k: string
  v: string
  mono?: boolean
  tone?: 'ok'
}

/** ① 评审包 · 8 段契约 —— pr_contract 校验通过的前提，缺一段不入评审。 */
export const PR_PACKET: PackRow[] = [
  { k: '① 动机', v: '为什么改：会话恢复后上下文丢失，重复澄清 3 次' },
  { k: '② 改动思路', v: '恢复前先回放 LOOP-STATE.json 的 goal 与约束' },
  { k: '③ 关键代码', v: 'src/session/restore.ts:41 注入回放钩子', mono: true },
  { k: '④ 具体改动', v: '新增 restoreContext()，3 个文件 +82 −11' },
  { k: '⑤ 修复后复现', v: '%ID% 复现脚本由 ✗ 转为 ✓' },
  { k: '⑥ 验证', v: 'npm test 全绿；12 项回归无新增失败' },
  { k: '⑦ 风险', v: '冷启动多一次磁盘读，预估 +18ms' },
  { k: '⑧ 关联 Issue', v: 'closes #412 · refs #398', mono: true, tone: 'ok' },
]

/** 完成定义 —— execution_profile.must_include + spend_rule，即"完成"的判据。 */
export const COMPLETION_DEF: PackRow[] = [
  { k: '必须包含', v: 'npm test 全绿 · 复现脚本由 ✗ 转 ✓' },
  { k: '花费规则', v: '≤ 2 轮重试 · 单任务 ≤ 40 万 token' },
  { k: '交付凭据', v: 'validation_receipt.json（含 diff 摘要与校验哈希）' },
]

export const DIFFSTAT = [
  { path: 'src/session/restore.ts', add: '+64', del: '−8' },
  { path: 'src/state/loop-state.ts', add: '+12', del: '−2' },
  { path: 'src/session/index.ts', add: '+6', del: '−1' },
]

/** 就绪检查 —— 交界契约的落地检查，阻断项必须显式标红而非静默通过。 */
export const READINESS: { ok: boolean; k: string; v: string }[] = [
  { ok: true, k: '运行时', v: 'codex-cli 已选定（4 选 1，无歧义）' },
  { ok: true, k: '技能', v: '已投递 3 个 loopx-* 技能' },
  { ok: false, k: '技能健康', v: '2 项 blocked · 作用域标记缺失' },
  { ok: false, k: '插件市场', v: 'openai-curated 等 2 个 manifest 缺失' },
]

/** 待宿主操作闸门 —— host_mutation.cli_can_mutate_directly = false。
 *  控制面能读回结果，但不能替宿主改配置：命令只交付，不代执行。 */
export const HOST_GATE = {
  warn: '控制面不会代改宿主配置 · 须在 Codex CLI 手动执行',
  cmd: '/goal <task_body>',
  arg: '%ID% · %TITLE%',
  copy: '复制',
  hint: '执行后由控制面读回结果',
}

export const RECEIPT: PackRow[] = [
  { k: '评审包', v: '8 段齐全 · pr_contract 校验通过' },
  { k: '验证', v: '✓ 修复通过 · npm test 12 / 12', tone: 'ok' },
  { k: '哈希', v: 'sha256:7f3a…c9e1', mono: true },
]

export const RUN_LOG_ROWS = [
  { id: '#3', text: '✓ 候选预检通过', time: '09-16 09:12', ok: true },
  { id: '#2', text: '✗ 复现失败 · 改动前基线', time: '09-16 09:04', ok: false },
  { id: '#1', text: '✗ 上下文缺失 · 需求澄清', time: '09-16 08:51', ok: false },
]

/* ---------- 屏幕 3 · 运行时接入（画布 34:21） ---------- */

export interface RuntimeHost {
  name: string
  loop: string
  entry: string
  status: string
  selected: boolean
  action: string
}

export const RUNTIME_GROUP = {
  title: '运行时接入',
  desc: 'LoopX 通过运行时适配器驱动 Codex 执行循环。同一台机器上四个宿主面的循环激活路径不同，必须明确选定其一。',
  hint: '输入 codex 会被控制面拒绝 —— 歧义值必须四选一，界面以受约束选择器呈现，不做自由文本。',
  columns: [
    { label: '运行时宿主面', width: 200 },
    { label: '宿主循环', width: 300 },
    { label: '入口命令', width: 168 },
    { label: '状态', width: 112 },
    { label: '操作', width: 120 },
  ],
  hosts: [
    { name: 'codex-cli', loop: '可见 Goal · Codex CLI TUI', entry: '$loopx <task>', status: '已选定', selected: true, action: '体检' },
    { name: 'codex-app', loop: '心跳自动化 · Codex 桌面应用', entry: '$loopx <task>', status: '可选', selected: false, action: '选定' },
    { name: 'codex-app-ssh', loop: '可见 Goal · SSH 场景回退', entry: '$loopx <task>', status: '可选', selected: false, action: '选定' },
    { name: 'codex-ide-plugin', loop: '可见 Goal · Codex IDE 插件', entry: '$loopx <task>', status: '可选', selected: false, action: '选定' },
  ] as RuntimeHost[],
}

/* ---------- 屏幕 4 · 插件与市场（画布 34:79） ---------- */

export interface MarketplaceRow {
  name: string
  source: string
  status: string
  /** the raw host error, shown under the status in mono */
  reason?: string
  tone: 'ok' | 'warn'
  action: string
}

export const MARKETPLACE_GROUP = {
  title: '插件与市场',
  desc: '扩展包来源与健康。单个市场加载失败不影响其它市场，受影响插件单独标记。',
  columns: [
    { label: '插件市场', width: 240 },
    { label: '来源', width: 150 },
    { label: '健康', width: 342 },
    { label: '操作', width: 120 },
  ],
  rows: [
    { name: 'openai-bundled', source: '本地快照', status: '正常 · 6 个插件已启用', tone: 'ok', action: '刷新快照' },
    { name: 'openai-primary-runtime', source: '本地快照', status: '正常 · 5 个插件已启用', tone: 'ok', action: '刷新快照' },
    {
      name: 'openai-curated',
      source: '本地快照',
      status: '加载失败',
      reason: 'marketplace root does not contain a supported manifest',
      tone: 'warn',
      action: '重新添加',
    },
    {
      name: 'openai-api-curated',
      source: '本地快照',
      status: '加载失败 · 1 个插件受影响',
      reason: 'marketplace root does not contain a supported manifest',
      tone: 'warn',
      action: '重新添加',
    },
  ] as MarketplaceRow[],
}

/* ---------- 屏幕 2 · 技能作用域与健康（画布 34:127） ---------- */

export const SKILL_SCOPE_BAR = {
  scope: '作用域 · codex-cli（CODEX_HOME/skills）',
  health: '阻塞 2 项：作用域标记缺失 · 技能包版本落后于控制面',
}

export const TEAM_ASSETS_HEADER = {
  title: '团队资产',
  desc: '个人用户仅可查看 Rules / Commands / Skills / MCP 等 AI 资产，按项目自动筛选。',
}

export const SETTINGS_MCP_HEADER = {
  title: 'MCP 与插件市场',
  desc: 'MCP 连接器按来源分两类：配置直配的可单独增删，随插件携带的只能随插件升级变动；插件市场各自独立健康。',
}
