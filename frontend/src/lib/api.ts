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

/** `PATCH /api/v1/tasks/{id}` —— 纯生命周期移动，不带裁决语义。
    只发送真正要改的字段：后端会把未提供的字段原样保留。 */
export interface TaskUpdatePayload {
  status?: string
  phase?: string
  title?: string
  template?: string
  intent?: string
  root?: string
}

export interface TaskUpdateResult {
  ok: boolean
  /** true = 这条任务此前只存在于画布种子里，本次 PATCH 才落进工作区。 */
  created?: boolean
  task?: ApiTask
  error?: string
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

export async function updateTask(
  taskId: string,
  payload: TaskUpdatePayload
): Promise<TaskUpdateResult> {
  try {
    const res = await fetch(`${API_BASE}/tasks/${encodeURIComponent(taskId)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      console.warn('PATCH task rejected by gateway:', data)
      return { ok: false, error: data?.error || `HTTP ${res.status}` }
    }
    return { ok: true, created: !!data.created, task: data.task }
  } catch (err) {
    console.error('Update task error:', err)
    return { ok: false, error: String(err) }
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

  const customEvents = [
    'task_created',
    'task_updated',
    'task_phase_changed',
    'gate_decision_recorded',
    'connected',
  ]
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


export interface ProjectItem {
  id: string
  name: string
  mode: 'local' | 'remote'
  root_path?: string
  remote_url?: string
  required_connector?: string
}

export async function fetchProjects(): Promise<ProjectItem[]> {
  try {
    const res = await fetch(API_BASE + "/projects")
    if (!res.ok) return []
    const data = await res.json()
    return data.projects || []
  } catch (err) {
    console.warn('fetchProjects fallback:', err)
    return [
      { id: 'default', name: 'Acme Platform (Local)', mode: 'local', root_path: '.' },
      { id: 'remote-jira', name: 'Cloud Core Repo (Remote)', mode: 'remote', remote_url: 'https://github.com/acme/core.git', required_connector: 'jira' },
    ]
  }
}

export interface TaskValidationResult {
  ok: boolean
  code?: string
  required_connector?: string
  message?: string
}

export async function validateTaskCreation(
  projectId: string,
  payload: { intent: string; template_id: string; remote?: boolean; required_connector?: string }
): Promise<TaskValidationResult> {
  try {
    const res = await fetch(API_BASE + "/projects/" + projectId + "/tasks/validate", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) return { ok: true }
    return await res.json()
  } catch (err) {
    console.warn('validateTaskCreation fallback:', err)
    return { ok: true }
  }
}

export async function createProject(payload: {
  name: string
  mode: "local" | "remote"
  root_path?: string
  remote_url?: string
  required_connector?: string
}): Promise<{ ok: boolean; project?: ProjectItem; error?: string }> {
  try {
    const res = await fetch(API_BASE + "/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
    return await res.json()
  } catch (err) {
    console.error("Failed to create project:", err)
    return { ok: false, error: String(err) }
  }
}

/* ============================================================
 * Phase 2 Extended Endpoints: PTY, Connectors, Templates & Assets
 * ============================================================ */

export interface PTYSessionCreatePayload {
  session_id: string;
  command: string[];
  workdir?: string;
}

export interface FlowStepPayload {
  template_id: "issue-fix" | "pr-commit" | "auto-research";
  issue_id?: string;
  title?: string;
  role?: string;
  output?: string;
  branch?: string;
  commits?: Array<{ hash: string; message: string; author: string }>;
  topic?: string;
  notes?: string;
  score?: number;
}

export async function createPTYSession(payload: PTYSessionCreatePayload, authToken?: string) {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  const res = await fetch(`${API_BASE}/orchestration/pty`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function readPTYSession(sessionId: string) {
  const res = await fetch(`${API_BASE}/orchestration/pty/${sessionId}/read`);
  return res.json();
}

export async function writePTYSession(sessionId: string, input: string) {
  const res = await fetch(`${API_BASE}/orchestration/pty/${sessionId}/write`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input }),
  });
  return res.json();
}

export async function fetchConnectorTasks(source: "jira" | "plane", token: string, baseUrl?: string, projectId?: string) {
  const params = new URLSearchParams({ source });
  if (baseUrl) params.append("base_url", baseUrl);
  if (projectId) params.append("project_id", projectId);

  const res = await fetch(`${API_BASE}/connectors/tasks?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

export async function fetchConnectorDoc(docId: string, token: string, baseUrl?: string) {
  const params = new URLSearchParams({ doc_id: docId });
  if (baseUrl) params.append("base_url", baseUrl);

  const res = await fetch(`${API_BASE}/connectors/knowledge?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

export async function listMarketplaceAssets(role?: string) {
  const params = new URLSearchParams({ root: "." });
  if (role) params.append("role", role);
  const res = await fetch(`${API_BASE}/assets?${params.toString()}`);
  return res.json();
}

export async function distributeAsset(asset: any, targetPath: string = ".") {
  const assetPayload = typeof asset === "string" ? { id: asset, name: asset, type: "rule", content: "" } : asset;
  const res = await fetch(`${API_BASE}/assets/distribute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ asset: assetPayload, target_dir: targetPath }),
  });
  return res.json();
}

export async function executeTemplateStep(payload: FlowStepPayload) {
  const res = await fetch(`${API_BASE}/templates/step`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function fetchLearningHealth(): Promise<{ ok: boolean; health?: { score: number; stale_rules_count: number; rejections_count: number } } | null> {
  try {
    const res = await fetch(`${API_BASE}/governance/learning/health`);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn("fetchLearningHealth fallback:", err);
    return null;
  }
}
