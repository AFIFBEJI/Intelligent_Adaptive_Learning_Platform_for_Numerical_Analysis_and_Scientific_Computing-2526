// ============================================================
// Design tokens and shared UI primitives
// ============================================================

const TOKENS_CSS = `
:root {
  color-scheme: dark;

  --bg-base: #07111f;
  --bg-base-soft: #0b1727;
  --bg-canvas: #0f1b2d;
  --bg-surface: rgba(15, 27, 45, 0.92);
  --bg-surface-2: rgba(21, 36, 58, 0.92);
  --bg-surface-3: rgba(35, 53, 80, 0.86);
  --bg-surface-hover: rgba(28, 47, 74, 0.96);
  --bg-overlay: rgba(8, 18, 31, 0.78);
  --bg-inverse: #f8fafc;
  --bg-inverse-soft: #e2e8f0;

  --border-subtle: rgba(148, 163, 184, 0.12);
  --border-default: rgba(148, 163, 184, 0.2);
  --border-emphasis: rgba(56, 189, 248, 0.42);
  --border-focus: rgba(125, 211, 252, 0.78);

  --text-primary: #f8fafc;
  --text-secondary: #dbe7f4;
  --text-muted: #9fb0c5;
  --text-subtle: #6f8197;
  --text-disabled: #4d5d72;
  --text-on-inverse: #0f172a;
  --text-muted-inverse: #475569;

  --brand-50: #ecfeff;
  --brand-100: #cffafe;
  --brand-300: #7dd3fc;
  --brand-400: #38bdf8;
  --brand-500: #38bdf8;
  --brand-600: #0ea5e9;
  --brand-gradient: linear-gradient(135deg, #38bdf8 0%, #6366f1 58%, #22c55e 100%);

  --accent-cyan: #38bdf8;
  --accent-indigo: #818cf8;
  --accent-purple: #a78bfa;
  --accent-pink: #f472b6;
  --accent-amber: #f59e0b;
  --accent-coral: #fb7185;

  --success: #34d399;
  --success-bg: rgba(52, 211, 153, 0.11);
  --success-border: rgba(52, 211, 153, 0.28);

  --warning: #fbbf24;
  --warning-bg: rgba(251, 191, 36, 0.11);
  --warning-border: rgba(251, 191, 36, 0.3);

  --danger: #f87171;
  --danger-bg: rgba(248, 113, 113, 0.11);
  --danger-border: rgba(248, 113, 113, 0.3);

  --info: #38bdf8;
  --info-bg: rgba(56, 189, 248, 0.11);
  --info-border: rgba(56, 189, 248, 0.28);

  --mastery-low: #f87171;
  --mastery-medium: #fbbf24;
  --mastery-high: #34d399;
  --mastery-expert: #a78bfa;

  --space-0: 0;
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-20: 5rem;

  --font-sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", Consolas, monospace;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 0.95rem;
  --text-md: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;

  --line-height-tight: 1.2;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.7;

  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 8px;
  --radius-xl: 8px;
  --radius-2xl: 8px;
  --radius-full: 9999px;

  --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-sm: 0 10px 26px rgba(0, 0, 0, 0.24);
  --shadow-md: 0 18px 42px rgba(0, 0, 0, 0.32);
  --shadow-lg: 0 30px 70px rgba(0, 0, 0, 0.42);
  --shadow-xl: 0 42px 95px rgba(0, 0, 0, 0.52);
  --shadow-glow-brand: 0 0 0 1px rgba(56, 189, 248, 0.18), 0 18px 42px rgba(56, 189, 248, 0.18);
  --shadow-focus: 0 0 0 3px rgba(56, 189, 248, 0.2);

  --transition-fast: 120ms ease-out;
  --transition-base: 190ms ease-out;
  --transition-slow: 300ms ease-out;

  --sidebar-width: 276px;
  --sidebar-width-collapsed: 76px;
  --topbar-height: 72px;
  --content-max-width: 1200px;
  --content-padding-x: clamp(1rem, 3vw, 2.25rem);
}

*, *::before, *::after { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  min-height: 100%;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--line-height-normal);
  color: var(--text-primary);
  background:
    linear-gradient(rgba(148, 163, 184, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.045) 1px, transparent 1px),
    linear-gradient(135deg, #07111f 0%, #0b1727 48%, #10192b 100%);
  background-size: 34px 34px, 34px 34px, auto;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    linear-gradient(180deg, rgba(7, 17, 31, 0.1), rgba(7, 17, 31, 0.92) 72%),
    linear-gradient(120deg, rgba(56, 189, 248, 0.08), transparent 32%, rgba(99, 102, 241, 0.07) 68%, transparent);
}

#app { position: relative; z-index: 1; min-height: 100vh; }

a { color: inherit; }
button, input, textarea, select { font: inherit; }
button { color: inherit; }
img, svg { display: block; max-width: 100%; }

*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-track { background: transparent; }
*::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.24);
  border-radius: var(--radius-full);
}
*::-webkit-scrollbar-thumb:hover { background: rgba(148, 163, 184, 0.38); }

:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 3px;
  border-radius: var(--radius-sm);
}

.ds-page {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.ds-page-narrow { max-width: 860px; margin: 0 auto; }

.ds-stack { display: flex; flex-direction: column; gap: var(--space-4); }
.ds-row { display: flex; align-items: center; gap: var(--space-3); flex-wrap: wrap; }
.ds-row-between { display: flex; align-items: center; justify-content: space-between; gap: var(--space-4); flex-wrap: wrap; }
.ds-grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-5); }
.ds-grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-5); }
.ds-grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--space-4); }

.ds-card,
.ds-panel {
  background: linear-gradient(180deg, rgba(15, 27, 45, 0.94), rgba(11, 23, 39, 0.94));
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.ds-card { padding: var(--space-5); }
.ds-panel { padding: var(--space-6); }
.ds-card-elevated { box-shadow: var(--shadow-md); }
.ds-card-interactive { cursor: pointer; transition: border-color var(--transition-base), transform var(--transition-base), background var(--transition-base), box-shadow var(--transition-base); }
.ds-card-interactive:hover {
  border-color: var(--border-emphasis);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.ds-page-header {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
}
.ds-page-header-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
}
.ds-eyebrow {
  margin: 0;
  color: var(--brand-300);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.ds-page-header-title,
.ds-section-title {
  margin: 0;
  color: var(--text-primary);
  letter-spacing: 0;
  line-height: var(--line-height-tight);
}
.ds-page-header-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-weight-extrabold);
}
.ds-section-title {
  font-size: var(--text-xl);
  font-weight: var(--font-weight-bold);
}
.ds-page-header-subtitle,
.ds-section-subtitle {
  margin: 0;
  color: var(--text-muted);
  line-height: var(--line-height-relaxed);
}
.ds-page-header-subtitle { max-width: 760px; font-size: var(--text-sm); }
.ds-section-subtitle { font-size: var(--text-sm); }
.ds-page-header-actions { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; }

.ds-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  min-height: 40px;
  padding: 0.64rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  font-size: var(--text-sm);
  font-weight: var(--font-weight-bold);
  line-height: 1;
  text-decoration: none;
  cursor: pointer;
  white-space: nowrap;
  transition: transform var(--transition-fast), border-color var(--transition-fast), background var(--transition-fast), color var(--transition-fast), box-shadow var(--transition-fast);
}
.ds-btn:hover:not(:disabled) { transform: translateY(-1px); }
.ds-btn:disabled { opacity: 0.55; cursor: not-allowed; }
.ds-btn-primary {
  color: #06111f;
  background: linear-gradient(135deg, #e0f2fe, #7dd3fc 55%, #a5b4fc);
  border-color: rgba(125, 211, 252, 0.6);
  box-shadow: var(--shadow-glow-brand);
}
.ds-btn-primary:hover:not(:disabled) { filter: brightness(1.06); }
.ds-btn-secondary {
  color: var(--text-primary);
  background: rgba(21, 36, 58, 0.86);
  border-color: var(--border-default);
}
.ds-btn-secondary:hover:not(:disabled) {
  background: var(--bg-surface-hover);
  border-color: var(--border-emphasis);
}
.ds-btn-ghost {
  color: var(--text-muted);
  background: transparent;
  border-color: transparent;
}
.ds-btn-ghost:hover:not(:disabled) {
  color: var(--text-primary);
  background: rgba(148, 163, 184, 0.08);
}
.ds-btn-danger {
  color: var(--danger);
  background: var(--danger-bg);
  border-color: var(--danger-border);
}

.ds-icon {
  width: 36px;
  height: 36px;
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: var(--radius-md);
  color: var(--brand-300);
  background: var(--info-bg);
  border: 1px solid var(--info-border);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-extrabold);
  letter-spacing: 0;
}

.ds-badge,
.ds-tag,
.ds-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
  min-height: 26px;
  padding: 0.22rem 0.6rem;
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-bold);
  text-decoration: none;
}
.ds-badge-brand, .ds-chip.active {
  color: var(--brand-300);
  background: var(--info-bg);
  border: 1px solid var(--info-border);
}
.ds-badge-success { color: var(--success); background: var(--success-bg); border: 1px solid var(--success-border); }
.ds-badge-warning { color: var(--warning); background: var(--warning-bg); border: 1px solid var(--warning-border); }
.ds-badge-danger { color: var(--danger); background: var(--danger-bg); border: 1px solid var(--danger-border); }
.ds-tag, .ds-chip {
  color: var(--text-muted);
  background: var(--bg-surface-2);
  border: 1px solid var(--border-subtle);
}
.ds-chip {
  min-height: 36px;
  padding: 0.5rem 0.85rem;
  cursor: pointer;
  transition: color var(--transition-fast), background var(--transition-fast), border-color var(--transition-fast);
}
.ds-chip:hover { color: var(--text-primary); border-color: var(--border-emphasis); }

.ds-tabs {
  display: inline-flex;
  gap: var(--space-1);
  padding: var(--space-1);
  background: var(--bg-surface-2);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}
.ds-tab {
  min-height: 34px;
  padding: 0.45rem 0.85rem;
  border: 0;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  background: transparent;
  font-size: var(--text-sm);
  font-weight: var(--font-weight-bold);
  cursor: pointer;
}
.ds-tab:hover { color: var(--text-primary); }
.ds-tab.active { color: var(--brand-100); background: rgba(56, 189, 248, 0.14); }

.ds-input,
.ds-select,
.ds-textarea {
  width: 100%;
  min-height: 42px;
  padding: 0.68rem 0.8rem;
  color: var(--text-primary);
  background: rgba(7, 17, 31, 0.72);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast), background var(--transition-fast);
}
.ds-textarea { resize: vertical; min-height: 110px; }
.ds-input::placeholder, .ds-textarea::placeholder { color: var(--text-subtle); }
.ds-input:hover, .ds-select:hover, .ds-textarea:hover { border-color: var(--border-emphasis); }
.ds-input:focus, .ds-select:focus, .ds-textarea:focus {
  border-color: var(--border-focus);
  box-shadow: var(--shadow-focus);
  background: rgba(8, 18, 31, 0.92);
}
.ds-label {
  display: block;
  margin: 0 0 var(--space-2);
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.ds-help { display: block; margin-top: var(--space-1); color: var(--text-subtle); font-size: var(--text-xs); }

.ds-alert {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  line-height: var(--line-height-relaxed);
}
.ds-alert-error { color: var(--danger); background: var(--danger-bg); border: 1px solid var(--danger-border); }
.ds-alert-info { color: var(--brand-300); background: var(--info-bg); border: 1px solid var(--info-border); }
.ds-alert-success { color: var(--success); background: var(--success-bg); border: 1px solid var(--success-border); }

.ds-stat {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  min-height: 112px;
  padding: var(--space-5);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}
.ds-stat-value {
  color: var(--text-primary);
  font-size: var(--text-3xl);
  font-weight: var(--font-weight-extrabold);
  line-height: 1;
}
.ds-stat-label {
  margin-top: var(--space-1);
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.ds-stat-trend { color: var(--text-muted); font-size: var(--text-xs); font-weight: var(--font-weight-semibold); }

.ds-progress {
  height: 8px;
  background: var(--bg-surface-3);
  border-radius: var(--radius-full);
  overflow: hidden;
}
.ds-progress-bar {
  height: 100%;
  background: var(--brand-gradient);
  border-radius: inherit;
  transition: width var(--transition-slow);
}
.ds-progress-bar-success { background: var(--success); }
.ds-progress-bar-warning { background: var(--warning); }
.ds-progress-bar-danger { background: var(--danger); }

.ds-table {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--bg-surface);
}
.ds-table th,
.ds-table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  text-align: left;
  vertical-align: top;
}
.ds-table th {
  color: var(--text-muted);
  background: var(--bg-surface-2);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.ds-table td { color: var(--text-secondary); font-size: var(--text-sm); }
.ds-table tr:last-child td { border-bottom: 0; }

.ds-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  min-height: 220px;
  padding: var(--space-10) var(--space-6);
  color: var(--text-muted);
  text-align: center;
  background: rgba(148, 163, 184, 0.055);
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-md);
}
.ds-empty-icon {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  color: var(--brand-300);
  background: var(--info-bg);
  border: 1px solid var(--info-border);
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-extrabold);
}
.ds-empty-title { margin: 0; color: var(--text-primary); font-size: var(--text-lg); font-weight: var(--font-weight-bold); }
.ds-empty-description { margin: 0; max-width: 440px; color: var(--text-muted); font-size: var(--text-sm); }

.ds-skeleton {
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.08) 25%, rgba(148, 163, 184, 0.16) 50%, rgba(148, 163, 184, 0.08) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-md);
  animation: ds-skeleton-shimmer 1.3s infinite;
}
@keyframes ds-skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.ds-link {
  color: var(--brand-300);
  text-decoration: none;
  font-weight: var(--font-weight-bold);
}
.ds-link:hover { color: var(--brand-100); text-decoration: underline; }

.ds-divider {
  height: 1px;
  margin: var(--space-6) 0;
  border: 0;
  background: var(--border-subtle);
}

.ds-mastery-dot {
  width: 10px;
  height: 10px;
  display: inline-block;
  flex: 0 0 auto;
  border-radius: var(--radius-full);
  background: var(--text-subtle);
}
.ds-mastery-low { background: var(--mastery-low); }
.ds-mastery-medium { background: var(--mastery-medium); }
.ds-mastery-high { background: var(--mastery-high); }
.ds-mastery-expert { background: var(--mastery-expert); }

/* Compatibility polish for older page-level styles. */
.ds-shell--app .page-header { display: none !important; }
.dashboard,
.concepts-page,
.content-page,
.path-page,
.quiz-page,
.quiz-ai-page {
  max-width: none !important;
  margin: 0 !important;
  padding: 0 !important;
}
.page-title,
.welcome-title,
.module-name,
.content-title,
.quiz-title,
.quiz-title-active,
.chat-header-info h3,
.session-item-title,
.auth-title,
.onboarding-title {
  color: var(--text-primary) !important;
  background: none !important;
  -webkit-text-fill-color: currentColor !important;
}
.page-sub,
.welcome-sub,
.module-count,
.concept-prereq,
.quiz-meta-item,
.q-counter,
.result-label,
.empty-state,
.no-results,
.session-item-meta {
  color: var(--text-muted) !important;
}
.stat-card,
.panel,
.overall-bar,
.module-section,
.flip-front,
.flip-back,
.content-area,
.sidebar,
.quiz-card,
.question-card,
.result-screen,
.setup-card,
.feedback-card,
.loading-card,
.history-table,
.auth-card,
.onboarding-card,
.home-visual,
.home-feature,
.home-node {
  background: linear-gradient(180deg, rgba(15, 27, 45, 0.95), rgba(11, 23, 39, 0.94)) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-sm) !important;
  backdrop-filter: blur(16px) !important;
}
.stat-card:hover,
.quiz-card:hover,
.concept-item:hover,
.rec-card:hover,
.flip-card:hover .flip-front,
.option:hover,
.option-btn:hover:not(:disabled) {
  border-color: var(--border-emphasis) !important;
  background: var(--bg-surface-hover) !important;
}
.stat-number,
.result-score,
.overall-pct,
.card-name,
.concept-name,
.q-text,
.question-text,
.content-body,
.rec-name,
.back-desc,
.quiz-title,
.quiz-title-active {
  color: var(--text-primary) !important;
  background: none !important;
  -webkit-text-fill-color: currentColor !important;
}
.content-body,
.content-body li,
.concept-row,
.option,
.field input,
.field select,
.field textarea,
.open-answer {
  color: var(--text-secondary) !important;
}
.skeleton,
.sk-card,
.sk-row,
.sk-title,
.sk-module,
.sk-sidebar {
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.08) 25%, rgba(148, 163, 184, 0.16) 50%, rgba(148, 163, 184, 0.08) 75%) !important;
  background-size: 200% 100% !important;
}
.progress-track,
.progress-bar,
.progress-bar-wrap,
.concept-bar-wrap,
.mastery-bar-wrap,
.ring-bg {
  background: var(--bg-surface-3) !important;
  stroke: var(--bg-surface-3) !important;
}
.progress-fill,
.progress-bar-fill,
.concept-bar,
.mastery-bar,
.ring-fill {
  background: var(--brand-gradient) !important;
}
.btn-primary,
.btn-next,
.btn-retry,
.new-session-btn,
.send-btn {
  color: #06111f !important;
  background: linear-gradient(135deg, #e0f2fe, #7dd3fc 55%, #a5b4fc) !important;
  border: 1px solid rgba(125, 211, 252, 0.6) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-glow-brand) !important;
}
.btn-secondary,
.btn-link,
.btn-back,
.btn-quit,
.action-btn {
  color: var(--text-primary) !important;
  background: rgba(21, 36, 58, 0.88) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-md) !important;
  text-decoration: none !important;
}
.btn-secondary:hover,
.btn-link:hover,
.btn-back:hover,
.btn-quit:hover,
.action-btn:hover {
  color: var(--brand-100) !important;
  border-color: var(--border-emphasis) !important;
  background: var(--bg-surface-hover) !important;
}
.filter-chip,
.level-tab,
.card-category-badge,
.diff-badge,
.q-type,
.q-diff,
.q-tag,
.rec-badge,
.level-badge {
  border-radius: var(--radius-md) !important;
}
.filter-chip.active,
.level-tab.active,
.concept-item.active,
.session-item.active,
.option-button.selected,
.option-btn.selected {
  color: var(--brand-100) !important;
  background: rgba(56, 189, 248, 0.13) !important;
  border-color: var(--border-emphasis) !important;
}
.tutor-page,
.chat-area {
  background: var(--bg-base) !important;
}
.tutor-sidebar,
.chat-header,
.input-area {
  background: rgba(11, 23, 39, 0.94) !important;
  border-color: var(--border-default) !important;
  backdrop-filter: blur(16px) !important;
}
.message-student .message-bubble {
  color: #06111f !important;
  background: linear-gradient(135deg, #e0f2fe, #7dd3fc 55%, #a5b4fc) !important;
  border-color: rgba(125, 211, 252, 0.6) !important;
  border-radius: var(--radius-md) !important;
}
.message-tutor .message-bubble {
  color: var(--text-secondary) !important;
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-xs) !important;
}
.input-field,
.field input,
.field select,
.field textarea,
.open-answer {
  background: rgba(7, 17, 31, 0.72) !important;
  border: 1px solid var(--border-default) !important;
  color: var(--text-primary) !important;
  border-radius: var(--radius-md) !important;
}
.input-field:focus,
.field input:focus,
.field select:focus,
.field textarea:focus,
.open-answer:focus {
  border-color: var(--border-focus) !important;
  box-shadow: var(--shadow-focus) !important;
}

@media (max-width: 900px) {
  .ds-grid-3,
  .ds-grid-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 680px) {
  :root { --content-padding-x: 1rem; }
  .ds-grid-2,
  .ds-grid-3,
  .ds-grid-4 { grid-template-columns: 1fr; }
  .ds-page-header-title { font-size: var(--text-2xl); }
}
`

/**
 * Injects global CSS variables and shared components. Idempotent.
 */
export function applyDesignTokens(): void {
  if (document.querySelector('style[data-ds-tokens]')) return
  const style = document.createElement('style')
  style.dataset.dsTokens = 'true'
  style.textContent = TOKENS_CSS
  document.head.appendChild(style)
}

export const Z_INDEX = {
  base: 1,
  sticky: 100,
  sidebar: 200,
  topbar: 300,
  modal: 1000,
  toast: 2000,
} as const
