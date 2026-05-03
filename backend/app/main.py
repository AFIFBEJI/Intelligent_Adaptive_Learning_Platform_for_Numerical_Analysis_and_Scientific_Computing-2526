from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# === Configuration logging globale ===
# Par defaut, uvicorn n'affiche que ses propres logs (HTTP access log).
# Les logger.info() de l'application sont silencieusement filtres car le
# logger root est en WARNING. On force ici INFO sur le namespace `app.*`
# pour rendre visibles les messages utiles (LLM provider, etc.).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
    force=True,  # override toute config heritee de uvicorn
)
# Logger applicatif a INFO, bibliotheques tierces a WARNING (moins de bruit)
logging.getLogger("app").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

from app.core.config import get_settings
from app.core.database import create_tables, engine
from app.core.migrations import ensure_columns
from app.routers import animations, auth, etudiants, graph, quiz, quiz_dynamic, tutor
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

API_VERSION = "2.0.0"
ALLOWED_ORIGINS = [
    # Vite dev server (npm run dev)
    "http://localhost:5173",
    "http://localhost:4200",
    # Container frontend (docker compose) : nginx ecoute sur l'hote
    # en port 8080 (mapping 8080:80 dans docker-compose.yml).
    # En mode docker, le SPA et l'API partagent l'origine via le proxy
    # nginx /api -> backend:8000, donc CORS n'est techniquement plus
    # necessaire ; on garde ces origines pour le cas ou le frontend
    # serait servi separement (ex: dev hybride).
    "http://localhost:8080",
    "http://localhost",
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
    animations.router,
)


def _print_llm_banner() -> None:
    """Affiche une banniere claire au demarrage indiquant le LLM actif.

    On utilise `print()` (et pas seulement logger.info) car la sortie
    standard est toujours visible quel que soit le niveau de logging.
    """
    settings = get_settings()
    # Caracteres ASCII uniquement pour eviter UnicodeEncodeError sur Windows
    # (cp1252 ne supporte pas les emojis ni les caracteres de boite).
    bar = "=" * 70
    provider_label = "OPENAI (cloud, paye)" if llm_service.provider == "openai" else "OLLAMA (local, gratuit)"
    status_icon = "[OK]" if llm_service.llm is not None else "[KO]"
    lines = [
        bar,
        f"  ADAPTIVE LEARNING PLATFORM API  v{API_VERSION}",
        bar,
        f"  LLM provider     : {llm_service.provider.upper()}  ({provider_label})",
        f"  LLM model        : {llm_service.model_name}",
        f"  LLM initialized  : {status_icon}",
    ]
    if llm_service.provider == "openai":
        key = settings.OPENAI_API_KEY or ""
        masked = (key[:7] + "..." + key[-4:]) if len(key) > 12 else "(empty)"
        lines.append(f"  OpenAI API key   : {masked}")
    else:
        lines.append(f"  Ollama base URL  : {settings.OLLAMA_BASE_URL}")
    lines.append(bar)
    # On utilise uniquement print() pour la banniere de demarrage afin
    # d'eviter le doublon avec le format logger ("HH:MM | INFO | app.main | ...").
    # La banniere doit rester lisible d'un coup d'oeil.
    for line in lines:
        print(line, flush=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    ensure_columns(engine)
    _print_llm_banner()
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


# ============================================================
# Static files : Manim animations served from /static/animations/<file>.mp4
# ============================================================
# Les videos Manim pre-rendues sont dans backend/static/animations/.
# On les expose en lecture publique car elles ne contiennent pas de
# donnees sensibles. Le frontend s'en sert via <video src="/static/animations/lagrange_en.mp4" />.
_static_dir = Path(__file__).resolve().parent.parent / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


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
    """Healthcheck enrichi : retourne aussi le LLM actif pour diagnostic rapide."""
    return {
        "status": "ok",
        "version": API_VERSION,
        "llm": {
            "provider": llm_service.provider,
            "model": llm_service.model_name,
            "initialized": llm_service.llm is not None,
        },
    }
