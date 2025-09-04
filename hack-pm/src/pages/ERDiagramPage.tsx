import { useMemo, useState } from 'react'
import type { Attribute, Entity, Relation } from '../state/store'
import { uid, useAppState } from '../state/store'
import Mermaid from '../components/Mermaid'

function EntityCard({ e, onUpdate, onRemove }: { e: Entity, onUpdate: (patch: Partial<Entity>) => void, onRemove: () => void }) {
  const [attrName, setAttrName] = useState('')
  const [attrType, setAttrType] = useState('TEXT')
  const addAttr = () => {
    if (!attrName.trim()) return
    const a: Attribute = { id: uid('attr'), name: attrName, type: attrType }
    onUpdate({ attributes: [...e.attributes, a] })
    setAttrName(''); setAttrType('TEXT')
  }
  const removeAttr = (id: string) => onUpdate({ attributes: e.attributes.filter(a => a.id !== id) })
  const toggle = (id: string, key: 'pk' | 'nullable') => onUpdate({ attributes: e.attributes.map(a => a.id === id ? { ...a, [key]: !a[key] } as any : a) })
  return (
    <div className="card">
      <div className="row space-between">
        <input className="grow" value={e.name} onChange={(ev) => onUpdate({ name: ev.target.value })} />
        <button onClick={onRemove}>削除</button>
      </div>
      <div className="row gap">
        <input placeholder="属性名" value={attrName} onChange={(e) => setAttrName(e.target.value)} />
        <input placeholder="型" value={attrType} onChange={(e) => setAttrType(e.target.value)} />
        <button onClick={addAttr}>追加</button>
      </div>
      <table className="attrs">
        <thead><tr><th>PK</th><th>属性名</th><th>型</th><th>NULL</th><th></th></tr></thead>
        <tbody>
          {e.attributes.map(a => (
            <tr key={a.id}>
              <td><input type="checkbox" checked={!!a.pk} onChange={() => toggle(a.id, 'pk')} /></td>
              <td>{a.name}</td>
              <td>{a.type}</td>
              <td><input type="checkbox" checked={!!a.nullable} onChange={() => toggle(a.id, 'nullable')} /></td>
              <td><button className="link" onClick={() => removeAttr(a.id)}>削除</button></td>
            </tr>
          ))}
          {e.attributes.length === 0 && <tr><td colSpan={5} className="muted">属性がありません</td></tr>}
        </tbody>
      </table>
    </div>
  )
}

