import { useLayoutEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import '../lp.css'

gsap.registerPlugin(ScrollTrigger)

export default function LandingPage() {
  const heroRef = useRef<HTMLDivElement>(null)
  const featuresRef = useRef<HTMLDivElement>(null)
  const stackRef = useRef<HTMLDivElement>(null)
  const timelineRef = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      // Hero intro
      gsap.from('.lp-hero h1 .word', { yPercent: 100, opacity: 0, stagger: 0.06, duration: 0.9, ease: 'power4.out' })
      gsap.from('.lp-hero .tagline', { y: 20, opacity: 0, delay: 0.4, duration: 0.8, ease: 'power2.out' })
      gsap.from('.lp-hero .cta', { y: 20, opacity: 0, delay: 0.6, duration: 0.8, ease: 'power2.out' })

      // Floating blobs
      gsap.to('.lp-blob.a', { x: 40, y: -30, scale: 1.1, rotate: 10, duration: 10, repeat: -1, yoyo: true, ease: 'sine.inOut' })
      gsap.to('.lp-blob.b', { x: -30, y: 40, scale: 0.9, rotate: -8, duration: 12, repeat: -1, yoyo: true, ease: 'sine.inOut' })
      gsap.to('.lp-blob.c', { x: 20, y: 20, scale: 1.05, rotate: 6, duration: 11, repeat: -1, yoyo: true, ease: 'sine.inOut' })

      // Features reveal
      ScrollTrigger.batch('.lp-feature', {
        start: 'top 80%',
        onEnter: batch => gsap.from(batch, { y: 24, opacity: 0, stagger: 0.08, duration: 0.8, ease: 'power3.out' })
      })

      // Stack tiles: reveal + micro 3D tilt + gentle float
      ScrollTrigger.batch('.stack-tile', {
        start: 'top 85%',
        onEnter: batch => gsap.from(batch, { y: 24, opacity: 0, stagger: 0.06, duration: 0.8, ease: 'power3.out' })
      })
      gsap.utils.toArray<HTMLElement>('.stack-tile').forEach((tile, i) => {
        gsap.to(tile, { y: gsap.utils.random(-6, 6), duration: 3 + Math.random()*1.5, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: i * 0.1 })
        const qx = gsap.quickTo(tile, 'rotationX', { duration: 0.6, ease: 'power3.out' })
        const qy = gsap.quickTo(tile, 'rotationY', { duration: 0.6, ease: 'power3.out' })
        const onMove = (e: MouseEvent) => {
          const r = tile.getBoundingClientRect()
          const cx = (e.clientX - r.left) / r.width - 0.5
          const cy = (e.clientY - r.top) / r.height - 0.5
          qx(-cy * 10)
          qy(cx * 12)
        }
        const onLeave = () => { qx(0); qy(0) }
        tile.addEventListener('mousemove', onMove)
        tile.addEventListener('mouseleave', onLeave)
      })

      // Timeline pin
      if (timelineRef.current) {
        ScrollTrigger.create({
          trigger: timelineRef.current, start: 'top top+=80', end: '+=160%', pin: true
        })
        gsap.utils.toArray('.timeline .row').forEach((row: any, i) => {
          gsap.from(row, {
            opacity: 0, x: i % 2 ? 40 : -40,
            scrollTrigger: { trigger: row, start: 'top 80%', end: 'bottom 70%', scrub: true }
          })
        })
      }
    }, heroRef)
    return () => ctx.revert()
  }, [])

  const split = (text: string) => text.split(/(\s+)/).map((t, i) => (
    <span key={i} className="word">{t}</span>
  ))

  return (
    <div className="lp" ref={heroRef}>
      <section className="lp-hero">
        <div className="lp-bg">
          <div className="lp-blob a" />
          <div className="lp-blob b" />
          <div className="lp-blob c" />
          <div className="lp-grid" />
        </div>
        <header className="lp-nav">
          <div className="logo"><img src="/logo.svg" alt="Hack PM" /></div>
          <nav>
            <a href="#features">Features</a>
            <a href="#stack">Stack</a>
            <a href="#timeline">Flow</a>
            <a href="/">Open App</a>
          </nav>
        </header>
        <div className="lp-hero-inner">
          <h1>{split('Hackathon Project Management, reimagined.')}</h1>
          <p className="tagline">Ideate. Plan. Design Data. Ship the demo. All-in-one.</p>
          <div className="cta">
            <a className="btn primary" href="/">Open the App</a>
            <a className="btn ghost" href="#features">Explore Features</a>
          </div>
          <div className="hero-card">
            <div className="glow" />
            <div className="hero-stats">
              <div><span className="kpi">7×</span><span className="label">Faster Planning</span></div>
              <div><span className="kpi">0 deps</span><span className="label">Gantt/ER Local</span></div>
              <div><span className="kpi">AI</span><span className="label">Prompt-powered</span></div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="lp-section lp-features" ref={featuresRef}>
        <h2>Features</h2>
        <p className="lead">必要なものを、最短ルートで。</p>
        <div className="feature-grid">
          <div className="lp-feature glass">
            <div className="icon">📋</div>
            <h3>Requirements</h3>
            <p>優先度・進捗・ストーリーをシンプルに整理。</p>
          </div>
          <div className="lp-feature glass">
            <div className="icon">📆</div>
            <h3>Gantt</h3>
            <p>日/時間スケール、ドラッグ&リサイズ対応。</p>
          </div>
          <div className="lp-feature glass">
            <div className="icon">🧩</div>
            <h3>ERD</h3>
            <p>Mermaidで即時プレビュー、編集も直感的。</p>
          </div>
          <div className="lp-feature glass">
            <div className="icon">✨</div>
            <h3>AI Assist</h3>
            <p>AI自動生成でPoC準備を一気に加速。</p>
          </div>
          <div className="lp-feature glass">
            <div className="icon">🔀</div>
            <h3>Git</h3>
            <p>ブランチ、コミット、Push、プレゼンス表示。</p>
          </div>
          <div className="lp-feature glass">
            <div className="icon">⚡</div>
            <h3>Local-first</h3>
            <p>localStorage保存、即動作、すぐ持ち込める。</p>
          </div>
        </div>
      </section>

      <section id="stack" className="lp-section lp-stack" ref={stackRef}>
        <h2>Minimal Stack, Maximum Flow</h2>
        <div className="stack-grid">
          <div className="stack-tile glass"><span className="chip">React</span><span className="chip sub">Vite</span></div>
          <div className="stack-tile glass"><span className="chip">TypeScript</span></div>
          <div className="stack-tile glass"><span className="chip">GSAP</span><span className="chip sub">ScrollTrigger</span></div>
          <div className="stack-tile glass"><span className="chip">Mermaid</span></div>
          <div className="stack-tile glass"><span className="chip">Express</span><span className="chip sub">simple-git</span></div>
          <div className="stack-tile glass"><span className="chip">Local-first</span></div>
        </div>
      </section>

      <section id="timeline" className="lp-section lp-timeline" ref={timelineRef}>
        <h2>Hackathon Flow</h2>
        <div className="timeline">
          <div className="row"><span>1</span><p>プロジェクト設定・目的整理</p></div>
          <div className="row"><span>2</span><p>機能の絞り込みと要件化</p></div>
          <div className="row"><span>3</span><p>ガント/ERのたたき作成</p></div>
          <div className="row"><span>4</span><p>AIでPoC素案 → 実装</p></div>
          <div className="row"><span>5</span><p>デモ準備/発表</p></div>
        </div>
      </section>

      <footer className="lp-footer">
        <div>© Hack PM Template</div>
        <a href="/">Open App</a>
      </footer>
    </div>
  )
}
