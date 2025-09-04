import type { AppState, Feature, Idea, Task, Entity, Relation } from '../state/store'
import { uid } from '../state/store'

export type GenerateOptions = {
  features?: boolean
  gantt?: boolean
  erd?: boolean
  overwrite?: boolean
  maxItems?: number
}

function pickIdeas(ideas: Idea[], max = 6): Idea[] {
  const selected = ideas.filter(i => i.status === 'selected')
  if (selected.length) return selected.slice(0, max)
  return [...ideas]
    .sort((a, b) => (b.impact - b.effort) - (a.impact - a.effort))
    .slice(0, max)
}

function toPriority(i: Idea['impact'], e: Idea['effort']): Feature['priority'] {
  if (i >= 4 && e <= 3) return 'P0'
  if (i >= 3 && e <= 4) return 'P1'
  return 'P2'
}

function addDays(dateISO: string, days: number) {
  const d = new Date(dateISO)
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}

export function generateFromIdeas(state: AppState, opt: GenerateOptions) {
  const ideas = pickIdeas(state.ideas, opt.maxItems ?? 6)
  const result: Partial<AppState> = {}

  if (opt.features) {
    const features: Feature[] = ideas.map(i => ({
      id: uid('feat'),
      title: i.title,
      description: i.description || `この機能は「${i.title}」アイデアに基づきます。`,
      priority: toPriority(i.impact, i.effort),
      status: 'planned',
      userStories: [
        `（仮）ユーザーとして、${i.title} を使いたい。なぜなら価値は ${i.impact} で工数 ${i.effort} だから。`,
      ],
    }))
    result.features = opt.overwrite ? features : [...state.features, ...features]
  }

  if (opt.gantt) {
    const tasks: Task[] = []
    const start = new Date()
    let current = start.toISOString().slice(0, 10)
    const feats = (result.features ?? state.features)
    const source = feats.length ? feats : ideas.map(i => ({ id: uid('feat'), title: i.title })) as any
    for (const f of source) {
      const devDays = 2
      const testDays = 1
      const devStart = current
      const devEnd = addDays(devStart, devDays)
      const testStart = devEnd
      const testEnd = addDays(testStart, testDays)
      tasks.push({ id: uid('task'), title: `実装: ${f.title}`, startDate: devStart, endDate: devEnd, assignee: '', progress: 0, dependsOn: [] })
      tasks.push({ id: uid('task'), title: `テスト/デモ: ${f.title}`, startDate: testStart, endDate: testEnd, assignee: '', progress: 0, dependsOn: [] })
      current = testEnd
    }
    // バッファと準備
    tasks.push({ id: uid('task'), title: '最終調整/発表準備', startDate: current, endDate: addDays(current, 1), assignee: '', progress: 0, dependsOn: [] })
    result.tasks = opt.overwrite ? tasks : [...state.tasks, ...tasks]
  }

  if (opt.erd) {
    // 基本エンティティ
    const base: Entity[] = [
      { id: uid('ent'), name: 'Project', attributes: [
        { id: uid('attr'), name: 'id', type: 'UUID', pk: true },
        { id: uid('attr'), name: 'name', type: 'TEXT' },
      ]},
      { id: uid('ent'), name: 'Feature', attributes: [
        { id: uid('attr'), name: 'id', type: 'UUID', pk: true },
        { id: uid('attr'), name: 'title', type: 'TEXT' },
        { id: uid('attr'), name: 'priority', type: 'TEXT' },
        { id: uid('attr'), name: 'status', type: 'TEXT' },
      ]},
      { id: uid('ent'), name: 'Task', attributes: [
        { id: uid('attr'), name: 'id', type: 'UUID', pk: true },
        { id: uid('attr'), name: 'title', type: 'TEXT' },
        { id: uid('attr'), name: 'start_date', type: 'DATE' },
        { id: uid('attr'), name: 'end_date', type: 'DATE' },
        { id: uid('attr'), name: 'progress', type: 'INT' },
      ]},
      { id: uid('ent'), name: 'Idea', attributes: [
        { id: uid('attr'), name: 'id', type: 'UUID', pk: true },
        { id: uid('attr'), name: 'title', type: 'TEXT' },
        { id: uid('attr'), name: 'impact', type: 'INT' },
        { id: uid('attr'), name: 'effort', type: 'INT' },
      ]},
    ]
    const ents = opt.overwrite ? base : [...state.entities, ...base]
    const find = (name: string) => ents.find(e => e.name === name)!.id
    const relations: Relation[] = [
      { id: uid('rel'), from: find('Project'), to: find('Feature'), type: '1..n' },
      { id: uid('rel'), from: find('Feature'), to: find('Task'), type: '1..n' },
      { id: uid('rel'), from: find('Idea'), to: find('Feature'), type: '1..n' },
    ]
    result.entities = ents
    result.relations = opt.overwrite ? relations : [...state.relations, ...relations]
  }

  return result
}

