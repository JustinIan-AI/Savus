import { useEffect } from 'react'
import { TopBar } from '../components/TopBar'
import { CloseIcon } from '../components/icons'
import { detailView, type DetailTask, type DetailAnchor } from '../data'

/** Everything on this page resolves from the card that was clicked. */
type DetailModel = ReturnType<typeof detailView>

/* ============================================================
   Screen 10 — 任务详情 · 处置 (canvas 34:132)

   This is where the two layers actually meet. The centre column is
   L2's *output* (what the runtime produced: the 8-segment review
   packet, the completion definition, the diff). The 360px panel is
   L1's *judgement* (readiness against the capability contract, and
   the commands the control plane must hand back to the host).

   The canvas draws this screen for one sample task (TDS-412). Here
   the header, the status tag and every `%ID%` / `%TITLE%` reference
   are bound to the opened card instead, so the page can never point
   at a different task than the one clicked.

   Note: unlike the board, the detail frame carries no conversation
   dock — the body runs the full 844px under the top bar.
   ============================================================ */

function SectionHead({ label, run }: { label: string; run: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <span style={{ fontSize: 11, color: 'var(--c-tm)', lineHeight: '15px' }}>{label}</span>
      <div style={{ flex: 1 }} />
      <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-tm)', lineHeight: '13px' }}>
        {run}
      </span>
    </div>
  )
}

/** Key/value row used by every card. `keyWidth` differs between the wide
    centre column (76) and the narrow panel (62). */
function Row({
  k,
  v,
  size = 12,
  keyWidth = 76,
  mono,
  tone,
}: {
  k: string
  v: string
  size?: number
  keyWidth?: number
  mono?: boolean
  tone?: 'ok'
}) {
  const lh = `${size + 4}px`
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <span
        style={{
          fontSize: size,
          fontWeight: 500,
          color: 'var(--c-tp)',
          lineHeight: lh,
          width: keyWidth,
          flexShrink: 0,
        }}
      >
        {k}
      </span>
      <span
        style={{
          fontFamily: mono ? 'var(--f-mono)' : 'var(--f-sans)',
          fontSize: size,
          color: tone === 'ok' ? 'var(--c-emerald)' : 'var(--c-ts)',
          lineHeight: lh,
          flex: 1,
          minWidth: 0,
          /* canvas text nodes are single-line: a wrapped value would push
             the fixed-height row out of its 32px box */
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}
      >
        {v}
      </span>
    </div>
  )
}

const CARD: React.CSSProperties = { borderRadius: 8, background: 'var(--c-rail)', width: '100%' }

function TaskHeader({ t }: { t: DetailTask }) {
  const sep = <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: '#3a4150', lineHeight: '15px' }}>·</span>
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-tm)', lineHeight: '15px' }}>
          {t.id}
        </span>
        <span
          style={{
            borderRadius: 4,
            background: 'var(--c-warn-well)',
            padding: '2px 6px',
            display: 'inline-flex',
            alignItems: 'center',
          }}
        >
          <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-amber)', lineHeight: '13px' }}>
            {t.priority}
          </span>
        </span>
        <span
          style={{
            borderRadius: 4,
            background: 'var(--c-selected)',
            padding: '2px 6px',
            display: 'inline-flex',
            alignItems: 'center',
          }}
        >
          <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: t.statusTone, lineHeight: '13px' }}>
            {t.status}
          </span>
        </span>
      </div>

      <span style={{ fontSize: 20, fontWeight: 600, color: 'var(--c-tp)', lineHeight: '26px' }}>{t.title}</span>

      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-tm)', lineHeight: '15px' }}>
          {t.owner}
        </span>
        {sep}
        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-tm)', lineHeight: '15px' }}>
          {t.assignee}
        </span>
        {sep}
        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-tm)', lineHeight: '15px' }}>
          {t.created}
        </span>
      </div>
    </div>
  )
}

