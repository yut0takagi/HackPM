import type { AppState, Feature } from '../state/store'

const LOCAL_KEY = 'hackpm_openai_api_key'

export function getStoredApiKey(): string | null {
  try { return localStorage.getItem(LOCAL_KEY) } catch { return null }
}
export function setStoredApiKey(key: string) {
  try { localStorage.setItem(LOCAL_KEY, key) } catch {}
}

function getApiKey(): string | null {
  const k = getStoredApiKey() || (import.meta as any).env?.VITE_OPENAI_API_KEY || null
  return k && k.trim() ? k : null
}

function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

export type AiOptions = {
  features?: boolean
  gantt?: boolean
  erd?: boolean
  maxItems?: number
}

export type AiPlan = {
  features?: Array<{ title: string; description?: string; priority?: Feature['priority'] }>
  tasks?: Array<{ title: string; duration_days?: number }>
  erd_mermaid?: string
}

export async function generatePlanWithAI(state: AppState, opt: AiOptions): Promise<AiPlan> {
  const apiKey = getApiKey()
  if (!apiKey) throw new Error('OpenAI APIキーが設定されていません。設定画面で保存してください。')

  const items = (opt.maxItems && opt.maxItems > 0) ? opt.maxItems : 6
  const startDate = todayISO()
  const wants: string[] = []
  if (opt.features) wants.push('features')
  if (opt.gantt) wants.push('tasks')
  if (opt.erd) wants.push('erd_mermaid')

  const body = {
    model: 'gpt-4o-mini',
    temperature: 0.2,
    messages: [
      { role: 'system', content: 'あなたは熟練のプロダクトマネージャー兼アーキテクトです。出力は必ず有効なJSONのみで返してください。' },
      { role: 'user', content: `以下のハッカソンPJT情報から、${wants.join(' / ')} を日本語で提案してください。必ずJSONのみで返し、コードフェンスは不要。最大アイテム数: ${items}。` },
      { role: 'user', content: JSON.stringify({
        project: state.project,
        ideas: state.ideas,
        start_date: startDate,
        want: wants,
        format: {
          features: [{ title: 'string', description: 'string', priority: 'P0|P1|P2' }],
          tasks: [{ title: 'string', duration_days: 1 }],
          erd_mermaid: 'string (MermaidのerDiagram)'
        }
      }) }
    ]
  }

  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const t = await res.text().catch(() => '')
    throw new Error(`OpenAI APIエラー: ${res.status} ${t}`)
  }
  const json = await res.json()
  const content: string = json.choices?.[0]?.message?.content || ''
  // JSON以外の文字を取り除く簡易パーサ
  const match = content.match(/\{[\s\S]*\}/)
  const payload = match ? match[0] : content
  let data: AiPlan
  try {
    data = JSON.parse(payload)
  } catch (e) {
    throw new Error('AI出力のJSON解析に失敗しました。')
  }
  return data
}

