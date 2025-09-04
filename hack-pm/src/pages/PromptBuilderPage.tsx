import { useMemo, useState } from 'react'
import { useAppState } from '../state/store'

function usePrompt(include: { overview: boolean; features: boolean; erd: boolean; gantt: boolean; instructions: boolean; }) {
  const { state } = useAppState()
  return useMemo(() => {
    const lines: string[] = []
    lines.push(`# Goal`)
    lines.push(`Create a PoC using Google AI Studio Build for a hackathon project management app.`)
    if (include.overview) {
      lines.push('', `## Project`, `Name: ${state.project.name}`, `Description: ${state.project.description || '(none)'}`)
    }
    if (include.features) {
      lines.push('', '## Functional Requirements')
      state.features.forEach(f => {
        lines.push(`- [${f.priority}] ${f.title} (${f.status})`)
        f.userStories.forEach(us => lines.push(`  - ${us}`))
      })
      if (state.features.length === 0) lines.push('- (no features yet)')
    }
    if (include.erd) {
      lines.push('', '## ER Model')
      state.entities.forEach(e => {
        lines.push(`- Entity ${e.name}`)
        e.attributes.forEach(a => lines.push(`  - ${a.name}: ${a.type}${a.pk ? ' PK' : ''}${a.nullable ? ' NULL' : ''}`))
      })
      if (state.relations.length) {
        lines.push('Relations:')
        state.relations.forEach(r => {
          const from = state.entities.find(e => e.id === r.from)?.name
          const to = state.entities.find(e => e.id === r.to)?.name
          lines.push(`- ${from} ${r.type} ${to}`)
        })
      }
    }
    if (include.gantt) {
      lines.push('', '## Timeline (Gantt)')
      state.tasks.forEach(t => lines.push(`- ${t.title}: ${t.startDate} -> ${t.endDate} (${t.progress}% done)`))
      if (state.tasks.length === 0) lines.push('- (no tasks yet)')
    }
    if (include.instructions) {
      lines.push('', '## Instructions')
      lines.push('- Generate a minimal UI that lists ideas, features, and tasks.')
      lines.push('- Focus on prototyping; prefer stubs/mocks where APIs are missing.')
      lines.push('- Provide concise, copy-pastable code snippets per component.')
    }
    return lines.join('\n')
  }, [state, include])
}

export default function PromptBuilderPage() {
  const [include, setInclude] = useState({ overview: true, features: true, erd: true, gantt: false, instructions: true })
  const prompt = usePrompt(include)
  const copy = async () => {
    try { await navigator.clipboard.writeText(prompt) } catch {}
  }
  return (
    <div className="page">
      <h1>プロンプト生成</h1>
      <div className="card">
        <div className="row gap wrap">
          <label><input type="checkbox" checked={include.overview} onChange={(e) => setInclude({ ...include, overview: e.target.checked })} /> 概要</label>
          <label><input type="checkbox" checked={include.features} onChange={(e) => setInclude({ ...include, features: e.target.checked })} /> 機能要件</label>
          <label><input type="checkbox" checked={include.erd} onChange={(e) => setInclude({ ...include, erd: e.target.checked })} /> ER図</label>
          <label><input type="checkbox" checked={include.gantt} onChange={(e) => setInclude({ ...include, gantt: e.target.checked })} /> ガント</label>
          <label><input type="checkbox" checked={include.instructions} onChange={(e) => setInclude({ ...include, instructions: e.target.checked })} /> 手順</label>
          <button onClick={copy}>クリップボードにコピー</button>
        </div>
      </div>
      <textarea rows={20} value={prompt} readOnly style={{ width: '100%', fontFamily: 'var(--font-mono)' }} />
    </div>
  )
}
