import { useState } from 'react'
import { ChevronDown, FolderIcon } from './icons'

/* Top Bar — 56px, 20px padding, hairline bottom rule.
   Search 296px; agent pills 30px tall with a full 15px radius. */

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

export function TopBar({
  projects = [],
  currentProjectId,
  onSelectProject,
}: {
  projects?: Array<{ id: string; name: string; mode?: string }>
  currentProjectId?: string
  onSelectProject?: (id: string) => void
}) {
  const [projectMenuOpen, setProjectMenuOpen] = useState(false)
  
  const currentProjObj = projects.find((p) => p.id === currentProjectId)
  const currentProjectName = currentProjObj?.name ?? '默认工作区'

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
          <span style={{ fontSize: 14, fontWeight: 500, color: 'var(--c-tp)' }}>{currentProjectName}</span>
          <ChevronDown size={14} style={{ color: 'var(--c-ts)' }} />
        </button>

        {projectMenuOpen && (
          <div
            style={{
              position: 'absolute',
              top: 40,
              left: 0,
              width: 220,
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
            {(projects.length > 0
              ? projects
              : [
                  { id: currentProjectId || 'default', name: currentProjectName },
                ]
            ).map((proj) => {
              const isSelected = proj.id === currentProjectId || proj.name === currentProjectName
              return (
                <button
                  key={proj.id}
                  onClick={() => {
                    if (onSelectProject) onSelectProject(proj.id)
                    setProjectMenuOpen(false)
                  }}
                  style={{
                    height: 32,
                    padding: '0 10px',
                    borderRadius: 6,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    fontSize: 13,
                    fontWeight: isSelected ? 500 : 400,
                    color: isSelected ? 'var(--c-tp)' : 'var(--c-ts)',
                    background: isSelected ? 'var(--c-selected)' : 'transparent',
                    textAlign: 'left',
                    cursor: 'pointer',
                  }}
                >
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {proj.name}
                  </span>
                  {proj.mode && (
                    <span
                      style={{
                        fontSize: 10,
                        padding: '1px 4px',
                        borderRadius: 3,
                        background: 'var(--c-chip)',
                        color: 'var(--c-tm)',
                        marginLeft: 6,
                        flexShrink: 0,
                      }}
                    >
                      {proj.mode}
                    </span>
                  )}
                </button>
              )
            })}
          </div>
        )}
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
