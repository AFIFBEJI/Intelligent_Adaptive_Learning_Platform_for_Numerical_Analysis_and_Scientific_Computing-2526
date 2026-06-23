# Tests E2E Playwright

Suite de tests bout-en-bout qui simulent un utilisateur reel (Chromium headless) sur la plateforme.

## Pre-requis

- Node 20+
- Backend FastAPI demarre sur **http://localhost:8000**
- Postgres + Neo4j accessibles (via docker compose ou natif)

## Installation (premiere fois)

```bash
cd frontend
npm install
npx playwright install --with-deps chromium
```

## Lancement local

**Terminal 1** : backend natif (avec Postgres + Neo4j en docker)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Terminal 2** : tests Playwright

```bash
cd frontend
npm run test:e2e          # mode CLI (rapide)
npm run test:e2e:ui       # mode interactif (debug visuel)
```

Vite est demarre automatiquement par `playwright.config.ts` via `webServer`. Si tu as deja un serveur Vite qui tourne sur :4200, il sera reutilise (`reuseExistingServer: true`).

## Specs

| Fichier | Couverture |
|---|---|
| `smoke.spec.ts` | Landing page se charge, /login + /register affichent leurs formulaires |
| `auth.spec.ts` | Registration -> token JWT pose, login OK, login echec sans token, garde route protegee |
| `quiz.spec.ts` | Chooser /quiz-ai, click adaptive, click practice, retour, banderole pendant quiz |

## CI

Le job `e2e-playwright` dans `.github/workflows/ci.yml` :
1. Spin up Postgres + Neo4j en service containers
2. Seed le graphe Neo4j + les quiz
3. Lance `uvicorn` en arriere-plan (port 8000)
4. Build et lance `vite preview` (port 4200)
5. Installe Chromium et lance `npx playwright test`
6. Upload le report HTML en cas d'echec
