"""
Cleanup script: deletes ALL students + their related data.

Usage:
    cd backend
    .\venv\Scripts\Activate.ps1
    python scripts/wipe_students.py

WARNING: destructive and irreversible action. Confirm with 'yes'.
"""
import sys
from pathlib import Path

# Allow importing 'app.*' from anywhere
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
        # TRUNCATE CASCADE also deletes all tables that reference
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
