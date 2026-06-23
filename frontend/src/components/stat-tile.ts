// ============================================================
// StatTile — small reusable "1 number = 1 signal" card
// ============================================================
//
// Created for the dashboard (commit UX #3): replace the banner with
// 4 tiles (TC/OK/IP/ND) by 3 more targeted tiles aligned with the
// "Today's plan" hero — mastery %, concepts in progress, next milestone.
// Also usable in the future on /tutor (sessions count) or
// /concepts (concepts discovered) if needed.
//
// Like NextStepHero: returns an HTML string, injects its styles
// once (idempotent), accepts already-localized strings. The
// component does NO fetch and has no business dependency.
//
// 'text' variant for non-numeric values (e.g. concept name):
// reduces the font size and enables ellipsis over 2 lines so
// the card is not broken by a title that is too long.
// ============================================================

function escapeHtml(s: string): string {
  return (s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export interface StatTileOptions {
  /** Small SMALL CAPS label under the value (e.g. "Current mastery"). */
  label: string
  /** Central value. Number shown as-is; string shown as-is
   *  (use with variant: 'text' for long strings). */
  value: string | number
  /** Optional caption at top right (e.g. "12 / 19 mastered"). */
  trend?: string
  /** Small 1-3 char token at top left (e.g. "%", "→"). Optional. */
  token?: string
  /** 'numeric' (default) = large font, single line.
   *  'text' = smaller font, ellipsis over 2 lines max. */
  variant?: 'numeric' | 'text'
}

// Idempotent, called by statTileHtml() on the first render.
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
 * Returns the (escaped) HTML of a stat tile.
 *
 * Side-effect: injects the styles on the first call (idempotent).
 *
 * The top-row (token + trend) is only rendered if at least one of the two
 * is provided — this lets the "pure" tiles (just value + label) have
 * a more spacious layout. The min-height of 110px ensures that the tiles in
 * the same row stay vertically aligned even if their contents
 * differ.
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
