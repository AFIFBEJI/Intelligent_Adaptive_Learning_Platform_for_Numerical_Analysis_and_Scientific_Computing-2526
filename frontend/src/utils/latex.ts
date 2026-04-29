// ============================================================
// LaTeX rendering utilities (KaTeX) — module partage
// ============================================================
// Charge KaTeX une seule fois (CDN) puis rend les expressions
// $...$ et $$...$$ dans n'importe quel element. Utilise par
// onboarding-quiz, quiz-ai, concepts, content, tutor.
// ============================================================

let _katexLoading: Promise<void> | null = null

export function loadKatex(): Promise<void> {
  if (typeof window !== 'undefined' && (window as { renderMathInElement?: unknown }).renderMathInElement) {
    return Promise.resolve()
  }
  if (_katexLoading) return _katexLoading

  _katexLoading = new Promise<void>((resolve) => {
    if (!document.querySelector('link[data-katex]')) {
      const css = document.createElement('link')
      css.rel = 'stylesheet'
      css.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css'
      css.dataset.katex = 'true'
      document.head.appendChild(css)
    }
    const coreScript = document.createElement('script')
    coreScript.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js'
    coreScript.onload = () => {
      const autoScript = document.createElement('script')
      autoScript.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js'
      autoScript.onload = () => resolve()
      autoScript.onerror = () => resolve()
      document.head.appendChild(autoScript)
    }
    coreScript.onerror = () => resolve()
    document.head.appendChild(coreScript)
  })
  return _katexLoading
}

export function renderLatexIn(el: HTMLElement): void {
  const renderer = (window as { renderMathInElement?: (el: HTMLElement, opts: unknown) => void }).renderMathInElement
  if (!renderer) return
  // KaTeX auto-render est idempotent : il ne matche que les "$...$" qui ne sont
  // pas deja convertis en .katex, donc appeler plusieurs fois est sans risque.
  try {
    renderer(el, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false },
        { left: '\\(', right: '\\)', display: false },
        { left: '\\[', right: '\\]', display: true },
      ],
      throwOnError: false,
      errorColor: '#fca5a5',
    })
  } catch {
    // ignore les expressions invalides
  }
}

/** Charge KaTeX puis rend les formules dans l'element */
export async function loadAndRender(el: HTMLElement): Promise<void> {
  await loadKatex()
  renderLatexIn(el)
}
