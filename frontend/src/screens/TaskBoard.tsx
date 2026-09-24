import { useState, useEffect, useRef } from 'react'
import { TopBar } from '../components/TopBar'
import { ConversationDock } from '../components/ConversationDock'
import { CloseIcon, PlusIcon } from '../components/icons'
import {
  boardColumns,
  cardsInColumn,
  CARD_STATE_TEXT,
  CARD_STATE_COLOR,
  STATUS_BADGE_TEXT,
  STATUS_BADGE_COLOR,
  AGENT_COLOR,
  CARD_ACTIONS,
  INSPECTOR_GROUP_RULES,
  TASK_STATUS_OPTIONS,
  SUBMIT_REVIEW_STATUS,
  inspectorView,
  taskById,
  taskStatusOf,
  type CardActionId,
  type Deliverable,
  type DetailAnchor,
  type TaskColumnId,
  type StageState,
} from '../data'

/* ============================================================
   Screen 1 — 任务看板 (default landing page)
   Board area: 20px padding, 16px gutters, four equal columns that all
   stay inside the centre track. Task is the first-class object: the
   board owns the create affordance and the in-card state transitions.
   Right panel is 360px on the #10141C well colour.

   单击卡片 = 选中（右栏跟随），不直接跳页；进入帧 10 的入口在右栏
   头部，以及交付物清单里的「内链」行。
   ============================================================ */

const TONE: Record<string, string> = {
  ts: 'var(--c-ts)',
  amber: 'var(--c-amber)',
  blue: 'var(--c-blue)',
}

/** 选中详情时的回调：卡片 id + 详情页里要滚到的区块。 */
export type OpenTask = (cardId: string, anchor?: DetailAnchor) => void

/** 「状态 ▾」菜单的实测高度（6 项 × 28px + 内边距 ≈ 190px）+ 余量。
    低于这个空间就向上弹，见 Card 里的 openMenu。 */
const STATUS_MENU_CLEARANCE = 202

/** Agent 芯片底色跟随 agent 色，claude 一档与画布样例逐字一致。 */
const AGENT_WELL: Record<string, string> = {
  claude: 'var(--c-selected)',
  codex: 'var(--c-cmd-well)',
  pi: 'var(--c-warn-well)',
}

