"""
Script de nettoyage : efface TOUS les etudiants + leurs donnees liees.

Usage :
    cd backend
    .\venv\Scripts\Activate.ps1
    python scripts/wipe_students.py

ATTENTION : action destructive et irreversible. Confirme avec 'yes'.
"""
import sys
from pathlib import Path

# Permettre d'importer 'app.*' depuis n'importe ou
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402


def main() -> None:
    print("Cette commande va EFFACER tous les etudiants et leurs donnees liees.")
    confirm = input("Tape 'yes' pour confirmer : ").strip().lower()
    if confirm != "yes":
        print("Annule.")
        return

    db = SessionLocal()
    try:
        # TRUNCATE CASCADE efface aussi toutes les tables qui referencent
        # etudiants via FK (progression, conversations, quiz_attempts, etc.).
        db.execute(text("TRUNCATE TABLE etudiants RESTART IDENTITY CASCADE;"))
        db.commit()
        print("OK : tous les etudiants ont ete supprimes.")
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        print(f"Erreur : {exc}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
