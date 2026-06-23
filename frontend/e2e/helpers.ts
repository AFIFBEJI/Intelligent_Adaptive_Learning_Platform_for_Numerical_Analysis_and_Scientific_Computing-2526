// ============================================================
// Helpers partages par les tests E2E
// ============================================================
import { Page, expect } from '@playwright/test'

/** Genere un email unique pour chaque test (evite les collisions). */
export function makeEmail(prefix = 'e2e'): string {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 10_000)}@test.local`
}

/**
 * Cree un compte etudiant en remplissant le formulaire de /register.
 * - Choisit la langue (obligatoire)
 * - Remplit nom + email + password
 * - Soumet
 *
 * Retourne le token JWT pose dans localStorage (utile pour skip le
 * formulaire dans les tests qui veulent juste etre "logged in").
 */
export async function registerUser(
  page: Page,
  opts: { email: string; password?: string; lang?: 'en' | 'fr'; fullName?: string } = { email: '' },
): Promise<string> {
  const { email, password = 'TestPass123', lang = 'fr', fullName = 'Test User' } = opts

  await page.goto('/register')

  // Choix de langue obligatoire (le bouton submit reste disable sinon).
  const langButton = lang === 'fr'
    ? page.getByRole('button', { name: /French|Francais/i }).first()
    : page.getByRole('button', { name: /English|Anglais/i }).first()
  await langButton.click()

  await page.locator('input[type="text"]').first().fill(fullName)
  await page.locator('input[type="email"]').fill(email)
  await page.locator('input[type="password"]').fill(password)

  await page.getByRole('button', { name: /Create account|Creer/i }).click()

  // Apres registration, on est rediriger soit vers /onboarding-quiz,
  // soit vers /dashboard. On attend que le token soit pose.
  await page.waitForFunction(() => Boolean(localStorage.getItem('token')), {
    timeout: 15_000,
  })

  return await page.evaluate(() => localStorage.getItem('token') || '')
}

/**
 * Connexion d'un compte deja existant. Retourne le token JWT.
 *
 * Important : la page /login exige aussi un choix de langue obligatoire
 * (comme /register). Le bouton submit reste disabled tant que ce choix
 * n'a pas ete fait. On le selectionne explicitement ici.
 *
 * Entre 2 tests Playwright, le contexte est isole donc app_lang du test
 * precedent n'est PAS conserve.
 */
export async function loginUser(
  page: Page,
  email: string,
  password = 'TestPass123',
  lang: 'en' | 'fr' = 'fr',
): Promise<string> {
  await page.goto('/login')

  // Choix de langue (sinon le bouton submit reste disabled).
  // ATTENTION : le clic sur la langue declenche router.navigate('/login')
  // dans login.ts, ce qui re-rend toute la page. On doit donc attendre
  // que le DOM soit reconstruit ET que #submit-btn soit enabled avant
  // de continuer.
  const langSelector = lang === 'fr'
    ? page.locator('[data-lang="fr"]').first()
    : page.locator('[data-lang="en"]').first()
  await langSelector.click()

  // Attendre que la page se re-rende et que le bouton submit ne soit
  // plus disabled. expect.toBeEnabled() retry jusqu'a 5s par defaut.
  await expect(page.locator('#submit-btn')).toBeEnabled({ timeout: 5_000 })

  await page.locator('input[type="email"]').fill(email)
  await page.locator('input[type="password"]').fill(password)

  await page.locator('#submit-btn').click()

  await page.waitForFunction(() => Boolean(localStorage.getItem('token')), {
    timeout: 10_000,
  })

  return await page.evaluate(() => localStorage.getItem('token') || '')
}

/** Helper pour assert qu'on est bien sur le dashboard. */
export async function expectOnDashboard(page: Page): Promise<void> {
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 10_000 })
  // Le titre "Dashboard" / "Tableau de bord" doit apparaitre.
  await expect(page.getByRole('heading', { name: /Dashboard|Tableau de bord/i }).first())
    .toBeVisible({ timeout: 10_000 })
}
