import { useEffect, useMemo, useRef, useState } from 'react'
import type { Task } from '../state/store'
import { uid, useAppState } from '../state/store'
import Modal from '../components/Modal'

function daysBetween(a: Date, b: Date) {
  return Math.max(1, Math.ceil((b.getTime() - a.getTime()) / (1000 * 60 * 60 * 24)))
}

function toISO(d: Date) {
  return d.toISOString().slice(0, 10)
}
function parseISODate(d: string) { return new Date(d + 'T00:00:00') }
function withHour(dateISO: string, hour: number) { const d = parseISODate(dateISO); d.setHours(hour, 0, 0, 0); return d }
function formatISODateTime(d: Date) { const s = d.toISOString(); return s.slice(0,16) }
function addDaysIso(iso: string, days: number) {
  const d = new Date(iso)
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0,10)
}

function clampHour(n: number) { return Math.max(0, Math.min(24, isNaN(n) ? 0 : n)) }

function clampToWindow(dt: Date, cfg: { workStart: number; workEnd: number }) {
  const d = new Date(dt)
  const hs = cfg.workStart, he = cfg.workEnd
  if (d.getHours() < hs) d.setHours(hs, 0, 0, 0)
  else if (d.getHours() > he) d.setHours(he, 0, 0, 0)
  else d.setMinutes(0, 0, 0)
  return d
}

function slotIndex(dt: Date, minDate: Date, cfg: { workStart: number }, hoursPerDay: number) {
  const base = new Date(minDate); base.setHours(0,0,0,0)
  const dayIdx = Math.floor((dt.getTime() - base.getTime()) / 86400000)
  const hourIdx = Math.max(0, Math.min(hoursPerDay - 1, dt.getHours() - cfg.workStart))
  return dayIdx * hoursPerDay + hourIdx
}

function compareDateTime(aISO: string, bISO: string) {
  return aISO.localeCompare(bISO)
}

function addWorkSlots(iso: string, slots: number, cfg: { workStart: number; workEnd: number }) {
  let d = new Date(iso)
  d.setMinutes(0,0,0)
  const step = slots >= 0 ? 1 : -1
  let remaining = Math.abs(slots)
  while (remaining > 0) {
    const hs = cfg.workStart, he = cfg.workEnd
    if (step > 0) {
      // forward
      if (d.getHours() < hs) d.setHours(hs,0,0,0)
      if (d.getHours() >= he) { // next day start
        d.setDate(d.getDate() + 1)
        d.setHours(hs,0,0,0)
      }
      d.setHours(d.getHours() + 1)
      remaining--
      if (d.getHours() > he) { d.setDate(d.getDate()); d.setHours(he,0,0,0) } // clamp
    } else {
      // backward
      if (d.getHours() > he) d.setHours(he,0,0,0)
      if (d.getHours() <= hs) { // prev day end
        d.setDate(d.getDate() - 1)
        d.setHours(he,0,0,0)
      }
      d.setHours(d.getHours() - 1)
      remaining--
      if (d.getHours() < hs) { d.setDate(d.getDate()); d.setHours(hs,0,0,0) }
    }
  }
  return formatISODateTime(d)
}

