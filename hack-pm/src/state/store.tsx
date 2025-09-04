import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'

export type Idea = {
  id: string
  title: string
  description?: string
  tags: string[]
  impact: number // 1-5
  effort: number // 1-5
  status: 'new' | 'selected' | 'icebox'
}

export type Feature = {
  id: string
  title: string
  description?: string
  priority: 'P0' | 'P1' | 'P2'
  status: 'planned' | 'in-progress' | 'done'
  userStories: string[]
}

export type Task = {
  id: string
  title: string
  assignee?: string
  startDate: string // ISO date (YYYY-MM-DD)
  endDate: string // ISO date (YYYY-MM-DD)
  // Optional datetime for hour-scale gantt (YYYY-MM-DDTHH:mm)
  startAt?: string
  endAt?: string
  progress: number // 0-100
  dependsOn: string[]
}

export type Attribute = {
  id: string
  name: string
  type: string
  pk?: boolean
  nullable?: boolean
}

export type Relation = {
  id: string
  from: string // entity id
  to: string // entity id
  type: '1..1' | '1..n' | 'n..m'
  name?: string
}

export type Entity = {
  id: string
  name: string
  attributes: Attribute[]
}

export type Project = {
  name: string
  description?: string
}

export type AppState = {
  project: Project
  ideas: Idea[]
  features: Feature[]
  tasks: Task[]
  entities: Entity[]
  relations: Relation[]
  erdMermaid?: string
  ganttConfig: {
    scale: 'day' | 'hour'
    workStart: number // 0-23
    workEnd: number // 1-24, > workStart
  }
}

const initialState: AppState = {
  project: { name: 'New Hackathon Project', description: '' },
  ideas: [],
  features: [],
  tasks: [],
  entities: [],
  relations: [],
  erdMermaid: 'erDiagram\n  Project ||--o{ Feature : has\n  Feature ||--o{ Task : includes\n  Idea ||--o{ Feature : inspires\n  Project {\n    UUID id PK\n    TEXT name\n  }\n  Feature {\n    UUID id PK\n    TEXT title\n    TEXT priority\n    TEXT status\n  }\n  Task {\n    UUID id PK\n    TEXT title\n    DATE start_date\n    DATE end_date\n    INT progress\n  }\n  Idea {\n    UUID id PK\n    TEXT title\n    INT impact\n    INT effort\n  }',
  ganttConfig: { scale: 'day', workStart: 9, workEnd: 18 }
}

function withDefaults(s: any): AppState {
  return {
    project: s?.project ?? initialState.project,
    ideas: s?.ideas ?? [],
    features: s?.features ?? [],
    tasks: s?.tasks ?? [],
    entities: s?.entities ?? [],
    relations: s?.relations ?? [],
    erdMermaid: s?.erdMermaid ?? initialState.erdMermaid,
    ganttConfig: s?.ganttConfig ?? { scale: 'day', workStart: 9, workEnd: 18 },
  }
}

type Ctx = {
  state: AppState
  setState: React.Dispatch<React.SetStateAction<AppState>>
  save: () => void
  exportJson: () => string
  importJson: (json: string) => void
}

const AppStateContext = createContext<Ctx | null>(null)

const STORAGE_KEY = 'hackpm_state_v1'

export function AppStateProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AppState>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? withDefaults(JSON.parse(raw)) : initialState
    } catch {
      return initialState
    }
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    // expose for simple utilities (e.g., Mermaid generator)
    ;(window as any).hackpm_state = state
  }, [state])

  const save = () => localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  const exportJson = () => JSON.stringify(state, null, 2)
  const importJson = (json: string) => {
    const obj = JSON.parse(json)
    setState(withDefaults(obj))
  }

  const value = useMemo(() => ({ state, setState, save, exportJson, importJson }), [state])
  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>
}

export function useAppState() {
  const ctx = useContext(AppStateContext)
  if (!ctx) throw new Error('useAppState must be used within AppStateProvider')
  return ctx
}

export function uid(prefix = 'id') {
  return `${prefix}_${Math.random().toString(36).slice(2, 9)}`
}
