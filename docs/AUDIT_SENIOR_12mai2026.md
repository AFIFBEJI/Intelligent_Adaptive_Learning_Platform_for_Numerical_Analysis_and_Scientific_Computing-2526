# AUDIT SENIOR DU PROJET PFE — 12 mai 2026

> **Projet :** Intelligent Adaptive Learning Platform for Numerical Analysis and Scientific Computing
> **Étudiant :** Yassine Ben Nessib (ESPRIT), encadré par Afif Beji
> **Phase théorique :** mois 4/6 — milieu Phase 2 / début Phase 3
> **Note finale : 14,5 / 20**

---

## 1. Inventaire général

| Zone | Volume |
|---|---|
| Backend Python (`backend/app/`) | ~7 900 lignes — 7 services, 7 routers, 4 modèles SQL, 5 schémas |
| Tests backend | 8 fichiers, **82 tests** |
| Scripts seed Neo4j + contenu | 12 scripts, ~6 350 lignes |
| Manim scenes | 19 fichiers, 19 MP4 EN |
| Banque questions | 75 + 30 questions × 15 concepts (bilingue) |
| Frontend TypeScript | ~10 800 lignes — 14 pages, 19 widgets JSXGraph |
| CI/CD | 1 workflow, 7 jobs (lint + smoke + build + graph + docker + integration + e2e) |
| Docker | docker-compose 4 services |

**Beaucoup de "vrai" code, pas du squelette. C'est sain.**

---

## 2. État par sous-système

### 2.1 Authentication — 4/5 — ~95% implémenté

✅ JWT + bcrypt, email verif, reset password, 23 tests d'intégration auth + email.
⚠️ Pas de `EmailStr`, pas de complexity password, `/etudiants/` IDOR, JWT 7 jours sans révocation.

### 2.2 Knowledge Assessment Engine — 4/5 — ~85-90%

✅ Double mode adaptive/practice, 105 questions hand-curated bilingues, évaluation déterministe QCM, calibration auto post-diagnostic.
⚠️ `build_feedback_card` court-circuite le LLM (prompt mort), `update_mastery` dupliqué entre 2 routers, RAG keyword fragile.

### 2.3 Knowledge Graph (Neo4j) — 5/5 — ~100%

✅ 4 modules, 19 concepts, 49 relations REQUIRES/COVERS/REMEDIATES_TO, **15 tests CI** d'intégrité, bilingue first-class, cross-module REQUIRES.
⚠️ Pas de pool, pas de fermeture driver, `generate_learning_path` dupliqué service/router.

### 2.4 AI Tutoring (LLM + RAG) — 3/5 — ~75% mais dette technique

✅ Provider abstraction Ollama+OpenAI, RAG GraphRAG vrai, vérification SymPy étendue (équations + dérivées + intégrales), 17 tests SymPy.
⚠️ Prompts hard-codés en français, **pas de rate-limit** (budget OpenAI à risque), pas de timeout SymPy, **XSS potentiel** via innerHTML LLM sans DOMPurify, mutable default arg.

### 2.5 Visualization Layer — 4/5 — ~85%

✅ 19 animations Manim + 19 widgets JSXGraph, router `/animations` avec fallback EN.
⚠️ Anims EN uniquement (alors que le reste est bilingue), pas de Desmos/GeoGebra, aucun test des scènes.

---

## 3. Erreurs critiques détectées

### 🔴 P0 — CRITIQUES (à corriger immédiatement)

1. **Clés sensibles sur disque** : OpenAI API key + Gmail App Password dans `.env`. Rotater.
2. **`GET /etudiants/` IDOR** : retourne tous les étudiants à tout user connecté (RGPD).
3. **XSS potentiel via le LLM** : `tutor.ts:1139` injecte en innerHTML sans sanitization.
4. **Pas de rate limiting** sur `/auth/login`, `/tutor/.../ask`, `/quiz-ai/generate`. Risque budget OpenAI.
5. **Pas de validation `EmailStr`** sur `EtudiantCreate`.

