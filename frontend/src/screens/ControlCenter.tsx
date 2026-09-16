import { TopBar } from '../components/TopBar'
import { ConversationDock } from '../components/ConversationDock'

/* 控制中心 — the canvas defines this nav entry but no screen for it yet,
   so this placeholder stays on-brand: same Top Bar / dock chrome and the
   same card well as 设置 · 其他配置. */

const ROWS = [
  { label: '运行中 Agent', value: '3' },
  { label: '排队任务', value: '2' },
  { label: '今日 Token 消耗', value: '$1.84' },
  { label: '熔断状态', value: '正常' },
]

export function ControlCenter() {
  return (
    <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', background: 'var(--c-base)' }}>
      <TopBar />

      <div style={{ flex: 1, minHeight: 0, padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 20 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <span style={{ fontSize: 16, fontWeight: 600, color: 'var(--c-tp)' }}>控制中心</span>
          <span style={{ fontSize: 13, color: 'var(--c-ts)' }}>
            集中查看循环运行状态、配额消耗与闸门触发情况。
          </span>
        </div>

        <div
          style={{
            borderRadius: 10,
            background: 'var(--c-rail)',
            boxShadow: 'inset 0 0 0 1px var(--c-border)',
            padding: '10px 18px',
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
          }}
        >
          <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--c-tp)' }}>运行概览</div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {ROWS.map((r) => (
              <div
                key={r.label}
                style={{
                  height: 40,
                  padding: '0 2px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <span style={{ fontSize: 13, color: 'var(--c-ts)' }}>{r.label}</span>
                <span style={{ fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--c-tp)' }}>{r.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <ConversationDock />
    </div>
  )
}
