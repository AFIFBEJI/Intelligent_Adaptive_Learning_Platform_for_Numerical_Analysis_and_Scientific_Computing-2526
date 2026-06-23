# ============================================================
# Backend Dockerfile — FastAPI + Uvicorn
# ============================================================
# Image legere basee sur Python 3.11-slim.
# Installe les dependances systeme necessaires a psycopg2-binary,
# numpy/scipy, puis les requirements Python, puis le code applicatif.
#
# A construire depuis la racine du projet :
#   docker build -t adaptive-backend -f backend/Dockerfile backend/
# Ou via docker-compose (recommande) :
#   docker compose -f docker/docker-compose.yml up backend
# ============================================================

FROM python:3.11-slim AS base

# Pas de prompt apt, pas de bytecode .pyc, sortie stdout non bufferisee
# (indispensable pour voir les logs FastAPI/Uvicorn en temps reel).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Dependances systeme :
#   - build-essential / gcc : compilation eventuelle de wheels
#   - libpq5 : runtime PostgreSQL (psycopg2-binary l'embarque mais
#     la lib systeme evite les warnings)
#   - curl : pour le HEALTHCHECK
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq5 \
      curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier d'abord les requirements (cache Docker : tant qu'ils ne
# changent pas, l'install pip n'est pas re-jouee a chaque rebuild).
COPY requirements.txt ./
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Copier le code applicatif. Le .dockerignore exclut venv/, __pycache__/,
# tests/, etc. pour garder l'image legere.
COPY app ./app
COPY scripts ./scripts

# Utilisateur non-root (bonne pratique securite : si une vulnerabilite
# permet du RCE, l'attaquant ne sera pas root dans le container).
RUN useradd --create-home --uid 1001 appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthcheck : ping /health toutes les 30s. docker-compose s'en sert
# pour savoir si le service est "healthy" avant de demarrer le frontend.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Lancement : uvicorn ecoute sur 0.0.0.0 (toutes interfaces du
# container) sur le port 8000. PAS de --reload en prod (ralentit + fuite memoire).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
