import { CloseIcon, PlusIcon, SearchIcon } from '../components/icons'
import { SESSIONS } from '../data'

/* ============================================================
   Screen 6 — 会话列表抽屉
   320px panel flush to the left edge on the #151922 surface, with an
   8/0/24 rgba(0,0,0,.45) shadow over a scrim that only covers the area
   to its right. The 新建会话 button is full-bleed (40px); the search row
   is a bare icon + placeholder (36px, no well); conversation rows are
   60px with a 3px emerald rail on the active one.
   ============================================================ */

interface Props {
  onClose: () => void
  onNewSession: () => void
}

export function SessionDrawer({ onClose, onNewSession }: Props) {
  return (
    <>
      <div
        style={{ position: 'absolute', left: 320, top: 0, right: 0, bottom: 0, background: 'rgba(7, 9, 13, 0.6)' }}
        onClick={onClose}
      />

      <aside
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: 320,
          height: '100%',
          background: 'var(--c-surface)',
          boxShadow: '8px 0 24px rgba(0, 0, 0, 0.45)',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* header — 56px, 18/14 insets */}
        <div
          style={{
            height: 56,
            flexShrink: 0,
            padding: '0 14px 0 18px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--c-tp)' }}>会话</span>
          <button
            onClick={onClose}
            style={{ width: 28, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <CloseIcon size={16} style={{ color: 'var(--c-ts)' }} />
          </button>
        </div>

        {/* new session — full-bleed, 40px, radius 8 */}
        <button
          onClick={onNewSession}
          style={{
            height: 40,
            width: '100%',
            flexShrink: 0,
            borderRadius: 8,
            background: 'var(--c-emerald)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
          }}
        >
          <PlusIcon size={14} style={{ color: 'var(--c-base)' }} />
          <span style={{ fontSize: 14, fontWeight: 500, color: 'var(--c-base)' }}>新建会话</span>
        </button>

        {/* search — bare row, 12px insets, no well */}
        <div
          style={{
            height: 36,
            flexShrink: 0,
            padding: '0 12px',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <SearchIcon size={16} style={{ color: 'var(--c-ts)' }} />
          <span style={{ fontSize: 13, color: 'var(--c-tm)' }}>搜索会话…</span>
        </div>

        <span
          style={{
            fontSize: 11,
            fontWeight: 500,
            lineHeight: '13px',
            color: 'var(--c-tm)',
          }}
        >
          最近
        </span>

        {/* conversations — 60px rows, hairline under each, 18/14 insets */}
        <div style={{ flex: 1, minHeight: 0, overflowY: 'auto' }}>
          {SESSIONS.map((s) => (
            <div
              key={s.title}
              style={{
                height: 60,
                padding: '0 14px 0 18px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                boxShadow: 'inset 0 -1px 0 0 var(--c-border-head)',
                cursor: 'pointer',
              }}
            >
              {s.active && (
                <span
                  style={{
                    width: 3,
                    height: 40,
                    borderRadius: 1.5,
                    background: 'var(--c-emerald)',
                    flexShrink: 0,
                    marginRight: 4,
                  }}
                />
              )}

              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 4,
                  minWidth: 0,
                  flex: 1,
                  paddingLeft: 30,
                }}
              >
                <span
                  style={{
                    fontSize: 13,
                    fontWeight: s.active ? 500 : 400,
                    color: 'var(--c-tp)',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {s.title}
                </span>
                <span
                  style={{
                    fontFamily: 'var(--f-mono)',
                    fontSize: 11,
                    color: 'var(--c-ts)',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {s.meta}
                </span>
              </div>

              <span style={{ fontSize: 11, color: 'var(--c-tm)', flexShrink: 0, marginLeft: 10 }}>{s.time}</span>
            </div>
          ))}
        </div>
      </aside>
    </>
  )
}