export default function GanttPage() {
  const { state, setState } = useAppState()
  const titleW = 'var(--gantt-title-w)'
  const [title, setTitle] = useState('')
  const today = new Date()
  const [start, setStart] = useState(toISO(today))
  const [end, setEnd] = useState(toISO(new Date(today.getTime() + 1000 * 60 * 60 * 24 * 3)))
  const [editing, setEditing] = useState<Task | null>(null)
  const [dragging, setDragging] = useState<{ id: string; kind: 'move'|'resize-start'|'resize-end'; originX: number; start0: string; end0: string } | null>(null)
  const slotWRef = useRef(0)
  const cellsRef = useRef<HTMLDivElement | null>(null)

  const addTask = () => {
    if (!title.trim()) return
    const cfg = state.ganttConfig
    const t: Task = cfg.scale === 'hour'
      ? { id: uid('task'), title, startDate: start, endDate: end, startAt: formatISODateTime(withHour(start, cfg.workStart)), endAt: formatISODateTime(withHour(end, cfg.workEnd)), assignee: '', progress: 0, dependsOn: [] }
      : { id: uid('task'), title, startDate: start, endDate: end, assignee: '', progress: 0, dependsOn: [] }
    setState(s => ({ ...s, tasks: [...s.tasks, t] }))
    setTitle('')
  }
  const removeTask = (id: string) => setState(s => ({ ...s, tasks: s.tasks.filter(t => t.id !== id) }))
  const updateTask = (id: string, patch: Partial<Task>) => setState(s => ({ ...s, tasks: s.tasks.map(t => t.id === id ? { ...t, ...patch } : t) }))

  const { minDate, totalDays, totalSlots, hoursPerDay } = useMemo(() => {
    const cfg = state.ganttConfig || { scale: 'day', workStart: 9, workEnd: 18 }
    const dates = state.tasks.flatMap(t => [parseISODate(t.startDate), parseISODate(t.endDate)])
    const min = dates.length ? new Date(Math.min(...dates.map(d => d.getTime()))) : today
    const max = dates.length ? new Date(Math.max(...dates.map(d => d.getTime()))) : new Date(today.getTime() + 86400000 * 7)
    const days = daysBetween(min, max) + 1
    const hpd = Math.max(1, (cfg.workEnd ?? 18) - (cfg.workStart ?? 9))
    const slots = cfg.scale === 'day' ? days : days * hpd
    return { minDate: min, totalDays: days, totalSlots: slots, hoursPerDay: hpd }
  }, [state.tasks, state.ganttConfig])

  // tick to update now-line periodically
  const [tick, setTick] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 60_000)
    return () => clearInterval(id)
  }, [])

  const nowIdx = useMemo(() => {
    const cfg = state.ganttConfig
    const now = new Date()
    const base = new Date(minDate); base.setHours(0,0,0,0)
    const dayIdx = Math.floor((now.getTime() - base.getTime()) / 86400000)
    if (cfg.scale === 'day') {
      if (dayIdx < 0 || dayIdx >= totalDays) return null
      return dayIdx
    } else {
      if (dayIdx < 0 || dayIdx >= totalDays) return null
      const hour = now.getHours()
      if (hour < cfg.workStart || hour >= cfg.workEnd) return null
      const hourIdx = hour - cfg.workStart
      const idx = dayIdx * hoursPerDay + hourIdx
      if (idx < 0 || idx >= totalSlots) return null
      return idx
    }
  }, [state.ganttConfig, minDate, totalDays, totalSlots, hoursPerDay, tick])

  useEffect(() => {
    const calc = () => {
      if (cellsRef.current) slotWRef.current = cellsRef.current.clientWidth / (state.ganttConfig.scale === 'day' ? totalDays : totalSlots)
    }
    calc()
    window.addEventListener('resize', calc)
    return () => window.removeEventListener('resize', calc)
  }, [totalDays, totalSlots, state.ganttConfig.scale])

  useEffect(() => {
    const onMove = (e: PointerEvent) => {
      if (!dragging) return
      const w = slotWRef.current || 1
      const dx = Math.round((e.clientX - dragging.originX) / w)
      if (dx === 0) return
      if (state.ganttConfig.scale === 'day') {
        const end0 = new Date(dragging.end0)
        if (dragging.kind === 'move') {
          const ns = addDaysIso(dragging.start0, dx)
          const ne = addDaysIso(dragging.end0, dx)
          updateTask(dragging.id, { startDate: ns, endDate: ne })
        } else if (dragging.kind === 'resize-start') {
          const ns = addDaysIso(dragging.start0, dx)
          const minEnd = addDaysIso(ns, 1)
          const ne = end0.toISOString().slice(0,10) < minEnd ? minEnd : dragging.end0
          updateTask(dragging.id, { startDate: ns, endDate: ne })
        } else if (dragging.kind === 'resize-end') {
          const ne = addDaysIso(dragging.end0, dx)
          const minEnd = addDaysIso(dragging.start0, 1)
          const final = ne < minEnd ? minEnd : ne
          updateTask(dragging.id, { endDate: final })
        }
      } else {
        const cfg = state.ganttConfig
        if (dragging.kind === 'move') {
          const ns = addWorkSlots(dragging.start0, dx, cfg)
          const ne = addWorkSlots(dragging.end0, dx, cfg)
          updateTask(dragging.id, { startAt: ns, endAt: ne, startDate: ns.slice(0,10), endDate: ne.slice(0,10) })
        } else if (dragging.kind === 'resize-start') {
          const ns = addWorkSlots(dragging.start0, dx, cfg)
          // ensure at least 1 hour
          let ne = dragging.end0
          if (compareDateTime(ns, ne) >= 0) ne = addWorkSlots(ns, 1, cfg)
          updateTask(dragging.id, { startAt: ns, endAt: ne, startDate: ns.slice(0,10), endDate: ne.slice(0,10) })
        } else if (dragging.kind === 'resize-end') {
          let ne = addWorkSlots(dragging.end0, dx, cfg)
          const minEnd = addWorkSlots(dragging.start0, 1, cfg)
          if (compareDateTime(ne, minEnd) < 0) ne = minEnd
          updateTask(dragging.id, { endAt: ne, endDate: ne.slice(0,10) })
        }
      }
    }
    const onUp = () => setDragging(null)
    window.addEventListener('pointermove', onMove)
    window.addEventListener('pointerup', onUp)
    return () => {
      window.removeEventListener('pointermove', onMove)
      window.removeEventListener('pointerup', onUp)
    }
  }, [dragging])

  return (
    <div className="page">
      <h1>ガントチャート</h1>
      <div className="card">
        <div className="row gap wrap">
          <input placeholder="タスク名" value={title} onChange={(e) => setTitle(e.target.value)} />
          <label>開始</label>
          <input type="date" value={start} onChange={(e) => setStart(e.target.value)} />
          <label>終了</label>
          <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} />
          <button onClick={addTask}>追加</button>
        </div>
        <div className="row gap wrap" style={{ marginTop: 8 }}>
          <label>スケール</label>
          <select value={state.ganttConfig.scale} onChange={(e) => setState(s => ({ ...s, ganttConfig: { ...s.ganttConfig, scale: e.target.value as any } }))}>
            <option value="day">日</option>
            <option value="hour">時間</option>
          </select>
          {state.ganttConfig.scale === 'hour' && (
            <>
              <label>業務時間</label>
              <input type="number" min={0} max={23} value={state.ganttConfig.workStart} onChange={(e) => setState(s => ({ ...s, ganttConfig: { ...s.ganttConfig, workStart: clampHour(parseInt(e.target.value || '0')), workEnd: Math.max(clampHour(s.ganttConfig.workEnd), clampHour(parseInt(e.target.value || '0')) + 1) } }))} />
              <span>〜</span>
              <input type="number" min={1} max={24} value={state.ganttConfig.workEnd} onChange={(e) => setState(s => ({ ...s, ganttConfig: { ...s.ganttConfig, workEnd: Math.max(clampHour(parseInt(e.target.value || '0')), s.ganttConfig.workStart + 1) } }))} />
            </>
          )}
        </div>
      </div>

      <div className="gantt">
        <div className="gantt-header" style={{ gridTemplateColumns: `${titleW} repeat(${state.ganttConfig.scale === 'day' ? totalDays : totalSlots}, 1fr)` }}>
          <div className="gantt-colhead">タスク</div>
          {state.ganttConfig.scale === 'day' ? (
            Array.from({ length: totalDays }).map((_, i) => {
              const d = new Date(minDate.getTime() + 86400000 * i)
              const label = `${d.getMonth() + 1}/${d.getDate()}`
              return <div key={i} className="gantt-colhead small">{label}</div>
            })
          ) : (
            Array.from({ length: totalSlots }).map((_, i) => {
              const dayIdx = Math.floor(i / hoursPerDay)
              const hour = state.ganttConfig.workStart + (i % hoursPerDay)
              const d = new Date(minDate.getTime() + 86400000 * dayIdx)
              const label = `${d.getMonth() + 1}/${d.getDate()} ${hour}:00`
              return <div key={i} className="gantt-colhead small">{label}</div>
            })
          )}
          {nowIdx !== null && <div className="gantt-now-header" style={{ gridColumn: `${(nowIdx as number) + 2} / span 1` }} />}
        </div>
        <div className="gantt-body">
          {state.tasks.map((t, idx) => {
            let offset = 0
            let span = 1
            if (state.ganttConfig.scale === 'day') {
              const s = new Date(t.startDate)
              const e = new Date(t.endDate)
              offset = Math.max(0, daysBetween(minDate, s) - 1)
              span = Math.max(1, daysBetween(s, e))
            } else {
              const cfg = state.ganttConfig
              const sdt = clampToWindow(t.startAt ? new Date(t.startAt) : withHour(t.startDate, cfg.workStart), cfg)
              const edt = clampToWindow(t.endAt ? new Date(t.endAt) : withHour(t.endDate, cfg.workEnd), cfg)
              const idxS = slotIndex(sdt, minDate, cfg, hoursPerDay)
              const idxE = slotIndex(edt, minDate, cfg, hoursPerDay)
              offset = Math.max(0, idxS)
              span = Math.max(1, idxE - idxS)
            }
            return (
              <div key={t.id} className="gantt-row" style={{ gridTemplateColumns: `${titleW} repeat(${state.ganttConfig.scale === 'day' ? totalDays : totalSlots}, 1fr)` }}>
                <div className="gantt-tasktitle">
                  <div className="row space-between">
                    <span>{t.title}</span>
                    <div className="row gap small">
                      <button className="link" onClick={() => setEditing(t)}>編集</button>
                      <button className="link" onClick={() => removeTask(t.id)}>削除</button>
                    </div>
                  </div>
                </div>
                <div className="gantt-cells" ref={idx === 0 ? cellsRef : undefined} style={{ gridColumn: `span ${state.ganttConfig.scale === 'day' ? totalDays : totalSlots}`, gridTemplateColumns: `repeat(${state.ganttConfig.scale === 'day' ? totalDays : totalSlots}, 1fr)` }}>
                  {nowIdx !== null && <div className="gantt-now" style={{ gridColumn: `${(nowIdx as number) + 1} / span 1` }} />}
                  <div
                    className={`gantt-bar${dragging?.id === t.id ? ' dragging' : ''}`}
                    style={{ gridColumn: `${offset + 1} / span ${span}` }}
                    onPointerDown={(e) => setDragging({ id: t.id, kind: 'move', originX: e.clientX, start0: state.ganttConfig.scale === 'day' ? t.startDate : (t.startAt || withHour(t.startDate, state.ganttConfig.workStart).toISOString().slice(0,16)), end0: state.ganttConfig.scale === 'day' ? t.endDate : (t.endAt || withHour(t.endDate, state.ganttConfig.workEnd).toISOString().slice(0,16)) })}
                  >
                    <div className="gantt-progress" style={{ width: `${t.progress}%` }} />
                    <div className="gantt-handle left" onPointerDown={(e) => { e.stopPropagation(); setDragging({ id: t.id, kind: 'resize-start', originX: e.clientX, start0: state.ganttConfig.scale === 'day' ? t.startDate : (t.startAt || withHour(t.startDate, state.ganttConfig.workStart).toISOString().slice(0,16)), end0: state.ganttConfig.scale === 'day' ? t.endDate : (t.endAt || withHour(t.endDate, state.ganttConfig.workEnd).toISOString().slice(0,16)) }) }} />
                    <div className="gantt-handle right" onPointerDown={(e) => { e.stopPropagation(); setDragging({ id: t.id, kind: 'resize-end', originX: e.clientX, start0: state.ganttConfig.scale === 'day' ? t.startDate : (t.startAt || withHour(t.startDate, state.ganttConfig.workStart).toISOString().slice(0,16)), end0: state.ganttConfig.scale === 'day' ? t.endDate : (t.endAt || withHour(t.endDate, state.ganttConfig.workEnd).toISOString().slice(0,16)) }) }} />
                  </div>
                </div>
              </div>
            )
          })}
          {state.tasks.length === 0 && <div className="muted">まだタスクがありません。</div>}
        </div>
      </div>

      <Modal open={!!editing} onClose={() => setEditing(null)} title="タスクを編集">
        {editing && (
          <>
            <div className="row gap">
              <label style={{ minWidth: 60 }}>名称</label>
              <input className="grow" value={editing.title} onChange={(e) => setEditing({ ...editing, title: e.target.value })} />
            </div>
            <div className="row gap wrap">
              <label style={{ minWidth: 60 }}>開始</label>
              <input type="date" value={editing.startDate} onChange={(e) => setEditing({ ...editing, startDate: e.target.value, startAt: state.ganttConfig.scale === 'hour' ? formatISODateTime(withHour(e.target.value, state.ganttConfig.workStart)) : editing.startAt })} />
              {state.ganttConfig.scale === 'hour' && (
                <input type="time" step={3600} value={(editing.startAt || formatISODateTime(withHour(editing.startDate, state.ganttConfig.workStart))).slice(11,16)} onChange={(e) => {
                  const [hh, mm] = e.target.value.split(':').map(Number)
                  const d = parseISODate(editing.startDate); d.setHours(hh, mm || 0, 0, 0)
                  setEditing({ ...editing, startAt: formatISODateTime(d) })
                }} />
              )}
              <label style={{ minWidth: 60 }}>終了</label>
              <input type="date" value={editing.endDate} onChange={(e) => setEditing({ ...editing, endDate: e.target.value, endAt: state.ganttConfig.scale === 'hour' ? formatISODateTime(withHour(e.target.value, state.ganttConfig.workEnd)) : editing.endAt })} />
              {state.ganttConfig.scale === 'hour' && (
                <input type="time" step={3600} value={(editing.endAt || formatISODateTime(withHour(editing.endDate, state.ganttConfig.workEnd))).slice(11,16)} onChange={(e) => {
                  const [hh, mm] = e.target.value.split(':').map(Number)
                  const d = parseISODate(editing.endDate); d.setHours(hh, mm || 0, 0, 0)
                  setEditing({ ...editing, endAt: formatISODateTime(d) })
                }} />
              )}
              <label style={{ minWidth: 60 }}>進捗</label>
              <input type="number" min={0} max={100} value={editing.progress} onChange={(e) => setEditing({ ...editing, progress: clamp0to100(parseInt(e.target.value || '0')) })} />
            </div>
            <div className="row gap">
              <label style={{ minWidth: 60 }}>担当</label>
              <input className="grow" placeholder="任意" value={editing.assignee || ''} onChange={(e) => setEditing({ ...editing, assignee: e.target.value })} />
            </div>
            <div className="modal-footer">
              <button onClick={() => setEditing(null)}>キャンセル</button>
              <button onClick={() => { updateTask(editing.id, editing); setEditing(null) }}>保存</button>
            </div>
          </>
        )}
      </Modal>
    </div>
  )
}

function clamp0to100(n: number) { return Math.max(0, Math.min(100, isNaN(n) ? 0 : n)) }
