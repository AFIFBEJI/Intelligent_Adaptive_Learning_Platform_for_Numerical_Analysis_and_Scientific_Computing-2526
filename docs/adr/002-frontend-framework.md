# ADR-002: Vanilla TypeScript SPA, no UI framework

**Status**: ✅ Accepted (lucid acceptance, see limitations below)
**Date**: May 12, 2026
**Author**: Yassine Ben Nessib

## Context

The application has a rich UI: 14 pages, 19 interactive JSXGraph widgets,
embedded Manim tutorials, analytics dashboard, user study forms.
Structural question at the start of the project (Phase 1, February 2026):
which framework to use?

**Initial constraints**:

- 6-month deadline → no time to learn a new framework.
- Demo that must load quickly (target: First Paint < 1 s).
- Minimalist stack for reproducibility (a paper reviewer must be able to
  clone + npm install + start in < 5 minutes).
- Existing skills: strong TypeScript + HTML/CSS, moderate React.

## Options considered

### Option A: React + Vite + React-Router + TanStack Query
- **+** De facto standard in 2026.
- **+** Huge ecosystem (chakra-ui, shadcn, etc.).
- **+** Excellent hot reload, mature devtools.
- **−** Base bundle ~150 KB.
- **−** Hydration + re-render on every setState → cognitive cost.
- **−** Learning curve: hooks, contexts, Suspense, server components.

### Option B: Vue 3 + Vite + Pinia
- **+** Easier to learn than React.
- **+** Fine-grained reactivity (Proxy-based).
- **−** Smaller French ecosystem than React.
- **−** Sometimes confusing documentation between Vue 2 / Vue 3.

### Option C: Svelte 5 + SvelteKit
- **+** Compile-time, tiny bundle (~30 KB).
- **+** Simplest syntax of the three.
- **−** Smaller ecosystem, fewer Stack Overflow answers.
- **−** Industrial adoption in 2026 still limited.

### Option D: Vanilla TypeScript + Vite + custom router
- **+** No framework to learn, no "magic".
- **+** Ultra-light bundle (~10 KB excluding deps).
- **+** Pedagogically clear: everything that happens is in `pages/*.ts`.
- **+** No risk of obsolete dependencies (React 17 → 18 → 19 broke code).
- **−** No reusable component system (each page rebuilds its DOM).
- **−** Manual re-render: `container.innerHTML = ...` on every navigation.
- **−** Untyped template strings → silent errors.

## Decision

**Option D retained: Vanilla TypeScript SPA with custom router (~107 lines).**

**Main reason**: total code mastery. Six months from the end, we cannot
afford a lost day on an obscure React hooks bug.

**Implementation**:

- `frontend/src/router.ts`: in-house router of ~100 lines (handles
  `pushState`, auth guards, wildcard routes).
- `frontend/src/pages/*.ts`: 14 pages, each exporting a function
  `XxxPage(): HTMLElement` that returns a DOM node.
- `frontend/src/i18n.ts`: FR/EN strings table (849 lines) read by `t(key)`.
- `frontend/src/api.ts`: typed REST client (484 lines) wrapping fetch.
- TypeScript `strict: true`, `noUnusedLocals`, `noUnusedParameters`.

**Tooling**:

- **Vite** for dev server + bundling (fast HMR, native ESM).
- **Playwright** for E2E (smoke + auth + quiz).
- No unit tests (Vitest absent) → deliberate, covered via E2E.

## Consequences

### Positive

- **Tiny bundle** (~80 KB compressed for the whole app).
- **First Paint < 700 ms** on average connection, even without CDN.
- **No build surprises**: no "works in dev, breaks in prod" issue (classic
  React SSR / hydration problem).
- **Readability for the jury**: each page is a standalone file, no hooks
  or hidden state management. A reviewer finds the logic in 30 seconds.
- **Paper reproducibility**: no dependency on a framework that might
  introduce breaking changes (React 19, Vue 4...).

### Negative / accepted debt

- **Massive pages**: some are 1500+ lines (`quiz-ai.ts:1560`,
  `tutor.ts:1450`, `dashboard.ts:714`, `home.ts:901`). Hard to maintain,
  style cleanly, or unit-test.
- **innerHTML everywhere**: XSS attack surface. Mitigation: DOMPurify for
  anything coming from the LLM (cf. ADR on security).
- **`i18n.ts` = 849 lines**: monolithic file that should be split, but
  refactor deferred to avoid breaking existing translations.
- **No reusable components**: HTML duplicated between pages (e.g., each
  page rebuilds its navbar). Acceptable for 14 pages, doesn't scale to 50+.
- **No frontend unit tests** (Vitest absent). SPA is covered by Playwright
  E2E, which are slower and more fragile.

### Evolution plan

**If the project becomes a product (post-PFE)**:

1. Phase 1: extract reusable helpers (navbar, sidebar, modal) into
   `frontend/src/components/` (partially done for app-shell, navbar,
   sidebar).
2. Phase 2: adopt Lit / Stencil for Web Components (compatible with
   existing code as W3C standard).
3. Phase 3 (if strong growth): progressive migration to React + shadcn/ui
   by rewriting the most complex pages (tutor, quiz-ai) first.

**If we stay on Vanilla TS**: target a split into sub-components of
~300 lines max per file.

## References

- Vite docs: https://vitejs.dev
- React vs Vanilla performance: https://blog.web.dev/javascript/measure-performance
- Lit web components: https://lit.dev
- Source file for this decision: `frontend/src/router.ts`, `frontend/src/main.ts`
