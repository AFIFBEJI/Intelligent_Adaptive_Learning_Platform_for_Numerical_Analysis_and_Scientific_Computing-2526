// ============================================================
// Design tokens - "Clear Calculus" theme
// ============================================================
// A clear mathematics workspace: whiteboard surfaces, ink-blue text,
// teal actions, indigo structure and amber notes.
// ============================================================

const TOKENS_CSS = `
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:wght@500;600;700&family=JetBrains+Mono:wght@400;500&display=swap");

:root {
  color-scheme: light;

  --bg-base: #f4f8fb;
  --bg-base-soft: #fbfdff;
  --bg-canvas: #ffffff;
  --bg-surface: rgba(255, 255, 255, 0.96);
  --bg-surface-2: rgba(239, 247, 249, 0.94);
  --bg-surface-3: rgba(213, 228, 234, 0.9);
  --bg-surface-hover: rgba(255, 255, 255, 0.99);
  --bg-overlay: rgba(248, 252, 255, 0.9);
  --bg-inverse: #102233;
  --bg-inverse-soft: #17334a;

  --border-subtle: rgba(15, 35, 51, 0.1);
  --border-default: rgba(15, 35, 51, 0.18);
  --border-emphasis: rgba(15, 118, 110, 0.4);
  --border-focus: rgba(14, 116, 144, 0.72);

  --text-primary: #142231;
  --text-secondary: #334155;
  --text-muted: #64748b;
  --text-subtle: #94a3b8;
  --text-disabled: #b6c2cf;
  --text-on-inverse: #f8fbff;
  --text-muted-inverse: rgba(248, 251, 255, 0.68);

  --brand-50: #ecfdf9;
  --brand-100: #ccfbef;
  --brand-300: #5eead4;
  --brand-400: #2dd4bf;
  --brand-500: #0f766e;
  --brand-600: #115e59;
  --brand-gradient: linear-gradient(135deg, #0f766e 0%, #2563eb 58%, #059669 100%);

  --accent-cyan: #0e7490;
  --accent-indigo: #3155a6;
  --accent-purple: #7c3aed;
  --accent-pink: #be4565;
  --accent-amber: #b7791f;
  --accent-coral: #d15b45;
  --accent-stone: #64748b;

  --success: #15803d;
  --success-bg: rgba(21, 128, 61, 0.1);
  --success-border: rgba(21, 128, 61, 0.26);

  --warning: #a16207;
  --warning-bg: rgba(183, 121, 31, 0.12);
  --warning-border: rgba(183, 121, 31, 0.3);

  --danger: #b4233a;
  --danger-bg: rgba(180, 35, 58, 0.1);
  --danger-border: rgba(180, 35, 58, 0.28);

  --info: #3155a6;
  --info-bg: rgba(49, 85, 166, 0.1);
  --info-border: rgba(49, 85, 166, 0.27);

  --mastery-low: #b4233a;
  --mastery-medium: #b7791f;
  --mastery-high: #15803d;
  --mastery-expert: #3155a6;

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

  --font-sans: "Inter", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
  --font-serif: "Source Serif 4", Georgia, "Times New Roman", serif;
  --font-mono: "JetBrains Mono", "Fira Code", Consolas, monospace;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-md: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.5rem;
  --text-5xl: 3.4rem;
  --text-6xl: 4.4rem;

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;

  --line-height-tight: 1.15;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.7;

  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-2xl: 16px;
  --radius-full: 9999px;

  --shadow-xs: 0 1px 2px rgba(15, 35, 51, 0.08);
  --shadow-sm: 0 8px 22px rgba(15, 35, 51, 0.08);
  --shadow-md: 0 18px 44px rgba(15, 35, 51, 0.11);
  --shadow-lg: 0 30px 70px rgba(15, 35, 51, 0.13);
  --shadow-xl: 0 42px 95px rgba(15, 35, 51, 0.15);
  --shadow-glow-brand: 0 10px 26px rgba(15, 118, 110, 0.2);
  --shadow-focus: 0 0 0 3px rgba(14, 116, 144, 0.18);

  --transition-fast: 140ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 220ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 360ms cubic-bezier(0.4, 0, 0.2, 1);

  --sidebar-width: 276px;
  --sidebar-width-collapsed: 76px;
  --topbar-height: 76px;
  --content-max-width: 1240px;
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
    radial-gradient(ellipse at 12% 4%, rgba(15, 118, 110, 0.1) 0%, transparent 34%),
    radial-gradient(ellipse at 88% 10%, rgba(49, 85, 166, 0.08) 0%, transparent 32%),
    linear-gradient(180deg, var(--bg-base) 0%, var(--bg-base-soft) 46%, var(--bg-base) 100%);
  background-attachment: fixed;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(15, 35, 51, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(15, 35, 51, 0.045) 1px, transparent 1px);
  background-size: 32px 32px, 32px 32px;
  mask-image: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.9) 0%, transparent 78%);
  -webkit-mask-image: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.9) 0%, transparent 78%);
}

body::after {
  content: "\\222B   \\2211   \\03C0   \\2202   \\2207   \\03BB   \\03C3   \\221E";
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  font-family: var(--font-serif);
  font-size: 11rem;
  font-weight: 600;
  color: rgba(15, 35, 51, 0.032);
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 0.55em;
  white-space: nowrap;
  overflow: hidden;
  user-select: none;
  font-style: italic;
}

#app { position: relative; z-index: 1; min-height: 100vh; }

a { color: inherit; }
button, input, textarea, select { font: inherit; }
button { color: inherit; }
img, svg { display: block; max-width: 100%; }

*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-track { background: transparent; }
*::-webkit-scrollbar-thumb {
  background: rgba(15, 118, 110, 0.26);
  border-radius: var(--radius-full);
}
*::-webkit-scrollbar-thumb:hover { background: rgba(15, 118, 110, 0.4); }

::selection {
  background: rgba(15, 118, 110, 0.2);
  color: var(--text-primary);
}

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
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(12px);
}

.ds-card { padding: var(--space-5); }
.ds-panel { padding: var(--space-6); }
.ds-card-elevated { box-shadow: var(--shadow-md); }
.ds-card-interactive {
  cursor: pointer;
  transition: border-color var(--transition-base), transform var(--transition-base), background var(--transition-base), box-shadow var(--transition-base);
}
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
  color: var(--brand-500);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.14em;
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
  min-height: 42px;
  padding: 0.7rem 1.15rem;
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
  color: var(--text-on-inverse);
  background: var(--brand-gradient);
  border-color: rgba(15, 118, 110, 0.42);
  box-shadow: var(--shadow-glow-brand);
}
.ds-btn-primary:hover:not(:disabled) {
  filter: saturate(1.04) brightness(1.02);
  box-shadow: 0 14px 34px rgba(15, 118, 110, 0.24);
}
.ds-btn-secondary {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.84);
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
  background: rgba(15, 118, 110, 0.08);
}
.ds-btn-danger {
  color: var(--danger);
  background: var(--danger-bg);
  border-color: var(--danger-border);
}

.ds-icon {
  width: 38px;
  height: 38px;
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: var(--radius-md);
  color: var(--brand-600);
  background: rgba(15, 118, 110, 0.11);
  border: 1px solid rgba(15, 118, 110, 0.22);
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
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-bold);
  text-decoration: none;
}
.ds-badge-brand, .ds-chip.active {
  color: var(--brand-600);
  background: rgba(15, 118, 110, 0.11);
  border: 1px solid rgba(15, 118, 110, 0.26);
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
.ds-tab.active { color: var(--brand-600); background: rgba(15, 118, 110, 0.1); }

.ds-input,
.ds-select,
.ds-textarea {
  width: 100%;
  min-height: 44px;
  padding: 0.7rem 0.9rem;
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.9);
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
  background: #ffffff;
}
.ds-label {
  display: block;
  margin: 0 0 var(--space-2);
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.08em;
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
.ds-alert-info { color: var(--brand-600); background: var(--info-bg); border: 1px solid var(--info-border); }
.ds-alert-success { color: var(--success); background: var(--success-bg); border: 1px solid var(--success-border); }

.ds-stat {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  min-height: 112px;
  padding: var(--space-5);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}
.ds-stat-value {
  color: var(--text-primary);
  font-size: var(--text-3xl);
  font-weight: var(--font-weight-extrabold);
  line-height: 1;
  font-family: var(--font-serif);
  letter-spacing: 0;
}
.ds-stat-label {
  margin-top: var(--space-1);
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.08em;
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
  border-radius: var(--radius-lg);
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
  letter-spacing: 0.08em;
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
  background: rgba(15, 118, 110, 0.05);
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-lg);
}
.ds-empty-icon {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  color: var(--brand-600);
  background: rgba(15, 118, 110, 0.1);
  border: 1px solid rgba(15, 118, 110, 0.22);
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-extrabold);
}
.ds-empty-title { margin: 0; color: var(--text-primary); font-size: var(--text-lg); font-weight: var(--font-weight-bold); }
.ds-empty-description { margin: 0; max-width: 440px; color: var(--text-muted); font-size: var(--text-sm); }

.ds-skeleton {
  background: linear-gradient(90deg, rgba(15, 35, 51, 0.06) 25%, rgba(15, 35, 51, 0.14) 50%, rgba(15, 35, 51, 0.06) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-md);
  animation: ds-skeleton-shimmer 1.4s infinite;
}
@keyframes ds-skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.ds-link {
  color: var(--brand-600);
  text-decoration: none;
  font-weight: var(--font-weight-bold);
  transition: color var(--transition-fast);
}
.ds-link:hover { color: var(--brand-500); text-decoration: underline; text-underline-offset: 3px; }

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

/* Compatibility shims for older inline page styles. */
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
.onboarding-title,
.hero-title,
.panel-title,
.concepts-toolbar-title,
.overall-label,
.mastery-label,
.llm-modal-title,
.llm-card-name {
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
.session-item-meta,
.panel-subtitle,
.hero-sub,
.mastery-caption,
.overall-caption,
.llm-modal-subtitle,
.llm-card-model,
.llm-card-tagline,
.llm-card-desc {
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
.home-node,
.hero-panel,
.mastery-panel,
.metric-card,
.dash-panel,
.quick-action,
.concepts-toolbar,
.overview-card,
.concept-card,
.priority-item,
.recommend-item,
.overall-stat,
.mastery-mini,
.llm-modal,
.llm-card,
.eval-row,
.fb-recommendations,
.adaptive-note,
.quiz-ai-header {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: var(--shadow-sm) !important;
  backdrop-filter: blur(10px) !important;
}

.stat-card:hover,
.quiz-card:hover,
.concept-item:hover,
.rec-card:hover,
.flip-card:hover .flip-front,
.option:hover,
.option-btn:hover:not(:disabled),
.quick-action:hover,
.concept-card:hover,
.llm-card:hover {
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
.quiz-title-active,
.metric-value,
.overview-value,
.recommend-name,
.priority-name,
.quick-title {
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
.open-answer,
.eval-ans,
.eval-exp,
.message-tutor .message-bubble {
  color: var(--text-secondary) !important;
}

.skeleton,
.sk-card,
.sk-row,
.sk-title,
.sk-module,
.sk-sidebar {
  background: linear-gradient(90deg, rgba(15, 35, 51, 0.06) 25%, rgba(15, 35, 51, 0.14) 50%, rgba(15, 35, 51, 0.06) 75%) !important;
  background-size: 200% 100% !important;
}

.progress-track,
.progress-bar,
.progress-bar-wrap,
.concept-bar-wrap,
.mastery-bar-wrap,
.priority-bar,
.ring-bg,
.mastery-ring-bg {
  background: var(--bg-surface-3) !important;
  stroke: var(--bg-surface-3) !important;
}
.progress-fill,
.progress-bar-fill,
.concept-bar,
.mastery-bar,
.ring-fill,
.level-dot.active,
.mastery-ring-fill {
  background: var(--brand-gradient) !important;
  stroke: var(--brand-500) !important;
}

.btn-primary,
.btn-next,
.btn-retry,
.new-session-btn,
.send-btn,
.btn-start,
.llm-btn-save,
.llm-card.selected .llm-card-action {
  color: var(--text-on-inverse) !important;
  background: var(--brand-gradient) !important;
  border: 1px solid rgba(15, 118, 110, 0.42) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-glow-brand) !important;
}

.btn-secondary,
.btn-link,
.btn-back,
.btn-quit,
.action-btn,
.llm-btn-cancel,
.fb-reco-chip,
.llm-picker-btn {
  color: var(--text-primary) !important;
  background: rgba(255, 255, 255, 0.84) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-md) !important;
  text-decoration: none !important;
}
.btn-secondary:hover,
.btn-link:hover,
.btn-back:hover,
.btn-quit:hover,
.action-btn:hover,
.llm-btn-cancel:hover,
.fb-reco-chip:hover {
  color: var(--brand-600) !important;
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
.level-badge,
.hero-kicker,
.metric-token,
.quick-token,
.module-icon,
.concept-status,
.q-num,
.tag-mcq {
  border-radius: var(--radius-md) !important;
  color: var(--brand-600) !important;
  background: rgba(15, 118, 110, 0.1) !important;
  border: 1px solid rgba(15, 118, 110, 0.23) !important;
}
.filter-chip.active,
.level-tab.active,
.concept-item.active,
.session-item.active,
.option-button.selected,
.option-btn.selected,
.llm-card.selected {
  color: var(--brand-600) !important;
  background: rgba(15, 118, 110, 0.14) !important;
  border-color: var(--border-emphasis) !important;
}

.tutor-page,
.chat-area {
  background: transparent !important;
}
.tutor-sidebar,
.chat-header,
.input-area {
  background: rgba(255, 255, 255, 0.94) !important;
  border-color: var(--border-default) !important;
  backdrop-filter: blur(12px) !important;
}
.message-student .message-bubble {
  color: var(--text-on-inverse) !important;
  background: var(--brand-gradient) !important;
  border-color: rgba(15, 118, 110, 0.42) !important;
  border-radius: var(--radius-md) !important;
}
.message-tutor .message-bubble {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-default) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-xs) !important;
}
.typing-dot {
  background: rgba(15, 118, 110, 0.46) !important;
}

.input-field,
.field input,
.field select,
.field textarea,
.open-answer {
  background: rgba(255, 255, 255, 0.9) !important;
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
.input-field::placeholder,
.open-answer::placeholder {
  color: var(--text-subtle) !important;
}

.language-option.active,
.ds-lang-btn.active,
.quiz-lang-btn.active {
  color: var(--text-on-inverse) !important;
  background: var(--brand-gradient) !important;
  box-shadow: var(--shadow-xs) !important;
}

.fb-summary,
.adaptive-note {
  background: rgba(15, 118, 110, 0.08) !important;
  border-color: rgba(15, 118, 110, 0.23) !important;
}

.content-body strong,
.content-body code,
.content-body th,
.content-body h2::before,
.concept-prereq.ready,
.fb-recommendations-title,
.fb-nexts h3 {
  color: var(--brand-600) !important;
}
.content-body em {
  color: var(--accent-amber) !important;
}
.cat-ode,
.mi-purple,
.level-tab.rigorous.active {
  color: var(--accent-amber) !important;
  background: rgba(183, 121, 31, 0.1) !important;
  border-color: rgba(183, 121, 31, 0.24) !important;
}
.content-body code {
  background: rgba(15, 118, 110, 0.08) !important;
  border-color: rgba(15, 118, 110, 0.18) !important;
}
.content-body .katex-display {
  background: var(--bg-surface-2) !important;
  border-color: var(--border-default) !important;
  border-left-color: var(--brand-500) !important;
}
.message-bubble code,
.message-bubble pre {
  background: rgba(15, 35, 51, 0.08) !important;
  color: var(--brand-600) !important;
}

.llm-card-icon,
.brand-icon,
.user-avatar {
  color: var(--text-on-inverse) !important;
  background: var(--brand-gradient) !important;
}
.llm-card-icon.cloud {
  background: linear-gradient(135deg, var(--accent-amber), var(--accent-coral)) !important;
}
.llm-tag.info {
  color: var(--info) !important;
  background: var(--info-bg) !important;
}
.navbar,
.navbar.scrolled,
.navbar-links {
  background: var(--bg-overlay) !important;
  border-color: var(--border-subtle) !important;
  box-shadow: var(--shadow-sm) !important;
}
.brand-text,
.nav-link.active {
  color: var(--brand-600) !important;
  background: none !important;
  -webkit-text-fill-color: currentColor !important;
}
.nav-link {
  color: var(--text-muted) !important;
}
.nav-link:hover {
  color: var(--text-primary) !important;
}

.content-body,
.message-bubble,
.question-text,
.q-text,
.eval-exp {
  overflow-wrap: anywhere;
}

.content-body p,
.content-body li,
.message-bubble p,
.message-bubble li {
  line-height: 1.85 !important;
}

.content-body .katex-display,
.message-bubble .katex-display,
.question-text .katex-display {
  max-width: 100%;
  overflow-x: auto;
  padding: var(--space-4) var(--space-5) !important;
}

.level-chip,
.mini-chip {
  color: var(--text-secondary) !important;
  background: var(--bg-surface-2) !important;
  border: 1px solid var(--border-subtle) !important;
}
.level-chip strong,
.mini-chip strong,
.card-level,
.module-progress,
.adaptive-note strong {
  color: var(--brand-600) !important;
}

@media (max-width: 900px) {
  .ds-grid-3,
  .ds-grid-4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 680px) {
  :root { --content-padding-x: 1rem; }
  body::after { font-size: 7rem; letter-spacing: 0.32em; }
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
