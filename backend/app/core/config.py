# ============================================================
# Configuration de l'application
# ============================================================
# Ce fichier lit TOUTES les variables depuis le fichier .env
# Pourquoi ? Pour ne JAMAIS mettre de mots de passe dans le code.
#
# Comment ca marche ?
# 1. Vous ecrivez SECRET_KEY=abc123 dans .env
# 2. Pydantic Settings lit automatiquement ce fichier
# 3. Vous accedez a la valeur avec : settings.SECRET_KEY
# ============================================================

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Lit automatiquement toutes les variables depuis le fichier .env

    Chaque attribut ci-dessous correspond à une ligne dans .env.
    Si une variable a une valeur par défaut (ex: ALGORITHM = "HS256"),
    elle est optionnelle dans .env. Sinon, elle est OBLIGATOIRE.
    """

    # --- PostgreSQL ---
    # L'URL de connexion à PostgreSQL
    # Format : postgresql://utilisateur:motdepasse@adresse:port/nom_base
    DATABASE_URL: str

    # --- Neo4j (Graphe de connaissances) ---
    # URI : l'adresse de Neo4j (bolt:// est le protocole de communication)
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    # --- JWT (Authentification) ---
    # SECRET_KEY : une clé secrète pour signer les tokens JWT
    # C'est comme un tampon officiel : si quelqu'un modifie le token, la signature ne match plus
    SECRET_KEY: str
    # ALGORITHM : l'algorithme de signature (HS256 = HMAC-SHA256, très courant)
    ALGORITHM: str = "HS256"
    # Durée de validité du token en minutes (60 min = 1 heure)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 jours (7 * 24 * 60)

    # ============================================================
    # Tuteur IA GraphRAG (Ollama / Gemma fine-tune local)
    # ============================================================
    # Mode 100% local via Ollama.

    # --- Paramètres du LLM ---
    # Temperature : contrôle la "créativité" de l'IA (0.0 à 1.0)
    # 0.0 = très déterministe (même question → même réponse)
    # 1.0 = très créatif (réponses variées mais parfois incohérentes)
    # 0.3 = bon équilibre pour les maths (précision > créativité)
    LLM_TEMPERATURE: float = 0.3

    # Nombre maximum de tokens dans la réponse
    # 1 token ≈ 0.75 mot en français
    # 2048 tokens ≈ 1500 mots (suffisant pour une explication détaillée)
    LLM_MAX_TOKENS: int = 2048

    # --- Paramètres du RAG (Retrieval-Augmented Generation) ---
    # Profondeur de recherche des prérequis dans Neo4j
    # Ex: Si depth=3 et l'étudiant pose une question sur RK4 :
    #   RK4 → REQUIRES → Improved Euler → REQUIRES → Euler → REQUIRES → Taylor Series
    # On remonte 3 niveaux dans l'arbre des prérequis
    RAG_PREREQUISITE_DEPTH: int = 3

    # Seuil de maîtrise (0-100) au-dessus duquel un concept est "maîtrisé"
    # Si maîtrise >= 70%, l'étudiant a compris le concept
    MASTERY_THRESHOLD: float = 70.0

    # Active/désactive la vérification SymPy des formules dans les réponses
    # True = on vérifie chaque formule LaTeX (plus sûr mais plus lent)
    ENABLE_SYMPY_VERIFICATION: bool = True

    # ============================================================
    # Choix du fournisseur LLM (provider)
    # ============================================================
    # "ollama"  -> Gemma local fine-tune (gratuit, prive, hors-ligne)
    # "openai"  -> GPT-4o-mini en API (cloud, paye, qualite premium)
    #
    # Tu peux changer dans .env sans toucher au code :
    #   LLM_PROVIDER=ollama   ou   LLM_PROVIDER=openai
    LLM_PROVIDER: str = "ollama"

    # Nom du modele a utiliser. Doit etre coherent avec LLM_PROVIDER :
    #   ollama  : "gemma-numerical-e2b" (ton fine-tune)
    #   openai  : "gpt-4o-mini" (recommande), "gpt-4o", "gpt-3.5-turbo"
    LLM_MODEL_NAME: str = "gemma-numerical-e2b"

    # ============================================================
    # Ollama (Modele local)
    # ============================================================
    # Ollama fait tourner des modeles d'IA directement sur ton PC.
    # Avantages : pas de quota, pas d'internet, donnees privees (RGPD).

    # Le modele Ollama a utiliser (doit etre cree avec "ollama create").
    # Conserve pour compatibilite : si LLM_PROVIDER=ollama et que
    # LLM_MODEL_NAME n'est pas defini, on retombe sur OLLAMA_MODEL.
    OLLAMA_MODEL: str = "gemma-numerical-e2b"

    # L'adresse du serveur Ollama sur ton PC
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # ============================================================
    # OpenAI (Modele cloud)
    # ============================================================
    # Cle API OpenAI (commence par sk-...). A obtenir sur :
    #   https://platform.openai.com/api-keys
    # Mettre cette valeur dans .env, jamais dans le code.
    OPENAI_API_KEY: str = ""

    # ============================================================
    # Picker LLM (interface utilisateur)
    # ============================================================
    # Si True, le frontend affiche un selecteur permettant a
    # l'utilisateur de choisir entre Gemma local et GPT-4o-mini cloud
    # AVANT chaque question au tuteur.
    #
    # Recommandations :
    #   - True  : pour la demo de soutenance (montre la flexibilite)
    #   - False : en production reelle (controle des couts cote admin)
    LLM_PICKER_ENABLED: bool = True

    # ============================================================
    # Email (Phase 3 : verification email + reset password)
    # ============================================================
    # Mode mail :
    #   "console" (defaut) : log l'email dans stdout, pas d'envoi reel.
    #                        Parfait pour la demo / dev local.
    #   "smtp"             : envoi via un serveur SMTP (Gmail, SendGrid,
    #                        Postmark, etc.). Necessite les SMTP_* ci-dessous.
    MAIL_MODE: str = "console"

    # URL publique du frontend, utilisee dans les liens contenus dans les
    # emails (ex: http://localhost:4200/verify-email/{token}).
    FRONTEND_URL: str = "http://localhost:4200"

    # Adresse expeditrice affichee dans les emails ("From: ...").
    MAIL_FROM: str = "noreply@adaptive-learning.local"
    MAIL_FROM_NAME: str = "Numera Platform"

    # Config SMTP (utilise uniquement si MAIL_MODE=smtp)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True

    # Anti-spam : delai minimum (secondes) entre deux envois de mail
    # de verification pour le meme utilisateur. Bloque les abus.
    EMAIL_VERIFICATION_RESEND_COOLDOWN_SEC: int = 60
    # Duree de vie des tokens (en heures pour verify, en heures pour reset).
    EMAIL_VERIFICATION_TOKEN_HOURS: int = 24
    EMAIL_RESET_TOKEN_HOURS: int = 1

    # Photo du fondateur (pour la signature dans les emails). Si laisse vide,
    # l'email affiche un avatar "Y" stylise par defaut. Path local sur le
    # serveur backend, ex: C:\Users\GIGABYTE\Documents\moi\photo.png
    AUTHOR_PHOTO_PATH: str = ""

    # ============================================================
    # Phase 4 : user study admin
    # ============================================================
    # Liste d'emails (separes par virgules) qui ont acces aux endpoints
    # /study/admin/*. Vide par defaut : aucun acces. Mettre par ex.
    # STUDY_ADMIN_EMAILS="eyabenncib100@gmail.com,afif.beji@esprit.tn"
    # dans .env pour activer l'acces a l'investigateur + a l'encadrant.
    STUDY_ADMIN_EMAILS: str = ""

    class Config:
        # Où chercher le fichier .env (2 niveaux au-dessus de app/core/)
        env_file = "../.env"
        # Tolere les variables supplementaires dans le .env qui ne sont
        # pas declarees ici. Necessaire car le .env partage avec
        # docker-compose contient aussi POSTGRES_USER, POSTGRES_PASSWORD,
        # POSTGRES_DB (utilises pour configurer le container Postgres)
        # qui ne sont pas pertinentes pour le backend Python lui-meme :
        # lui utilise DATABASE_URL deja deduit de ces variables. Sans
        # ce flag, pydantic-settings leve un ValidationError au demarrage.
        extra = "ignore"


@lru_cache
def get_settings():
    """
    Retourne les settings en cache.

    @lru_cache() = la première fois qu'on appelle get_settings(),
    Python lit le .env et crée l'objet Settings.
    Les appels suivants retournent le même objet sans relire le .env.
    C'est une optimisation de performance.
    """
    return Settings()