export default function ERDiagramPage() {
  const { state, setState } = useAppState()
  const [newEntityName, setNewEntityName] = useState('')
  const [relFrom, setRelFrom] = useState('')
  const [relTo, setRelTo] = useState('')
  const [relType, setRelType] = useState<Relation['type']>('1..n')
  const [mm, setMm] = useState(state.erdMermaid || '')

  const addEntity = () => {
    if (!newEntityName.trim()) return
    const e: Entity = { id: uid('ent'), name: newEntityName, attributes: [] }
    setState(s => ({ ...s, entities: [...s.entities, e] }))
    setNewEntityName('')
  }
  const updateEntity = (id: string, patch: Partial<Entity>) => setState(s => ({ ...s, entities: s.entities.map(e => e.id === id ? { ...e, ...patch } : e) }))
  const removeEntity = (id: string) => setState(s => ({ ...s, entities: s.entities.filter(e => e.id !== id), relations: s.relations.filter(r => r.from !== id && r.to !== id) }))

  const addRelation = () => {
    if (!relFrom || !relTo || relFrom === relTo) return
    const r: Relation = { id: uid('rel'), from: relFrom, to: relTo, type: relType }
    setState(s => ({ ...s, relations: [...s.relations, r] }))
    setRelFrom(''); setRelTo('')
  }
  const removeRelation = (id: string) => setState(s => ({ ...s, relations: s.relations.filter(r => r.id !== id) }))

  const layout = useMemo(() => {
    // Simple vertical layout
    const width = 900
    const rowH = 160
    const positions = new Map<string, { x: number, y: number, w: number, h: number }>()
    state.entities.forEach((e, idx) => {
      positions.set(e.id, { x: 40, y: 40 + idx * rowH, w: 300, h: 120 })
    })
    const height = 80 + state.entities.length * rowH
    return { width, height, positions }
  }, [state.entities])

  return (
    <div className="page">
      <h1>ER 図</h1>
      <div className="card">
        <h3>Mermaid 表記</h3>
        <div className="row gap wrap">
          <button onClick={() => setState(s => ({ ...s, erdMermaid: mm }))}>保存</button>
          <button className="link" onClick={() => setMm(state.erdMermaid || '')}>元に戻す</button>
          <button className="link" onClick={() => setMm(generateMermaidFromState())}>エンティティから生成</button>
        </div>
        <div className="grid-2">
          <textarea rows={18} value={mm} onChange={(e) => setMm(e.target.value)} />
          <div style={{ overflow: 'auto' }}>
            <Mermaid code={mm || 'erDiagram\n  %% ここにMermaidを入力してください'} />
          </div>
        </div>
      </div>
      <div className="card">
        <div className="row gap wrap">
          <input placeholder="エンティティ名" value={newEntityName} onChange={(e) => setNewEntityName(e.target.value)} />
          <button onClick={addEntity}>追加</button>
          <div className="divider" />
          <label>リレーション</label>
          <select value={relFrom} onChange={(e) => setRelFrom(e.target.value)}>
            <option value="">から</option>
            {state.entities.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
          </select>
          <select value={relType} onChange={(e) => setRelType(e.target.value as any)}>
            <option value="1..1">1..1</option>
            <option value="1..n">1..n</option>
            <option value="n..m">n..m</option>
          </select>
          <select value={relTo} onChange={(e) => setRelTo(e.target.value)}>
            <option value="">へ</option>
            {state.entities.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
          </select>
          <button onClick={addRelation}>追加</button>
        </div>
      </div>

      <div className="grid-2">
        <div>
          {state.entities.map(e => (
            <EntityCard key={e.id} e={e} onUpdate={(patch) => updateEntity(e.id, patch)} onRemove={() => removeEntity(e.id)} />
          ))}
          {state.entities.length === 0 && <div className="muted">No entities yet.</div>}
        </div>
        <div>
          <svg width={layout.width} height={layout.height} style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8 }}>
            {state.relations.map(r => {
              const a = layout.positions.get(r.from)!
              const b = layout.positions.get(r.to)!
              const x1 = a.x + a.w
              const y1 = a.y + a.h / 2
              const x2 = b.x
              const y2 = b.y + b.h / 2
              const mid = (x1 + x2) / 2
              return (
                <g key={r.id}>
                  <path d={`M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}`} stroke="var(--text-muted)" fill="none" />
                  <text x={(x1 + x2) / 2} y={(y1 + y2) / 2 - 6} fontSize="10" textAnchor="middle" fill="var(--text-muted)">{r.type}</text>
                </g>
              )
            })}
          </svg>
          <div className="list">
            {state.relations.map(r => (
              <div className="row space-between" key={r.id}>
                <span>
                  {state.entities.find(e => e.id === r.from)?.name} — {r.type} → {state.entities.find(e => e.id === r.to)?.name}
                </span>
                <button className="link" onClick={() => removeRelation(r.id)}>削除</button>
              </div>
            ))}
            {state.relations.length === 0 && <div className="muted">リレーションがありません</div>}
          </div>
        </div>
      </div>
    </div>
  )
}

function generateMermaidFromState() {
  // 画面上の state からMermaidを生成する（シンプル版）
  // 注意: 実体の state はクロージャ外なので、呼び出し元で反映された値になる
  // ここではウィンドウから取得
  try {
    const s = (window as any).hackpm_state as import('../state/store').AppState | undefined
    if (!s) return ''
    const lines: string[] = ['erDiagram']
    s.relations.forEach(r => {
      const from = s.entities.find(e => e.id === r.from)?.name || r.from
      const to = s.entities.find(e => e.id === r.to)?.name || r.to
      const symbol = r.type === '1..1' ? '||--||' : r.type === '1..n' ? '||--o{' : '}o--o{'
      lines.push(`  ${from} ${symbol} ${to} : rel`)
    })
    s.entities.forEach(e => {
      lines.push(`  ${e.name} {`)
      e.attributes.forEach(a => {
        const mods = `${a.pk ? ' PK' : ''}`
        lines.push(`    ${a.type} ${a.name}${mods}`)
      })
      lines.push('  }')
    })
    return lines.join('\n')
  } catch { return '' }
}
