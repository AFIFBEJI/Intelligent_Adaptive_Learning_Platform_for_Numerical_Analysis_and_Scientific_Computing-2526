# Guide du projet — Pour débutant

Ce guide t'explique **chaque fichier** de ton projet en mots simples. Si un mot technique apparaît, il est expliqué juste après.

---

## 1. C'est quoi ce projet ?

Une **plateforme d'apprentissage adaptatif** pour l'analyse numérique. L'idée : un étudiant apprend les maths assisté par une IA qui s'adapte à son niveau (débutant, intermédiaire, avancé). Il y a :

- des **cours** (3 niveaux de difficulté pour chaque concept)
- des **quiz** générés automatiquement
- un **tuteur IA** qui répond aux questions
- un **graphe de connaissances** qui sait quels concepts dépendent de quels autres

> **Mot technique : graphe de connaissances** = une carte qui dit « pour comprendre X il faut d'abord comprendre Y ». Comme un arbre généalogique mais pour des notions de cours.

---

## 2. Architecture en 3 morceaux

Ton projet a **3 grandes parties** qui communiquent ensemble :

```
[ FRONTEND ]  <-- ce que l'utilisateur voit (boutons, pages)
     |
     | (envoie des requêtes HTTP)
     v
[ BACKEND  ]  <-- le cerveau (Python, FastAPI)
     |
     v
[ BASES DE DONNÉES ]  <-- où les choses sont stockées
   - PostgreSQL : utilisateurs, scores, sessions de chat
   - Neo4j      : concepts, modules, dépendances
```

> **Frontend** = la partie visible dans le navigateur. Site web.  
> **Backend** = le serveur qui répond aux questions du frontend.  
> **HTTP** = le langage que le frontend et le backend utilisent pour se parler (GET, POST, etc.).  
> **PostgreSQL** = base de données classique en tableaux (lignes/colonnes).  
> **Neo4j** = base de données en graphe (nœuds reliés par des flèches).

---

## 3. Le BACKEND — dossier `backend/`

Le backend est écrit en **Python** avec le framework **FastAPI**.

> **Python** = langage de programmation.  
> **Framework** = boîte à outils. **FastAPI** est une boîte à outils pour créer une API web rapidement.  
> **API** = ensemble d'URLs auxquelles le frontend peut envoyer des requêtes pour obtenir/modifier des données. Ex: `POST /auth/login` envoie un email+mdp et reçoit un token.

### `backend/app/main.py` — le démarreur

C'est le **point d'entrée**. Quand tu lances `uvicorn app.main:app`, ce fichier se lance en premier. Il :

