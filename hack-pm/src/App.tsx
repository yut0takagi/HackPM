import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import './App.css'
import { AppStateProvider } from './state/store'
import HomePage from './pages/HomePage'
import RequirementsPage from './pages/RequirementsPage'
import GanttPage from './pages/GanttPage'
import ERDiagramPage from './pages/ERDiagramPage'
import PromptBuilderPage from './pages/PromptBuilderPage'
import SettingsPage from './pages/SettingsPage'
import GitPage from './pages/GitPage'
import { useState } from 'react'
import LandingPage from './pages/LandingPage'

function App() {
  const [collapsed, setCollapsed] = useState<boolean>(() => {
    try { return localStorage.getItem('hackpm_sidebar_collapsed') === '1' } catch { return false }
  })
  const toggle = () => {
    const v = !collapsed; setCollapsed(v)
    try { localStorage.setItem('hackpm_sidebar_collapsed', v ? '1' : '0') } catch {}
  }
  const loc = useLocation()
  if (loc.pathname.startsWith('/lp')) {
    return (
      <AppStateProvider>
        <LandingPage />
      </AppStateProvider>
    )
  }
  return (
    <AppStateProvider>
      <div className={`app-shell${collapsed ? ' collapsed' : ''}`}>
        <aside className="sidebar">
          <div className="brand">
            <button className="icon" title="メニュー" onClick={toggle}>{collapsed ? '☰' : '«'}</button>
            <span className="brand-text">Hack PM</span>
          </div>
          <nav>
            <NavLink to="/" end><span className="icon">🏠</span><span className="label">ホーム</span></NavLink>
            <NavLink to="/requirements"><span className="icon">📋</span><span className="label">機能要件</span></NavLink>
            <NavLink to="/gantt"><span className="icon">📆</span><span className="label">ガント</span></NavLink>
            <NavLink to="/er"><span className="icon">🧩</span><span className="label">ER 図</span></NavLink>
            <NavLink to="/prompt"><span className="icon">✨</span><span className="label">プロンプト</span></NavLink>
            <NavLink to="/git"><span className="icon">🔀</span><span className="label">Git</span></NavLink>
            <NavLink to="/settings"><span className="icon">⚙️</span><span className="label">設定</span></NavLink>
          </nav>
        </aside>
        <main className="content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/requirements" element={<RequirementsPage />} />
            <Route path="/gantt" element={<GanttPage />} />
            <Route path="/er" element={<ERDiagramPage />} />
            <Route path="/prompt" element={<PromptBuilderPage />} />
            <Route path="/git" element={<GitPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </AppStateProvider>
  )
}

export default App
