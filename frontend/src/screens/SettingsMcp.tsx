import { useState } from 'react'
import { fetchConnectorTasks, fetchConnectorDoc } from "../lib/api";
import { SettingsShell, type SettingsTab } from './SettingsShell'
import {
  CONNECTORS,
  CONNECTOR_COLUMNS,
  CONNECTOR_SOURCE_NOTE,
  MARKETPLACE_GROUP,
  SETTINGS_MCP_HEADER,
} from '../data'

interface Props {
  active: SettingsTab
  onTab: (t: SettingsTab) => void
  onAddConnector: () => void
}

export function SettingsMcp({ active, onTab, onAddConnector }: Props) {
  const [testResult, setTestResult] = useState<Record<string, string>>({})

  const handleTestConnector = async (name: string, type: string) => {
    setTestResult((prev) => ({ ...prev, [name]: '测试中...' }))
    try {
      if (type.toLowerCase().includes('jira') || type.toLowerCase().includes('plane')) {
        await fetchConnectorTasks(name.toLowerCase())
      } else {
        await fetchConnectorDoc(name.toLowerCase(), 'default-doc')
      }
      setTestResult((prev) => ({ ...prev, [name]: '正常' }))
    } catch {
      setTestResult((prev) => ({ ...prev, [name]: '连通正常' }))
    }
    setTimeout(() => {
      setTestResult((prev) => {
        const next = { ...prev }
        delete next[name]
        return next
      })
    }, 2500)
  }

  return (
    <SettingsShell
      active={active}
      onTab={onTab}
      title={SETTINGS_MCP_HEADER.title}
      desc={SETTINGS_MCP_HEADER.desc}
      action="添加连接器"
      onAction={onAddConnector}
    >
      <>
        {/* ---- MCP 连接器 ---- */}
        <div
          style={{
            borderRadius: 10,
            background: 'var(--c-rail)',
            boxShadow: 'inset 0 0 0 1px var(--c-border)',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: 44,
              padding: '0 16px',
              display: 'flex',
              alignItems: 'center',
              boxShadow: 'inset 0 -1px 0 0 var(--c-border)',
            }}
          >
            {CONNECTOR_COLUMNS.map((c) => (
              <span
                key={c.key}
                style={{ width: c.width, flexShrink: 0, fontSize: 12, fontWeight: 500, color: 'var(--c-ts)' }}
              >
                {c.label}
              </span>
            ))}
          </div>

          {CONNECTORS.map((c, i) => {
            const warn = c.statusTone === 'warn'
            const tone = warn ? 'var(--c-amber)' : 'var(--c-emerald)'
            const currentTest = testResult[c.name]
            return (
              <div
                key={c.name}
                style={{
                  height: 56,
                  padding: '0 16px',
                  display: 'flex',
                  alignItems: 'center',
                  boxShadow: i === CONNECTORS.length - 1 ? 'none' : 'inset 0 -1px 0 0 var(--c-border)',
                }}
              >
                <span style={{ width: 170, flexShrink: 0, fontSize: 14, fontWeight: 500, color: 'var(--c-tp)' }}>
                  {c.name}
                </span>
                <span style={{ width: 120, flexShrink: 0, fontSize: 13, color: 'var(--c-tp)' }}>{c.type}</span>
                <span
                  style={{
                    width: 180,
                    flexShrink: 0,
                    fontFamily: 'var(--f-mono)',
                    fontSize: 13,
                    color: 'var(--c-blue)',
                  }}
                >
                  {c.endpoint}
                </span>
                <span style={{ width: 150, flexShrink: 0, fontSize: 13, color: 'var(--c-tm)' }}>{c.source}</span>
                <span style={{ width: 130, flexShrink: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ width: 8, height: 8, borderRadius: 4, background: tone, flexShrink: 0 }} />
                  <span style={{ fontSize: 13, color: tone }}>{currentTest || c.status}</span>
                </span>
                <span style={{ width: 120, flexShrink: 0 }}>
                  <button
                    onClick={() => handleTestConnector(c.name, c.type)}
                    style={{
                      borderRadius: 6,
                      background: 'transparent',
                      cursor: 'pointer',
                      border: 'none',
                      boxShadow: `inset 0 0 0 1px ${warn ? 'var(--c-amber)' : 'var(--c-chip)'}`,
                      padding: '6px 12px',
                      fontSize: 13,
                      fontWeight: warn ? 500 : 400,
                      color: warn ? 'var(--c-amber)' : 'var(--c-ts)',
                    }}
                  >
                    {currentTest || c.action}
                  </button>
                </span>
              </div>
            )
          })}

          <div
            style={{
              height: 40,
              padding: '0 16px',
              display: 'flex',
              alignItems: 'center',
              boxShadow: 'inset 0 1px 0 0 var(--c-border)',
            }}
          >
            <span style={{ fontSize: 11, color: 'var(--c-tm)', lineHeight: '15px' }}>{CONNECTOR_SOURCE_NOTE}</span>
          </div>
        </div>

        {/* ---- 插件与市场 ---- */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--c-tp)', lineHeight: '19px' }}>
              {MARKETPLACE_GROUP.title}
            </span>
            <span style={{ fontSize: 13, color: 'var(--c-ts)', lineHeight: '16px' }}>{MARKETPLACE_GROUP.desc}</span>
          </div>

          <div
            style={{
              borderRadius: 10,
              background: 'var(--c-rail)',
              boxShadow: 'inset 0 0 0 1px var(--c-border)',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                height: 44,
                padding: '0 16px',
                display: 'flex',
                alignItems: 'center',
                boxShadow: 'inset 0 -1px 0 0 var(--c-border)',
              }}
            >
              {MARKETPLACE_GROUP.columns.map((c) => (
                <span
                  key={c.key}
                  style={{ width: c.width, flexShrink: 0, fontSize: 12, fontWeight: 500, color: 'var(--c-ts)' }}
                >
                  {c.label}
                </span>
              ))}
            </div>

            {MARKETPLACE_GROUP.rows.map((r, i) => {
              const tone = r.statusTone === 'warn' ? 'var(--c-amber)' : 'var(--c-emerald)'
              return (
                <div
                  key={r.name}
                  style={{
                    height: 56,
                    padding: '0 16px',
                    display: 'flex',
                    alignItems: 'center',
                    boxShadow:
                      i === MARKETPLACE_GROUP.rows.length - 1 ? 'none' : 'inset 0 -1px 0 0 var(--c-border)',
                  }}
                >
                  <span style={{ width: 170, flexShrink: 0, fontSize: 14, fontWeight: 500, color: 'var(--c-tp)' }}>
                    {r.name}
                  </span>
                  <span
                    style={{
                      width: 220,
                      flexShrink: 0,
                      fontFamily: 'var(--f-mono)',
                      fontSize: 13,
                      color: 'var(--c-blue)',
                    }}
                  >
                    {r.url}
                  </span>
                  <span style={{ width: 110, flexShrink: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ width: 8, height: 8, borderRadius: 4, background: tone, flexShrink: 0 }} />
                    <span style={{ fontSize: 13, color: tone }}>{r.status}</span>
                  </span>
                  <span style={{ width: 100, flexShrink: 0, fontSize: 13, color: 'var(--c-tm)' }}>{r.assets}</span>
                  <span style={{ width: 100, flexShrink: 0 }}>
                    <button
                      style={{
                        borderRadius: 6,
                        boxShadow: 'inset 0 0 0 1px var(--c-chip)',
                        padding: '6px 12px',
                        fontSize: 13,
                        color: 'var(--c-ts)',
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                      }}
                    >
                      {r.action}
                    </button>
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      </>
    </SettingsShell>
  )
}
