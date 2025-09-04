import { useState } from 'react'
import type { Feature } from '../state/store'
import { uid, useAppState } from '../state/store'

function FeatureForm({ onAdd }: { onAdd: (f: Feature) => void }) {
  const [title, setTitle] = useState('')
  const [desc, setDesc] = useState('')
  const [priority, setPriority] = useState<Feature['priority']>('P1')
  return (
    <div className="card">
      <h3>機能追加</h3>
      <input placeholder="タイトル" value={title} onChange={(e) => setTitle(e.target.value)} />
      <textarea placeholder="説明" rows={4} value={desc} onChange={(e) => setDesc(e.target.value)} />
      <div className="row gap">
        <label>優先度</label>
        <select value={priority} onChange={(e) => setPriority(e.target.value as any)}>
          <option value="P0">P0</option>
          <option value="P1">P1</option>
          <option value="P2">P2</option>
        </select>
      </div>
      <button onClick={() => {
        if (!title.trim()) return
        onAdd({ id: uid('feat'), title, description: desc, priority, status: 'planned', userStories: [] })
        setTitle(''); setDesc(''); setPriority('P1')
      }}>追加</button>
    </div>
  )
}

export default function RequirementsPage() {
  const { state, setState } = useAppState()
  const [story, setStory] = useState('')

  const addFeature = (f: Feature) => setState(s => ({ ...s, features: [f, ...s.features] }))
  const removeFeature = (id: string) => setState(s => ({ ...s, features: s.features.filter(f => f.id !== id) }))
  const updateFeature = (id: string, patch: Partial<Feature>) => setState(s => ({ ...s, features: s.features.map(f => f.id === id ? { ...f, ...patch } : f) }))

  return (
    <div className="page">
      <h1>機能要件</h1>
      <FeatureForm onAdd={addFeature} />
      <div className="list">
        {state.features.map(f => (
          <div key={f.id} className="card">
            <div className="row space-between">
              <div className="row gap">
                <strong>{f.title}</strong>
                <span className={`badge ${f.priority.toLowerCase()}`}>{f.priority}</span>
              </div>
              <div className="row gap">
                <select value={f.status} onChange={(e) => updateFeature(f.id, { status: e.target.value as any })}>
                  <option value="planned">計画</option>
                  <option value="in-progress">進行中</option>
                  <option value="done">完了</option>
                </select>
                <button onClick={() => removeFeature(f.id)}>削除</button>
              </div>
            </div>
            {f.description && <p>{f.description}</p>}
            <div className="card light">
              <h4>ユーザーストーリー</h4>
              <div className="row">
                <input className="grow" placeholder="（例）〜として、〜したい。なぜなら〜だからだ。" value={story} onChange={(e) => setStory(e.target.value)} />
                <button onClick={() => { if (story.trim()) { updateFeature(f.id, { userStories: [story, ...f.userStories] }); setStory('') } }}>追加</button>
              </div>
              <ul className="bullets">
                {f.userStories.map((s, idx) => (
                  <li key={idx}>
                    {s}
                    <button className="link" onClick={() => updateFeature(f.id, { userStories: f.userStories.filter((_, i) => i !== idx) })}>削除</button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
        {state.features.length === 0 && <div className="muted">まだ機能がありません。</div>}
      </div>
    </div>
  )
}
