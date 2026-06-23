// ============================================================
// Smoke test : la landing page se charge correctement
// ============================================================
// C'est le test le plus basique : si CE test casse, il y a probablement
// un probleme grave (Vite ne build pas, le router ne demarre pas, etc.).
// ============================================================
import { test, expect } from '@playwright/test'

test.describe('Smoke - Landing page', () => {
  test('la home page se charge avec le titre Numera', async ({ page }) => {
    await page.goto('/')
    // Le titre "Numera" est affiche dans la sidebar/topbar.
    await expect(page.locator('text=Numera').first()).toBeVisible({ timeout: 10_000 })
    // Aucune erreur de console critique.
    page.on('pageerror', (err) => {
      throw new Error(`Console error sur la home : ${err.message}`)
    })
  })

  test('navigation vers /login affiche le formulaire', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('input[type="email"]')).toBeVisible({ timeout: 10_000 })
    await expect(page.locator('input[type="password"]')).toBeVisible()
  })

  test('navigation vers /register affiche le picker de langue', async ({ page }) => {
    await page.goto('/register')
    // Les 2 boutons de langue doivent etre presents.
    await expect(page.getByRole('button', { name: /English/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /French|Francais/i })).toBeVisible()
  })
})
