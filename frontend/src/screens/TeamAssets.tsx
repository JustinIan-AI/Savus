import { useState, useEffect } from 'react'
import { listMarketplaceAssets, distributeAsset } from "../lib/api";
import { TopBar } from '../components/TopBar'
import { ConversationDock } from '../components/ConversationDock'
import { CloseIcon, FolderIcon, LockIcon, SearchIcon } from '../components/icons'
import { ASSETS, ASSET_TABS, ASSET_KIND_STYLE, ASSET_PREVIEW, SKILL_SCOPE_BAR, type AssetCard, type AssetKind } from '../data'

function Badge({ kind, height = 20 }: { kind: AssetKind; height?: number }) {
  const s = ASSET_KIND_STYLE[kind] || ASSET_KIND_STYLE.rule
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

function AssetTile({ a, onClick }: { a: AssetCard; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
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

interface PreviewProps {
  asset: AssetCard | null
  onClose: () => void
  onDistribute: () => void
  distributeStatus: string | null
}

function Preview({ asset, onClose, onDistribute, distributeStatus }: PreviewProps) {
  const p = asset || ASSET_PREVIEW
  const codeLines = 'code' in p && Array.isArray((p as any).code) ? (p as any).code : [
    `// ${p.name}`,
    `version = "${p.version}"`,
    `scope = "team"`,
    `# auto-generated asset definition`,
  ]

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
        <button
          onClick={onClose}
          style={{ background: 'transparent', border: 'none', cursor: 'pointer', padding: 0 }}
        >
          <CloseIcon size={16} style={{ color: 'var(--c-tm)' }} />
        </button>
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
            {codeLines.map((line: string) => (
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
          <span style={{ fontSize: 12, color: 'var(--c-amber)' }}>
            {'notice' in p ? (p as any).notice : '只读资产：受项目主干版本锁定'}
          </span>
        </div>

        <button
          onClick={onDistribute}
          style={{
            height: 36,
            borderRadius: 8,
            background: distributeStatus === '下发成功' ? 'var(--c-emerald)' : '#1b202b',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            flexShrink: 0,
          }}
        >
          <span style={{ fontSize: 12, color: distributeStatus === '下发成功' ? '#000' : 'var(--c-tp)', lineHeight: '15px' }}>
            {distributeStatus || ('action' in p ? (p as any).action : '一键下发至项目')}
          </span>
        </button>
      </div>
    </aside>
  )
}

export function TeamAssets() {
  const [tab, setTab] = useState<string>(ASSET_TABS[0])
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [selectedAsset, setSelectedAsset] = useState<AssetCard | null>(ASSETS[0])
  const [showPreview, setShowPreview] = useState<boolean>(true)
  const [distributeStatus, setDistributeStatus] = useState<string | null>(null)
  const [assetList, setAssetList] = useState<AssetCard[]>(ASSETS)

  useEffect(() => {
    let active = true
    async function load() {
      try {
        const res = await listMarketplaceAssets()
        if (active && res && Array.isArray(res.assets) && res.assets.length > 0) {
          const mapped: AssetCard[] = res.assets.map((item: any, idx: number) => ({
            id: item.id || `api-${idx}`,
            kind: (item.type || 'rule').toLowerCase() as AssetKind,
            name: item.name || item.id,
            desc: item.description || '由团队注册中心分发的标准化资产',
            version: item.version || 'v1.0.0',
            usage: '100% 规则合规',
            height: 180,
          }))
          setAssetList([...ASSETS, ...mapped])
        }
      } catch {
        // fallback to default assets
      }
    }
    load()
    return () => { active = false }
  }, [])

  const handleDistribute = async () => {
    if (!selectedAsset) return
    try {
      setDistributeStatus('正在下发...')
      await distributeAsset({
        id: selectedAsset.id,
        name: selectedAsset.name,
        type: selectedAsset.kind,
        content: `# ${selectedAsset.name}\n`,
      })
      setDistributeStatus('下发成功')
      setTimeout(() => setDistributeStatus(null), 2500)
    } catch {
      setDistributeStatus('下发失败')
      setTimeout(() => setDistributeStatus(null), 2500)
    }
  }

  const filteredAssets = assetList.filter((a) => {
    const matchTab =
      tab === '全部' ||
      (tab === 'Rules' && a.kind === 'rule') ||
      (tab === 'Commands' && a.kind === 'cmd') ||
      (tab === 'Skills' && a.kind === 'skill') ||
      (tab === 'MCP' && a.kind === 'mcp')
    const matchSearch =
      !searchQuery ||
      a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.desc.toLowerCase().includes(searchQuery.toLowerCase())
    return matchTab && matchSearch
  })

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
                    border: 'none',
                    cursor: 'pointer',
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
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索资产…"
                style={{
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  fontSize: 12,
                  color: 'var(--c-tp)',
                  width: '100%',
                }}
              />
            </div>
          </div>

          <ScopeHealthBar />

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
            {filteredAssets.map((a) => (
              <AssetTile
                key={a.id}
                a={a}
                onClick={() => {
                  setSelectedAsset(a)
                  setShowPreview(true)
                }}
              />
            ))}
          </div>
        </div>

        <ConversationDock />
      </div>

      {showPreview && (
        <Preview
          asset={selectedAsset}
          onClose={() => setShowPreview(false)}
          onDistribute={handleDistribute}
          distributeStatus={distributeStatus}
        />
      )}
    </>
  )
}
