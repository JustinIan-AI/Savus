import { useState, useEffect } from 'react'
import { CloseIcon } from '../components/icons'
import {
  ADD_AGENT_FIELDS,
  ADD_CONNECTOR_FIELDS,
  NEW_TASK_DEFAULTS,
  TASK_TEMPLATES,
  type FieldSpec,
} from '../data'

/* ============================================================
   Screens 7 & 8 — overlay modals
   480px card, 12px radius, 56px header, 20px body with 16px stack,
   64px footer with the button pair centred as a group.
   Shadows: 0 12px 28px rgba(0,0,0,.5) over a #07090D 60% scrim.
   ============================================================ */

function Field({ f }: { f: FieldSpec }) {
  const height = f.textarea ? 72 : 40
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
      <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--c-ts)', lineHeight: '15px' }}>
        {f.label}
      </span>

      <div
        style={{
          height,
          borderRadius: 8,
          background: 'var(--c-rail)',
          boxShadow: 'inset 0 0 0 1px var(--c-chip)',
          padding: f.textarea ? '10px 12px' : '0 12px',
          display: 'flex',
          alignItems: f.textarea ? 'flex-start' : 'center',
          justifyContent: f.caret ? 'space-between' : 'flex-start',
          gap: 8,
        }}
      >
        <span
          style={{
            fontFamily: f.mono ? 'var(--f-mono)' : 'var(--f-sans)',
            fontSize: 13,
            color: f.muted ? 'var(--c-tm)' : 'var(--c-tp)',
            lineHeight: '16px',
          }}
        >
          {f.value}
        </span>
        {f.caret && <span style={{ fontSize: 12, color: 'var(--c-ts)', flexShrink: 0 }}>▾</span>}
      </div>

      {f.hint && <span style={{ fontSize: 11, lineHeight: '13px', color: 'var(--c-tm)' }}>{f.hint}</span>}
    </div>
  )
}

function Modal({
  title,
  fields,
  top,
  onClose,
  onConfirm,
}: {
  title: string
  fields: FieldSpec[]
  top: number
  onClose: () => void
  onConfirm: () => void
}) {
  return (
    <>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(7, 9, 13, 0.6)' }} onClick={onClose} />

      <div
        style={{
          position: 'absolute',
          left: 480,
          top,
          width: 480,
          borderRadius: 12,
          background: 'var(--c-surface)',
          boxShadow: '0 12px 28px rgba(0, 0, 0, 0.5), inset 0 0 0 1px var(--c-border)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: 56,
            flexShrink: 0,
            padding: '0 16px 0 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: 'inset 0 -1px 0 0 var(--c-border)',
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 600, color: 'var(--c-tp)' }}>{title}</span>
          <button onClick={onClose} style={{ display: 'flex' }}>
            <CloseIcon size={16} style={{ color: 'var(--c-ts)' }} />
          </button>
        </div>

        <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>
          {fields.map((f) => (
            <Field key={f.label} f={f} />
          ))}
        </div>

        <div
          style={{
            height: 64,
            flexShrink: 0,
            padding: '0 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 12,
            boxShadow: 'inset 0 1px 0 0 var(--c-border)',
          }}
        >
          <button
            onClick={onClose}
            style={{
              height: 34,
              borderRadius: 8,
              boxShadow: 'inset 0 0 0 1px var(--c-chip)',
              padding: '0 16px',
              fontSize: 13,
              color: 'var(--c-ts)',
            }}
          >
            取消
          </button>
          <button
            onClick={onConfirm}
            style={{
              height: 34,
              borderRadius: 8,
              background: 'var(--c-emerald)',
              padding: '0 16px',
              fontSize: 13,
              fontWeight: 500,
              color: 'var(--c-base)',
            }}
          >
            确认添加
          </button>
        </div>
      </div>
    </>
  )
}

export function AddAgentModal({ onClose, onConfirm }: { onClose: () => void; onConfirm: () => void }) {
  return (
    <Modal title="添加 Agent" fields={ADD_AGENT_FIELDS} top={170} onClose={onClose} onConfirm={onConfirm} />
  )
}

