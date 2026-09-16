import { useState } from 'react'
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

export function NewTaskModal({
  onClose,
  onConfirm,
}: {
  onClose: () => void
  onConfirm: (payload: NewTaskPayload) => void
}) {
  const [tpl, setTpl] = useState(TASK_TEMPLATES[0].id)
  const [desc, setDesc] = useState('')

  /** 画布上没有独立的「标题」字段，任务标题就取描述的首行。 */
  const submit = () => {
    const intent = desc.trim() || NEW_TASK_DEFAULTS.desc
    const title = intent.split('\n')[0].trim().slice(0, 60)
    onConfirm({ title, template: tpl, intent })
  }

  return (
    <>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(7, 9, 13, 0.6)' }} onClick={onClose} />

      <div
        style={{
          position: 'absolute',
          left: 440,
          top: 118,
          width: 560,
          borderRadius: 12,
          background: 'var(--c-surface)',
          boxShadow: '0 12px 28px rgba(0, 0, 0, 0.5), inset 0 0 0 1px var(--c-border)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* header */}
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
          <span style={{ fontSize: 16, fontWeight: 600, color: 'var(--c-tp)' }}>新建任务</span>
          <button onClick={onClose} style={{ display: 'flex' }}>
            <CloseIcon size={16} style={{ color: 'var(--c-ts)' }} />
          </button>
        </div>

        {/* body */}
        <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <C4Field label="归属项目">
            <div style={well({ height: 40, padding: '0 12px', alignItems: 'center', gap: 8 })}>
              <span style={{ flex: 1, fontSize: 13, color: 'var(--c-tp)', lineHeight: '20px' }}>
                {NEW_TASK_DEFAULTS.project}
              </span>
              {CARET}
            </div>
          </C4Field>

          <C4Field label="选择模板">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
              {TASK_TEMPLATES.map((t) => {
                const on = t.id === tpl
                return (
                  <button
                    key={t.id}
                    onClick={() => setTpl(t.id)}
                    style={{
                      /* 50% - half the 10px gap → 两列；ring 为 inset 不占宽。 */
                      width: 'calc(50% - 5px)',
                      padding: '10px 12px',
                      borderRadius: 8,
                      background: on ? 'var(--c-selected)' : 'var(--c-rail)',
                      boxShadow: `inset 0 0 0 1px ${on ? 'var(--c-emerald-edge)' : 'var(--c-chip)'}`,
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 4,
                      textAlign: 'left',
                    }}
                  >
                    <span
                      style={{
                        fontFamily: 'var(--f-mono)',
                        fontSize: 12,
                        color: on ? 'var(--c-emerald)' : 'var(--c-tp)',
                        lineHeight: '16px',
                      }}
                    >
                      {t.name}
                    </span>
                    <span
                      style={{
                        fontSize: 11,
                        color: on ? 'var(--c-ts)' : 'var(--c-tm)',
                        lineHeight: '13px',
                      }}
                    >
                      {t.desc}
                    </span>
                  </button>
                )
              })}
            </div>
          </C4Field>

          <C4Field label="模板参数（随所选模板变化）">
            <div style={{ display: 'flex', gap: 10 }}>
              <div style={well({ flex: 1, minWidth: 0, height: 40, padding: '0 12px', alignItems: 'center' })}>
                <span style={{ fontSize: 13, color: 'var(--c-tm)', lineHeight: '20px' }}>
                  {NEW_TASK_DEFAULTS.issue}
                </span>
              </div>
              <div style={well({ width: 150, height: 40, padding: '0 12px', alignItems: 'center' })}>
                <span style={{ fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--c-tp)', lineHeight: '20px' }}>
                  {NEW_TASK_DEFAULTS.budget}
                </span>
              </div>
            </div>
          </C4Field>

          <C4Field label="描述">
            <div style={well({ height: 72, padding: '10px 12px', alignItems: 'stretch' })}>
              <textarea
                data-testid="new-task-desc"
                value={desc}
                onChange={(e) => setDesc(e.target.value)}
                placeholder={NEW_TASK_DEFAULTS.desc}
                style={{
                  flex: 1,
                  width: '100%',
                  resize: 'none',
                  fontFamily: 'var(--f-sans)',
                  fontSize: 13,
                  color: 'var(--c-tp)',
                  lineHeight: '20px',
                }}
              />
            </div>
          </C4Field>

          <C4Field label="执行 Agent">
            <div style={well({ height: 40, padding: '0 12px', alignItems: 'center', gap: 8 })}>
              <span style={{ width: 7, height: 7, borderRadius: 3.5, background: 'var(--c-emerald)', flexShrink: 0 }} />
              <span style={{ flex: 1, fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--c-tp)', lineHeight: '20px' }}>
                {NEW_TASK_DEFAULTS.agent}
              </span>
              {CARET}
            </div>
          </C4Field>
        </div>

        {/* footer */}
        <div
          style={{
            height: 64,
            flexShrink: 0,
            padding: '0 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 12,
            boxShadow: 'inset 0 1px 0 0 var(--c-border)',
          }}
        >
          <span style={{ fontSize: 11, color: 'var(--c-tm)', lineHeight: '16px' }}>{NEW_TASK_DEFAULTS.hint}</span>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button
              onClick={onClose}
              style={{
                height: 36,
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
              onClick={submit}
              style={{
                height: 36,
                borderRadius: 8,
                background: 'var(--c-emerald)',
                padding: '0 16px',
                fontSize: 13,
                fontWeight: 500,
                color: 'var(--c-base)',
              }}
            >
              开始任务
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

/* ============================================================
   Gate Approval Modal (Feature F1.1)
   Supports approving or rejecting pending Gate items with feedback.
   ============================================================ */

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
