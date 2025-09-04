import { useEffect, useId, useState } from 'react'
import mermaid from 'mermaid'

mermaid.initialize({ startOnLoad: false, theme: 'dark', fontFamily: 'Inter, ui-sans-serif' })

export default function Mermaid({ code }: { code: string }) {
  const id = useId().replace(/:/g, '')
  const [svg, setSvg] = useState<string>('')

  useEffect(() => {
    let cancelled = false
    const render = async () => {
      try {
        const { svg } = await mermaid.render(`m_${id}`, code)
        if (!cancelled) setSvg(svg)
      } catch (e) {
        if (!cancelled) setSvg(`<pre style="color:#ff9090">Mermaid エラー: ${String((e as Error)?.message || e)}</pre>`) }
    }
    render()
    return () => { cancelled = true }
  }, [code, id])

  return <div dangerouslySetInnerHTML={{ __html: svg }} />
}

