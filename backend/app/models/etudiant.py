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
    # Verification email (Phase 3)
    # ============================================================
    # is_verified : passe a True quand l'utilisateur clique sur le lien
    # de verification recu par mail. Tant que False, certaines
    # fonctionnalites (envoi de feedback au tuteur, etc.) peuvent etre
    # bloquees si on veut etre strict ; aujourd'hui on log juste un
    # warning pour ne pas casser l'experience demo.
    is_verified = Column(Boolean, default=False, nullable=False)
    # Date+heure de la verification reussie (utile pour analytics et debug).
    email_verified_at = Column(DateTime, nullable=True)
    # Date+heure du dernier envoi d'email de verification (rate limit cote API
    # pour eviter les abus de spam : on accepte un nouvel envoi toutes les 60s).
    verification_sent_at = Column(DateTime, nullable=True)
