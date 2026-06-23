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
    """Transform the password into an undecipherable code."""
    return pwd_context.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, mot_de_passe_hache: str) -> bool:
    """Check whether the password matches the stored hash."""
    return pwd_context.verify(mot_de_passe, mot_de_passe_hache)



def creer_token(data: dict) -> str:
    """Create a JWT token to keep the student logged in."""
    to_encode = data.copy()
    to_encode["sub"] = str(to_encode["sub"])  # <- ADD THIS LINE
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ============================================================
# Dedicated tokens for email verification and password reset
# ============================================================
# We sign a short JWT with a "purpose" field that clearly distinguishes
# the usage. Without this field, a verify token could be used to
# reset password (which would be a vulnerability). Verifying the purpose in the
# decoder is the defense.
# ============================================================
def _create_purpose_token(user_id: int, purpose: str, hours: int) -> str:
    payload = {
        "sub": str(user_id),
        "purpose": purpose,
        "exp": datetime.now(UTC) + timedelta(hours=hours),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _decode_purpose_token(token: str, expected_purpose: str) -> int:
    """Decode a token and verify its purpose. Returns the user_id or raises."""
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
    """Email verification token (valid 24h by default)."""
    return _create_purpose_token(user_id, "verify_email", settings.EMAIL_VERIFICATION_TOKEN_HOURS)


def decode_verification_token(token: str) -> int:
    return _decode_purpose_token(token, "verify_email")


def create_reset_password_token(user_id: int) -> str:
    """Password reset token (valid 1h by default)."""
    return _create_purpose_token(user_id, "reset_password", settings.EMAIL_RESET_TOKEN_HOURS)


def decode_reset_password_token(token: str) -> int:
    return _decode_purpose_token(token, "reset_password")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> int:
    """Verify the JWT token and return the ID of the logged-in student.

    In addition to decoding the JWT, we VERIFY that the user still exists
    in Postgres. Without that, a client keeping an old token (e.g.
    after a `docker compose down -v` that wiped the database) would hit
    SQL ForeignKeyViolation errors when writing to the database.
    By doing the check here, we return a clean 401 that the frontend
    knows how to handle (automatic redirection to /login).
    """
    # Local import to avoid circular imports (Etudiant -> security
    # via the routers).
    from app.models.etudiant import Etudiant

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        user_id_int = int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    # Existence check on the DB side. Avoids ForeignKeyViolation
    # when the user has been deleted / the database reset.
    exists = db.query(Etudiant.id).filter(Etudiant.id == user_id_int).first()
    if exists is None:
        raise HTTPException(
            status_code=401,
            detail="Compte introuvable. Reconnecte-toi.",
        )
    return user_id_int