1. Crée l'application FastAPI
2. Crée les tables PostgreSQL si elles n'existent pas
3. Configure les CORS (autorise le frontend à appeler l'API depuis localhost:5173 et 4200)
4. Branche tous les **routers** (auth, etudiants, graph, quiz, quiz_dynamic, tutor)

> **Router** = un fichier qui regroupe des URLs reliées (ex: tout ce qui touche à l'auth).  
> **CORS** = règle de sécurité du navigateur : par défaut, ton frontend ne peut pas appeler une API d'un autre domaine. CORS dit « OK, j'autorise ce domaine ».

### `backend/app/core/` — les outils centraux

Tous les fichiers **utilitaires** que les autres parties du backend utilisent.

**`config.py`** — Lit le fichier `.env` et expose les paramètres : URL de la base, mot de passe Neo4j, clé secrète JWT, modèle Ollama, etc. Si tu veux ajouter une nouvelle variable d'environnement, c'est ici.

**`database.py`** — Crée la connexion à PostgreSQL. Définit `get_db()` qui ouvre une session de base de données pour chaque requête HTTP.

> **Session de base de données** = un « tunnel » temporaire vers la base, ouvert le temps d'une requête, fermé après.

**`migrations.py`** — Si tu ajoutes une nouvelle colonne dans un modèle, ce fichier ajoute cette colonne à la table existante sans tout casser. Au démarrage, `ensure_columns()` vérifie que toutes les colonnes existent.

> **Migration** = mise à jour de la structure d'une base de données (ajouter/renommer/supprimer une colonne) sans perdre les données.

**`security.py`** — Gère les **JWT** (JSON Web Tokens) et le hash des mots de passe.

> **JWT** = un long texte qui prouve que tu es connecté. Quand tu te connectes, le serveur te donne un JWT. À chaque requête suivante, le frontend renvoie ce JWT pour dire « regarde, je suis bien Eya ».  
> **Hash** = transformation à sens unique d'un mot de passe. On stocke `hash("mot_de_passe")` au lieu du mot de passe lui-même. Si la base est volée, les vrais mots de passe restent secrets.  
> **bcrypt** = algorithme de hash spécifiquement fait pour les mots de passe (lent exprès pour bloquer les attaques par force brute).

**`i18n.py`** (que j'ai créé) — Messages d'erreur HTTP traduits FR/EN. Si tu veux ajouter un nouveau message d'erreur traduit, ajoute une clé dans le dictionnaire `MESSAGES`.

> **i18n** = abréviation de « internationalization » (i + 18 lettres + n). Système de traduction.

### `backend/app/models/` — les tables de PostgreSQL

Chaque fichier décrit **une table** dans la base. Si tu veux ajouter une nouvelle table (ex: « notifications »), tu crées un nouveau fichier ici.

> **Modèle** (en SQLAlchemy) = classe Python qui correspond à une table. Une instance = une ligne. Manipuler des objets Python = écrire dans la table.  
> **SQLAlchemy** = bibliothèque Python qui traduit ton code Python en requêtes SQL automatiquement.

**`etudiant.py`** — Table `etudiants`. Colonnes : id, nom_complet, email, mot_de_passe (hashé), niveau_actuel (beginner/intermediate/advanced), langue_preferee (fr/en), is_active.

**`mastery.py`** — Table `concept_mastery`. Stocke « l'étudiant X a Y% de maîtrise sur le concept Z ». Colonnes : etudiant_id, concept_neo4j_id, niveau_maitrise (0-100), derniere_mise_a_jour. Une ligne par paire (étudiant, concept).

**`quiz.py`** — Deux tables :
- `quiz` : un quiz généré (titre, module, difficulté, questions en JSON, source = "static" ou "generated")
- `quiz_resultats` : une tentative d'un étudiant (score, temps, réponses, evaluation_detaillee, feedback_card)

**`tutor.py`** — Deux tables :
- `tutor_sessions` : une session de chat avec le tuteur IA
- `tutor_messages` : chaque message de la session (role = "student" ou "tutor", verified = true/false par SymPy)

### `backend/app/schemas/` — les contrats de l'API

Les **schemas Pydantic** disent « si quelqu'un envoie ça à mon API, voici la forme attendue ». Si la forme est mauvaise, l'API renvoie une erreur 422 automatiquement.

> **Pydantic** = bibliothèque qui valide les données entrantes/sortantes (« le champ email doit être un email », « le champ score doit être un nombre entre 0 et 100 »).  
> **Schema** = description de la forme attendue. Différent du « modèle » (qui est une table de base) : un schema ne touche pas à la base, il valide juste le format.

**`etudiant.py`** : `EtudiantCreate` (pour register), `EtudiantResponse` (ce qu'on renvoie au frontend), `EtudiantUpdate` (pour modifier), `EtudiantLanguageUpdate`, `Token`.

**`quiz.py`** et **`quiz_dynamic.py`** : formats des questions, des soumissions, des résultats, de la feedback card.

**`tutor.py`** : formats pour les sessions et les messages du tuteur.

### `backend/app/routers/` — les URLs de l'API

Chaque fichier regroupe les URLs liées à un domaine. C'est ici que tu ajoutes un nouveau endpoint.

> **Endpoint** = une URL spécifique de l'API avec une méthode (GET/POST/PUT/DELETE) et un comportement.

**`auth.py`** — 4 endpoints :
- `POST /auth/register` : créer un compte
- `POST /auth/login` : se connecter
- `GET /auth/me` : obtenir le profil de l'utilisateur connecté
- `PUT /auth/me/language` : changer la langue préférée

**`etudiants.py`** — 4 endpoints CRUD pour les étudiants (un étudiant ne peut modifier que son propre profil).

> **CRUD** = Create, Read, Update, Delete (créer, lire, modifier, supprimer). Les 4 actions de base sur des données.

**`graph.py`** — 10 endpoints qui interrogent **Neo4j** : modules, concepts, prérequis, ressources, contenu, learning-path, remediation, stats. Tous acceptent `?lang=en` ou `?lang=fr`.

**`quiz.py`** — Quiz **statiques** (pré-définis) : créer, lister, soumettre, voir les résultats.

**`quiz_dynamic.py`** — Quiz **adaptatifs** générés par l'IA :
- `POST /quiz-ai/generate` : génère un quiz sur mesure
- `POST /quiz-ai/{id}/submit` : soumet les réponses, reçoit la feedback card
- `POST /quiz-ai/diagnostic` : quiz initial pour calibrer le niveau
- `GET /quiz-ai/attempts/list` : historique des tentatives
- `GET /quiz-ai/attempts/{id}` : détail d'une tentative

**`tutor.py`** — Tuteur IA :
- `POST /tutor/sessions` : créer une session
- `GET /tutor/sessions` : lister mes sessions
- `POST /tutor/sessions/{id}/ask` : poser une question
- `GET /tutor/sessions/{id}/history` : historique d'une session

### `backend/app/services/` — la logique métier

Les routers délèguent le travail compliqué aux **services**. C'est ici que se trouve la vraie intelligence du backend.

> **Service** = une classe ou un module qui fait UN travail bien défini. Avantage : si le travail change, tu modifies un seul endroit.  
> **Logique métier** = la logique propre à ton application (« comment calculer la maîtrise d'un étudiant », « comment construire un prompt IA ») par opposition à la logique technique (HTTP, base de données).

**`llm_service.py`** — Parle à **Ollama** (le serveur local qui héberge Gemma).

> **LLM** = Large Language Model. Une IA qui comprend et génère du texte (comme ChatGPT mais en local).  
> **Ollama** = un programme local qui fait tourner des LLM sur ton ordinateur. Pas besoin d'internet ni d'API payante.  
> **Gemma** = la famille de modèles de Google, dont Gemma-Numerical-E2B (4B paramètres, fine-tuné sur 144 exemples bilingues d'analyse numérique).  
> **Fine-tuner** = entraîner davantage un modèle existant sur tes propres données pour qu'il soit meilleur sur ton domaine spécifique.

Ce service fait : `wrap_with_bilingual_tags()` qui préfixe chaque question avec `[level: beginner|intermediate|advanced] [lang: en|fr]`. Le modèle a été entraîné à reconnaître ces tags pour adapter sa réponse.

**`rag_service.py`** — Le **RAG** (Retrieval-Augmented Generation).

> **RAG** = avant de poser une question à l'IA, on lui donne du contexte pertinent (les prérequis du concept, le niveau de l'étudiant, les ressources disponibles). Ça évite que l'IA invente des choses.

Méthodes : `find_concept` (trouve le concept à partir des mots de la question), `get_prerequisites` (remonte l'arbre des prérequis dans Neo4j), `get_resources`, `build_context` (assemble tout dans un objet `ConceptContext`).

**`verification_service.py`** — Vérifie les **maths** avec **SymPy**.

> **SymPy** = bibliothèque Python qui comprend les maths symboliquement (pas juste des nombres : des `x`, des intégrales, etc.). Elle peut dire si `(x+1)² = x² + 2x + 1` est vrai.

Méthodes : `extract_latex` (extrait `$...$` et `$$...$$`), `verify_expression` (la formule est-elle valide ?), `verify_equivalence` (deux formules sont-elles équivalentes ?).

> **LaTeX** = langage pour écrire des formules mathématiques. Ex: `\frac{a}{b}` produit une fraction.

**`quiz_service.py`** — Génère un quiz adaptatif. Calcule la difficulté selon la maîtrise (< 30 → facile, < 70 → moyen, sinon difficile). Construit le prompt LLM. Parse la réponse JSON.

**`feedback_service.py`** — Évalue les réponses d'un quiz (déterministe pour QCM/Vrai-Faux, LLM pour les questions ouvertes) et génère la **feedback card** (carte de retour pédagogique).

**`quiz_localization.py`** — Service de traduction pour les questions de quiz. Si le dict question a `question_en`, l'utilise prioritairement. Sinon, fallback sur la fonction `translate_fr_to_en` (regex de 350+ correspondances). Maintenant que toutes les questions ont des champs `_en`, la traduction est de qualité humaine.

**`graph_service.py`** — Service utilitaire pour Neo4j (peut être vide ou minimal selon les versions).

### `backend/app/graph/neo4j_connection.py` — connecteur Neo4j

Singleton qui crée UNE connexion à Neo4j et la réutilise. Méthodes : `run_query` (lecture), `run_write_query` (écriture).

> **Singleton** = une classe qui n'a qu'une seule instance dans tout le programme. Évite d'ouvrir 1000 connexions à la base.

### `backend/app/data/` — banques de questions

**`quiz_question_bank.py`** — 75 questions (15 concepts × 5) avec champs FR + EN.

**`diagnostic_questions.py`** — 30 questions (15 concepts × 2) pour le quiz initial. Aussi bilingues.

Si tu veux ajouter des questions, c'est ici.

### `backend/scripts/` — scripts de seed

> **Seed** (« graine ») = remplir une base vide avec des données initiales. À lancer une seule fois après installation.

**`seed_neo4j.py`** — Crée les 3 modules, 15 concepts, 8 ressources et 37 relations dans Neo4j. Tous bilingues (`name`, `name_fr`).

**`seed_content.py`** — Crée le contenu des cours pour modules 1+2 en anglais (`title_en`, `body_en`).

**`seed_content_modules1_2_fr.py`** (que j'ai créé) — Ajoute la version française pour modules 1+2 (`title_fr`, `body_fr`).

**`seed_content_approximation.py`** — Contenu module 3 en français.

**`seed_content_approximation_en.py`** (que j'ai créé) — Contenu module 3 en anglais.

**`seed_quizzes.py`** — Quiz statiques pré-définis dans PostgreSQL (utilisé par `/quiz` classique, pas `/quiz-ai`).

### `backend/tests/` — tests automatisés

**`test_seed_integrity.py`** — Vérifie que le seed Neo4j a bien créé 3 modules, 15 concepts, 8 ressources, 37 relations. Lancé par la CI GitHub.

> **Test** = un programme qui vérifie automatiquement qu'une autre partie du code marche. Si les tests passent en vert, c'est rassurant.  
> **CI** = Continuous Integration. À chaque push sur GitHub, la CI lance les tests automatiquement.

### Fichiers de config backend

**`pyproject.toml`** — Config Ruff (linter Python) et Pytest. Définit les règles de style.

> **Linter** = un outil qui vérifie que ton code suit les bonnes pratiques (lignes pas trop longues, pas d'imports inutiles…).

**`requirements.txt`** — Liste des bibliothèques Python à installer (`fastapi`, `sqlalchemy`, `neo4j`, `langchain`, `sympy`, etc.). Lancé par `pip install -r requirements.txt`.

**`requirements-dev.txt`** — Bibliothèques de développement seulement (`pytest`, `ruff`).

---

## 4. Le FRONTEND — dossier `frontend/`

Écrit en **TypeScript** sans framework lourd. Bundlé avec **Vite**.

> **TypeScript** = JavaScript + types. Tu déclares qu'une variable est un nombre ou une chaîne, et le compilateur te crie dessus si tu fais une erreur.  
> **Bundler** = un outil qui prend tes 50 fichiers `.ts` et les fusionne en un ou deux gros fichiers `.js` chargeables par le navigateur. **Vite** est un bundler rapide.

### `frontend/index.html` — la page de base

Une coquille vide avec `<div id="app"></div>`. Le JS injecte tout le contenu dans cette div.

### `frontend/vite.config.ts` — config du bundler

Définit le port (4200), le proxy (`/api/*` est redirigé vers `http://localhost:8000/*`), et le dossier de build (`dist`).

> **Proxy** = quand le frontend appelle `/api/auth/login`, Vite redirige automatiquement vers le backend `localhost:8000/auth/login`. Ça évite les problèmes CORS en dev.

### `frontend/tsconfig.json` — config TypeScript

Définit le mode strict, la version de JS cible (ES2020), etc.

### `frontend/package.json` — dépendances frontend

Très minimaliste : seulement `typescript` et `vite`. Pas de React, Vue, etc. Tout le DOM est manipulé à la main.

> **DOM** = Document Object Model, l'arbre HTML que le navigateur affiche. « Manipuler le DOM » = ajouter/modifier/supprimer des éléments HTML par JavaScript.

### `frontend/src/main.ts` — point d'entrée frontend

L'équivalent de `main.py` côté backend. Il :
1. Applique les design tokens (couleurs, espacements)
2. Lit la langue stockée
3. Restaure le JWT depuis localStorage
4. Enregistre toutes les routes
5. Démarre le routeur

### `frontend/src/router.ts` — routeur SPA

> **SPA** = Single Page Application. Une seule page HTML, le contenu change en JavaScript sans recharger la page entière.

Gère la navigation entre les pages. Garde-fous :
- Si une route est protégée et qu'il n'y a pas de JWT → redirige vers `/login`
- Si pas de langue choisie → redirige vers `/login`
- Clic sur `<a data-link>` → navigation sans reload

### `frontend/src/api.ts` — client API typé

Toutes les méthodes pour parler au backend (login, register, getMe, generateAiQuiz, askTutor, etc.). Ajoute automatiquement le JWT en header. Si une réponse est 401 (non autorisé), efface le token et redirige vers /login.

> **Header HTTP** = des « étiquettes » qu'on peut attacher à chaque requête. Le header `Authorization: Bearer <jwt>` dit au backend qui tu es.

### `frontend/src/i18n.ts` — système de traduction

Dictionnaire de ~370 clés FR/EN. Fonctions exportées :
- `t('key')` : retourne la traduction
- `getLang()`, `setLang()`, `hasChosenLang()`, `clearLang()`
- `tLevel(level)` : traduit beginner/intermediate/advanced
- `formatDateTime()` : formate une date selon la langue

Si tu veux ajouter une page avec du texte, ajoute les clés dans le `DICT` et utilise `t('ma.cle')`.

### `frontend/src/design/tokens.ts` — design system

Définit toutes les **variables CSS** (couleurs, espacements, typo) injectées dans la page. Si tu veux changer la palette, c'est ici. Définit aussi les classes CSS réutilisables (`.ds-btn`, `.ds-card`, `.ds-input`, etc.).

> **Variable CSS** = `--brand-300: #38bdf8;`. Tu peux ensuite faire `color: var(--brand-300);` partout.

### `frontend/src/utils/latex.ts` — rendu LaTeX

Charge **KaTeX** (rendu maths) depuis un CDN à la demande, et fournit `renderMathIn(element)` qui transforme les `$...$` en formules visuelles.

> **KaTeX** = bibliothèque qui transforme `\frac{a}{b}` en jolie fraction.  
> **CDN** = serveur public qui héberge des fichiers JavaScript. Pas besoin de les télécharger soi-même.

### `frontend/src/components/` — composants réutilisables

**`app-shell.ts`** — La **coquille** de l'app : sidebar à gauche, topbar en haut. Toutes les pages connectées sont enveloppées dans ce shell. Contient le sélecteur de langue (en bas de la sidebar) et le bouton de déconnexion.

**`navbar.ts`, `sidebar.ts`** — Versions simplifiées (utilisées dans certains layouts).

**`particles.ts`** — Animation de particules en fond (effet visuel).

**`tilt.ts`** — Effet 3D de basculement sur la souris.

### `frontend/src/pages/` — les pages

Chaque fichier exporte une fonction qui retourne un `HTMLElement`. Le routeur appelle cette fonction quand l'utilisateur navigue vers la route.

**`home.ts`** (`/`) — Page d'accueil publique. Présente les fonctionnalités. Boutons « Sign in » et « Create account ».

**`login.ts`** (`/login`) — Connexion. **Choix de langue obligatoire** (bouton désactivé tant que rien n'est sélectionné). Au submit : appelle `POST /auth/login`, stocke le JWT, met à jour la langue côté backend.

**`register.ts`** (`/register`) — Inscription. Idem, choix de langue obligatoire. Le backend refuse une inscription sans `langue_preferee`.

**`dashboard.ts`** (`/dashboard`) — La page d'accueil après connexion. Affiche : « Bonjour, X », niveau de maîtrise globale, concepts à réviser en priorité, prochaines étapes, quick actions (quiz, tuteur).

**`concepts.ts`** (`/concepts`) — Carte des 15 concepts groupés par module avec filtre par catégorie.

**`content.ts`** (`/content`) — Cours par concept. Pour chaque concept, 3 niveaux (simplifié, standard, rigoureux). Le concept et le niveau sont stockés dans l'URL (`?concept=...&level=...`) pour persister au changement de langue.

**`learning-path.ts`** (`/path`) — Progression globale. Concepts maîtrisés, en cours, à découvrir.

**`onboarding-quiz.ts`** (`/onboarding-quiz`) — Quiz diagnostique au premier login. 5 questions pour estimer le niveau initial.

**`quiz-ai.ts`** (`/quiz-ai`) — Quiz adaptatif. Setup (choisir concept, difficulté, types) → génération via API → résolution → feedback card avec score, points forts, erreurs détaillées, prochaines étapes.

**`quiz.ts`** (`/quiz`) — Alias vers `quiz-ai.ts` pour compatibilité.

**`tutor.ts`** (`/tutor`) — Chat avec l'IA. Multi-sessions à gauche, chat à droite. Rendu LaTeX. Badge de vérification SymPy. Niveau adaptatif (simplifié/standard/rigoureux) selon la maîtrise. La session est stockée dans l'URL (`?session=...`).

---

## 5. Infrastructure

### `docker/docker-compose.yml`

> **Docker** = un programme qui fait tourner des « conteneurs » (mini-serveurs isolés). **Docker Compose** lance plusieurs conteneurs ensemble.

Lance 2 conteneurs :
- **neo4j** sur les ports 7475 (interface web) et 7687 (Bolt, le protocole de Neo4j)
- **postgres** sur le port 5433 (5432 dans le conteneur, mappé vers 5433 sur ta machine pour ne pas entrer en conflit avec un éventuel Postgres local)

Pour les démarrer : `docker compose -f docker/docker-compose.yml up -d`.

### `.github/workflows/ci.yml`

> **GitHub Actions** = à chaque push sur GitHub, GitHub lance automatiquement des scripts (tests, lint, build).

5 jobs en parallèle :
1. **backend-lint** : Ruff vérifie le style Python
2. **backend-smoke** : importe `app.main` pour vérifier qu'il n'y a pas d'erreur de syntaxe
3. **frontend-build** : `npm run build` (TypeScript + Vite)
4. **graph-integrity** : démarre Neo4j, lance `seed_neo4j.py`, vérifie 3 modules / 15 concepts / 8 ressources / 37 relations
5. **docker-validate** : valide la syntaxe de `docker-compose.yml`

### `scripts/generate_uml.py`

Génère 5 diagrammes **UML** dans `docs/uml/` à partir du code. Use case, classes, séquence (login + quiz), déploiement.

> **UML** = Unified Modeling Language. Diagrammes pour décrire visuellement un logiciel.

### `.env`

Fichier secret à ne JAMAIS commiter sur GitHub. Contient : `DATABASE_URL`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `SECRET_KEY` (pour signer les JWT), `OLLAMA_BASE_URL`, etc.

### `.gitignore`

Liste des fichiers à ne pas commiter sur Git (venv, node_modules, .env, dist, etc.).

---

## 6. Documentation

**`README.md`** — Présentation rapide du projet, comment lancer.

**`research_state_of_art.md`** — Revue de littérature sur les plateformes d'apprentissage adaptatif. Justifie les choix architecturaux (knowledge graph, neuro-symbolic, etc.).

**`docs/PROJECT_PLAN.md`** — Roadmap en 4 phases.

**`docs/PHASE2_AUDIT_22avril2026.md`** — Audit intermédiaire de la Phase 2.

**`docs/uml/`** — 5 diagrammes UML générés par `scripts/generate_uml.py`.

**`literature_review_intelligent_adaptive_learning_platforms.pdf`** — Document de littérature long format.

**`LICENSE`** — MIT 2026 © Afif Beji.

---

## 7. Ressources hors-versionning

**`Module de Math/`** — Corpus pour le fine-tuning de Gemma : PDFs, datasets bilingues, llama.cpp workdir, animations Manim. Pas dans Git (gros fichiers).

**`venv_finetune/`** — Environnement Python pour entraîner Gemma. Pas dans Git.

**`rapport/`** — Livrables Word : rapports Phase 1/3, justification des hyperparamètres LLM, roadmap Phase 2. Pas dans Git.

---

## 8. Glossaire des termes techniques

| Terme | Définition simple |
|---|---|
| **API** | URLs auxquelles on envoie des requêtes pour obtenir/modifier des données |
| **Backend** | Le serveur qui répond aux requêtes |
| **Bcrypt** | Algorithme spécialisé pour hasher les mots de passe |
| **Bundler** | Outil qui fusionne plusieurs fichiers JS en un seul (Vite) |
| **CDN** | Serveur public qui héberge des fichiers (KaTeX, MathJax) |
| **CI** | Tests automatiques lancés à chaque push sur GitHub |
| **CORS** | Règle de sécurité du navigateur pour les appels d'API |
| **CRUD** | Create / Read / Update / Delete (les 4 actions de base) |
| **Cypher** | Langage de requête de Neo4j (équivalent du SQL pour graphes) |
| **Docker** | Conteneurs isolés (Postgres + Neo4j tournent là-dedans) |
| **DOM** | Arbre HTML manipulable par JavaScript |
| **Endpoint** | Une URL spécifique de l'API |
| **FastAPI** | Framework Python pour créer une API |
| **Fine-tuning** | Entraîner un modèle existant sur tes propres données |
| **Frontend** | Le site web côté navigateur |
| **Framework** | Boîte à outils pour construire un type d'application |
| **Hash** | Transformation à sens unique d'un texte (utilisé pour les mots de passe) |
| **HTTP** | Protocole utilisé pour les requêtes entre frontend et backend |
| **i18n** | Internationalization (traduction multi-langue) |
| **JSON** | Format texte pour structurer des données : `{"name": "Eya", "age": 22}` |
| **JWT** | Token qui prouve qui tu es après connexion |
| **KaTeX** | Bibliothèque qui rend le LaTeX en formules visuelles |
| **LangChain** | Bibliothèque qui orchestre les appels à un LLM |
| **LaTeX** | Langage pour écrire des formules maths |
| **Linter** | Outil qui vérifie le style du code (Ruff, ESLint) |
| **LLM** | Large Language Model (IA qui comprend/génère du texte) |
| **Migration** | Mise à jour de la structure d'une base de données |
| **Neo4j** | Base de données en graphe (nœuds + relations) |
| **Ollama** | Programme local qui fait tourner des LLM sur ta machine |
| **ORM** | Object-Relational Mapping. Manipuler une base avec des objets Python (SQLAlchemy) |
| **PostgreSQL** | Base de données SQL classique (lignes/colonnes) |
| **Pydantic** | Bibliothèque Python qui valide les données |
| **Python** | Langage de programmation utilisé pour le backend |
| **RAG** | Retrieval-Augmented Generation. Donner du contexte à l'IA avant qu'elle réponde |
| **Router** | Fichier qui regroupe des URLs liées |
| **Schema** | Description de la forme attendue de données (Pydantic) |
| **Seed** | Remplir une base vide avec des données initiales |
| **Service** | Module Python qui fait UNE tâche spécifique |
| **Singleton** | Classe qui n'a qu'une seule instance dans tout le programme |
| **SPA** | Single Page Application. Site qui se charge une fois et change de contenu en JS |
| **SQLAlchemy** | ORM Python pour PostgreSQL |
| **SymPy** | Bibliothèque Python qui comprend les maths symboliquement |
| **Token** | Texte qui prouve l'identité (JWT) |
| **TypeScript** | JavaScript + types |
| **UML** | Diagrammes pour décrire un logiciel visuellement |
| **Uvicorn** | Serveur qui fait tourner FastAPI |
| **Variable d'environnement** | Paramètre lu depuis `.env` (mots de passe, URLs) |
| **Vite** | Bundler frontend rapide |

---

## 9. Comment ajouter une nouvelle fonctionnalité ?

Si tu veux ajouter une nouvelle fonctionnalité, voici la **checklist** typique :

### Cas 1 : Nouvelle page frontend uniquement (pas de nouvelles données)

1. Créer `frontend/src/pages/ma-page.ts` (copier une page existante simple)
2. Ajouter les clés de traduction dans `frontend/src/i18n.ts`
3. Enregistrer la route dans `frontend/src/main.ts` : `router.addRoute('/ma-page', MaPage, true)`
4. Ajouter un lien dans la sidebar (`frontend/src/components/app-shell.ts`)

### Cas 2 : Nouvelle table en base de données

1. Créer `backend/app/models/mon_modele.py` (copier `etudiant.py`)
2. Créer `backend/app/schemas/mon_modele.py` pour les schemas Pydantic
3. Au prochain démarrage, `create_tables()` créera la table automatiquement
4. Si tu modifies un modèle existant (ajouter une colonne), penser à `migrations.py`

### Cas 3 : Nouvel endpoint API

1. Créer ou éditer un router dans `backend/app/routers/`
2. Si la logique est complexe, créer un service dans `backend/app/services/`
3. Ajouter le router dans `backend/app/main.py` si c'est nouveau (`app.include_router(...)`)
4. Côté frontend, ajouter une méthode dans `frontend/src/api.ts`
5. Appeler cette méthode depuis une page

### Cas 4 : Nouveau concept dans le graphe

1. Ajouter le concept dans `backend/scripts/seed_neo4j.py` (avec `name_fr` et `description_fr`)
2. Ajouter les relations REQUIRES, COVERS, REMEDIATES_TO appropriées
3. Ajouter le contenu de cours dans les seeds appropriés (`seed_content.py` pour EN, `seed_content_modules1_2_fr.py` pour FR si module 1+2)
4. Ajouter des questions de quiz dans `backend/app/data/quiz_question_bank.py` (avec champs `_en`)
5. Ajouter 2 questions diagnostiques dans `backend/app/data/diagnostic_questions.py`
6. Re-seeder Neo4j (lancer les 5 scripts dans l'ordre)
7. Mettre à jour `_MODULE_ORDER_CASE` dans `graph.py` si c'est un nouveau module

### Cas 5 : Nouvelle langue (par exemple arabe)

C'est un gros chantier. En gros :
1. Ajouter `'ar'` dans `SUPPORTED_LANGS` du i18n frontend
2. Ajouter une 3ème valeur dans toutes les ~370 clés du `DICT`
3. Étendre `Langue = Literal["en", "fr"]` dans `backend/app/schemas/etudiant.py` à `Literal["en", "fr", "ar"]`
4. Ajouter `name_ar` / `description_ar` dans tous les modèles Neo4j
5. Étendre tous les `coalesce` SQL/Cypher
6. Pour l'arabe : gérer le **RTL** (right-to-left) dans le CSS
7. Fine-tuner le LLM sur des exemples arabes ou utiliser un LLM multilingue

> **RTL** = Right-To-Left. L'arabe et l'hébreu s'écrivent de droite à gauche, ce qui demande de basculer toute la mise en page.

---

## 10. Comment lancer le projet en local ?

```powershell
# 1. Démarrer Postgres + Neo4j
cd C:\Users\GIGABYTE\Desktop\Intelligent_Adaptive_Learning_Platform_for_Numerical_Analysis_and_Scientific_Computing-2526
docker compose -f docker/docker-compose.yml up -d

# 2. Backend
cd backend
.\venv\Scripts\Activate.ps1            # active le venv
pip install -r requirements.txt        # première fois seulement
uvicorn app.main:app --reload          # démarre l'API sur localhost:8000

# 3. Frontend (dans un autre terminal)
cd frontend
npm install                            # première fois seulement
npm run dev                            # démarre Vite sur localhost:4200

# 4. Ollama (dans un autre terminal)
ollama serve                           # démarre Ollama
ollama run gemma-numerical-e2b         # première fois pour télécharger le modèle

# 5. Naviguer vers http://localhost:4200
```

Si c'est la première fois, il faut d'abord seeder les bases :

```powershell
cd backend
.\venv\Scripts\python.exe scripts/seed_neo4j.py
.\venv\Scripts\python.exe scripts/seed_content.py
.\venv\Scripts\python.exe scripts/seed_content_modules1_2_fr.py
.\venv\Scripts\python.exe scripts/seed_content_approximation.py
.\venv\Scripts\python.exe scripts/seed_content_approximation_en.py
```

---

Voilà ! Tu as maintenant une vue d'ensemble claire de chaque morceau. Si tu veux creuser un fichier en particulier, demande-moi.
