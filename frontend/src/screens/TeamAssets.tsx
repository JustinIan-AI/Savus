import { useState } from 'react'
import { TopBar } from '../components/TopBar'
import { ConversationDock } from '../components/ConversationDock'
import { CloseIcon, FolderIcon, LockIcon, SearchIcon } from '../components/icons'
import { ASSETS, ASSET_TABS, ASSET_KIND_STYLE, ASSET_PREVIEW, SKILL_SCOPE_BAR, type AssetCard, type AssetKind } from '../data'

/* ============================================================
   Screen 2 — 团队资产 (read-only asset market)
   Header 24px title, 30px filter row, 250px cards in a 16px gutter
   rail that scrolls horizontally. Preview panel uses the #10141C well.
   ============================================================ */

function Badge({ kind, height = 20 }: { kind: AssetKind; height?: number }) {
  const s = ASSET_KIND_STYLE[kind]
  return (
    <span
      style={{
        height,
        borderRadius: 5,
        background: s.bg,
        boxShadow: `inset 0 0 0 1px ${s.edge}`,
        padding: '0 6px',
        display: 'inline-flex',
        alignItems: 'center',
        fontFamily: 'var(--f-mono)',
        fontSize: 10,
        color: s.fg,
        flexShrink: 0,
      }}
    >
      {kind}
    </span>
  )
}

function AssetTile({ a }: { a: AssetCard }) {
  return (
    <div
      style={{
        width: 250,
        height: a.height,
        flexShrink: 0,
        borderRadius: 12,
        background: 'var(--c-surface)',
        boxShadow: 'inset 0 0 0 1px var(--c-divider)',
        padding: 16,
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
        cursor: 'pointer',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Badge kind={a.kind} />
        <LockIcon size={14} style={{ color: 'var(--c-tm)' }} />
      </div>

      <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--c-tp)', lineHeight: '18px' }}>{a.name}</div>
      <div style={{ fontSize: 12, color: 'var(--c-ts)', lineHeight: '18px' }}>{a.desc}</div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--c-tm)', lineHeight: '12px' }}>
          {a.version}
        </span>
        <span
          style={{
            fontFamily: 'var(--f-mono)',
            fontSize: 10,
            color: a.blocked ? 'var(--c-amber)' : 'var(--c-ts)',
            lineHeight: '12px',
          }}
        >
          {a.usage}
        </span>
      </div>
    </div>
  )
}

/** 作用域 + 健康条 —— 资产是按运行时作用域投递的，作用域标记缺失
 *  会让技能直接 blocked，必须放在列表上方而不是藏在详情里。 */
function ScopeHealthBar() {
  return (
    <div
      style={{
        borderRadius: 8,
        background: 'var(--c-warn-well)',
        padding: '9px 12px',
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        flexShrink: 0,
      }}
    >
      <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-amber)', flexShrink: 0 }}>!</span>
      <span style={{ fontSize: 11, color: 'var(--c-tp)', lineHeight: '15px' }}>{SKILL_SCOPE_BAR.scope}</span>
      <div style={{ flex: 1 }} />
      <span style={{ fontSize: 11, color: 'var(--c-amber)', lineHeight: '15px' }}>{SKILL_SCOPE_BAR.health}</span>
    </div>
  )
}

