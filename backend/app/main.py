from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_tables, engine
from app.core.migrations import ensure_columns
from app.routers import auth, etudiants, graph, quiz, quiz_dynamic, tutor

logger = logging.getLogger(__name__)

API_VERSION = "2.0.0"
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:4200",
]
FEATURES = [
    "Authentification JWT",
    "Graphe de connaissances Neo4j",
    "Quiz adaptatifs",
    "Tuteur IA GraphRAG + SymPy",
]
ROUTERS = (
    auth.router,
    etudiants.router,
    graph.router,
    quiz.router,
    quiz_dynamic.router,
    tutor.router,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    ensure_columns(engine)
    logger.info("Adaptive Learning Platform API started")
    yield


app = FastAPI(
    title="PFE - Adaptive Learning Platform",
    description=(
        "API Backend pour la plateforme d'apprentissage adaptatif "
        "avec tuteur IA base sur GraphRAG et verification SymPy"
    ),
    version=API_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in ROUTERS:
    app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "PFE API fonctionne!",
        "version": API_VERSION,
        "docs": "/docs",
        "features": FEATURES,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
