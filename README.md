# Intelligent Adaptive Learning Platform

Plateforme d'apprentissage adaptatif pour l'analyse numerique et le calcul scientifique.

Le projet combine un backend FastAPI, une SPA TypeScript/Vite, PostgreSQL pour les donnees applicatives, Neo4j pour le graphe de connaissances, et un tuteur IA local via Ollama/LangChain.

## Stack

| Zone | Technologies |
| --- | --- |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Frontend | TypeScript, Vite |
| Donnees | PostgreSQL, Neo4j |
| IA | LangChain, Ollama, GraphRAG |
| Maths | NumPy, SciPy, SymPy, MathJax/KaTeX |
| Dev | Docker Compose, Ruff, Pytest |

## Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- core/        # configuration, database, security, migrations legeres
|   |   |-- data/        # banques de questions et donnees statiques
|   |   |-- graph/       # connexion Neo4j
|   |   |-- models/      # modeles SQLAlchemy
|   |   |-- routers/     # routes FastAPI par domaine
|   |   |-- schemas/     # schemas Pydantic
|   |   `-- services/    # logique metier, RAG, quiz, feedback, verification
|   |-- scripts/         # scripts de seed/export
|   `-- tests/           # tests backend
|-- frontend/
|   |-- src/
|   |   |-- components/  # composants UI reutilisables
|   |   |-- design/      # tokens visuels
|   |   |-- pages/       # pages/routes SPA
|   |   |-- utils/       # helpers frontend
|   |   |-- api.ts       # client API type
|   |   `-- router.ts    # routeur SPA
|   `-- vite.config.ts
|-- docker/              # orchestration locale
|-- docs/                # audit, UML, documentation technique
|-- scripts/             # scripts transverses
|-- Module de Math/      # corpus et artefacts locaux non versionnes
`-- rapport/             # livrables documentaires non versionnes
```

## Lancement

Backend:

```powershell
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Build frontend:

```powershell
cd frontend
npm run build
```

## Hygiene du depot

Les environnements virtuels, builds, caches, rapports, corpus volumineux et modeles locaux sont ignores par Git. Le code applicatif versionnable doit rester dans `backend/app`, `backend/tests`, `frontend/src`, `docs`, `docker` et `scripts`.