export function AddConnectorModal({ onClose, onConfirm }: { onClose: () => void; onConfirm: () => void }) {
  return (
    <Modal title="添加连接器" fields={ADD_CONNECTOR_FIELDS} top={150} onClose={onClose} onConfirm={onConfirm} />
  )
}

/* ============================================================
   Screen 9 (new) — C4 新建任务面板
   560px card, 12px radius, 56px header, 20px body with a 16px stack;
   the template picker is a 2×2 grid of 255px cards, then the params
   row, the description and the executor.
   ============================================================ */

function well(extra?: React.CSSProperties): React.CSSProperties {
  return {
    borderRadius: 8,
    background: 'var(--c-rail)',
    boxShadow: 'inset 0 0 0 1px var(--c-chip)',
    display: 'flex',
    ...extra,
  }
}

function C4Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
      <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--c-ts)', lineHeight: '15px' }}>{label}</span>
      {children}
    </div>
  )
}

const CARET = <span style={{ fontSize: 12, color: 'var(--c-ts)', flexShrink: 0 }}>▾</span>

/** C4 面板提交出去的负载 —— 直接映射到 `POST /api/v1/projects/{id}/tasks`。 */
export interface NewTaskPayload {
  title: string
  template: string
  intent: string
}


const header = (): React.CSSProperties => ({
  height: 56,
  padding: '0 20px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  boxShadow: 'inset 0 -1px 0 0 var(--c-border)',
})

const hTitle = (): React.CSSProperties => ({
  fontSize: 16,
  fontWeight: 600,
  color: 'var(--c-tp)',
})

const closeBtn = (): React.CSSProperties => ({
  background: 'none',
  border: 'none',
  color: 'var(--c-ts)',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
})

const body = (opts: { gap?: number } = {}): React.CSSProperties => ({
  padding: 20,
  display: 'flex',
  flexDirection: 'column',
  gap: opts.gap ?? 16,
  maxHeight: '75vh',
  overflowY: 'auto',
})

const footer = (): React.CSSProperties => ({
  height: 64,
  padding: '0 20px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-end',
  gap: 12,
  boxShadow: 'inset 0 1px 0 0 var(--c-border)',
})

const textInput = (): React.CSSProperties => ({
  width: '100%',
  height: 38,
  padding: '0 12px',
  borderRadius: 6,
  background: 'var(--c-well)',
  border: '1px solid var(--c-chip)',
  color: 'var(--c-tp)',
  fontSize: 13,
  outline: 'none',
  boxSizing: 'border-box',
})

const btnGhost = (): React.CSSProperties => ({
  height: 36,
  padding: '0 16px',
  borderRadius: 8,
  background: 'transparent',
  border: '1px solid var(--c-chip)',
  color: 'var(--c-tp)',
  fontSize: 13,
  fontWeight: 500,
  cursor: 'pointer',
})

const btnPrimary = (disabled?: boolean): React.CSSProperties => ({
  height: 36,
  padding: '0 18px',
  borderRadius: 8,
  background: disabled ? 'var(--c-chip)' : 'var(--c-accent)',
  border: 'none',
  color: disabled ? 'var(--c-tm)' : '#07090D',
  fontSize: 13,
  fontWeight: 600,
  cursor: disabled ? 'not-allowed' : 'pointer',
})

