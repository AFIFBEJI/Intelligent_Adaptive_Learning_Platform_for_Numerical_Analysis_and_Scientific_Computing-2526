// ============================================================
// Playwright config — tests E2E pour la plateforme adaptative
// ============================================================
// Demarre le frontend Vite en mode dev (qui proxy /api -> 8000)
// avant de lancer les tests, et le coupe a la fin. Le backend
// uvicorn doit tourner separement sur :8000 (lance soit en natif,
// soit via docker compose up postgres neo4j backend).
//
// Pour lancer en local :
//   1. Demarrer Postgres + Neo4j + backend natif sur :8000
//   2. cd frontend && npm install
//   3. npx playwright install --with-deps chromium  (premiere fois)
//   4. npm run test:e2e
//
// Pour le CI : voir .github/workflows/ci.yml job 'e2e-playwright'.
// ============================================================
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  // Timeout par test (les flows passent par LLM qui peut etre lent en pratice).
  timeout: 60_000,
  // Pas de parallele : les tests partagent la meme DB et l'ordre compte
  // (registration cree un user que login utilise).
  fullyParallel: false,
  workers: 1,
  // Retry une fois sur la CI uniquement, pour absorber les flakes reseau.
  retries: process.env.CI ? 1 : 0,
  // Reporter HTML pour les artefacts CI.
  reporter: process.env.CI ? [['html', { open: 'never' }], ['list']] : [['list']],

  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:4200',
    // Capture une trace au premier essai si on retry, screenshots a l'echec,
    // video gardee uniquement en cas d'echec.
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    // Locale FR pour matcher les strings i18n par defaut.
    locale: 'fr-FR',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Auto-start du frontend dev server si pas deja la. Le backend doit
  // tourner separement (sinon les API calls echouent).
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    url: 'http://localhost:4200',
    timeout: 30_000,
    reuseExistingServer: true,
    stderr: 'pipe',
    stdout: 'pipe',
  },
})
