import { SettingsShell, type SettingsTab } from './SettingsShell'
import { CONFIG_CARDS } from '../data'

/* Screen 5 — 设置 · 其他配置
   Three gate cards on the rail well, stacked with an 8px gutter.
   The rows are direct children of the card so they share its 12px gap
   (row pitch 52px) — padding 9/18, radius 10, exactly as in the canvas. */

interface Props {
  active: SettingsTab
  onTab: (t: SettingsTab) => void
}

export function SettingsOther({ active, onTab }: Props) {
  return (
    <SettingsShell
      active={active}
      onTab={onTab}
      title="其他配置"
      desc="配置成本闸门、安全策略与 worktree 隔离等全局运行约束。"
      action="导出配置"
      gap={8}
    >
      {CONFIG_CARDS.map((card) => (
        <div
          key={card.title}
          style={{
            borderRadius: 10,
            background: 'var(--c-rail)',
            boxShadow: 'inset 0 0 0 1px var(--c-border)',
            padding: '10px 18px',
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
            flexShrink: 0,
          }}
        >
          <div style={{ fontSize: 14, fontWeight: 600, lineHeight: '17px', color: 'var(--c-tp)' }}>
            {card.title}
          </div>

          {card.rows.map((r) => (
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

              {r.toggle ? (
                <span
                  style={{
                    borderRadius: 11,
                    background: 'var(--c-emerald)',
                    padding: '4px 10px',
                    display: 'inline-flex',
                    alignItems: 'center',
                  }}
                >
                  <span style={{ fontSize: 11, fontWeight: 500, color: 'var(--c-base)', lineHeight: '13px' }}>
                    {r.toggle}
                  </span>
                </span>
              ) : (
                <span
                  style={{
                    fontSize: 13,
                    color: 'var(--c-tp)',
                    fontFamily: r.mono ? 'var(--f-mono)' : 'var(--f-sans)',
                  }}
                >
                  {r.value}
                </span>
              )}
            </div>
          ))}
        </div>
      ))}
    </SettingsShell>
  )
}