function Card({
  id,
  selected,
  actions,
  onSelect,
  onAction,
  onSetStatus,
}: {
  id: string
  selected: boolean
  actions?: { id: CardActionId; label: string; primary?: boolean }[]
  onSelect: () => void
  /** 动作按钮的落点 —— 裁决类进模态，其余直接走 PATCH。 */
  onAction: (action: CardActionId) => void
  /** 「状态 ▾」选定后的落点：写后端，然后由 App 重新取快照。 */
  onSetStatus: (status: string) => void
}) {
  const t = taskById(id)
  /* 状态下拉自己管开合：它只影响这一张卡，不该让整个看板重渲染。
     向上还是向下弹由按钮的视口位置决定 —— 看板行是 overflow:hidden，
     照固定方向弹会让最后一张卡的菜单被裁掉。 */
  const [menuOpen, setMenuOpen] = useState(false)
  const [menuUp, setMenuUp] = useState(false)
  const actionsRef = useRef<HTMLDivElement | null>(null)
  const toggleRef = useRef<HTMLButtonElement | null>(null)
  const cardRef = useRef<HTMLDivElement | null>(null)
  const currentStatus = taskStatusOf(id)

  useEffect(() => {
    if (selected && cardRef.current) {
      cardRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [selected])

  useEffect(() => {
    if (!menuOpen) return
    const onDocMouseDown = (e: MouseEvent) => {
      if (!actionsRef.current?.contains(e.target as Node)) setMenuOpen(false)
    }
    document.addEventListener('mousedown', onDocMouseDown)
    return () => document.removeEventListener('mousedown', onDocMouseDown)
  }, [menuOpen])

  const openMenu = () => {
    const btn = toggleRef.current
    const column = btn?.closest('[data-column]') as HTMLElement | null
    const rect = btn?.getBoundingClientRect()
    /* 装在列里才不会被裁：看板行是 overflow:hidden，按视口高度判断会让
       靠下的卡片弹出一个下半截被切掉的菜单。以**所在列的底边**为准，
       装不下就向上弹。 */
    const limit = column ? column.getBoundingClientRect().bottom : window.innerHeight
    setMenuUp(!!rect && rect.bottom + STATUS_MENU_CLEARANCE > limit)
    setMenuOpen(true)
  }
  return (
    <div
      onClick={onSelect}
      ref={cardRef}
      /* 纯观测钩子（不产生任何像素）：端到端走查据此定位到具体卡片。 */
      data-card-id={id}
      style={{
        position: 'relative',
        width: '100%',
        borderRadius: 10,
        background: selected ? 'var(--c-selected)' : 'var(--c-surface)',
        /* canvas strokes do not consume layout space — an inset ring keeps the
           content box at the canvas' 140px instead of shrinking it to 138. */
        boxShadow: `inset 0 0 0 1px ${selected ? 'var(--c-emerald-edge)' : 'var(--c-divider)'}`,
        padding: 12,
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
        cursor: 'pointer',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 8,
          lineHeight: '14px',
        }}
      >
        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-tm)' }}>{t.id}</span>
        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: AGENT_COLOR[t.agent] }}>{t.agent}</span>
      </div>

      <div style={{ fontSize: 13, color: 'var(--c-tp)', lineHeight: '16px' }}>{t.title}</div>

      <div
        style={{
          alignSelf: 'flex-start',
          height: 20,
          borderRadius: 5,
          background: 'var(--c-rail)',
          padding: '0 7px',
          display: 'flex',
          alignItems: 'center',
          gap: 5,
        }}
      >
        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-blue)' }}>{t.branch}</span>
      </div>

      {(() => {
        const rawStatus = taskStatusOf(t.id)
        const badgeText = rawStatus ? (STATUS_BADGE_TEXT[rawStatus] ?? CARD_STATE_TEXT[t.state]) : CARD_STATE_TEXT[t.state]
        const badgeColor = rawStatus ? (STATUS_BADGE_COLOR[rawStatus] ?? CARD_STATE_COLOR[t.state]) : CARD_STATE_COLOR[t.state]
        return (
          <div style={{ fontSize: 11, color: badgeColor, lineHeight: '13px' }}>
            {badgeText}
          </div>
        )
      })()}

      {/* 任务管理动作 — 提交评审 / 状态下拉，或通过 / 打回 */}
      {actions && (
        <div ref={actionsRef} style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 6 }}>
          {actions.map((a) => (
            <button
              key={a.label}
              ref={a.id === 'set-status' ? toggleRef : undefined}
              data-action={a.id}
              aria-expanded={a.id === 'set-status' ? menuOpen : undefined}
              onClick={() => {
                if (a.id === 'set-status') {
                  if (menuOpen) setMenuOpen(false)
                  else openMenu()
                  return
                }
                onAction(a.id)
              }}
              style={{
                height: 26,
                borderRadius: 6,
                padding: '0 10px',
                background: a.primary ? 'var(--c-selected)' : 'var(--c-rail)',
                boxShadow: `inset 0 0 0 1px ${
                  a.primary || (a.id === 'set-status' && menuOpen) ? 'var(--c-emerald-edge)' : 'var(--c-chip)'
                }`,
                display: 'flex',
                alignItems: 'center',
                flexShrink: 0,
                cursor: 'pointer',
              }}
            >
              <span
                style={{
                  fontSize: 11,
                  fontWeight: a.primary ? 500 : 400,
                  color: a.primary ? 'var(--c-emerald)' : 'var(--c-ts)',
                  whiteSpace: 'nowrap',
                }}
              >
                {a.label}
              </span>
            </button>
          ))}

          {/* 状态下拉 —— 值与后端 LoopWorkspaceStatus 同名，选完即 PATCH。 */}
          {menuOpen && (
            <div
              data-testid={`status-menu-${id}`}
              style={{
                position: 'absolute',
                ...(menuUp ? { bottom: 32 } : { top: 32 }),
                left: 0,
                width: 152,
                background: 'var(--c-surface)',
                boxShadow: '0 8px 24px rgba(0,0,0,0.25), inset 0 0 0 1px var(--c-chip)',
                borderRadius: 8,
                padding: 6,
                zIndex: 120,
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
              }}
            >
              {TASK_STATUS_OPTIONS.map((o) => {
                const current = currentStatus === o.value
                return (
                  <button
                    key={o.value}
                    data-status-option={o.value}
                    data-current={current ? 'true' : 'false'}
                    onClick={() => {
                      setMenuOpen(false)
                      onSetStatus(o.value)
                    }}
                    style={{
                      height: 28,
                      padding: '0 10px',
                      borderRadius: 6,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      background: current ? 'var(--c-selected)' : 'transparent',
                      textAlign: 'left',
                      cursor: 'pointer',
                      flexShrink: 0,
                    }}
                  >
                    <span
                      style={{
                        fontFamily: 'var(--f-mono)',
                        fontSize: 11,
                        color: 'var(--c-emerald)',
                        lineHeight: '14px',
                        width: 8,
                        flexShrink: 0,
                      }}
                    >
                      {current ? '·' : ''}
                    </span>
                    <span
                      style={{
                        fontSize: 12,
                        fontWeight: current ? 500 : 400,
                        color: current ? 'var(--c-tp)' : 'var(--c-ts)',
                        lineHeight: '15px',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {o.label}
                    </span>
                  </button>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

/** 待办列顶部的创建入口 —— 点开 C4 新建任务表单。 */
function NewTaskTile({ onNewTask }: { onNewTask: () => void }) {
  return (
    <button
      onClick={onNewTask}
      style={{
        width: '100%',
        height: 44,
        flexShrink: 0,
        borderRadius: 10,
        boxShadow: 'inset 0 0 0 1px var(--c-chip)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 8,
      }}
    >
      <PlusIcon size={14} style={{ color: 'var(--c-emerald)' }} />
      <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--c-emerald)', lineHeight: '15px' }}>
        新建任务
      </span>
    </button>
  )
}

function Column({
  id,
  title,
  count,
  active,
  onNewTask,
  selectedId,
  onSelect,
  onAction,
  onSetStatus,
}: {
  id: TaskColumnId
  title: string
  count: number
  active?: boolean
  onNewTask: () => void
  selectedId: string
  onSelect: (cardId: string) => void
  onAction: (cardId: string, action: CardActionId) => void
  onSetStatus: (cardId: string, status: string) => void
}) {
  /* 列成员 = 画布种子 ⊕ 后端状态改写 ⊕ 后端追加，见 data.ts 的叠加层。 */
  const cards = cardsInColumn(id)
  return (
    <div
      data-column={id}
      style={{
        flex: 1,
        minWidth: 0,
        borderRadius: 10,
        background: 'var(--c-rail)',
        padding: 12,
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span
          style={{
            fontSize: 13,
            fontWeight: 600,
            lineHeight: '16px',
            color: active ? 'var(--c-emerald)' : 'var(--c-tp)',
          }}
        >
          {title}
        </span>
        <span
          style={{
            height: 18,
            borderRadius: 9,
            padding: '0 7px',
            background: active ? 'var(--c-selected)' : 'var(--c-border)',
            display: 'inline-flex',
            alignItems: 'center',
            fontFamily: 'var(--f-mono)',
            fontSize: 11,
            color: active ? 'var(--c-emerald)' : 'var(--c-ts)',
          }}
        >
          {count}
        </span>
        <div style={{ flex: 1 }} />
      </div>

      {id === 'todo' && <NewTaskTile onNewTask={onNewTask} />}

      <div
        style={{
          flex: 1,
          minHeight: 0,
          overflowY: 'auto',
          overflowX: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
          paddingRight: 2,
          paddingBottom: 8,
          scrollBehavior: 'smooth',
        }}
      >
        {cards.length === 0 ? (
          <div
            style={{
              padding: '24px 12px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              color: 'var(--c-tm)',
              border: '1px dashed var(--c-border)',
              borderRadius: 8,
            }}
          >
            <span style={{ fontSize: 20 }}>📭</span>
            <span style={{ fontSize: 12, color: 'var(--c-ts)' }}>暂无任务</span>
            <span style={{ fontSize: 11, color: 'var(--c-tm)' }}>点击上方 + 发起新循环</span>
          </div>
        ) : (
          cards.map((cid) => (
            <Card
              key={cid}
              id={cid}
              selected={cid === selectedId}
              actions={CARD_ACTIONS[id]}
              onSelect={() => onSelect(cid)}
              onAction={(a) => onAction(cid, a)}
              onSetStatus={(s) => onSetStatus(cid, s)}
            />
          ))
        )}
      </div>
    </div>
  )
}

/* ============================================================
   右栏 · 任务检视器

   整块内容按被选中的卡片生成，规则是三段加一个尾部：
     ① 任务状态   ← card.state
     ② 详情       ← card 字段
     ③ 交付物清单 ← card.state（产出物 + 链接）
     尾部         成本 / 配额，这一次运行的资源消耗
   面板因此不持有自己的文案，也就不会与看板脱钩。
   ============================================================ */

type InspectorView = ReturnType<typeof inspectorView>

/** 分组标题 —— 段名 + 生成依据；与 pr_contract / run_log 同一种标注语言。 */
function GroupHead({ label, rule }: { label: string; rule: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--c-ts)', lineHeight: '16px' }}>{label}</span>
      <div style={{ flex: 1 }} />
      <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-tm)', lineHeight: '13px' }}>
        {rule}
      </span>
    </div>
  )
}

/** Small section heading used by every block in the inspector. */
function Label({ children }: { children: React.ReactNode }) {
  return <div style={{ fontSize: 11, color: 'var(--c-tm)', lineHeight: '13px' }}>{children}</div>
}

const STAGE_STYLE: Record<StageState, React.CSSProperties> = {
  done: { background: 'var(--c-selected)', color: 'var(--c-emerald)' },
  current: { background: 'var(--c-warn-well)', boxShadow: 'inset 0 0 0 1px var(--c-amber)', color: 'var(--c-amber)' },
  todo: { background: 'var(--c-rail)', color: 'var(--c-tm)' },
}

/** 三级区块 —— 默认折叠，术语不再铺在顶层。 */
function Accordion({
  label,
  summary,
  summaryTone,
  open,
  onToggle,
  children,
}: {
  label: string
  summary: string
  summaryTone?: string
  open: boolean
  onToggle: () => void
  children: React.ReactNode
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <button
        onClick={onToggle}
        style={{
          height: 28,
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 8,
        }}
      >
        <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--c-ts)', lineHeight: '15px' }}>
          {open ? '▾' : '▸'}  {label}
        </span>
        <span
          style={{
            fontFamily: 'var(--f-mono)',
            fontSize: 11,
            lineHeight: '14px',
            color: summaryTone ?? 'var(--c-tm)',
          }}
        >
          {summary}
        </span>
      </button>

      {open && children}
    </div>
  )
}

/* ---------- ① 任务状态 ---------- */

function StatusGroup({ view }: { view: InspectorView }) {
  const { card, status } = view
  const d = status.disposition
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <GroupHead label="任务状态" rule={INSPECTOR_GROUP_RULES.status} />

      {/* 概览 —— 第三枚芯片就是这条任务的状态，随 card.state 换色换词 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 12, color: 'var(--c-tm)', lineHeight: '16px' }}>
          {card.id}
        </span>
        <span style={{ fontSize: 16, fontWeight: 500, color: 'var(--c-tp)', lineHeight: '19px' }}>{card.title}</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span
            style={{
              height: 22,
              borderRadius: 5,
              background: AGENT_WELL[card.agent],
              padding: '0 8px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 5,
            }}
          >
            <span style={{ width: 6, height: 6, borderRadius: 3, background: AGENT_COLOR[card.agent] }} />
            <span
              style={{
                fontFamily: 'var(--f-mono)',
                fontSize: 11,
                color: AGENT_COLOR[card.agent],
                lineHeight: '15px',
              }}
            >
              {card.agent}
            </span>
          </span>
          <span
            style={{
              height: 22,
              borderRadius: 5,
              background: 'var(--c-rail)',
              padding: '0 8px',
              display: 'inline-flex',
              alignItems: 'center',
            }}
          >
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-blue)', lineHeight: '15px' }}>
              {card.branch}
            </span>
          </span>
          <span
            style={{
              height: 22,
              borderRadius: 5,
              background: 'var(--c-rail)',
              padding: '0 8px',
              display: 'inline-flex',
              alignItems: 'center',
            }}
          >
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: status.tone, lineHeight: '15px' }}>
              {status.label}
            </span>
          </span>
        </div>
      </div>

      {/* 进度 —— 六阶段按 state 推进 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
          <span style={{ fontSize: 11, color: 'var(--c-tm)', lineHeight: '13px' }}>进度 · Loop 六阶段</span>
          <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-tm)', lineHeight: '13px' }}>
            简化视图 ▾
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          {status.stages.map((s) => (
            <div
              key={s.label}
              style={{
                padding: '5px 8px',
                borderRadius: 5,
                display: 'flex',
                alignItems: 'center',
                ...STAGE_STYLE[s.state],
              }}
            >
              <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, lineHeight: '13px' }}>{s.label}</span>
            </div>
          ))}
        </div>

        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-tm)', lineHeight: '13px' }}>
          {status.stageSummary}
        </span>
      </div>

      {/* 处置 —— 分诊路由（三选一）+ 两段式验证徽标。
          验证必须同时呈现"改动前失败 / 改动后通过"，单看结果无法判断
          修复是否真的生效。 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 11, color: 'var(--c-tm)', lineHeight: '13px' }}>{d.label}</span>
          <div style={{ flex: 1 }} />
          <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-tm)', lineHeight: '13px' }}>
            {d.run}
          </span>
        </div>

        <div
          style={{
            borderRadius: 8,
            background: 'var(--c-rail)',
            padding: 12,
            display: 'flex',
            flexDirection: 'column',
            gap: 9,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {d.routes.map((r) => (
              <span
                key={r.key}
                style={{
                  borderRadius: 5,
                  background: r.active ? 'var(--c-selected)' : 'var(--c-rail)',
                  padding: '5px 8px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  flexShrink: 0,
                }}
              >
                <span
                  style={{
                    fontFamily: 'var(--f-mono)',
                    fontSize: 10,
                    color: r.active ? 'var(--c-emerald)' : 'var(--c-ts)',
                    lineHeight: '13px',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {r.label}
                </span>
              </span>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 11, color: 'var(--c-tm)', lineHeight: '14px' }}>{d.key}</span>
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-tm)', lineHeight: '14px' }}>
              {d.repro}
            </span>
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-tm)', lineHeight: '13px' }}>→</span>
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-emerald)', lineHeight: '14px' }}>
              {d.validated}
            </span>
            <div style={{ flex: 1 }} />
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-tm)', lineHeight: '13px' }}>
              {d.cmd}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ---------- ② 详情 ---------- */

function DetailGroup({
  view,
  open,
  toggle,
}: {
  view: InspectorView
  open: Record<string, boolean>
  toggle: (k: string) => void
}) {
  const { detail } = view
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <GroupHead label="详情" rule={INSPECTOR_GROUP_RULES.detail} />

      {/* Goal（默认折叠） */}
      <Accordion
        label="Goal · 目标"
        summary={detail.goalSummary}
        open={!!open.goal}
        onToggle={() => toggle('goal')}
      >
        <div style={{ fontSize: 13, color: 'var(--c-ts)', lineHeight: '20px' }}>{detail.goal}</div>
      </Accordion>

      {/* Handoff 上下文包 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <Label>Handoff 上下文包</Label>
        <div
          style={{
            borderRadius: 8,
            background: 'var(--c-rail)',
            boxShadow: 'inset 0 0 0 1px var(--c-divider)',
            padding: 12,
            display: 'flex',
            flexDirection: 'column',
            gap: 9,
          }}
        >
          {detail.handoff.map((h) => (
            <div key={h.k} style={{ display: 'flex', gap: 10 }}>
              <span
                style={{
                  fontFamily: 'var(--f-mono)',
                  fontSize: 11,
                  color: 'var(--c-tm)',
                  width: 48,
                  flexShrink: 0,
                  lineHeight: '14px',
                }}
              >
                {h.k}
              </span>
              <span style={{ fontSize: 12, color: 'var(--c-ts)', flex: 1, minWidth: 0, lineHeight: '15px' }}>
                {h.v}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Agent 执行 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <Label>Agent 执行</Label>
        <div
          style={{
            borderRadius: 8,
            background: 'var(--c-rail)',
            boxShadow: 'inset 0 0 0 1px var(--c-divider)',
            padding: 12,
            display: 'flex',
            flexDirection: 'column',
            gap: 10,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 8, height: 8, borderRadius: 4, background: detail.exec.tone, flexShrink: 0 }} />
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 12, color: 'var(--c-tp)', lineHeight: '16px' }}>
              {detail.exec.agent}
            </span>
            <span style={{ fontSize: 12, color: 'var(--c-ts)', lineHeight: '15px' }}>{detail.exec.status}</span>
            <div style={{ flex: 1 }} />
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-tm)', lineHeight: '14px' }}>
              {detail.exec.step}
            </span>
          </div>
          <div style={{ height: 4, borderRadius: 2, background: 'var(--c-border)', overflow: 'hidden' }}>
            <div
              style={{
                width: `${detail.exec.pct * 100}%`,
                height: 4,
                borderRadius: 2,
                background: detail.exec.tone,
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

/* ---------- ③ 交付物清单 ---------- */

/** 一行交付物。外链是新窗口打开的真实形态地址，内链跳进详情页的对应区块 ——
 *  两者用同一行的第三列区分，不靠颜色。 */
function DeliverableRow({ d, onOpenAnchor }: { d: Deliverable; onOpenAnchor: (a: DetailAnchor) => void }) {
  const rowStyle: React.CSSProperties = {
    width: '100%',
    height: 26,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    textAlign: 'left',
  }
  const body = (
    <>
      <span
        style={{
          fontFamily: d.kind === 'external' ? 'var(--f-mono)' : 'var(--f-sans)',
          fontSize: 11,
          color: 'var(--c-tp)',
          lineHeight: '15px',
          width: 110,
          flexShrink: 0,
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}
      >
        {d.name}
      </span>
      <span
        style={{
          fontFamily: 'var(--f-mono)',
          fontSize: 10,
          color: 'var(--c-tm)',
          lineHeight: '13px',
          flex: 1,
          minWidth: 0,
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}
      >
        {d.target}
      </span>
      <span
        style={{
          fontFamily: 'var(--f-mono)',
          fontSize: 11,
          color: 'var(--c-emerald)',
          lineHeight: '15px',
          flexShrink: 0,
        }}
      >
        {d.kind === 'external' ? '外链' : '内链'}
      </span>
    </>
  )

  if (d.kind === 'external') {
    return (
      <a href={d.href} target="_blank" rel="noreferrer" style={{ ...rowStyle, textDecoration: 'none' }}>
        {body}
      </a>
    )
  }
  return (
    <button onClick={() => d.anchor && onOpenAnchor(d.anchor)} style={rowStyle}>
      {body}
    </button>
  )
}

function DeliverablesGroup({
  view,
  open,
  toggle,
  onOpenAnchor,
}: {
  view: InspectorView
  open: Record<string, boolean>
  toggle: (k: string) => void
  onOpenAnchor: (a: DetailAnchor) => void
}) {
  const { deliverables, detail } = view
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <GroupHead
        label="交付物清单"
        rule={`${INSPECTOR_GROUP_RULES.deliverables} · ${deliverables.length} 项`}
      />

      <div
        style={{
          borderRadius: 8,
          background: 'var(--c-rail)',
          padding: '8px 12px',
          display: 'flex',
          flexDirection: 'column',
          gap: 0,
        }}
      >
        {deliverables.map((d) => (
          <DeliverableRow key={d.name} d={d} onOpenAnchor={onOpenAnchor} />
        ))}
      </div>

      {/* 三级 · 审批门（默认折叠，摘要保留琥珀信号） */}
      <Accordion
        label="审批门 · operator gate"
        summary={detail.gate.summary}
        summaryTone={detail.gate.tone}
        open={!!open.gate}
        onToggle={() => toggle('gate')}
      >
        <div
          style={{
            borderRadius: 8,
            background: detail.gate.pending ? 'var(--c-warn-well)' : 'var(--c-rail)',
            boxShadow: `inset 0 0 0 1px ${detail.gate.tone}`,
            padding: 10,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
          }}
        >
          <span style={{ width: 8, height: 8, borderRadius: 4, background: detail.gate.tone, flexShrink: 0 }} />
          <span style={{ fontSize: 12, color: 'var(--c-tp)' }}>{detail.gate.text}</span>
          <div style={{ flex: 1 }} />
          <button
            style={{
              width: 88,
              height: 26,
              borderRadius: 6,
              background: detail.gate.pending ? 'var(--c-warn-well)' : 'var(--c-rail)',
              boxShadow: `inset 0 0 0 1px ${detail.gate.tone}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: 'var(--f-mono)',
              fontSize: 11,
              color: detail.gate.tone,
              flexShrink: 0,
            }}
          >
            {detail.gate.action}
          </button>
        </div>
      </Accordion>

      {/* 三级 · Run Log（默认折叠） */}
      <Accordion
        label="Run Log"
        summary={detail.runLogSummary}
        open={!!open.runLog}
        onToggle={() => toggle('runLog')}
      >
        <div
          style={{
            borderRadius: 8,
            background: 'var(--c-base)',
            boxShadow: 'inset 0 0 0 1px var(--c-divider)',
            padding: 12,
            display: 'flex',
            flexDirection: 'column',
            gap: 6,
          }}
        >
          {detail.runLog.map((l) => (
            <div
              key={l.text}
              style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: TONE[l.tone], lineHeight: '16px' }}
            >
              {l.text}
            </div>
          ))}
        </div>
      </Accordion>
    </div>
  )
}

/* ---------- 尾部 · 成本 / 配额 ---------- */

function CostBlock({ cost }: { cost: InspectorView['cost'] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <Label>成本 / 配额</Label>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 12, color: 'var(--c-ts)', lineHeight: '15px' }}>{cost.label}</span>
        <div style={{ flex: 1 }} />
        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-tm)', lineHeight: '14px' }}>
          {cost.value}
        </span>
      </div>
      <div style={{ height: 6, borderRadius: 3, background: 'var(--c-border)', overflow: 'hidden' }}>
        <div style={{ width: `${cost.pct * 100}%`, height: 6, borderRadius: 3, background: 'var(--c-emerald)' }} />
      </div>
      <div style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-tm)', lineHeight: '14px' }}>
        {cost.note}
      </div>
    </div>
  )
}

function Inspector({
  taskId,
  onOpenTask,
  onClose,
}: {
  taskId: string
  onOpenTask: (cardId: string, anchor?: DetailAnchor) => void
  onClose?: () => void
}) {
  const view = inspectorView(taskId)
  const [open, setOpen] = useState<Record<string, boolean>>({})
  const toggle = (k: string) => setOpen((o) => ({ ...o, [k]: !o[k] }))

  return (
    <aside
      style={{
        width: 360,
        flexShrink: 0,
        background: '#10141c',
        /* canvas strokes sit *inside* the frame and never shrink it, so the
           panel keeps its full 360px and its content lands on x=1098. */
        boxShadow: 'inset 1px 0 0 0 var(--c-border-head)',
        display: 'flex',
        flexDirection: 'column',
        minHeight: 0,
      }}
    >
      <div
        style={{
          height: 56,
          flexShrink: 0,
          padding: '0 18px',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          boxShadow: 'inset 0 -1px 0 0 var(--c-border-head)',
        }}
      >
        <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--c-tp)', lineHeight: '17px' }}>任务检视器</span>
        <div style={{ flex: 1 }} />
        {/* 单击卡片只选中；进帧 10 走这里 */}
        <button
          onClick={() => onOpenTask(taskId)}
          style={{
            height: 20,
            borderRadius: 5,
            background: 'var(--c-selected)',
            padding: '0 8px',
            display: 'flex',
            alignItems: 'center',
            flexShrink: 0,
          }}
        >
          <span style={{ fontSize: 10, color: 'var(--c-emerald)', lineHeight: '13px' }}>查看详情 →</span>
        </button>
        {/* IconProps 不收 onClick —— 直接挂在 svg 上会被 React 静默丢弃。
            包一层 button（与弹窗头部同一种写法），折叠才真的生效。 */}
        <button data-testid="inspector-close" onClick={onClose} title="折叠右栏 (⌘B)" style={{ display: 'flex' }}>
          <CloseIcon size={16} style={{ color: 'var(--c-tm)', cursor: 'pointer' }} />
        </button>
      </div>

      <div
        style={{
          flex: 1,
          minHeight: 0,
          overflowY: 'auto',
          padding: 18,
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
        }}
      >
        <StatusGroup view={view} />
        <DetailGroup view={view} open={open} toggle={toggle} />
        <DeliverablesGroup
          view={view}
          open={open}
          toggle={toggle}
          onOpenAnchor={(a) => onOpenTask(taskId, a)}
        />
        <CostBlock cost={view.cost} />
      </div>
    </aside>
  )
}

export function TaskBoard({
  onNewTask,
  onOpenTask,
  selectedId,
  onSelect,
  onGate,
  onSetStatus,
  projects = [],
  currentProjectId,
  onSelectProject,
}: {
  onNewTask: () => void
  onOpenTask: OpenTask
  selectedId: string
  onSelect: (cardId: string) => void
  /** 卡片动作 → 打开审批门裁决模态，并预选一个裁决（打回 = 驳回）。 */
  onGate: (cardId: string, initialDecision: 'approved' | 'denied') => void
  /** 卡片动作「提交评审」/「状态 ▾」→ PATCH 状态，不经过裁决模态。 */
  onSetStatus: (cardId: string, status: string) => void
  projects?: Array<{ id: string; name: string; mode?: string }>
  currentProjectId?: string
  onSelectProject?: (id: string) => void
}) {
  const [collapsed, setCollapsed] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'b') {
        e.preventDefault()
        setCollapsed((c) => !c)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <>
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', background: 'var(--c-base)' }}>
        <TopBar projects={projects} currentProjectId={currentProjectId} onSelectProject={onSelectProject} />

        <div
          style={{
            flex: 1,
            minHeight: 0,
            display: 'flex',
            gap: 16,
            padding: 20,
            overflow: 'hidden',
          }}
        >
          {boardColumns().map((c) => (
            <Column
              key={c.id}
              id={c.id}
              title={c.title}
              count={c.count}
              active={c.active}
              onNewTask={onNewTask}
              selectedId={selectedId}
              onSelect={onSelect}
              onSetStatus={onSetStatus}
              /* 裁决类动作进模态；「提交评审」是纯状态移动，直接 PATCH。 */
              onAction={(cid, action) => {
                if (action === 'start-task') {
                  onSetStatus(cid, 'active')
                } else if (action === 'submit-review') {
                  onSetStatus(cid, SUBMIT_REVIEW_STATUS)
                } else {
                  onGate(cid, action === 'gate-deny' ? 'denied' : 'approved')
                }
              }}
            />
          ))}
        </div>

        <ConversationDock />
      </div>

      {!collapsed && (
        <Inspector
          taskId={selectedId}
          onOpenTask={onOpenTask}
          onClose={() => setCollapsed(true)}
        />
      )}
    </>
  )
}
