// ============================================================
// Point d'entrée principal - Adaptive Learning Platform SPA
// ============================================================
// C'est quoi ce fichier ?
//
// C'est le PREMIER fichier JavaScript exécuté par le navigateur.
// Il fait 3 choses :
//   1. Restaurer le token JWT (si l'étudiant était déjà connecté)
//   2. Définir les ROUTES (quelle URL → quelle page)
//   3. Démarrer le router (écouter les changements d'URL)
//
// C'est quoi une SPA (Single Page Application) ?
// Contrairement à un site classique où chaque clic charge
// une NOUVELLE page depuis le serveur, ici le navigateur
// charge UNE SEULE page (index.html) et JavaScript change
// le contenu dynamiquement. C'est plus rapide et fluide.
//
// C'est quoi un Router ?
// C'est le "GPS" de l'application. Il regarde l'URL et décide
// quelle page afficher :
//   /           → Page d'accueil (HomePage)
//   /login      → Page de connexion
//   /dashboard  → Tableau de bord (protégé : faut être connecté)
//   /tutor      → Tuteur IA (NOUVEAU \! protégé)
// ============================================================

import { router } from './router'
import { api } from './api'
import { HomePage } from './pages/home'
import { LoginPage } from './pages/login'
import { RegisterPage } from './pages/register'
import { DashboardPage } from './pages/dashboard'
import { ConceptsPage } from './pages/concepts'
import { ContentPage } from './pages/content'
import { LearningPathPage } from './pages/learning-path'
import { QuizPage } from './pages/quiz'
import { TutorPage } from './pages/tutor'  // ← NOUVEAU : la page du tuteur IA

// ============================================================
// Restauration du Token JWT
// ============================================================
// NB: on importe `api` en statique (voir les imports en haut) plutôt qu'en
// dynamique avec `await import()`. Le top-level await est interdit par la
// cible `es2020` de Vite, et une importation statique ajoute ~0 Ko au bundle
// car `api` est de toute façon utilisé partout dans l'app (ce n'est pas
// du code "rarement exécuté" qui mériterait un code-split).
// ============================================================
const token = localStorage.getItem('token')
if (token) {
  api.setToken(token)
}

// ============================================================
// Définition des Routes
// ============================================================
// addRoute(chemin, PageComponent, protégé?)
//
// Le 3ème paramètre (true/false) dit si la route est PROTÉGÉE :
//   false → accessible à tout le monde (accueil, login, register)
//   true  → accessible SEULEMENT si connecté (dashboard, quiz, tutor)
//
// Si un étudiant non connecté essaie d'aller sur /dashboard,
// le router le redirige automatiquement vers /login.
// ============================================================
router
  .addRoute('/', HomePage, false)
  .addRoute('/login', LoginPage, false)
  .addRoute('/register', RegisterPage, false)
  .addRoute('/dashboard', DashboardPage, true)
  .addRoute('/concepts', ConceptsPage, true)
  .addRoute('/content', ContentPage, true)
  .addRoute('/path', LearningPathPage, true)
  .addRoute('/quiz', QuizPage, true)
  .addRoute('/tutor', TutorPage, true)  // ← NOUVEAU : route protégée du tuteur IA

// Démarrer le router (commence à écouter les changements d'URL)
router.start()
