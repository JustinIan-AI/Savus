import { useState } from 'react'
import { ChevronDown, FolderIcon, SearchIcon } from './icons'

/* Top Bar — 56px, 20px padding, hairline bottom rule.
   Search 296px (narrowed from 320 so the avatar is no longer pushed
   under the inspector); agent pills 30px tall with a full 15px radius. */

function Pill({ dot, name, nameTone, status }: { dot: string; name: string; nameTone: string; status: string }) {
  return (
    <div
      style={{
        height: 30,
        borderRadius: 15,
        background: 'var(--c-surface)',
        boxShadow: 'inset 0 0 0 1px var(--c-chip)',
        padding: '0 10px',
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        flexShrink: 0,
      }}
    >
      <span style={{ width: 7, height: 7, borderRadius: 3.5, background: dot, flexShrink: 0 }} />
      <span style={{ fontFamily: 'var(--f-mono)', fontSize: 12, color: nameTone }}>{name}</span>
      <span style={{ fontFamily: 'var(--f-mono)', fontSize: 12, color: 'var(--c-tm)' }}>{status}</span>
    </div>
  )
}

export function TopBar() {
  const [projectMenuOpen, setProjectMenuOpen] = useState(false)
  const [currentProject, setCurrentProject] = useState('Acme Platform')
  return (
    <header
      style={{
        height: 56,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '0 20px',
        boxShadow: 'inset 0 -1px 0 0 var(--c-border-head)',
      }}
    >
      {/* project switcher with dropdown (L1) */}
      <div style={{ position: 'relative' }}>
        <button
          onClick={() => setProjectMenuOpen((o) => !o)}
          style={{
            height: 34,
            borderRadius: 8,
            background: 'var(--c-surface)',
            boxShadow: 'inset 0 0 0 1px var(--c-chip)',
            padding: '0 12px',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            flexShrink: 0,
            cursor: 'pointer',
          }}
        >
          <FolderIcon size={16} style={{ color: 'var(--c-ts)' }} />
          <span style={{ fontSize: 14, fontWeight: 500, color: 'var(--c-tp)' }}>{currentProject}</span>
          <ChevronDown size={14} style={{ color: 'var(--c-ts)' }} />
        </button>

        {projectMenuOpen && (
          <div
            style={{
              position: 'absolute',
              top: 40,
              left: 0,
              width: 200,
              background: 'var(--c-surface)',
              boxShadow: '0 8px 24px rgba(0,0,0,0.25), inset 0 0 0 1px var(--c-chip)',
              borderRadius: 8,
              padding: 6,
              zIndex: 100,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
            }}
          >
            {['Acme Platform', 'LoopDesk Core', 'Savus Runtime'].map((proj) => (
              <button
                key={proj}
                onClick={() => {
                  setCurrentProject(proj)
                  setProjectMenuOpen(false)
                }}
                style={{
                  height: 32,
                  padding: '0 10px',
                  borderRadius: 6,
                  display: 'flex',
                  alignItems: 'center',
                  fontSize: 13,
                  fontWeight: proj === currentProject ? 500 : 400,
                  color: proj === currentProject ? 'var(--c-tp)' : 'var(--c-ts)',
                  background: proj === currentProject ? 'var(--c-selected)' : 'transparent',
                  textAlign: 'left',
                  cursor: 'pointer',
                }}
              >
                {proj}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* search */}
      <div
        style={{
          width: 296,
          height: 34,
          borderRadius: 8,
          background: 'var(--c-surface)',
          boxShadow: 'inset 0 0 0 1px var(--c-chip)',
          padding: '0 12px',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          flexShrink: 0,
        }}
      >
        <SearchIcon size={16} style={{ color: 'var(--c-tm)' }} />
        <span style={{ fontSize: 13, color: 'var(--c-tm)', flex: 1, whiteSpace: 'nowrap', overflow: 'hidden' }}>
          搜索任务、资产或 agent…
        </span>
        <span
          style={{
            fontFamily: 'var(--f-mono)',
            fontSize: 11,
            color: 'var(--c-ts)',
            background: 'var(--c-rail)',
            boxShadow: 'inset 0 0 0 1px var(--c-kbd)',
            borderRadius: 5,
            padding: '1px 4px',
            flexShrink: 0,
          }}
        >
          Ctrl K
        </span>
      </div>

      <div style={{ flex: 1, minWidth: 0 }} />

      <Pill dot="var(--c-emerald)" name="claude" nameTone="var(--c-tp)" status="· 3 运行" />
      <Pill dot="var(--c-tm)" name="codex" nameTone="var(--c-ts)" status="· 空闲" />

      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: 16,
          background: 'var(--c-avatar)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <span style={{ fontFamily: 'var(--f-display)', fontSize: 12, fontWeight: 700, color: 'var(--c-tp)' }}>FY</span>
      </div>
    </header>
  )
}
