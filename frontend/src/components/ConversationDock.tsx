import { useState } from 'react'
import { ArrowUp } from './icons'
import { CHANNEL_SCOPES } from '../data'

/* Conversation Dock — pinned under every workspace screen.
   The dock is the 会话 *channel*, not the primary object: besides the two
   selector chips it carries the four manual actions a session can serve
   (需求澄清 / 背景查找 / 任务澄清 / 任务实施), with 任务实施 active by default.
   Background is the canvas base with a single hairline rule on top. */

function Chip({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        height: 34,
        borderRadius: 8,
        boxShadow: 'inset 0 0 0 1px var(--c-chip)',
        padding: '0 10px',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        flexShrink: 0,
      }}
    >
      {children}
    </div>
  )
}

function Scope({ label, on, onClick }: { label: string; on: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        height: 26,
        borderRadius: 6,
        padding: '0 10px',
        background: on ? 'var(--c-selected)' : 'var(--c-rail)',
        boxShadow: `inset 0 0 0 1px ${on ? 'var(--c-emerald-edge)' : 'var(--c-chip)'}`,
        display: 'flex',
        alignItems: 'center',
        flexShrink: 0,
      }}
    >
      <span
        style={{
          fontSize: 11,
          fontWeight: on ? 500 : 400,
          color: on ? 'var(--c-emerald)' : 'var(--c-ts)',
          whiteSpace: 'nowrap',
        }}
      >
        {label}
      </span>
    </button>
  )
}

const caret = <span style={{ fontSize: 12, color: 'var(--c-ts)', lineHeight: 1 }}>▾</span>

export function ConversationDock() {
  const [scope, setScope] = useState<string>('任务实施')

  return (
    <div
      style={{
        flexShrink: 0,
        background: 'var(--c-base)',
        padding: '14px 24px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}
    >
      <div style={{ height: 1, background: 'var(--c-border)' }} />

      {/* selector row — agent / model, then the channel's four manual actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Chip>
          <span style={{ width: 7, height: 7, borderRadius: 3.5, background: 'var(--c-emerald)', flexShrink: 0 }} />
          <span style={{ fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--c-tp)' }}>claude</span>
          {caret}
        </Chip>

        <Chip>
          <span style={{ fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--c-blue)' }}>opus-4</span>
          {caret}
        </Chip>

        <div style={{ flex: 1, minWidth: 0 }} />

        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {CHANNEL_SCOPES.map((s) => (
            <Scope key={s} label={s} on={s === scope} onClick={() => setScope(s)} />
          ))}
        </div>
      </div>

      {/* input row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div
          style={{
            flex: 1,
            minWidth: 0,
            height: 48,
            borderRadius: 10,
            background: 'var(--c-rail)',
            boxShadow: 'inset 0 0 0 1px var(--c-chip)',
            padding: '0 16px',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <input
            placeholder="描述你的任务，或先与 Agent / 模型澄清需求…"
            style={{ flex: 1, fontSize: 13, color: 'var(--c-tp)' }}
            className="placeholder:text-[var(--c-tm)]"
          />
        </div>

        <button
          style={{
            width: 48,
            height: 48,
            borderRadius: 10,
            background: 'var(--c-emerald)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <ArrowUp size={20} style={{ color: 'var(--c-base)' }} />
        </button>
      </div>
    </div>
  )
}
