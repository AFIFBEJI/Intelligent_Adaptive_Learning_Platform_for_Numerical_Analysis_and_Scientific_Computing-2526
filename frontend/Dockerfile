# ============================================================
# Frontend Dockerfile — Vite build + nginx serve
# ============================================================
# Multi-stage build :
#   1. STAGE "build"  : Node 20 alpine, npm ci, npm run build (vite + tsc)
#   2. STAGE "runtime": nginx:alpine sert le dist/ statique et proxy
#                       /api/* vers le container backend.
#
# A construire :
#   docker build -t adaptive-frontend -f frontend/Dockerfile frontend/
# Ou via docker-compose :
#   docker compose -f docker/docker-compose.yml up frontend
# ============================================================

# ---------- STAGE 1 : build ----------
FROM node:20-alpine AS build

WORKDIR /app

# Cache des dependances : on copie d'abord les manifests, install,
# puis le code. Si le code change mais pas package.json, npm ci n'est
# pas re-execute.
COPY package.json package-lock.json* ./
# Si package-lock.json existe -> npm ci (deterministe).
# Sinon -> npm install (premier build, fait office de fallback).
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copier les sources et builder.
# tsc --noEmit + vite build -> output dans /app/dist
COPY tsconfig.json vite.config.ts index.html ./
COPY src ./src
RUN npm run build

# ---------- STAGE 2 : runtime ----------
FROM nginx:1.27-alpine AS runtime

# Retirer le default.conf de nginx pour eviter les conflits.
RUN rm /etc/nginx/conf.d/default.conf

# Copier notre config nginx (SPA fallback + reverse proxy /api).
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copier le dist du stage build.
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

# Healthcheck : nginx repond sur /. -k pour ignorer le HTTP/HTTPS mismatch.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost/ || exit 1

# nginx demarre automatiquement via le CMD par defaut de l'image base
# (nginx -g "daemon off;"). On le redeclare pour la lisibilite.
CMD ["nginx", "-g", "daemon off;"]
