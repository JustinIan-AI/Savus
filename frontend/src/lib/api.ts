/**
 * LoopDesk API Client for Gateway Tasks & Gate Management
 */

export interface ApiTask {
  id: string
  title: string
  status: string
  template?: string
  phase?: string
  gate_status?: string
  created_at?: string
  [key: string]: any
}

export interface GateDecisionPayload {
  decision: 'approved' | 'denied'
  comment?: string
  /** 任务显示名。看板上的画布标题只存在于前端，裁决时随请求带上，
      后端据此更新任务集合，不会把标题写成裁决批注。 */
  title?: string
  root?: string
}

export const API_BASE = '/api/v1'

/** 后端 project_id 目前是占位参数（网关尚未按项目分区），统一走 default。 */
export const DEFAULT_PROJECT_ID = 'default'

export interface TasksSnapshot {
  /** 网关是否应答了。false 时看板回落到纯画布种子（优雅降级）。 */
  ok: boolean
  tasks: ApiTask[]
  error?: string
}

export async function fetchTasks(projectId = DEFAULT_PROJECT_ID): Promise<TasksSnapshot> {
  try {
    const res = await fetch(`${API_BASE}/projects/${projectId}/tasks`)
    if (!res.ok) {
      throw new Error(`Failed to fetch tasks: ${res.statusText}`)
    }
    const data = await res.json()
    return { ok: true, tasks: data.tasks || [] }
  } catch (err) {
    console.warn('Gateway API fetchTasks fallback to local:', err)
    return { ok: false, tasks: [], error: String(err) }
  }
}

export async function createTask(
  projectId = DEFAULT_PROJECT_ID,
  payload: { title: string; template?: string; intent?: string }
): Promise<ApiTask | null> {
  try {
    const res = await fetch(`${API_BASE}/projects/${projectId}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error(`Create task failed: ${res.statusText}`)
    const data = await res.json()
    return data.task
  } catch (err) {
    console.error('Error creating task:', err)
    return null
  }
}

export async function submitGateDecision(
  taskId: string,
  payload: GateDecisionPayload
): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/tasks/${taskId}/gate/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    return res.ok
  } catch (err) {
    console.error('Submit gate decision error:', err)
    return false
  }
}

export function subscribeToEvents(
  onEvent: (event: string, data: any) => void,
  onError?: (err: any) => void
): () => void {
  /* 必须显式给出事件流地址：`new EventSource()` 无参数会抛
     TypeError（TS 也报 TS2554），事件总线因此永远接不上。 */
  const eventSource = new EventSource(`${API_BASE}/events`)

  eventSource.onmessage = (e) => {
    try {
      const parsed = JSON.parse(e.data)
      onEvent('message', parsed)
    } catch {
      onEvent('message', e.data)
    }
  }

  const customEvents = ['task_created', 'task_phase_changed', 'gate_decision_recorded', 'connected']
  customEvents.forEach((evtName) => {
    eventSource.addEventListener(evtName, (e: any) => {
      try {
        const parsed = JSON.parse(e.data)
        onEvent(evtName, parsed)
      } catch {
        onEvent(evtName, e.data)
      }
    })
  })

  eventSource.onerror = (err) => {
    if (onError) onError(err)
  }

  return () => {
    eventSource.close()
  }
}
