import { SettingsShell, type SettingsTab } from './SettingsShell'
import { AGENTS, AGENT_COLUMNS, RUNTIME_GROUP } from '../data'

/* Screen 3 — 设置 · Agent 编排
   Table well is #0E1118 with #1B2030 hairlines; 44px header, 56px rows. */

const STATUS_TONE: Record<string, string> = {
  ok: 'var(--c-emerald)',
  idle: 'var(--c-ts)',
  off: 'var(--c-tm)',
  warn: 'var(--c-amber)',
}

interface Props {
  active: SettingsTab
  onTab: (t: SettingsTab) => void
  onAddAgent: () => void
}

export function SettingsAgent({ active, onTab, onAddAgent }: Props) {
  return (
    <SettingsShell
      active={active}
      onTab={onTab}
      title="Agent 编排"
      desc="注册并管理参与循环执行的 Agent 运行时，统一编排跨工具的任务流。"
      action="添加 Agent"
      onAction={onAddAgent}
    >
      <>
      <div
        style={{
          borderRadius: 10,
          background: 'var(--c-rail)',
          /* canvas strokes are drawn inside the frame and never shrink it */
          boxShadow: 'inset 0 0 0 1px var(--c-border)',
          overflow: 'hidden',
        }}
      >        {/* header */}
        <div
          style={{
            height: 44,
            padding: '0 16px',
            display: 'flex',
            alignItems: 'center',
            boxShadow: 'inset 0 -1px 0 0 var(--c-border)',
          }}
        >
          {AGENT_COLUMNS.map((c) => (
            <span
              key={c.key}
              style={{
                width: c.width,
                flexShrink: 0,
                fontSize: 12,
                fontWeight: 500,
                color: 'var(--c-ts)',
              }}
            >
              {c.label}
            </span>
          ))}
        </div>

        {/* rows */}
        {AGENTS.map((a, i) => (
          <div
            key={a.name}
            style={{
              height: 56,
              padding: '0 16px',
              display: 'flex',
              alignItems: 'center',
              boxShadow: i === AGENTS.length - 1 ? 'none' : 'inset 0 -1px 0 0 var(--c-border)',
            }}
          >
            <span
              style={{
                width: 200,
                flexShrink: 0,
                fontFamily: 'var(--f-mono)',
                fontSize: 14,
                fontWeight: 500,
                color: 'var(--c-tp)',
              }}
            >
              {a.name}
            </span>
            <span style={{ width: 160, flexShrink: 0, fontSize: 13, color: 'var(--c-tp)' }}>{a.provider}</span>
            <span style={{ width: 160, flexShrink: 0, fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--c-tp)' }}>
              {a.runtime}
            </span>
            <span style={{ width: 120, flexShrink: 0, fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--c-tp)' }}>
              {a.concurrency}
            </span>
            <span style={{ width: 140, flexShrink: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: 4,
                  background: STATUS_TONE[a.statusTone],
                  flexShrink: 0,
                }}
              />
              <span style={{ fontSize: 13, color: STATUS_TONE[a.statusTone] }}>{a.status}</span>
            </span>
            <span style={{ width: 120, flexShrink: 0 }}>
              <button
                style={{
                  borderRadius: 6,
                  boxShadow: `inset 0 0 0 1px ${a.statusTone === 'warn' ? 'var(--c-amber)' : 'var(--c-chip)'}`,
                  padding: '6px 12px',
                  fontSize: 13,
                  fontWeight: a.statusTone === 'warn' ? 500 : 400,
                  color: a.statusTone === 'warn' ? 'var(--c-amber)' : 'var(--c-ts)',
                }}
              >
                {a.action}
              </button>
            </span>
          </div>
        ))}
      </div>

      {/* 运行时接入 —— LoopX 是控制面，真正的循环在 Codex 宿主里跑。
          四个宿主面互斥，控制面拒绝裸 codex 这类歧义值，所以这里必须是
          受约束的选择器而不是自由文本输入。 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--c-tp)', lineHeight: '19px' }}>
            {RUNTIME_GROUP.title}
          </span>
          <span style={{ fontSize: 13, color: 'var(--c-ts)', lineHeight: '16px' }}>{RUNTIME_GROUP.desc}</span>
        </div>

        <div
          style={{
            borderRadius: 10,
            background: 'var(--c-rail)',
            boxShadow: 'inset 0 0 0 1px var(--c-border)',
            overflow: 'hidden',
          }}
        >
          <div style={{ height: 44, padding: '0 16px', display: 'flex', alignItems: 'center' }}>
            {RUNTIME_GROUP.columns.map((c) => (
              <span
                key={c.label}
                style={{ width: c.width, flexShrink: 0, fontSize: 12, fontWeight: 500, color: 'var(--c-ts)' }}
              >
                {c.label}
              </span>
            ))}
          </div>

          {RUNTIME_GROUP.hosts.map((h) => {
            const tone = h.selected ? 'var(--c-emerald)' : 'var(--c-tm)'
            return (
              <div
                key={h.name}
                style={{ height: 56, padding: '0 16px', display: 'flex', alignItems: 'center' }}
              >
                <span
                  style={{
                    width: 200,
                    flexShrink: 0,
                    fontFamily: 'var(--f-mono)',
                    fontSize: 14,
                    fontWeight: 500,
                    color: 'var(--c-tp)',
                  }}
                >
                  {h.name}
                </span>
                <span style={{ width: 300, flexShrink: 0, fontSize: 13, color: 'var(--c-tp)' }}>{h.loop}</span>
                <span
                  style={{ width: 168, flexShrink: 0, fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--c-blue)' }}
                >
                  {h.entry}
                </span>
                <span style={{ width: 112, flexShrink: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ width: 8, height: 8, borderRadius: 4, background: tone, flexShrink: 0 }} />
                  <span style={{ fontSize: 13, color: tone }}>{h.status}</span>
                </span>
                <span style={{ width: 120, flexShrink: 0 }}>
                  <button
                    style={{
                      borderRadius: 6,
                      boxShadow: 'inset 0 0 0 1px var(--c-chip)',
                      padding: '6px 12px',
                      fontSize: 13,
                      color: 'var(--c-ts)',
                    }}
                  >
                    {h.action}
                  </button>
                </span>
              </div>
            )
          })}
        </div>

        <div
          style={{
            borderRadius: 8,
            background: 'var(--c-warn-well)',
            padding: '9px 12px',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-amber)', flexShrink: 0 }}>!</span>
          <span style={{ fontSize: 12, color: 'var(--c-ts)', lineHeight: '16px' }}>{RUNTIME_GROUP.hint}</span>
        </div>
      </div>
      </>
    </SettingsShell>
  )
}
