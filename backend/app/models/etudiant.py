from sqlalchemy import Boolean, Column, Integer, String

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
