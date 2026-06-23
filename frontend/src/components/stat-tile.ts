// ============================================================
// StatTile — petit card "1 chiffre = 1 signal" reutilisable
// ============================================================
//
// Cree pour le dashboard (commit UX #3) : remplacer le bandeau a
// 4 tiles (TC/OK/IP/ND) par 3 tiles plus ciblees alignees sur le
// hero "Today's plan" — mastery %, concepts en cours, next milestone.
// Egalement utilisable en futur sur /tutor (sessions count) ou
// /concepts (concepts decouverts) si besoin.
//
// Comme NextStepHero : retourne une string HTML, injecte ses styles
// une fois (idempotent), accepte des chaines deja localisees. Le
// composant ne fait AUCUN fetch et n'a aucune dependance metier.
//
// Variante 'text' pour les valeurs non-numeriques (ex: nom de concept) :
// reduit la taille de police et active l'ellipsis sur 2 lignes pour
// que la card ne soit pas defoncee par un titre trop long.
// ============================================================

function escapeHtml(s: string): string {
  return (s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export interface StatTileOptions {
  /** Petit label SMALL CAPS sous la valeur (ex: "Current mastery"). */
  label: string
  /** Valeur centrale. Number affiche tel quel ; string affichee telle
   *  quelle (utiliser avec variant: 'text' pour les longues chaines). */
  value: string | number
  /** Caption optionnelle en haut a droite (ex: "12 / 19 mastered"). */
  trend?: string
  /** Petit token 1-3 chars en haut a gauche (ex: "%", "→"). Optionnel. */
  token?: string
  /** 'numeric' (defaut) = police grosse, ligne unique.
   *  'text' = police plus petite, ellipsis sur 2 lignes max. */
  variant?: 'numeric' | 'text'
}

// Idempotent, appele par statTileHtml() au 1er rendu.
function injectStatTileStyles(): void {
  if (document.querySelector('style[data-ds-stat-tile]')) return
  const style = document.createElement('style')
  style.dataset.dsStatTile = 'true'
  style.textContent = `
    .stat-tile {
      min-height: 110px;
      padding: var(--space-5);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: var(--space-3);
      background: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
    }
    .stat-tile-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: var(--space-3);
    }
    .stat-tile-token {
      width: 32px;
      height: 32px;
      display: grid;
      place-items: center;
      color: var(--brand-600);
      background: rgba(15, 118, 110, 0.1);
      border: 1px solid rgba(15, 118, 110, 0.22);
      border-radius: var(--radius-md);
      font-size: var(--text-xs);
      font-weight: var(--font-weight-extrabold);
    }
    .stat-tile-trend {
      color: var(--text-muted);
      font-size: var(--text-xs);
      font-weight: var(--font-weight-bold);
    }
    .stat-tile-value {
      color: var(--text-primary);
      font-size: var(--text-4xl);
      font-weight: var(--font-weight-extrabold);
      line-height: 1.05;
    }
    .stat-tile--text .stat-tile-value {
      font-size: var(--text-lg);
      line-height: 1.3;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
      word-break: break-word;
    }
    .stat-tile-label {
      margin-top: var(--space-1);
      color: var(--text-muted);
      font-size: var(--text-xs);
      font-weight: var(--font-weight-extrabold);
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
  `
  document.head.appendChild(style)
}

/**
 * Renvoie le HTML (escape) d'une stat tile.
 *
 * Side-effect : injecte les styles au 1er appel (idempotent).
 *
 * Le top-row (token + trend) n'est rendu que si au moins l'un des deux
 * est fourni — cela permet aux tiles "pures" (juste value + label) d'avoir
 * un layout plus aere. La min-height de 110px assure que les tiles d'une
 * meme rangee restent alignees verticalement meme si leurs contenus
 * different.
 */
export function statTileHtml(opts: StatTileOptions): string {
  injectStatTileStyles()

  const variantClass = opts.variant === 'text' ? ' stat-tile--text' : ''

  const hasTop = Boolean(opts.token || opts.trend)
  const tokenHtml = opts.token
    ? `<div class="stat-tile-token">${escapeHtml(opts.token)}</div>`
    : '<span aria-hidden="true"></span>'
  const trendHtml = opts.trend
    ? `<div class="stat-tile-trend">${escapeHtml(opts.trend)}</div>`
    : ''
  const topRow = hasTop
    ? `<div class="stat-tile-top">${tokenHtml}${trendHtml}</div>`
    : ''

  return `
    <article class="stat-tile${variantClass}">
      ${topRow}
      <div>
        <div class="stat-tile-value">${escapeHtml(String(opts.value))}</div>
        <div class="stat-tile-label">${escapeHtml(opts.label)}</div>
      </div>
    </article>
  `
}