### 🟠 P1 — IMPORTANTS

6. `build_feedback_card` court-circuite le LLM (prompt mort).
7. `update_mastery` dupliqué entre 2 routers.
8. `generate_learning_path` dupliqué service/router.
9. Pas de pool de connexions Neo4j (session par requête).
10. Pas de vraies migrations (Alembic absent).
11. JWT 7 jours sans refresh, sans révocation.
12. Pas de timeout SymPy (peut bloquer).
13. CORS permissif (`allow_methods=["*"]`).
14. **0 test sur `/tutor/*`** (router le plus complexe).
15. `use_llm` paramétrable par le client (exploitable budgétairement).

### 🟡 P2 — MINEURS

16. Valeurs `niveau_actuel` incohérentes back/front.
17. Pas de fermeture `neo4j_conn.close()` au shutdown.
18. README artefacts copier-coller.
19. PROJECT_PLAN.md mentionne "ODEs" alors que code = Module 3 Polynomial Approximation.
20. PHASE2_AUDIT_22avril2026.md mentionne Gemini alors que code = Ollama/OpenAI.

---

## 4. Sécurité

| Domaine | État |
|---|---|
| Secrets gitignored | OK (mais rotater par hygiène) |
| JWT HS256 64hex | Acceptable, mais 7j sans révocation |
| Bcrypt rounds 12 | OK |
| Purpose tokens | Très bon |
| User enumeration | Partiel sur /forgot-password |
| CORS | Trop permissif |
| SQL Injection | OK (SQLAlchemy ORM) |
| Cypher Injection | OK (paramètres bindés) |
| Validation Pydantic | Lacune (EmailStr, password complexity) |
| Rate limiting | ❌ ABSENT |
| IDOR | 1 cas critique (/etudiants/) |
| XSS frontend | Risque latent (LLM output) |

---

## 5. Qualité du code

### Backend — forces

Architecture en couches stricte, pas d'imports circulaires, schémas Pydantic propres, singletons cohérents, logs structurés, docstrings pédagogiques riches.

### Backend — dette

Variables et fonctions en français (`hacher_mot_de_passe`, `niveau_actuel`...). DRY violé (3 duplications majeures). Async/sync mélangé. Pas d'injection de dépendances.

### Frontend — forces

TypeScript strict, API client typé, E2E Playwright 3 specs, widgets séparés.

### Frontend — dette

Pas de framework UI : pages 1500+ lignes en innerHTML, dur à maintenir. 7 `any` types. innerHTML partout (XSS surface). `i18n.ts` 849 lignes. Pas de tests unitaires frontend (Vitest absent). Router custom réinventé.

---

## 6. Tests & CI/CD

**82 tests backend**, couverture par module :

| Module | Couverture |
|---|---|
| auth | ★★★★★ |
| quiz statique | ★★★☆☆ |
| quiz dynamique | ★★☆☆☆ |
| **tutor** | **★☆☆☆☆ — ZÉRO test** |
| graph (Neo4j) | ★★★★☆ |
| verification SymPy | ★★★★★ (17 tests) |
| feedback | ★★★☆☆ |
| mail | ★★★★☆ |

**CI : 7 jobs en parallèle**. Manques : pas de mypy, pas de coverage, pas de scan dépendances/secrets.

---

## 7. Documentation

| Fichier | Évaluation |
|---|---|
| `README.md` | Artefacts copier-coller → à nettoyer |
| `GUIDE_PROJET.md` | EXCELLENT (564 lignes) |
| `docs/PROJECT_PLAN.md` | Incohérence doc/code sur Module 3 |
| `docs/PHASE2_AUDIT_22avril2026.md` | Mentionne Gemini alors que code = Ollama/OpenAI |
| `research_state_of_art.md` | Anémique (51 lignes) pour un paper IEEE |

