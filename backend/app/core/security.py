from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Transforme le mot de passe en code indéchiffrable."""
    return pwd_context.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, mot_de_passe_hache: str) -> bool:
    """Vérifie si le mot de passe correspond au hash stocké."""
    return pwd_context.verify(mot_de_passe, mot_de_passe_hache)



def creer_token(data: dict) -> str:
    """Crée un token JWT pour garder l'étudiant connecté."""
    to_encode = data.copy()
    to_encode["sub"] = str(to_encode["sub"])  # ← AJOUTER CETTE LIGNE
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ============================================================
# Tokens dedies pour email verification et reset password
# ============================================================
# On signe un JWT court avec un champ "purpose" qui distingue clairement
# l'usage. Sans ce champ, un token de verify pourrait etre utilise pour
# reset password (ce qui serait une faille). Verifier le purpose dans le
# decoder est la defense.
# ============================================================
def _create_purpose_token(user_id: int, purpose: str, hours: int) -> str:
    payload = {
        "sub": str(user_id),
        "purpose": purpose,
        "exp": datetime.now(UTC) + timedelta(hours=hours),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _decode_purpose_token(token: str, expected_purpose: str) -> int:
    """Decode un token et verifie son purpose. Retourne le user_id ou leve."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=400, detail="Token invalide ou expire") from exc

    if payload.get("purpose") != expected_purpose:
        raise HTTPException(
            status_code=400,
            detail=f"Token usage incorrect (attendu : {expected_purpose})",
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token sans sub")
    try:
        return int(user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Token sub invalide") from exc


def create_verification_token(user_id: int) -> str:
    """Token de verification d'email (valide 24h par defaut)."""
    return _create_purpose_token(user_id, "verify_email", settings.EMAIL_VERIFICATION_TOKEN_HOURS)


def decode_verification_token(token: str) -> int:
    return _decode_purpose_token(token, "verify_email")


def create_reset_password_token(user_id: int) -> str:
    """Token de reset password (valide 1h par defaut)."""
    return _create_purpose_token(user_id, "reset_password", settings.EMAIL_RESET_TOKEN_HOURS)


def decode_reset_password_token(token: str) -> int:
    return _decode_purpose_token(token, "reset_password")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> int:
    """Vérifie le token JWT et retourne l'ID de l'étudiant connecté.

    En plus de décoder le JWT, on VÉRIFIE que l'utilisateur existe encore
    dans Postgres. Sans ça, un client qui garde un vieux token (par ex.
    après un `docker compose down -v` qui a wipé la base) tomberait sur
    des erreurs SQL ForeignKeyViolation au moment d'écrire en base.
    En faisant la vérif ici, on retourne un 401 propre que le frontend
    sait gérer (redirection automatique vers /login).
    """
    # Import local pour éviter les imports circulaires (Etudiant -> security
    # via les routers).
    from app.models.etudiant import Etudiant

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        user_id_int = int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    # Vérification d'existence côté DB. Évite ForeignKeyViolation
    # quand le user a été supprimé / la base réinitialisée.
    exists = db.query(Etudiant.id).filter(Etudiant.id == user_id_int).first()
    if exists is None:
        raise HTTPException(
            status_code=401,
            detail="Compte introuvable. Reconnecte-toi.",
        )
    return user_id_int