function DetailBody({ view }: { view: DetailModel }) {
  const { task, packet, completionDef, diffstat } = view
  return (
    <div
      style={{
        flex: 1,
        minHeight: 0,
        overflowY: 'auto',
        padding: '20px 24px',
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
      }}
    >
      <TaskHeader t={task} />

      {/* ① 评审包 —— L2 交回来的 8 段契约；看板「交付物清单」的内链锚点 */}
      <div id="packet" style={{ display: 'flex', flexDirection: 'column', gap: 8, scrollMarginTop: 20 }}>
        <SectionHead label="评审包 · 8 段契约" run="pr_contract · 8 / 8" />
        <div style={{ ...CARD, padding: '8px 12px' }}>
          {packet.map((r) => (
            <div key={r.k} style={{ height: 32, display: 'flex', alignItems: 'center' }}>
              <Row k={r.k} v={r.v} mono={r.mono} tone={r.tone} />
            </div>
          ))}
        </div>
      </div>

      {/* 完成定义 —— must_include + spend_rule，即"完成"的判据 */}
      <div id="completion" style={{ display: 'flex', flexDirection: 'column', gap: 8, scrollMarginTop: 20 }}>
        <SectionHead label="完成定义 · 判定依据" run="execution_profile" />
        <div style={{ ...CARD, padding: 12, display: 'flex', flexDirection: 'column', gap: 9 }}>
          {completionDef.map((r) => (
            <Row key={r.k} k={r.k} v={r.v} size={11} mono={r.mono} tone={r.tone} />
          ))}
        </div>
      </div>

      {/* 变更文件 —— 让评审者不必离开工作台就能看到改动规模 */}
      <div id="diff" style={{ display: 'flex', flexDirection: 'column', gap: 8, scrollMarginTop: 20 }}>
        <SectionHead label={`变更文件 · ${diffstat.length}`} run="diff --stat" />
        <div style={{ ...CARD, padding: '8px 12px' }}>
          {diffstat.map((f) => (
            <div key={f.path} style={{ height: 30, display: 'flex', alignItems: 'center', gap: 12 }}>
              <span
                style={{
                  fontFamily: 'var(--f-mono)',
                  fontSize: 12,
                  color: 'var(--c-tp)',
                  lineHeight: '16px',
                  flex: 1,
                  minWidth: 0,
                }}
              >
                {f.path}
              </span>
              <span style={{ fontFamily: 'var(--f-mono)', fontSize: 12, color: 'var(--c-emerald)', lineHeight: '16px' }}>
                {f.add}
              </span>
              <span style={{ fontFamily: 'var(--f-mono)', fontSize: 12, color: 'var(--c-tm)', lineHeight: '16px' }}>
                {f.del}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function DisposePanel({ view, onClose }: { view: DetailModel; onClose: () => void }) {
  const { readiness, hostGate, receipt, runLog } = view
  return (
    <aside
      style={{
        width: 360,
        flexShrink: 0,
        background: '#10141c',
        /* canvas strokes sit inside the frame and never shrink it */
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
        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--c-tp)', lineHeight: '17px' }}>任务处置</span>
        <div style={{ flex: 1 }} />
        <button data-testid="detail-back" onClick={onClose} style={{ display: 'flex', alignItems: 'center' }}>
          <CloseIcon size={16} style={{ color: 'var(--c-tm)' }} />
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
          gap: 20,
        }}
      >
        {/* 就绪检查 —— 交界契约的阻断项必须显式暴露 */}
        <div id="readiness" style={{ display: 'flex', flexDirection: 'column', gap: 8, scrollMarginTop: 18 }}>
          <SectionHead label={`就绪检查 · ${readiness.length} 项`} run="agent-onboard" />
          <div style={{ ...CARD, padding: 12, display: 'flex', flexDirection: 'column', gap: 9 }}>
            {readiness.map((r) => {
              const tone = r.ok ? 'var(--c-emerald)' : 'var(--c-amber)'
              return (
                <div key={r.k} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span
                    style={{
                      fontFamily: 'var(--f-mono)',
                      fontSize: 11,
                      color: tone,
                      lineHeight: '15px',
                      width: 10,
                      flexShrink: 0,
                    }}
                  >
                    {r.ok ? '✓' : '✗'}
                  </span>
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 500,
                      color: 'var(--c-tp)',
                      lineHeight: '15px',
                      width: 62,
                      flexShrink: 0,
                    }}
                  >
                    {r.k}
                  </span>
                  <span
                    style={{
                      fontSize: 11,
                      color: r.ok ? 'var(--c-ts)' : 'var(--c-amber)',
                      lineHeight: '15px',
                      flex: 1,
                      minWidth: 0,
                    }}
                  >
                    {r.v}
                  </span>
                </div>
              )
            })}
          </div>
        </div>

        {/* 待宿主操作 —— cli_can_mutate_directly = false，命令只交付不代执行 */}
        <div id="host-gate" style={{ display: 'flex', flexDirection: 'column', gap: 8, scrollMarginTop: 18 }}>
          <SectionHead label="待宿主操作" run="host_mutation" />
          <div
            style={{
              borderRadius: 8,
              background: 'var(--c-warn-well)',
              padding: 12,
              display: 'flex',
              flexDirection: 'column',
              gap: 9,
            }}
          >
            <span style={{ fontSize: 11, color: 'var(--c-amber)', lineHeight: '15px' }}>{hostGate.warn}</span>

            <div
              style={{
                borderRadius: 6,
                background: 'var(--c-base)',
                padding: '8px 10px',
                display: 'flex',
                flexDirection: 'column',
                gap: 4,
              }}
            >
              <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-emerald)', lineHeight: '15px' }}>
                {hostGate.cmd}
              </span>
              <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-tm)', lineHeight: '13px' }}>
                {hostGate.arg}
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <button
                style={{
                  borderRadius: 5,
                  background: 'var(--c-selected)',
                  padding: '4px 8px',
                  display: 'flex',
                  alignItems: 'center',
                  flexShrink: 0,
                }}
              >
                <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-emerald)', lineHeight: '13px' }}>
                  {hostGate.copy}
                </span>
              </button>
              <span
                style={{
                  fontFamily: 'var(--f-mono)',
                  fontSize: 10,
                  color: 'var(--c-tm)',
                  lineHeight: '13px',
                  flex: 1,
                  minWidth: 0,
                }}
              >
                {hostGate.hint}
              </span>
            </div>
          </div>
        </div>

        {/* 交付凭据 —— 可离线校验的 Validation Receipt */}
        <div id="receipt" style={{ display: 'flex', flexDirection: 'column', gap: 8, scrollMarginTop: 18 }}>
          <SectionHead label="交付凭据" run="validation_receipt" />
          <div style={{ ...CARD, padding: 12, display: 'flex', flexDirection: 'column', gap: 9 }}>
            {receipt.map((r) => (
              <Row key={r.k} k={r.k} v={r.v} size={11} keyWidth={62} mono={r.mono} tone={r.tone} />
            ))}
          </div>
        </div>

        {/* 运行记录 —— 每次 run 的结果，失败也要留在台面上 */}
        <div id="run-log" style={{ display: 'flex', flexDirection: 'column', gap: 8, scrollMarginTop: 18 }}>
          <SectionHead label={`运行记录 · ${runLog.length} 次`} run="run_log" />
          <div style={{ ...CARD, padding: '8px 12px' }}>
            {runLog.map((l) => (
              <div key={l.id} style={{ height: 30, display: 'flex', alignItems: 'center', gap: 10 }}>
                <span
                  style={{
                    fontFamily: 'var(--f-mono)',
                    fontSize: 11,
                    color: 'var(--c-tm)',
                    lineHeight: '15px',
                    width: 26,
                    flexShrink: 0,
                  }}
                >
                  {l.id}
                </span>
                <span
                  style={{
                    fontSize: 11,
                    color: l.ok ? 'var(--c-emerald)' : 'var(--c-ts)',
                    lineHeight: '15px',
                    flex: 1,
                    minWidth: 0,
                  }}
                >
                  {l.text}
                </span>
                <span
                  style={{
                    fontFamily: 'var(--f-mono)',
                    fontSize: 10,
                    color: 'var(--c-tm)',
                    lineHeight: '13px',
                    width: 62,
                    flexShrink: 0,
                  }}
                >
                  {l.time}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </aside>
  )
}

export function TaskDetail({
  taskId,
  anchor,
  onBack,
}: {
  taskId: string
  /** 从看板「交付物清单」的内链进来时带的区块锚点 */
  anchor?: DetailAnchor
  onBack: () => void
}) {
  const view = detailView(taskId)

  /* 锚点分属两个滚动容器（中列 / 右栏），scrollIntoView 自己会找最近的
     可滚动祖先，因此一条调用就能覆盖两边。 */
  useEffect(() => {
    if (!anchor) return
    document.getElementById(anchor)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [anchor, taskId])

  return (
    <>
      <div
        style={{
          flex: 1,
          minWidth: 0,
          display: 'flex',
          flexDirection: 'column',
          background: 'var(--c-base)',
        }}
      >
        <TopBar />
        <DetailBody view={view} />
      </div>

      <DisposePanel view={view} onClose={onBack} />
    </>
  )
}
