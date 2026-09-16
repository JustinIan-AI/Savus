import { BoardIcon, AssetsIcon, ControlIcon, SettingsIcon, LogoMark, PlusIcon, ChatIcon } from './icons'
import { NAV_ITEMS, PROJECTS, DOT_COLOR, CHANNEL_SCOPE_HINT } from '../data'
import type { NavKey } from '../data'

interface Props {
  active: NavKey
  onNav: (k: NavKey) => void
  onNewTask: () => void
  onOpenChannel: () => void
}

const ICONS: Record<string, (p: { size?: number; style?: React.CSSProperties }) => JSX.Element> = {
  board: BoardIcon,
  assets: AssetsIcon,
  control: ControlIcon,
  'settings-agent': SettingsIcon,
}

/* Left Rail — 240px: flush 40px "新建任务" CTA (task is the first-class
   object), the 会话 · 渠道 card for manual actions, then 38px nav rows. */

function NavRow({
  navKey,
  label,
  badge,
  active,
  onNav,
}: {
  navKey: NavKey
  label: string
  badge?: string
  active: boolean
  onNav: (k: NavKey) => void
}) {
  const Icon = ICONS[navKey]
  const tone = active ? 'var(--c-emerald)' : 'var(--c-ts)'

  return (
    <button
      onClick={() => onNav(navKey)}
      style={{
        width: '100%',
        height: 38,
        borderRadius: 8,
        background: active ? 'var(--c-selected)' : 'transparent',
        padding: '0 10px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
      }}
    >
      {active && (
        <span
          style={{ width: 3, height: 16, borderRadius: 1.5, background: 'var(--c-emerald)', flexShrink: 0 }}
        />
      )}
      <Icon size={18} style={{ color: tone }} />
      <span style={{ fontSize: 14, fontWeight: active ? 500 : 400, color: active ? 'var(--c-tp)' : 'var(--c-ts)' }}>
        {label}
      </span>
      {badge && (
        <span
          style={{
            marginLeft: 2,
            padding: '0 6px',
            height: 18,
            borderRadius: 9,
            background: navKey === 'board' ? 'var(--c-amber-bg, rgba(217, 119, 6, 0.15))' : 'var(--c-border)',
            border: navKey === 'board' ? '1px solid rgba(217, 119, 6, 0.3)' : 'none',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: 'var(--f-mono)',
            fontSize: 11,
            color: navKey === 'board' ? 'var(--c-amber, #d97706)' : 'var(--c-ts)',
            gap: 4,
          }}
          title={navKey === 'board' ? '待审批 / 活动任务' : undefined}
        >
          {navKey === 'board' && (
            <span style={{ width: 6, height: 6, borderRadius: 3, background: 'var(--c-amber, #d97706)' }} />
          )}
          {badge}
        </span>
      )}
    </button>
  )
}

export function LeftRail({ active, onNav, onNewTask, onOpenChannel }: Props) {
  const isSettings = active.startsWith('settings')

  return (
    <aside
      style={{
        width: 240,
        flexShrink: 0,
        background: 'var(--c-rail)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* brand */}
      <div
        style={{
          height: 56,
          flexShrink: 0,
          padding: '0 16px',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          boxShadow: 'inset 0 -1px 0 0 var(--c-border-head)',
        }}
      >
        <LogoMark size={22} />
        <span
          style={{
            fontFamily: 'var(--f-display)',
            fontSize: 15,
            fontWeight: 700,
            color: 'var(--c-tp)',
            lineHeight: '20px',
          }}
        >
          LoopDesk
        </span>
        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-tm)', lineHeight: '13px' }}>
          v0.2
        </span>
      </div>

      {/* new task — flush to the rail edges, per the canvas.
          Task is the first-class object, so it owns the primary CTA. */}
      <button
        onClick={onNewTask}
        style={{
          width: '100%',
          height: 40,
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
        <span style={{ fontSize: 14, fontWeight: 500, color: 'var(--c-base)' }}>新建任务</span>
      </button>

      {/* session — a *channel* for manual actions, not the primary object */}
      <div style={{ flexShrink: 0, padding: '8px 12px 0' }}>
        <button
          onClick={onOpenChannel}
          style={{
            width: '100%',
            padding: 10,
            borderRadius: 8,
            background: 'var(--c-rail)',
            boxShadow: 'inset 0 0 0 1px var(--c-chip)',
            display: 'flex',
            flexDirection: 'column',
            gap: 3,
            textAlign: 'left',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <ChatIcon size={18} style={{ color: 'var(--c-ts)' }} />
            <span style={{ fontSize: 14, fontWeight: 500, color: 'var(--c-tp)', lineHeight: '18px' }}>会话</span>
            <div style={{ flex: 1, minWidth: 0 }} />
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-tm)', lineHeight: '12px' }}>
              渠道
            </span>
          </div>
          <span style={{ fontSize: 10, color: 'var(--c-tm)', lineHeight: '12px' }}>{CHANNEL_SCOPE_HINT}</span>
        </button>
      </div>

      {/* nav */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: 12 }}>
        {NAV_ITEMS.map((item) => (
          <NavRow
            key={item.key}
            navKey={item.key}
            label={item.label}
            badge={item.badge}
            active={item.key === 'settings-agent' ? isSettings : active === item.key}
            onNav={onNav}
          />
        ))}
      </nav>

      <div style={{ height: 24, flexShrink: 0 }} />

      {/* projects */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, padding: 8 }}>
        <span style={{ fontSize: 11, color: 'var(--c-tm)', paddingLeft: 4, lineHeight: '13px' }}>项目</span>
        {PROJECTS.map((p) => (
          <div
            key={p.name}
            style={{
              height: 34,
              borderRadius: 8,
              background: p.active ? 'var(--c-surface)' : 'transparent',
              boxShadow: p.active ? 'inset 0 0 0 1px var(--c-proj-active)' : 'none',
              padding: '0 12px',
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              cursor: 'pointer',
            }}
          >
            <span
              style={{ width: 8, height: 8, borderRadius: 4, background: DOT_COLOR[p.dot], flexShrink: 0 }}
            />
            <span
              style={{
                fontSize: 13,
                fontWeight: p.active ? 500 : 400,
                color: p.active ? 'var(--c-tp)' : 'var(--c-ts)',
              }}
            >
              {p.name}
            </span>
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 12, color: 'var(--c-tm)' }}>{p.count}</span>
          </div>
        ))}
      </div>
    </aside>
  )
}
