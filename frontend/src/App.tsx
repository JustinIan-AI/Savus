import { useCallback, useEffect, useState } from 'react'
import { useScale } from './lib/useScale'
import { LeftRail } from './components/LeftRail'
import { TaskBoard, type OpenTask } from './screens/TaskBoard'
import { TaskDetail } from './screens/TaskDetail'
import { TeamAssets } from './screens/TeamAssets'
import { ControlCenter } from './screens/ControlCenter'
import { SettingsAgent } from './screens/SettingsAgent'
import { SettingsMcp } from './screens/SettingsMcp'
import { SettingsOther } from './screens/SettingsOther'
import { SessionDrawer } from './overlays/SessionDrawer'
import {
  AddAgentModal,
  AddConnectorModal,
  GateDecisionModal,
  NewTaskModal,
  type NewTaskPayload,
} from './overlays/Modals'
import {
  DEFAULT_PROJECT_ID,
  createTask,
  fetchTasks,
  submitGateDecision,
  subscribeToEvents,
  updateTask,
  type ApiTask,
} from './lib/api'
import { DEFAULT_TASK_ID, setRuntimeTasks, taskById, type DetailAnchor, type NavKey } from './data'
import type { SettingsTab } from './screens/SettingsShell'

/* ============================================================
   App —— 前端与任务控制面（gateway）的唯一接线点

   数据单向下行：网关 → `fetchTasks` → `setRuntimeTasks`（data.ts 的
   叠加层）→ 看板 / 右栏 / 详情重新生成。界面上没有任何一处再持有
   会与后端脱钩的本地副本。
   上行两条：`createTask`（新建任务）、`submitGateDecision`（审批门
   裁决）。两条都写完之后重新取一次快照，而不是本地推测状态。
   事件总线 `subscribeToEvents` 负责把别处发生的变更推回来。
   ============================================================ */

