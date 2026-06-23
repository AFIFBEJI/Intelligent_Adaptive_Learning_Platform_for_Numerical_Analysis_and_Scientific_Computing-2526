# Adaptive Learning Platform — Stack Docker

Containerisation complete : Postgres + Neo4j + Backend FastAPI + Frontend nginx.
Lance toute la plateforme avec **une seule commande**.

## Demarrage rapide

```bash
# 1. Cree ton fichier .env a la racine du projet (une seule fois)
cp .env.example .env
# Puis edite .env : OPENAI_API_KEY, SECRET_KEY (en prod), etc.

# 2. Build + lance les 4 services
cd docker
docker compose up --build
```

A l'ouverture des connexions :

| Service     | URL                          | Usage                                       |
|-------------|------------------------------|---------------------------------------------|
| Frontend    | http://localhost:8080        | SPA (login, dashboard, tuteur, ...)         |
| API docs    | http://localhost:8000/docs   | Swagger UI FastAPI                          |
| API health  | http://localhost:8000/health | Status JSON (provider LLM, version, etc.)  |
| Neo4j UI    | http://localhost:7475        | Browser Neo4j (auth: voir .env)             |
| Postgres    | localhost:5433               | psql / DBeaver (auth: voir .env)            |

## Premier demarrage : seed des donnees

Au premier `up`, les bases sont vides. Il faut peupler Neo4j et le contenu :

```bash
# 1. Seed du graphe de connaissances (concepts, prerequis, ressources)
docker compose exec backend python scripts/seed_neo4j.py

# 2. Seed du contenu pedagogique bilingue (FR+EN, 4 modules)
docker compose exec backend python scripts/seed_content_modules1_2_fr.py
docker compose exec backend python scripts/seed_content_module4_fr.py
docker compose exec backend python scripts/seed_content_module4_en.py
docker compose exec backend python scripts/seed_content_approximation_en.py

# 3. (optionnel) Verifier l'integrite
docker compose exec backend pytest tests/test_seed_integrity.py
```

## Commandes utiles

```bash
# Voir les logs en temps reel
docker compose logs -f backend
docker compose logs -f frontend

# Redemarrer un service apres modif du code
docker compose restart backend
docker compose up -d --build backend   # rebuild + restart

# Stop sans perdre les donnees
docker compose down

# Stop + EFFACER les donnees Postgres et Neo4j (reset complet)
docker compose down -v
```

## Architecture

```
                     ┌────────────────────────────────┐
                     │  Navigateur (localhost:8080)   │
                     └──────────────┬─────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────┐
        │  frontend (nginx:alpine)                        │
        │   - sert /usr/share/nginx/html (Vite dist/)     │
        │   - proxy /api/* -> backend:8000/*              │
        └──────────────────┬──────────────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────────────────┐
        │  backend (python:3.11-slim, uvicorn)            │
        │   - FastAPI sur 0.0.0.0:8000                    │
        │   - parle a postgres:5432 et neo4j:7687         │
        │   - parle a Ollama via host.docker.internal     │
        │     (ou a OpenAI selon LLM_PROVIDER)            │
        └────────┬────────────────┬───────────────────────┘
                 │                │
                 ▼                ▼
        ┌──────────────┐   ┌──────────────┐
        │  postgres:15 │   │   neo4j:5    │
        │  volume:     │   │  volume:     │
        │  postgres_   │   │  neo4j_data  │
        │  data        │   │              │
        └──────────────┘   └──────────────┘
```

## Notes

### Ollama (LLM local)

Ollama tourne sur la **machine hote**, pas dans un container :
- L'image fait plusieurs Go, et le modele Gemma fine-tune (~7Go) doit
  rester sur le disque hote pour les performances.
- Le backend joint Ollama via `host.docker.internal:11434` (deja
  configure dans `docker-compose.yml`).
- Sur Linux pur, `host.docker.internal` est resolu via `extra_hosts` +
  `host-gateway` (Docker 20.10+).

Si tu veux faire tourner uniquement avec OpenAI (cloud), mets
`LLM_PROVIDER=openai` dans `.env` et Ollama n'est pas necessaire.

### Volumes persistants

- `adaptive_postgres_data` : donnees Postgres (utilisateurs, quiz, sessions)
- `adaptive_neo4j_data`    : graphe Neo4j (concepts, prerequis)
- `adaptive_neo4j_logs`    : logs Neo4j (debug)

`docker compose down` PRESERVE ces volumes. Pour reset total (re-seed
necessaire) : `docker compose down -v`.

### Healthchecks

Le backend attend que Postgres ET Neo4j soient `healthy` avant de
demarrer (`depends_on.condition: service_healthy`). Le frontend
n'attend que le start du backend (pas son health) — il peut afficher
sa landing page meme si l'API met du temps a se reveiller.

### Environnements separes

Pour dev local hybride (DB en docker, backend/frontend en natif) :

```bash
# Lance uniquement les bases
docker compose up postgres neo4j

# Puis dans deux autres terminaux :
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

Les ports exposes (5433, 7687) sont compatibles avec l'ancien
`docker-compose.yml` : aucun changement de `.env` necessaire.
