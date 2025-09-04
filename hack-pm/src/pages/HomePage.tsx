import { useAppState } from '../state/store'
import { useState } from 'react'
import type { Feature } from '../state/store'
import { generateFromIdeas } from '../auto/planner'
import { generatePlanWithAI } from '../ai/openai'

export default function HomePage() {
  const { state, setState } = useAppState()
  const [gen, setGen] = useState({ features: true, gantt: true, erd: true, overwrite: false })
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  return (
    <div className="page">
      <h1>プロジェクト概要</h1>
      <div className="card">
        <label>プロジェクト名</label>
        <input
          value={state.project.name}
          onChange={(e) => setState(s => ({ ...s, project: { ...s.project, name: e.target.value } }))}
        />
      </div>
      <div className="card">
        <label>説明</label>
        <textarea
          rows={6}
          placeholder="ハッカソンの目的・制約・関係者などを記述してください"
          value={state.project.description}
          onChange={(e) => setState(s => ({ ...s, project: { ...s.project, description: e.target.value } }))}
        />
      </div>
      <div className="grid-3">
        <div className="tile">
          <div className="tile-title">アイデア</div>
          <div className="tile-value">{state.ideas.length}</div>
        </div>
        <div className="tile">
          <div className="tile-title">機能</div>
          <div className="tile-value">{state.features.length}</div>
        </div>
        <div className="tile">
          <div className="tile-title">タスク</div>
          <div className="tile-value">{state.tasks.length}</div>
        </div>
      </div>
      <div className="card">
        <h3>自動生成</h3>
        <p className="muted">PJT設定とアイデアをもとに、機能要件・ガント・ER 図を一括で作成します。</p>
        <div className="row gap wrap">
          <label><input type="checkbox" checked={gen.features} onChange={e => setGen({ ...gen, features: e.target.checked })} /> 機能要件</label>
          <label><input type="checkbox" checked={gen.gantt} onChange={e => setGen({ ...gen, gantt: e.target.checked })} /> ガント</label>
          <label><input type="checkbox" checked={gen.erd} onChange={e => setGen({ ...gen, erd: e.target.checked })} /> ER 図</label>
          <label><input type="checkbox" checked={gen.overwrite} onChange={e => setGen({ ...gen, overwrite: e.target.checked })} /> 既存を上書き</label>
          <button onClick={() => {
            const patch = generateFromIdeas(state, gen)
            setState(s => ({
              ...s,
              features: patch.features ?? s.features,
              tasks: patch.tasks ?? s.tasks,
              entities: patch.entities ?? s.entities,
              relations: patch.relations ?? s.relations,
            }))
          }}>自動生成</button>
          <button onClick={async () => {
            setBusy(true); setMsg(null)
            try {
              const plan = await generatePlanWithAI(state, gen)
              // features
              if (gen.features && plan.features?.length) {
                setState(s => ({ ...s, features: gen.overwrite ? plan.features!.map((f, i) => ({ id: `feat_ai_${i}`, title: f.title, description: f.description, priority: (f.priority || 'P1') as Feature['priority'], status: 'planned' as const, userStories: [] })) : [
                  ...s.features,
                  ...plan.features!.map((f, i) => ({ id: `feat_ai_${i}`, title: f.title, description: f.description, priority: (f.priority || 'P1') as Feature['priority'], status: 'planned' as const, userStories: [] }))
                ] }))
              }
              // tasks: sequential schedule from today
              if (gen.gantt && plan.tasks?.length) {
                const start = new Date()
                let startISO = start.toISOString().slice(0,10)
                const tasks = plan.tasks.map((t, i) => {
                  const dur = Math.max(1, Math.floor(t.duration_days || 1))
                  const s = startISO
                  const e = addDaysISO(s, dur)
                  startISO = e
                  return { id: `task_ai_${i}`, title: t.title, startDate: s, endDate: e, assignee: '', progress: 0, dependsOn: [] as string[] }
                })
                setState(s => ({ ...s, tasks: gen.overwrite ? tasks : [...s.tasks, ...tasks] }))
              }
              if (gen.erd && plan.erd_mermaid) {
                setState(s => ({ ...s, erdMermaid: plan.erd_mermaid! }))
              }
              setMsg('AIによる自動生成が完了しました。')
            } catch (e) {
              setMsg(String((e as Error)?.message || e))
            } finally { setBusy(false) }
          }} disabled={busy}>{busy ? 'AI生成中...' : 'AI自動生成'}</button>
        </div>
        {msg && <p className="muted">{msg}</p>}
      </div>
    </div>
  )
}

function addDaysISO(iso: string, days: number) {
  const d = new Date(iso)
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0,10)
}