export function AddProjectModal({
  onClose,
  onConfirm,
}: {
  onClose: () => void
  onConfirm: (project: any) => void
}) {
  const [name, setName] = useState('')
  const [mode, setMode] = useState<'local' | 'remote'>('local')
  const [pathOrUrl, setPathOrUrl] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  const handleSubmit = async () => {
    if (!name.trim()) {
      setErr('请输入项目名称')
      return
    }
    setSubmitting(true)
    setErr(null)
    try {
      const res = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          mode,
          root_path: mode === 'local' ? pathOrUrl : undefined,
          remote_url: mode === 'remote' ? pathOrUrl : undefined,
        }),
      })
      const data = await res.json()
      if (data.ok && data.project) {
        onConfirm(data.project)
        onClose()
      } else {
        setErr(data.error || '创建项目失败')
      }
    } catch (e: any) {
      setErr(e.message || '网络请求错误')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(7, 9, 13, 0.6)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ width: 520, borderRadius: 12, background: 'var(--c-surface)', boxShadow: '0 12px 28px rgba(0,0,0,0.5)', display: 'flex', flexDirection: 'column', overflow: 'hidden', zIndex: 101 }}>
        <div style={header()}>
          <div style={hTitle()}>创建新工作区项目</div>
          <button style={closeBtn()} onClick={onClose}>
            <CloseIcon size={16} />
          </button>
        </div>

        <div style={body({ gap: 16 })}>
          <C4Field label="项目名称">
            <input
              type="text"
              placeholder="例如：Acme Microservices 或 Client SDK"
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={textInput()}
            />
          </C4Field>

          <C4Field label="项目模式 (Project Mode)">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <button
                type="button"
                onClick={() => setMode('local')}
                style={{
                  padding: '10px 12px',
                  borderRadius: 6,
                  border: `1px solid ${mode === 'local' ? 'var(--c-accent)' : 'var(--c-border)'}`,
                  background: mode === 'local' ? 'rgba(52, 211, 153, 0.08)' : 'var(--c-well)',
                  textAlign: 'left',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 4,
                }}
              >
                <div style={{ fontSize: 13, fontWeight: 600, color: mode === 'local' ? 'var(--c-accent)' : 'var(--c-tp)' }}>
                  💻 本地模式 (Local)
                </div>
                <div style={{ fontSize: 11, color: 'var(--c-tm)' }}>
                  绑定本机已有文件夹，无需联网，离线优先。
                </div>
              </button>

              <button
                type="button"
                onClick={() => setMode('remote')}
                style={{
                  padding: '10px 12px',
                  borderRadius: 6,
                  border: `1px solid ${mode === 'remote' ? '#38BDF8' : 'var(--c-border)'}`,
                  background: mode === 'remote' ? 'rgba(56, 189, 248, 0.08)' : 'var(--c-well)',
                  textAlign: 'left',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 4,
                }}
              >
                <div style={{ fontSize: 13, fontWeight: 600, color: mode === 'remote' ? '#38BDF8' : 'var(--c-tp)' }}>
                  ☁️ 远端模式 (Remote)
                </div>
                <div style={{ fontSize: 11, color: 'var(--c-tm)' }}>
                  基于 Git 远端仓库，自动托管与拉取。
                </div>
              </button>
            </div>
          </C4Field>

          <C4Field label={mode === 'local' ? '本地目录绝对路径 (Workspace Path)' : 'Git 仓库地址 (Remote Git URL)'}>
            <input
              type="text"
              placeholder={mode === 'local' ? '/Users/yourname/projects/my-repo' : 'https://github.com/org/repo.git'}
              value={pathOrUrl}
              onChange={(e) => setPathOrUrl(e.target.value)}
              style={textInput()}
            />
          </C4Field>

          {err && (
            <div style={{ padding: '8px 12px', borderRadius: 6, background: 'rgba(239, 68, 68, 0.1)', color: '#EF4444', fontSize: 12 }}>
              {err}
            </div>
          )}
        </div>

        <div style={footer()}>
          <button style={btnGhost()} onClick={onClose} disabled={submitting}>
            取消
          </button>
          <button style={btnPrimary()} onClick={handleSubmit} disabled={submitting}>
            {submitting ? '创建中...' : '确认创建项目'}
          </button>
        </div>
      </div>
    </div>
  )
}

