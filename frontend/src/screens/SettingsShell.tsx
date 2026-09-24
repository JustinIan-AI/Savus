import { createPTYSession, readPTYSession, writePTYSession } from "../lib/api";
import { TopBar } from '../components/TopBar'
import { ConversationDock } from '../components/ConversationDock'

/* ============================================================
   Settings shell — shared by screens 3 / 4 / 5.
   Inside the centre column: Top Bar, then a 220px sub-nav beside the
   content well, then the conversation dock. Content padding is
   24/28 with a 20px stack (8px on 其他配置, which uses tight cards).
   ============================================================ */

export type SettingsTab = 'settings-agent' | 'settings-mcp' | 'settings-other'

const SUB_NAV: { key: SettingsTab; label: string }[] = [
  { key: 'settings-agent', label: 'Agent 编排' },
  { key: 'settings-mcp', label: 'MCP 连接器' },
  { key: 'settings-other', label: '其他配置' },
]

interface Props {
  active: SettingsTab
  onTab: (t: SettingsTab) => void
  title: string
  desc: string
  action?: string
  onAction?: () => void
  gap?: number
  children: React.ReactNode
}

export function SettingsShell({ active, onTab, title, desc, action, onAction, gap = 20, children }: Props) {
  return (
    <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', background: 'var(--c-base)' }}>
      <TopBar />

      <div style={{ flex: 1, minHeight: 0, display: 'flex' }}>
        {/* sub-nav */}
        <nav
          style={{
            width: 220,
            flexShrink: 0,
            background: 'var(--c-rail)',
            padding: '24px 16px',
            display: 'flex',
            flexDirection: 'column',
            gap: 4,
          }}
        >
          <span style={{ fontSize: 11, color: 'var(--c-tm)', lineHeight: '13px', paddingLeft: 4 }}>配置中心</span>
          {SUB_NAV.map((s) => {
            const on = s.key === active
            return (
              <button
                key={s.key}
                onClick={() => onTab(s.key)}
                style={{
                  height: 40,
                  borderRadius: 8,
                  background: on ? 'var(--c-selected)' : 'transparent',
                  padding: '0 10px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                }}
              >
                {on && (
                  <span
                    style={{
                      width: 3,
                      height: 16,
                      borderRadius: 1.5,
                      background: 'var(--c-emerald)',
                      flexShrink: 0,
                    }}
                  />
                )}
                <span
                  style={{
                    fontSize: 14,
                    fontWeight: on ? 500 : 400,
                    lineHeight: '17px',
                    color: on ? 'var(--c-tp)' : 'var(--c-ts)',
                  }}
                >
                  {s.label}
                </span>
              </button>
            )
          })}
        </nav>

        {/* content */}
        <div
          style={{
            flex: 1,
            minWidth: 0,
            padding: '24px 28px',
            display: 'flex',
            flexDirection: 'column',
            gap,
            overflowY: 'auto',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexShrink: 0 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <span style={{ fontSize: 16, fontWeight: 600, color: 'var(--c-tp)', lineHeight: '19px' }}>{title}</span>
              <span style={{ fontSize: 13, color: 'var(--c-ts)', lineHeight: '16px' }}>{desc}</span>
            </div>

            {action && (
              <button
                onClick={onAction}
                style={{
                  height: 32,
                  borderRadius: 8,
                  background: 'var(--c-emerald)',
                  padding: '0 14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  flexShrink: 0,
                }}
              >
                <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--c-base)' }}>{action}</span>
              </button>
            )}
          </div>

          {children}
        </div>
      </div>

      <ConversationDock />
    </div>
  )
}
