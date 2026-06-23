from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.core.database import Base


class Etudiant(Base):
    __tablename__ = "etudiants"

    id = Column(Integer, primary_key=True, index=True)
    nom_complet = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    mot_de_passe = Column(String(255), nullable=False)
    niveau_actuel = Column(String, default="beginner")
    langue_preferee = Column(String(2), nullable=False, default="en")
    is_active = Column(Boolean, default=True)

    # ============================================================
    # Email verification (Phase 3)
    # ============================================================
    # is_verified : becomes True when the user clicks the verification
    # link received by email. While False, certain features (sending
    # feedback to the tutor, etc.) can be blocked if we want to be
    # strict ; today we just log a warning to avoid breaking the demo
    # experience.
    is_verified = Column(Boolean, default=False, nullable=False)
    # Date+time of the successful verification (useful for analytics and debug).
    email_verified_at = Column(DateTime, nullable=True)
    # Date+time of the last verification email sent (API-side rate limit
    # to avoid spam abuse : we accept a new send every 60s).
    verification_sent_at = Column(DateTime, nullable=True)
