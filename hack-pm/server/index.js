// Minimal local Git API + Presence WS
import express from 'express'
import cors from 'cors'
import { WebSocketServer } from 'ws'
import simpleGit from 'simple-git'

const PORT = 8787
const app = express()
app.use(cors())
app.use(express.json())

const git = simpleGit({ baseDir: process.cwd() })

app.get('/git/status', async (req, res) => {
  try { const s = await git.status(); res.json(s) } catch (e) { res.status(500).json({ error: String(e) }) }
})
app.get('/git/branches', async (req, res) => {
  try { const b = await git.branch(); res.json(b.all.map(name => ({ name, current: b.current === name }))) } catch (e) { res.status(500).json({ error: String(e) }) }
})
app.post('/git/checkout', async (req, res) => {
  try { await git.checkout(req.body.name); res.json({ ok: true }) } catch (e) { res.status(500).json({ error: String(e) }) }
})
app.post('/git/create-branch', async (req, res) => {
  try { const { name, checkout } = req.body; await git.checkoutLocalBranch(name); if (!checkout) await git.checkout(name); res.json({ ok: true }) } catch (e) { res.status(500).json({ error: String(e) }) }
})
app.post('/git/add', async (req, res) => {
  try { const paths = req.body?.paths || ['.']; await git.add(paths); res.json({ ok: true }) } catch (e) { res.status(500).json({ error: String(e) }) }
})
app.post('/git/commit', async (req, res) => {
  try { const { message } = req.body; const r = await git.commit(message || 'chore: update'); res.json(r) } catch (e) { res.status(500).json({ error: String(e) }) }
})
app.post('/git/push', async (req, res) => {
  try { const { remote, branch } = req.body || {}; const r = await git.push(remote || undefined, branch || undefined); res.json(r) } catch (e) { res.status(500).json({ error: String(e) }) }
})
app.post('/git/fetch', async (req, res) => {
  try { const { remote } = req.body || {}; const r = await git.fetch(remote || undefined); res.json(r) } catch (e) { res.status(500).json({ error: String(e) }) }
})

const server = app.listen(PORT, () => console.log(`[git-api] http://localhost:${PORT}`))

// Presence WS
const wss = new WebSocketServer({ server, path: '/presence' })
const clients = new Map() // ws -> { id, name }
function broadcast() {
  const list = [...clients.values()].map(c => ({ id: c.id, name: c.name }))
  const payload = JSON.stringify({ type: 'presence', list })
  wss.clients.forEach(ws => { if (ws.readyState === 1) ws.send(payload) })
}
wss.on('connection', (ws) => {
  const id = Math.random().toString(36).slice(2, 8)
  clients.set(ws, { id, name: '' })
  broadcast()
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data)
      if (msg.type === 'hello') { const c = clients.get(ws); c.name = msg.name || ''; clients.set(ws, c); broadcast() }
    } catch {}
  })
  ws.on('close', () => { clients.delete(ws); broadcast() })
})

