// ============================================================
// LaTeX rendering utilities (KaTeX) — shared module
// ============================================================
// Loads KaTeX only once (CDN) then renders the expressions
// $...$ and $$...$$ in any element. Used by
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
  // KaTeX auto-render is idempotent: it only matches the "$...$" that are
  // not already converted into .katex, so calling it multiple times is safe.
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
    // ignore invalid expressions
  }
}

/** Loads KaTeX then renders the formulas in the element */
export async function loadAndRender(el: HTMLElement): Promise<void> {
  await loadKatex()
  renderLatexIn(el)
}
