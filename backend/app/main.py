from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

# === Global logging configuration ===
# By default, uvicorn only shows its own logs (HTTP access log).
# The application's logger.info() calls are silently filtered out because the
# root logger is at WARNING. Here we force INFO on the `app.*` namespace
# to make useful messages visible (LLM provider, etc.).
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
    force=True,  # override any config inherited from uvicorn
)
# Application logger at INFO, third-party libraries at WARNING (less noise)
logging.getLogger("app").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

from app.core.config import get_settings
from app.core.database import create_tables, engine
from app.core.migrations import ensure_columns
from app.core.rate_limit import limiter
from app.routers import animations, auth, etudiants, graph, quiz, quiz_dynamic, study, tutor
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

API_VERSION = "2.0.0"
ALLOWED_ORIGINS = [
    # Vite dev server (npm run dev)
    "http://localhost:5173",
    "http://localhost:4200",
    # Frontend container (docker compose): nginx listens on the host
    # on port 8080 (mapping 8080:80 in docker-compose.yml).
    # In docker mode, the SPA and the API share the origin via the
    # nginx proxy /api -> backend:8000, so CORS is technically no longer
    # necessary; we keep these origins for the case where the frontend
    # is served separately (e.g. hybrid dev).
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
    study.router,
)


def _print_llm_banner() -> None:
    """Print a clear banner at startup indicating the active LLM.

    We use `print()` (and not only logger.info) because the standard
    output is always visible regardless of the logging level.
    """
    settings = get_settings()
    # ASCII characters only to avoid UnicodeEncodeError on Windows
    # (cp1252 does not support emojis nor box-drawing characters).
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
    # We use only print() for the startup banner in order
    # to avoid duplication with the logger format ("HH:MM | INFO | app.main | ...").
    # The banner must remain readable at a glance.
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

# ============================================================
# Rate limiting (slowapi)
# ============================================================
# The `limiter` is defined as a singleton in `app/core/rate_limit.py` and
# decorates the sensitive endpoints (`/auth/login`, `/tutor/.../ask`, etc.).
# Here we attach it to the FastAPI instance, register the exception
# handler (which returns 429 + Retry-After), and mount the middleware
# that injects the counter on each request.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Security headers
# ============================================================
# Add standard hardening headers to every response. These mitigate
# MIME-sniffing, clickjacking and referrer leakage at zero cost.
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


for router in ROUTERS:
    app.include_router(router)


# ============================================================
# Static files : Manim animations served from /static/animations/<file>.mp4
# ============================================================
# The pre-rendered Manim videos are in backend/static/animations/.
# We expose them publicly for reading because they do not contain
# sensitive data. The frontend uses them via <video src="/static/animations/lagrange_en.mp4" />.
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
    """Enriched healthcheck: also returns the active LLM for quick diagnosis."""
    return {
        "status": "ok",
        "version": API_VERSION,
        "llm": {
            "provider": llm_service.provider,
            "model": llm_service.model_name,
            "initialized": llm_service.llm is not None,
        },
    }