function Preview() {
  const p = ASSET_PREVIEW
  return (
    <aside
      style={{
        width: 360,
        flexShrink: 0,
        background: '#10141c',
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
        <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--c-tp)' }}>资产预览</span>
        <div style={{ flex: 1 }} />
        <CloseIcon size={16} style={{ color: 'var(--c-tm)', cursor: 'pointer' }} />
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
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Badge kind={p.kind} />
            <LockIcon size={14} style={{ color: 'var(--c-tm)' }} />
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--c-tm)' }}>{p.version}</span>
          </div>
          <div style={{ fontSize: 18, fontWeight: 500, color: 'var(--c-tp)', lineHeight: '24px' }}>{p.name}</div>
          <div style={{ fontSize: 13, color: 'var(--c-ts)', lineHeight: '18px' }}>{p.desc}</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ fontSize: 11, color: 'var(--c-tm)', lineHeight: '13px' }}>内容预览</div>
          <div
            style={{
              borderRadius: 8,
              background: 'var(--c-base)',
              boxShadow: 'inset 0 0 0 1px var(--c-divider)',
              padding: 12,
              display: 'flex',
              flexDirection: 'column',
              gap: 6,
            }}
          >
            {p.code.map((line) => (
              <div
                key={line}
                style={{
                  fontFamily: 'var(--f-mono)',
                  fontSize: 11,
                  color: 'var(--c-ts)',
                  whiteSpace: 'pre',
                  lineHeight: '14px',
                }}
              >
                {line}
              </div>
            ))}
          </div>
        </div>

        <div
          style={{
            height: 34,
            borderRadius: 8,
            background: 'var(--c-warn-well)',
            boxShadow: 'inset 0 0 0 1px var(--c-amber)',
            padding: '0 10px',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            flexShrink: 0,
          }}
        >
          <LockIcon size={14} style={{ color: 'var(--c-amber)' }} />
          <span style={{ fontSize: 12, color: 'var(--c-amber)' }}>{p.notice}</span>
        </div>

        <div
          style={{
            height: 36,
            borderRadius: 8,
            background: '#1b202b',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <span style={{ fontSize: 12, color: 'var(--c-tm)', lineHeight: '15px' }}>{p.action}</span>
        </div>
      </div>
    </aside>
  )
}

export function TeamAssets() {
  const [tab, setTab] = useState<string>(ASSET_TABS[0])

  return (
    <>
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', background: 'var(--c-base)' }}>
        <TopBar />

        <div
          style={{
            flex: 1,
            minHeight: 0,
            padding: 20,
            display: 'flex',
            flexDirection: 'column',
            gap: 20,
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flexShrink: 0 }}>
            <span style={{ fontSize: 24, fontWeight: 600, color: 'var(--c-tp)', lineHeight: '30px' }}>团队资产</span>
            <span style={{ fontSize: 13, color: 'var(--c-ts)', lineHeight: '15px' }}>
              个人用户仅可查看 Rules / Commands / Skills / MCP 等 AI 资产，按项目自动筛选。
            </span>
          </div>

          {/* filter bar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
            {ASSET_TABS.map((t) => {
              const on = t === tab
              return (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  style={{
                    height: 30,
                    borderRadius: 6,
                    background: on ? 'var(--c-selected)' : 'var(--c-surface)',
                    padding: '0 10px',
                    display: 'flex',
                    alignItems: 'center',
                    fontFamily: 'var(--f-mono)',
                    fontSize: 13,
                    fontWeight: on ? 500 : 400,
                    color: on ? 'var(--c-emerald)' : 'var(--c-ts)',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {t}
                </button>
              )
            })}

            <div style={{ flex: 1 }} />

            <div
              style={{
                height: 30,
                borderRadius: 6,
                background: 'var(--c-surface)',
                boxShadow: 'inset 0 0 0 1px var(--c-chip)',
                padding: '0 8px',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                flexShrink: 0,
              }}
            >
              <FolderIcon size={14} style={{ color: 'var(--c-ts)' }} />
              <span style={{ fontSize: 12, color: 'var(--c-tp)' }}>Acme Platform</span>
            </div>

            <div
              style={{
                width: 180,
                height: 30,
                borderRadius: 6,
                background: 'var(--c-surface)',
                boxShadow: 'inset 0 0 0 1px var(--c-chip)',
                padding: '0 8px',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                flexShrink: 0,
              }}
            >
              <SearchIcon size={14} style={{ color: 'var(--c-tm)' }} />
              <span style={{ fontSize: 12, color: 'var(--c-tm)' }}>搜索资产…</span>
            </div>
          </div>

          {/* scope + health — sits directly under the filter bar */}
          <ScopeHealthBar />

          {/* asset grid — wraps 3 per row inside the 800px content well */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'flex-start',
              alignContent: 'flex-start',
              gap: 16,
              flexShrink: 0,
            }}
          >
            {ASSETS.map((a) => (
              <AssetTile key={a.id} a={a} />
            ))}
          </div>
        </div>

        <ConversationDock />
      </div>

      <Preview />
    </>
  )
}
