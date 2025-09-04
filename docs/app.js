window.addEventListener('DOMContentLoaded', () => {
  const { gsap } = window
  gsap.registerPlugin(window.ScrollTrigger)
  // hero
  gsap.from('.headline .word', { yPercent: 100, opacity: 0, stagger: 0.06, duration: 0.9, ease: 'power4.out' })
  gsap.from('.tagline', { y: 20, opacity: 0, delay: 0.4, duration: 0.8, ease: 'power2.out' })
  gsap.from('.cta', { y: 20, opacity: 0, delay: 0.6, duration: 0.8, ease: 'power2.out' })
  // blobs
  gsap.to('.lp-blob.a', { x: 40, y: -30, scale: 1.1, rotate: 10, duration: 10, repeat: -1, yoyo: true, ease: 'sine.inOut' })
  gsap.to('.lp-blob.b', { x: -30, y: 40, scale: 0.9, rotate: -8, duration: 12, repeat: -1, yoyo: true, ease: 'sine.inOut' })
  gsap.to('.lp-blob.c', { x: 20, y: 20, scale: 1.05, rotate: 6, duration: 11, repeat: -1, yoyo: true, ease: 'sine.inOut' })
  // features
  window.ScrollTrigger.batch('.lp-feature', { start: 'top 80%', onEnter: (els) => gsap.from(els, { y: 24, opacity: 0, stagger: 0.08, duration: 0.8, ease: 'power3.out' }) })
  // tiles float + tilt
  document.querySelectorAll('.stack-tile').forEach((tile, i) => {
    gsap.to(tile, { y: gsap.utils.random(-6, 6), duration: 3 + Math.random() * 1.5, repeat: -1, yoyo: true, ease: 'sine.inOut', delay: i * 0.1 })
    const qx = gsap.quickTo(tile, 'rotationX', { duration: 0.6, ease: 'power3.out' })
    const qy = gsap.quickTo(tile, 'rotationY', { duration: 0.6, ease: 'power3.out' })
    tile.addEventListener('mousemove', (e) => {
      const r = tile.getBoundingClientRect()
      const cx = (e.clientX - r.left) / r.width - 0.5
      const cy = (e.clientY - r.top) / r.height - 0.5
      qx(-cy * 10); qy(cx * 12)
    })
    tile.addEventListener('mouseleave', () => { qx(0); qy(0) })
  })
  // timeline
  document.querySelectorAll('.timeline .row').forEach((row, i) => {
    gsap.from(row, { opacity: 0, x: i % 2 ? 40 : -40, scrollTrigger: { trigger: row, start: 'top 80%', end: 'bottom 70%', scrub: true } })
  })
})

