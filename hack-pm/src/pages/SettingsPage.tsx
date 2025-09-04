import { useEffect, useRef, useState } from 'react'
import { useAppState } from '../state/store'
import { getStoredApiKey, setStoredApiKey } from '../ai/openai'

export default function SettingsPage() {
  const { exportJson, importJson, setState } = useAppState()
  const fileRef = useRef<HTMLInputElement>(null)
  const [apiKey, setApiKey] = useState('')

  useEffect(() => {
    setApiKey(getStoredApiKey() || '')
  }, [])

  const onExport = () => {
    const blob = new Blob([exportJson()], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'hackpm_data.json'
    a.click()
    URL.revokeObjectURL(url)
  }
  const onImport = (file?: File) => {
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => { importJson(String(reader.result || '')) }
    reader.readAsText(file)
  }
  const onReset = () => {
    if (confirm('全データをリセットしますか？')) setState(s => ({
      project: { name: 'New Hackathon Project', description: '' },
      ideas: [], features: [], tasks: [], entities: [], relations: [],
      erdMermaid: s.erdMermaid,
      ganttConfig: { scale: 'day', workStart: 9, workEnd: 18 }
    }))
  }

  return (
    <div className="page">
      <h1>設定</h1>
      <div className="card">
        <div className="row gap wrap">
          <button onClick={onExport}>JSONエクスポート</button>
          <input ref={fileRef} type="file" accept="application/json" style={{ display: 'none' }} onChange={(e) => onImport(e.target.files?.[0])} />
          <button onClick={() => fileRef.current?.click()}>JSONインポート</button>
          <button className="danger" onClick={onReset}>リセット</button>
        </div>
      </div>
      <div className="card">
        <h3>OpenAI API</h3>
        <p className="muted">APIキーはこの端末の localStorage に保存され、ブラウザからOpenAI APIへ直接アクセスします（セキュリティ上のリスクを理解した上で利用してください）。</p>
        <div className="row gap wrap">
          <input type="password" className="grow" placeholder="OpenAI API Key (sk-...)" value={apiKey} onChange={(e) => setApiKey(e.target.value)} />
          <button onClick={() => setStoredApiKey(apiKey)}>保存</button>
        </div>
      </div>
      <p className="muted">データはブラウザの localStorage に自動保存されます。</p>
    </div>
  )
}
