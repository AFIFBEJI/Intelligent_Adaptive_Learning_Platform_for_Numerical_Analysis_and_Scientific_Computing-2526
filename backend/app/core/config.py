# ============================================================
# Application configuration
# ============================================================
# This file reads ALL the variables from the .env file
# Why? To NEVER put passwords in the code.
#
# How does it work?
# 1. You write SECRET_KEY=abc123 in .env
# 2. Pydantic Settings automatically reads this file
# 3. You access the value with: settings.SECRET_KEY
# ============================================================

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

# ABSOLUTE path of the .env file, computed from the location of this
# file (and not from the launch directory). config.py is in
# backend/app/core/; the .env is at the project root (3 levels above).
# This way the OPENAI_API_KEY is read even if uvicorn is launched from the
# root, from backend/, or via a script, without depending on the cwd.
_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    """
    Automatically reads all the variables from the .env file

    Each attribute below corresponds to a line in .env.
    If a variable has a default value (e.g. ALGORITHM = "HS256"),
    it is optional in .env. Otherwise, it is MANDATORY.
    """

    # --- PostgreSQL ---
    # The PostgreSQL connection URL
    # Format: postgresql://user:password@host:port/db_name
    DATABASE_URL: str

    # --- Neo4j (Knowledge graph) ---
    # URI: the address of Neo4j (bolt:// is the communication protocol)
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    # --- JWT (Authentication) ---
    # SECRET_KEY: a secret key to sign the JWT tokens
    # It is like an official stamp: if someone modifies the token, the signature no longer matches
    SECRET_KEY: str
    # ALGORITHM: the signing algorithm (HS256 = HMAC-SHA256, very common)
    ALGORITHM: str = "HS256"
    # Token validity duration in minutes (60 min = 1 hour)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days (7 * 24 * 60)

    # ============================================================
    # GraphRAG AI Tutor (Ollama / local fine-tuned Gemma)
    # ============================================================
    # 100% local mode via Ollama.

    # --- LLM parameters ---
    # Temperature: controls the "creativity" of the AI (0.0 to 1.0)
    # 0.0 = very deterministic (same question -> same answer)
    # 1.0 = very creative (varied but sometimes incoherent answers)
    # 0.3 = good balance for math (precision > creativity)
    LLM_TEMPERATURE: float = 0.3

    # Maximum number of tokens in the response
    # 1 token ~ 0.75 word in French
    # 2048 tokens ~ 1500 words (enough for a detailed explanation)
    LLM_MAX_TOKENS: int = 2048

    # --- RAG parameters (Retrieval-Augmented Generation) ---
    # Search depth of prerequisites in Neo4j
    # Ex: If depth=3 and the student asks a question about RK4:
    #   RK4 -> REQUIRES -> Improved Euler -> REQUIRES -> Euler -> REQUIRES -> Taylor Series
    # We go up 3 levels in the prerequisites tree
    RAG_PREREQUISITE_DEPTH: int = 3

    # Mastery threshold (0-100) above which a concept is "mastered"
    # If mastery >= 70%, the student has understood the concept
    MASTERY_THRESHOLD: float = 70.0

    # Enable/disable the SymPy verification of formulas in the responses
    # True = we verify each LaTeX formula (safer but slower)
    ENABLE_SYMPY_VERIFICATION: bool = True

    # ============================================================
    # LLM provider choice
    # ============================================================
    # "ollama"  -> local fine-tuned Gemma (free, private, offline)
    # "openai"  -> GPT-4o-mini via API (cloud, paid, premium quality)
    #
    # You can change it in .env without touching the code:
    #   LLM_PROVIDER=ollama   or   LLM_PROVIDER=openai
    LLM_PROVIDER: str = "ollama"

    # Name of the model to use. Must be consistent with LLM_PROVIDER:
    #   ollama  : "gemma-numerical-e2b" (your fine-tune)
    #   openai  : "gpt-4o-mini" (recommended), "gpt-4o", "gpt-3.5-turbo"
    LLM_MODEL_NAME: str = "gemma-numerical-e2b"

    # ============================================================
    # Ollama (Local model)
    # ============================================================
    # Ollama runs AI models directly on your PC.
    # Advantages: no quota, no internet, private data (GDPR).

    # The Ollama model to use (must be created with "ollama create").
    # Kept for compatibility: if LLM_PROVIDER=ollama and
    # LLM_MODEL_NAME is not defined, we fall back to OLLAMA_MODEL.
    OLLAMA_MODEL: str = "gemma-numerical-e2b"

    # The address of the Ollama server on your PC
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # ============================================================
    # OpenAI (Cloud model)
    # ============================================================
    # OpenAI API key (starts with sk-...). To obtain at:
    #   https://platform.openai.com/api-keys
    # Put this value in .env, never in the code.
    OPENAI_API_KEY: str = ""

    # ============================================================
    # LLM picker (user interface)
    # ============================================================
    # If True, the frontend displays a selector allowing the
    # user to choose between local Gemma and GPT-4o-mini cloud
    # BEFORE each question to the tutor.
    #
    # Recommendations:
    #   - True  : for the defense demo (shows the flexibility)
    #   - False : in real production (cost control on the admin side)
    LLM_PICKER_ENABLED: bool = True

    # ============================================================
    # Email (Phase 3: email verification + password reset)
    # ============================================================
    # Mail mode:
    #   "console" (default): logs the email to stdout, no real sending.
    #                        Perfect for the demo / local dev.
    #   "smtp"             : sends via an SMTP server (Gmail, SendGrid,
    #                        Postmark, etc.). Requires the SMTP_* below.
    MAIL_MODE: str = "console"

    # Public URL of the frontend, used in the links contained in the
    # emails (e.g. http://localhost:4200/verify-email/{token}).
    FRONTEND_URL: str = "http://localhost:4200"

    # Sender address displayed in the emails ("From: ...").
    MAIL_FROM: str = "noreply@adaptive-learning.local"
    MAIL_FROM_NAME: str = "Numera Platform"

    # SMTP config (used only if MAIL_MODE=smtp)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True

    # Anti-spam: minimum delay (seconds) between two verification mail
    # sends for the same user. Blocks abuse.
    EMAIL_VERIFICATION_RESEND_COOLDOWN_SEC: int = 60
    # Token lifetime (in hours for verify, in hours for reset).
    EMAIL_VERIFICATION_TOKEN_HOURS: int = 24
    EMAIL_RESET_TOKEN_HOURS: int = 1

    # Founder's photo (for the signature in the emails). If left empty,
    # the email displays a default stylized "Y" avatar. Local path on the
    # backend server, e.g. C:\Users\GIGABYTE\Documents\moi\photo.png
    AUTHOR_PHOTO_PATH: str = ""

    # ============================================================
    # Phase 4: user study admin
    # ============================================================
    # List of emails (comma-separated) that have access to the
    # /study/admin/* endpoints. Empty by default: no access. Set e.g.
    # STUDY_ADMIN_EMAILS="eyabenncib100@gmail.com,afif.beji@esprit.tn"
    # in .env to enable access for the investigator + the supervisor.
    STUDY_ADMIN_EMAILS: str = ""

    class Config:
        # ABSOLUTE path of the .env (project root), independent of the cwd.
        # A "../.env" fallback remains useful if the structure changes.
        env_file = (str(_ENV_PATH), "../.env")
        # Tolerates extra variables in the .env that are
        # not declared here. Necessary because the .env shared with
        # docker-compose also contains POSTGRES_USER, POSTGRES_PASSWORD,
        # POSTGRES_DB (used to configure the Postgres container)
        # which are not relevant to the Python backend itself:
        # it uses DATABASE_URL already derived from these variables. Without
        # this flag, pydantic-settings raises a ValidationError at startup.
        extra = "ignore"


@lru_cache
def get_settings():
    """
    Return the cached settings.

    @lru_cache() = the first time get_settings() is called,
    Python reads the .env and creates the Settings object.
    Subsequent calls return the same object without re-reading the .env.
    This is a performance optimization (cached singleton).
    """
    return Settings()
