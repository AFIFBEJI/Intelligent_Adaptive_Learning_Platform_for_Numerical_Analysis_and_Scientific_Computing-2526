// ============================================================
// Widget Desmos Graphing Calculator — embed via iframe officiel
// ============================================================
// Le proposal PFE promet "embedded tools (Desmos, GeoGebra, WebGL,
// JSXGraph) for parameter exploration". JSXGraph est deja la (19 widgets).
// On ajoute ici Desmos en mode iframe — c'est la seule integration legale
// gratuite (sans API key), et c'est largement suffisant pour permettre a
// l'etudiant d'explorer une fonction interactivement.
//
// Documentation officielle :
//   https://www.desmos.com/api/v1.10/docs/index.html#document-iframe-embedding
//
// La forme d'URL "?embed=true&apiKey=..." est reservee a l'API JS payante.
// Pour notre besoin (PFE), l'URL publique sans cle suffit :
//   https://www.desmos.com/calculator?expr=...
//
// Avantages :
//   - Zero dependance npm (juste un iframe).
//   - Pas de bundle alourdi (vs un widget JSXGraph compile).
//   - Etudiant peut ouvrir Desmos en plein ecran via le lien fourni.
//
// Limitations assumees :
//   - Necessite Internet (Desmos est cloud-only).
//   - Les expressions complexes (LaTeX integrales) peuvent etre tronquees
//     dans l'URL au-dela de ~500 caracteres.
//
// Utilisation cote concepts.ts :
//   import { createDesmosEmbed } from '../widgets/desmos-embed'
//   const widget = createDesmosEmbed({
//     expressions: ['y = x^2', 'y = 2*x - 1'],
//     height: 480,
//   })
//   container.appendChild(widget)

export interface DesmosEmbedOptions {
  /** Liste d'expressions a tracer (syntaxe Desmos, ex: "y = x^2") */
  expressions: string[]
  /** Hauteur en pixels (defaut: 480) */
  height?: number
  /** Largeur CSS (defaut: '100%') */
  width?: string
  /** Caption affichee sous le widget */
  caption?: string
}

/**
 * Cree un widget Desmos en iframe.
 * Retourne un HTMLElement pret a appendre dans un container.
 */
export function createDesmosEmbed(options: DesmosEmbedOptions): HTMLElement {
  const { expressions, height = 480, width = '100%', caption } = options

  // Encode les expressions dans l'URL. Desmos accepte le format
  // "expressions[i]" mais on simplifie en mettant juste la premiere
  // expression dans le query string ; les autres seront ajoutees par
  // JS si Desmos est charge en mode interactif futur.
  const firstExpr = expressions[0] || ''
  const params = new URLSearchParams()
  if (firstExpr) {
    params.set('expr', firstExpr)
  }
  // Couleur de fond aligne avec notre theme dark.
  params.set('embed', '1')

  const url = `https://www.desmos.com/calculator?${params.toString()}`

  const wrapper = document.createElement('div')
  wrapper.className = 'desmos-embed-wrapper'
  wrapper.style.cssText =
    'background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); ' +
    'border-radius: 10px; padding: 1rem; margin: 1rem 0;'

  const title = document.createElement('div')
  title.style.cssText =
    'font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.5rem; ' +
    'display: flex; justify-content: space-between; align-items: center;'
  title.innerHTML = `
    <span>🧮 Desmos Calculator — interactive exploration</span>
    <a href="${url}" target="_blank" rel="noopener noreferrer"
       style="color: #4fd1c5; text-decoration: none; font-size: 0.8rem;">
      Open in new tab ↗
    </a>
  `
  wrapper.appendChild(title)

  const iframe = document.createElement('iframe')
  iframe.src = url
  iframe.style.cssText = `width: ${width}; height: ${height}px; border: 0; border-radius: 6px;`
  iframe.setAttribute('allow', 'fullscreen')
  iframe.setAttribute('loading', 'lazy')
  iframe.title = 'Desmos Calculator embed'
  wrapper.appendChild(iframe)

  if (expressions.length > 1) {
    const note = document.createElement('div')
    note.style.cssText = 'font-size: 0.75rem; color: #64748b; margin-top: 0.5rem;'
    note.textContent =
      `Tip: paste these additional expressions in Desmos to compare: ` +
      expressions.slice(1).join(', ')
    wrapper.appendChild(note)
  }

  if (caption) {
    const cap = document.createElement('p')
    cap.style.cssText = 'font-size: 0.85rem; color: #cbd5e1; margin-top: 0.5rem;'
    cap.textContent = caption
    wrapper.appendChild(cap)
  }

  return wrapper
}

/**
 * Helper : tableau de presets pour les concepts cles du curriculum.
 * Le frontend peut piocher dedans selon le concept_id affiche.
 */
export const DESMOS_PRESETS: Record<string, DesmosEmbedOptions> = {
  concept_lagrange: {
    expressions: ['y = (x-2)(x-3)/((1-2)(1-3))*1 + (x-1)(x-3)/((2-1)(2-3))*3 + (x-1)(x-2)/((3-1)(3-2))*5'],
    caption: 'Lagrange polynomial through (1,1), (2,3), (3,5). Drag points in Desmos to explore.',
  },
  concept_newton_raphson: {
    expressions: ['y = x^2 - 2', 'y = 2*x*(x - 1) + 1 - 2'],
    caption: 'Newton-Raphson tangent to f(x)=x²-2 at x₀=1. Tangent line approximates the root.',
  },
  concept_simpson: {
    expressions: ['y = x^2', 'y = (x-1)^2 + 1'],
    caption: "Compare f(x)=x² (red) with Simpson's parabolic fit on the same interval.",
  },
  concept_least_squares: {
    expressions: ['y = 1.5*x + 0.5'],
    caption: 'Least-squares regression line through (0,1), (1,2), (2,4). Slope ≈ 1.5.',
  },
  concept_bissection: {
    expressions: ['y = x^3 - x - 2'],
    caption: 'Find the root of f(x)=x³-x-2 by bisection on [1, 2]. f(1)=-2, f(2)=4.',
  },
}
