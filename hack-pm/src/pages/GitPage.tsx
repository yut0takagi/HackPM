import { useEffect, useMemo, useRef, useState } from 'react'

type Branch = { current: boolean; name: string }
type Status = { branch: string; ahead: number; behind: number; files: Array<{ path: string; index: string; working_dir: string }> }

const API = (path: string) => `${location.origin.replace(/:\d+$/, '')}:8787${path}`

export default function GitPage() {
  const [branches, setBranches] = useState<Branch[]>([])
  const [status, setStatus] = useState<Status | null>(null)
  const [msg, setMsg] = useState('')
  const [autoFetch, setAutoFetch] = useState(true)
  const [presence, setPresence] = useState<{ id: string; name: string }[]>([])
  const [name, setName] = useState(() => localStorage.getItem('hackpm_name') || '')
  const wsRef = useRef<WebSocket | null>(null)

  const currentBranch = useMemo(() => branches.find(b => b.current)?.name || status?.branch || '', [branches, status])

  async function loadBranches() {
    try { const r = await fetch(API('/git/branches')); setBranches(await r.json()) } catch {}
  }
  async function loadStatus() {
    try { const r = await fetch(API('/git/status')); setStatus(await r.json()) } catch {}
  }
  async function doCheckout(name: string) {
    await fetch(API('/git/checkout'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name }) })
    await Promise.all([loadBranches(), loadStatus()])
  }
  async function doCreateBranch(name: string) {
    await fetch(API('/git/create-branch'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, checkout: true }) })
    await Promise.all([loadBranches(), loadStatus()])
  }
  async function doAddAll() {
    await fetch(API('/git/add'), { method: 'POST' })
    await loadStatus()
  }
  async function doCommit() {
    if (!msg.trim()) return
    await fetch(API('/git/commit'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: msg }) })
    setMsg(''); await loadStatus()
  }
  async function doPush() {
    await fetch(API('/git/push'), { method: 'POST' })
    await loadStatus()
  }
  async function doFetch() { await fetch(API('/git/fetch'), { method: 'POST' }); await loadStatus() }

  useEffect(() => { loadBranches(); loadStatus() }, [])
  useEffect(() => {
    if (!autoFetch) return
    const id = setInterval(() => { doFetch().catch(() => {}) }, 30000)
    return () => clearInterval(id)
  }, [autoFetch])

  useEffect(() => {
    localStorage.setItem('hackpm_name', name)
    try {
      if (wsRef.current) wsRef.current.close()
      const ws = new WebSocket(`ws://${location.hostname}:8787/presence`)
      wsRef.current = ws
      ws.onopen = () => { ws.send(JSON.stringify({ type: 'hello', name })) }
      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data)
          if (data.type === 'presence') setPresence(data.list)
        } catch {}
      }
      return () => ws.close()
    } catch { return }
  }, [name])

  return (
    <div className="page">
      <h1>Git</h1>

      <div className="card">
        <div className="row gap wrap">
          <label>ブランチ</label>
          <select value={currentBranch} onChange={(e) => doCheckout(e.target.value)}>
            {branches.map(b => <option key={b.name} value={b.name}>{b.current ? '✓ ' : ''}{b.name}</option>)}
          </select>
          <input placeholder="新規ブランチ名" onKeyDown={(e) => { if (e.key==='Enter') doCreateBranch((e.target as HTMLInputElement).value) }} />
          <button onClick={() => { const el = document.activeElement as HTMLInputElement; if (el?.value) doCreateBranch(el.value) }}>作成してチェックアウト</button>
          <label><input type="checkbox" checked={autoFetch} onChange={(e) => setAutoFetch(e.target.checked)} /> 自動fetch</label>
          <button onClick={doFetch}>Fetch</button>
        </div>
      </div>

      <div className="card">
        <div className="row gap wrap">
          <button onClick={doAddAll}>Add .</button>
          <input className="grow" placeholder="コミットメッセージ" value={msg} onChange={(e) => setMsg(e.target.value)} onKeyDown={(e) => { if (e.key==='Enter') doCommit() }} />
          <button onClick={doCommit}>Commit</button>
          <button onClick={doPush}>Push</button>
        </div>
        <div className="row gap wrap" style={{ marginTop: 8 }}>
          <span className="muted">HEAD: {status?.branch} ↑{status?.ahead ?? 0} ↓{status?.behind ?? 0}</span>
        </div>
      </div>

      <div className="card">
        <h3>変更ファイル</h3>
        {status?.files?.length ? (
          <ul className="bullets">
            {status?.files?.map((f, i) => <li key={i}><code>{f.path}</code> <span className="muted">[{f.index}{f.working_dir}]</span></li>)}
          </ul>
        ) : <div className="muted">未変更</div>}
      </div>

      <div className="card">
        <h3>メンバーのプレゼンス</h3>
        <div className="row gap wrap">
          <label>名前</label>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="あなたの名前" />
        </div>
        <ul className="bullets" style={{ marginTop: 8 }}>
          {presence.map(p => <li key={p.id}>{p.name || '(名無し)'} <span className="muted">{p.id}</span></li>)}
        </ul>
      </div>
    </div>
  )
}