**Manques :** ADRs (Architecture Decision Records), runbook démo.

---

## 8. Conformité avec la proposition PFE

| Phase | Promis | Livré | Verdict |
|---|---|---|---|
| **Phase 1 (m. 1-2)** | Foundation, archi, KG, auth | TOUT | **100%** |
| **Phase 2 (m. 3-4) : ICI** | Quiz adapt., KG complet, LLM+RAG, Manim | TOUT (Manim EN uniquement) | **~85-90%** |
| **Phase 3 (m. 5)** | Remédiation, dashboards, recommandations | Email verif, learning-path, dashboards, adaptive content | **~50% en avance** |
| **Phase 4 (m. 6)** | User study 25-30 étudiants, paper IEEE | **RIEN** | **0%** ⚠️ |

---

## 9. Qualité scientifique / mathématique

**Forces :** banque 105 questions hand-curated rigoureuses, **validation SymPy étendue (équations + dérivées + intégrales) avec 17 tests** = la partie la plus publiable, KG cohérent avec REQUIRES cross-module, calibration auto post-diagnostic, algorithmes Manim sains.

**Faiblesses :** RAG fragile (matching keywords, pas embeddings), pas de métriques RAG loggées, pas de garde-fou math sur quiz généré par LLM, loss fine-tune Gemma E2B 3.22 (élevé).

---

## 10. TOP 10 actions prioritaires

### 🔴 P0 — bloquants soutenance

1. **Rate-limiting** `/auth/login`, `/tutor/.../ask`, `/quiz-ai/generate` (slowapi) — S, 2-4h
2. **Rotater OpenAI + SMTP** — S, 15min
3. **Restreindre `GET /etudiants/`** — S, 15min
4. **Sanitiser HTML LLM** (DOMPurify) — S, 1h

### 🟠 P1 — importants

5. **`EmailStr` + min_length password** sur EtudiantCreate — S, 30min
6. **10-15 tests d'intégration sur `/tutor/*`** — M, 1-2j
7. **Préparer protocole Phase 4 MAINTENANT** — L, 1 sem + 4 sem
8. **Déduplifier `update_mastery` / `generate_learning_path`** → `services/mastery_service.py` — M, 4-6h
9. **5 ADRs clés** — M, 1j

### 🟡 P2

10. Isoler prompts LLM + timeout SymPy — M, 4h

---

## 11. Verdict senior global

**Note : 14,5 / 20.**

**Très bien placé pour la soutenance.** Projet ambitieux, périmètre cohérent avec la proposition PFE, architecture saine, ~25 000 lignes utiles, CI verte, réellement fonctionnel.

### Ce qui distingue ce projet de 90% des PFE

1. **Validation SymPy ÉTENDUE** (équations, dérivées, intégrales) avec 17 tests — angle scientifique original, défendable IEEE.
2. **GraphRAG GENUINELY backed** par Neo4j avec REQUIRES cross-module testés.
3. **Banque bilingue 105 questions** hand-curated.
4. **Double mode adaptive/practice** pédagogiquement pensé.
5. **19 animations Manim + 19 widgets JSXGraph**, pas du PowerPoint.

### Ce qui empêche le 18/20

1. Audit interne d'il y a 3 semaines avait déjà identifié rate-limit + tests tuteur, toujours pas corrigés. Manque de priorisation des risques.
2. Duplication (mastery, learning_path).
3. Frontend vanilla limite la lisibilité.
4. **Phase 4 sans amorçage à 12 semaines de la fin**.

### Recommandation immédiate

S'attaquer aux **4 actions P0** (4-6h total). Ça transforme un projet "joli mais brittle en démo" en projet "solide et présentable".

---

**Auditeur :** Senior Software Engineer (20 ans XP)
**Date :** 12 mai 2026
**Référence :** PFE Adaptive Learning Platform — ESPRIT 2025-2026