export default function App() {
  const scale = useScale()
  const [nav, setNav] = useState<NavKey>('board')
  /** 看板选中态：右栏整块内容跟着它走。单击卡片改它，不跳页。 */
  const [selectedId, setSelectedId] = useState(DEFAULT_TASK_ID)
  /** 帧 10 详情：哪个任务 + 要滚到哪个区块。交付物清单的「内链」会带锚点进来。 */
  const [detail, setDetail] = useState<{ id: string; anchor?: DetailAnchor } | null>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [newTaskOpen, setNewTaskOpen] = useState(false)
  const [addAgentOpen, setAddAgentOpen] = useState(false)
  const [addConnectorOpen, setAddConnectorOpen] = useState(false)
  /** 审批门裁决模态：目标任务 + 预选裁决（「打回」进来就是驳回）。 */
  const [gateModal, setGateModal] = useState<
    { id: string; title: string; decision: 'approved' | 'denied' } | null
  >(null)

  /** 网关任务快照 —— 同时是「接线是否活着」的可观测面。 */
  const [tasks, setTasks] = useState<ApiTask[]>([])
  const [online, setOnline] = useState(false)

  /** 拉一次任务快照。必须先灌叠加层再 setState —— 渲染时读的就是它。 */
  const refresh = useCallback(async () => {
    const snap = await fetchTasks(DEFAULT_PROJECT_ID)
    setRuntimeTasks(snap.tasks)
    setTasks(snap.tasks)
    setOnline(snap.ok)
    return snap
  }, [])

  useEffect(() => {
    void refresh()
    /* 后端 SSE 事件总线：task_created / gate_decision_recorded 都会推过来，
       收到就重新取快照，看板因此不需要本地推测状态。 */
    const stop = subscribeToEvents(
      () => {
        void refresh()
      },
      () => {
        /* EventSource 会自己重连。唯一要处理的错误是「连上了但服务没了」，
           此时下一次 refresh 会把 online 打回 false。 */
        setOnline(false)
      }
    )
    return stop
  }, [refresh])

  const isSettings = nav.startsWith('settings')
  const settingsTab = (isSettings ? nav : 'settings-agent') as SettingsTab

  const handleNav = (k: NavKey) => {
    setNav(k)
    setDetail(null)
    if (k.startsWith('settings')) setDrawerOpen(false)
  }

  const handleSettingsTab = (t: SettingsTab) => setNav(t)

  const openTask: OpenTask = (cardId, anchor) => setDetail({ id: cardId, anchor })

  /** 卡片动作 → 审批门裁决。打回预选驳回，其余预选放行。 */
  const openGate = (cardId: string, decision: 'approved' | 'denied') => {
    setSelectedId(cardId)
    setGateModal({ id: cardId, title: taskById(cardId)?.title ?? cardId, decision })
  }

  /** POST 新建任务，随后重新取快照，并选中刚建出来的那条。 */
  const handleCreateTask = async (payload: NewTaskPayload) => {
    setNewTaskOpen(false)
    const created = await createTask(DEFAULT_PROJECT_ID, payload)
    await refresh()
    if (created && created.id) setSelectedId(created.id)
  }

  /** POST 审批门裁决，随后重新取快照 —— 卡片状态与列位由后端说话。 */
  const handleGateDecision = async (decision: 'approved' | 'denied', comment: string) => {
    const target = gateModal
    setGateModal(null)
    if (!target) return
    await submitGateDecision(target.id, { decision, comment, title: target.title })
    await refresh()
  }

  /** PATCH 任务状态（提交评审 / 状态下拉），随后重新取快照。

      这条路径是 **upsert**：看板上的画布卡片只是设计稿夹具，工作区里
      未必有对应条目，因此把一张种子卡移到「评审中」必须顺便把它物化，
      否则卡片会在下次取快照时跌回原列。带了标题就是为了这一步。 */
  const handleSetStatus = async (cardId: string, status: string) => {
    const card = taskById(cardId)
    const res = await updateTask(cardId, { status, title: card?.title })
    if (!res.ok) console.warn('Set status failed:', res.error)
    await refresh()
  }

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'var(--c-base)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
      }}
    >
      <div
        /* 纯观测钩子（不产生任何像素）：给端到端走查读接线状态用。 */
        data-loopdesk-online={online ? 'true' : 'false'}
        data-loopdesk-tasks={tasks.length}
        style={{
          width: 1440,
          height: 900,
          flexShrink: 0,
          transform: `scale(${scale})`,
          transformOrigin: 'center center',
          display: 'flex',
          overflow: 'hidden',
          background: 'var(--c-base)',
        }}
      >
        <LeftRail
          active={nav}
          onNav={handleNav}
          onNewTask={() => setNewTaskOpen(true)}
          onOpenChannel={() => setDrawerOpen(true)}
        />

        <main style={{ flex: 1, display: 'flex', minWidth: 0 }}>
          {nav === 'board' &&
            (detail ? (
              <TaskDetail taskId={detail.id} anchor={detail.anchor} onBack={() => setDetail(null)} />
            ) : (
              <TaskBoard
                onNewTask={() => setNewTaskOpen(true)}
                onOpenTask={openTask}
                selectedId={selectedId}
                onSelect={setSelectedId}
                onGate={openGate}
                onSetStatus={handleSetStatus}
              />
            ))}
          {nav === 'assets' && <TeamAssets />}
          {nav === 'control' && <ControlCenter />}
          {nav === 'settings-agent' && (
            <SettingsAgent active={settingsTab} onTab={handleSettingsTab} onAddAgent={() => setAddAgentOpen(true)} />
          )}
          {nav === 'settings-mcp' && (
            <SettingsMcp active={settingsTab} onTab={handleSettingsTab} onAddConnector={() => setAddConnectorOpen(true)} />
          )}
          {nav === 'settings-other' && <SettingsOther active={settingsTab} onTab={handleSettingsTab} />}
        </main>

        {drawerOpen && <SessionDrawer onClose={() => setDrawerOpen(false)} onNewSession={() => setDrawerOpen(false)} />}
        {newTaskOpen && <NewTaskModal onClose={() => setNewTaskOpen(false)} onConfirm={handleCreateTask} onNavigateSettings={() => setNav('settings-mcp')} />}
        {addAgentOpen && <AddAgentModal onClose={() => setAddAgentOpen(false)} onConfirm={() => setAddAgentOpen(false)} />}
        {addConnectorOpen && (
          <AddConnectorModal onClose={() => setAddConnectorOpen(false)} onConfirm={() => setAddConnectorOpen(false)} />
        )}
        {gateModal && (
          <GateDecisionModal
            /* 换一张卡或换一个预选裁决都要重新挂载，否则 useState 会留住上一次的选择 */
            key={`${gateModal.id}:${gateModal.decision}`}
            taskId={gateModal.id}
            taskTitle={gateModal.title}
            initialDecision={gateModal.decision}
            onClose={() => setGateModal(null)}
            onConfirm={handleGateDecision}
          />
        )}
      </div>
    </div>
  )
}
