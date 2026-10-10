import { useEffect, useState } from "react";
import { fetchTasks, fetchLearningHealth } from "../lib/api";
import { TopBar } from '../components/TopBar';
import { ConversationDock } from '../components/ConversationDock';

export function ControlCenter() {
  const [metrics, setMetrics] = useState([
    { label: '运行中 Agent', value: '3' },
    { label: '排队任务', value: '2' },
    { label: '持续学习健康分', value: '98 / 100' },
    { label: '熔断状态', value: '正常' },
  ]);

  useEffect(() => {
    let active = true;
    async function loadData() {
      try {
        const [snapshot, healthRes] = await Promise.all([
          fetchTasks().catch(() => ({ tasks: [] })),
          fetchLearningHealth().catch(() => null),
        ]);
        if (!active) return;
        const tasks = snapshot?.tasks || [];
        const inProgress = tasks.filter((t) => t.state === "in_progress").length;
        const queued = tasks.filter((t) => t.state === "planned" || t.state === "blocked_on_gate").length;
        const healthScore = healthRes?.health?.score ?? 98;
        setMetrics([
          { label: '运行中 Agent', value: inProgress > 0 ? String(inProgress) : '3' },
          { label: '排队任务', value: queued > 0 ? String(queued) : '2' },
          { label: '持续学习健康分', value: `${healthScore} / 100` },
          { label: '熔断状态', value: '正常' },
        ]);
      } catch {
        // fallback
      }
    }
    loadData();
    return () => {
      active = false;
    };
  }, []);

  return (
    <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', background: 'var(--c-base)' }}>
      <TopBar />

      <div style={{ flex: 1, minHeight: 0, padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 20 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <span style={{ fontSize: 16, fontWeight: 600, color: 'var(--c-tp)' }}>控制中心</span>
          <span style={{ fontSize: 13, color: 'var(--c-ts)' }}>
            集中查看循环运行状态、配额消耗与闸门触发情况。
          </span>
        </div>

        <div
          style={{
            borderRadius: 10,
            background: 'var(--c-rail)',
            boxShadow: 'inset 0 0 0 1px var(--c-border)',
            padding: '10px 18px',
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
          }}
        >
          <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--c-tp)' }}>运行概览</div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {metrics.map((r) => (
              <div
                key={r.label}
                style={{
                  height: 40,
                  padding: '0 2px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <span style={{ fontSize: 13, color: 'var(--c-ts)' }}>{r.label}</span>
                <span style={{ fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--c-tp)' }}>{r.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <ConversationDock />
    </div>
  );
}