export function NewTaskModal({
  onClose,
  onConfirm,
  onNavigateSettings,
}: {
  onClose: () => void
  onConfirm: () => void
  onNavigateSettings?: () => void
}) {
  const [projects, setProjects] = useState<any[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<string>('default')
  const [addProjectOpen, setAddProjectOpen] = useState(false)
  const [selectedTpl, setSelectedTpl] = useState(TASK_TEMPLATES[0].id)
  const [taskDesc, setTaskDesc] = useState(NEW_TASK_DEFAULTS.taskDesc)
  const [submitting, setSubmitting] = useState(false)
  const [validation, setValidation] = useState<{ ok: boolean; reason?: string; error?: string } | null>(null)

  // 1. 加载所有项目
  const loadProjects = async () => {
    try {
      const res = await fetch('/api/v1/projects')
      const data = await res.json()
      if (data.projects && data.projects.length > 0) {
        setProjects(data.projects)
      }
    } catch {
      // fallback default
    }
  }

  useEffect(() => {
    loadProjects()
  }, [])

  // 2. 项目或模板变动时触发 Pre-flight 强拦截校验
  useEffect(() => {
    let active = true
    const checkValidation = async () => {
      try {
        const res = await fetch(`/api/v1/projects/${selectedProjectId}/tasks/validate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ template_id: selectedTpl, intent: taskDesc }),
        })
        const data = await res.json()
        if (active) {
          setValidation(data)
        }
      } catch {
        if (active) setValidation(null)
      }
    }
    checkValidation()
    return () => { active = false }
  }, [selectedProjectId, selectedTpl])

  const selectedProj = projects.find((p) => p.id === selectedProjectId) || {
    id: 'default',
    name: 'Acme Platform (Default)',
    mode: 'local',
  }

  const isBlocked = validation && !validation.ok

  const handleSubmit = async () => {
    if (isBlocked) return
    setSubmitting(true)
    try {
      await fetch(`/api/v1/projects/${selectedProjectId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intent: taskDesc.trim(),
          template_id: selectedTpl,
        }),
      })
      onConfirm()
      onClose()
    } catch (e) {
      console.error('Failed to create task', e)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <div style={{ position: 'fixed', inset: 0, background: 'rgba(7, 9, 13, 0.6)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 560, borderRadius: 12, background: 'var(--c-surface)', boxShadow: '0 12px 28px rgba(0,0,0,0.5)', display: 'flex', flexDirection: 'column', overflow: 'hidden', zIndex: 101 }}>
          <div style={header()}>
            <div style={hTitle()}>新建任务</div>
            <button style={closeBtn()} onClick={onClose}>
              <CloseIcon size={16} />
            </button>
          </div>

          <div style={body({ gap: 16 })}>
            {/* 归属项目选择器 */}
            <C4Field label="归属项目 (Project)">
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <div style={{ position: 'relative', flex: 1 }}>
                  <select
                    value={selectedProjectId}
                    onChange={(e) => setSelectedProjectId(e.target.value)}
                    style={{
                      width: '100%',
                      height: 40,
                      padding: '0 32px 0 12px',
                      borderRadius: 6,
                      background: 'var(--c-well)',
                      border: '1px solid var(--c-border)',
                      color: 'var(--c-tp)',
                      fontSize: 13,
                      appearance: 'none',
                      cursor: 'pointer',
                    }}
                  >
                    {projects.map((p) => (
                      <option key={p.id} value={p.id} style={{ background: 'var(--c-surface)', color: 'var(--c-tp)' }}>
                        {p.name} [{p.mode === 'local' ? 'Local 本地目录' : 'Remote 远端仓库'}]
                      </option>
                    ))}
                  </select>
                  <div style={{ position: 'absolute', right: 12, top: 12, pointerEvents: 'none', color: 'var(--c-tm)' }}>
                    {CARET}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setAddProjectOpen(true)}
                  style={{
                    height: 40,
                    padding: '0 12px',
                    borderRadius: 6,
                    border: '1px solid var(--c-border)',
                    background: 'var(--c-well)',
                    color: 'var(--c-tp)',
                    fontSize: 12,
                    fontWeight: 500,
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                  }}
                >
                  + 新建项目
                </button>
              </div>

              {/* 模式提示标签 */}
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 4 }}>
                <span
                  style={{
                    fontSize: 11,
                    padding: '2px 6px',
                    borderRadius: 4,
                    background: selectedProj.mode === 'local' ? 'rgba(52, 211, 153, 0.1)' : 'rgba(56, 189, 248, 0.1)',
                    color: selectedProj.mode === 'local' ? 'var(--c-accent)' : '#38BDF8',
                    fontWeight: 600,
                  }}
                >
                  {selectedProj.mode === 'local' ? '本地模式 · 路径直连' : '远端模式 · Git 自动拉取'}
                </span>
                <span style={{ fontSize: 11, color: 'var(--c-tm)' }}>
                  {selectedProj.mode === 'local'
                    ? selectedProj.root_path || '当前工作空间文件夹'
                    : selectedProj.remote_url || '远端 Git 仓库'}
                </span>
              </div>
            </C4Field>

            {/* 选择任务模板 */}
            <C4Field label="选择模板 (Task Template)">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                {TASK_TEMPLATES.map((t) => {
                  const sel = t.id === selectedTpl
                  return (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setSelectedTpl(t.id)}
                      style={{
                        padding: '10px 12px',
                        borderRadius: 6,
                        border: `1px solid ${sel ? 'var(--c-accent)' : 'var(--c-border)'}`,
                        background: sel ? 'rgba(52, 211, 153, 0.08)' : 'var(--c-well)',
                        textAlign: 'left',
                        cursor: 'pointer',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 4,
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontSize: 13, fontWeight: 600, color: sel ? 'var(--c-accent)' : 'var(--c-tp)' }}>
                          {t.title}
                        </span>
                        {t.isFixed && (
                          <span style={{ fontSize: 10, padding: '1px 5px', borderRadius: 4, background: 'var(--c-surface)', color: 'var(--c-tm)' }}>
                            固定
                          </span>
                        )}
                      </div>
                      <span style={{ fontSize: 11, color: 'var(--c-tm)' }}>{t.desc}</span>
                    </button>
                  )
                })}
              </div>
            </C4Field>

            {/* 外部工单服务前置强拦截告警 (Pre-flight Guardrail) */}
            {isBlocked && (
              <div
                style={{
                  padding: '12px 14px',
                  borderRadius: 8,
                  background: 'rgba(245, 158, 11, 0.1)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 6,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#F59E0B', fontSize: 13, fontWeight: 600 }}>
                  <span>⚠️</span>
                  <span>外部工单服务前置拦截 (Pre-flight Guardrail)</span>
                </div>
                <div style={{ fontSize: 12, color: 'var(--c-tp)', lineHeight: '18px' }}>
                  {validation?.reason || validation?.error || '远端工单任务需挂载相应的 MCP 任务管理工具。'}
                </div>
                {onNavigateSettings && (
                  <button
                    type="button"
                    onClick={() => {
                      onClose()
                      onNavigateSettings()
                    }}
                    style={{
                      alignSelf: 'flex-start',
                      marginTop: 4,
                      fontSize: 12,
                      color: 'var(--c-accent)',
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      cursor: 'pointer',
                      textDecoration: 'underline',
                    }}
                  >
                    前往「设置 · MCP 连接器」配置连接器 →
                  </button>
                )}
              </div>
            )}

            {/* 任务目标输入框 */}
            <C4Field label="一句话目标 (Task Intent)">
              <textarea
                value={taskDesc}
                onChange={(e) => setTaskDesc(e.target.value)}
                placeholder="简要描述任务目标，如：修复 LoopWorkspaceState 序列化时的编码异常 (Fixes #102)"
                rows={3}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: 6,
                  background: 'var(--c-well)',
                  border: '1px solid var(--c-border)',
                  color: 'var(--c-tp)',
                  fontSize: 13,
                  resize: 'none',
                  outline: 'none',
                  fontFamily: 'inherit',
                }}
              />
            </C4Field>
          </div>

          <div style={footer()}>
            <button style={btnGhost()} onClick={onClose} disabled={submitting}>
              取消
            </button>
            <button
              style={{
                ...btnPrimary(),
                ...(isBlocked ? { opacity: 0.5, cursor: 'not-allowed', background: 'var(--c-border)' } : {}),
              }}
              onClick={handleSubmit}
              disabled={submitting || !!isBlocked}
              title={isBlocked ? '需先解除前置服务依赖拦截' : undefined}
            >
              {submitting ? '创建中...' : isBlocked ? '等待前置服务' : '开始任务'}
            </button>
          </div>
        </div>
      </div>

      {/* 新建项目子弹窗 */}
      {addProjectOpen && (
        <AddProjectModal
          onClose={() => setAddProjectOpen(false)}
          onConfirm={(newProj) => {
            loadProjects()
            setSelectedProjectId(newProj.id)
          }}
        />
      )}
    </>
  )
}
export function GateDecisionModal({
  taskId,
  taskTitle,
  initialDecision = 'approved',
  onClose,
  onConfirm,
}: {
  taskId: string
  taskTitle: string
  initialDecision?: 'approved' | 'denied'
  onClose: () => void
  onConfirm: (decision: 'approved' | 'denied', comment: string) => void
}) {
  const [decision, setDecision] = useState<'approved' | 'denied'>(initialDecision)
  const [comment, setComment] = useState('')

  return (
    <>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(7, 9, 13, 0.6)', zIndex: 100 }} onClick={onClose} />
      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: 160,
          transform: 'translateX(-50%)',
          width: 480,
          borderRadius: 12,
          background: 'var(--c-surface)',
          boxShadow: '0 12px 28px rgba(0,0,0,0.5)',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 101,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: 56,
            padding: '0 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: 'inset 0 -1px 0 0 var(--c-border)',
          }}
        >
          <span style={{ fontSize: 15, fontWeight: 600, color: 'var(--c-tp)' }}>
            审批门裁决（Gate Decision）
          </span>
          <button onClick={onClose} style={{ color: 'var(--c-ts)', cursor: 'pointer' }}>
            <CloseIcon />
          </button>
        </div>

        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <div style={{ fontSize: 12, color: 'var(--c-ts)', marginBottom: 4 }}>目标任务</div>
            <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--c-tp)' }}>
              [{taskId}] {taskTitle}
            </div>
          </div>

          <div>
            <div style={{ fontSize: 12, color: 'var(--c-ts)', marginBottom: 8 }}>裁决选项</div>
            <div style={{ display: 'flex', gap: 12 }}>
              <button
                onClick={() => setDecision('approved')}
                style={{
                  flex: 1,
                  height: 36,
                  borderRadius: 8,
                  background: decision === 'approved' ? 'var(--c-emerald)' : 'var(--c-rail)',
                  color: decision === 'approved' ? 'var(--c-base)' : 'var(--c-tp)',
                  fontWeight: 500,
                  fontSize: 13,
                  cursor: 'pointer',
                  border: 'none',
                }}
              >
                ✓ 放行并执行 (Approve)
              </button>
              <button
                onClick={() => setDecision('denied')}
                style={{
                  flex: 1,
                  height: 36,
                  borderRadius: 8,
                  background: decision === 'denied' ? '#ef4444' : 'var(--c-rail)',
                  color: decision === 'denied' ? '#fff' : 'var(--c-tp)',
                  fontWeight: 500,
                  fontSize: 13,
                  cursor: 'pointer',
                  border: 'none',
                }}
              >
                ✕ 驳回并整改 (Deny)
              </button>
            </div>
          </div>

          <div>
            <div style={{ fontSize: 12, color: 'var(--c-ts)', marginBottom: 4 }}>审批批注与整改说明</div>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="请输入放行凭据或驳回的具体修复建议..."
              style={{
                width: '100%',
                height: 72,
                borderRadius: 8,
                background: 'var(--c-rail)',
                border: '1px solid var(--c-chip)',
                padding: '8px 12px',
                color: 'var(--c-tp)',
                fontSize: 13,
                resize: 'none',
                boxSizing: 'border-box',
              }}
            />
          </div>
        </div>

        <div
          style={{
            height: 64,
            padding: '0 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            gap: 12,
            boxShadow: 'inset 0 1px 0 0 var(--c-border)',
          }}
        >
          <button
            onClick={onClose}
            style={{
              height: 36,
              borderRadius: 8,
              padding: '0 16px',
              fontSize: 13,
              color: 'var(--c-ts)',
              background: 'transparent',
              border: '1px solid var(--c-chip)',
              cursor: 'pointer',
            }}
          >
            取消
          </button>
          <button
            onClick={() => onConfirm(decision, comment)}
            style={{
              height: 36,
              borderRadius: 8,
              background: decision === 'approved' ? 'var(--c-emerald)' : '#ef4444',
              padding: '0 16px',
              fontSize: 13,
              fontWeight: 500,
              color: '#fff',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            确认提交
          </button>
        </div>
      </div>
    </>
  )
}
