# ============================================================
# Migrations légères — ajout de colonnes manquantes
# ============================================================
# Ce fichier complète Base.metadata.create_all() qui ne sait
# créer que des tables complètes — il ne sait PAS ajouter des
# colonnes à une table existante.
#
# Ici on inspecte le schéma réel puis on exécute ALTER TABLE
# ADD COLUMN pour chaque colonne déclarée dans les modèles
# mais absente de la base (idempotent, sans effet si déjà OK).
#
# C'est une solution pragmatique pour un projet étudiant ; en
# production on utiliserait Alembic pour tracer l'historique.
# ============================================================
from __future__ import annotations

import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


# ============================================================
# Colonnes à garantir sur les tables existantes
# ============================================================
# Chaque entrée : (table, colonne, DDL SQL portable).
# Les DDL sont compatibles PostgreSQL / SQLite / MySQL pour les
# types de base (VARCHAR, INTEGER, JSON) qu'on utilise.
COLUMN_SPECS: list[tuple[str, str, str]] = [
    # Preferred language (default English)
    ("etudiants", "langue_preferee", "VARCHAR(2) NOT NULL DEFAULT 'en'"),
    # Phase 3 - email verification + reset password
    ("etudiants", "is_verified", "BOOLEAN NOT NULL DEFAULT FALSE"),
    ("etudiants", "email_verified_at", "TIMESTAMP"),
    ("etudiants", "verification_sent_at", "TIMESTAMP"),
    # Nouveaux champs Quiz dynamique
    ("quiz", "source", "VARCHAR(20) NOT NULL DEFAULT 'static'"),
    ("quiz", "etudiant_generateur_id", "INTEGER"),
    ("quiz", "concept_neo4j_id", "VARCHAR(255)"),
    ("quiz", "seed", "VARCHAR(64)"),
    # Double mode pedagogique :
    #   - "adaptive" (par defaut) : met a jour le mastery
    #   - "practice"             : entrainement libre, sans impact mastery
    ("quiz", "mode", "VARCHAR(20) NOT NULL DEFAULT 'adaptive'"),
    # Nouveaux champs QuizResult (feedback)
    ("quiz_resultats", "evaluation_detaillee", "JSON"),
    ("quiz_resultats", "feedback_card", "JSON"),
]


def ensure_columns(engine: Engine) -> None:
    """Ajoute les colonnes manquantes de COLUMN_SPECS.

    Appelée au démarrage FastAPI juste après create_tables().
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table, column, ddl in COLUMN_SPECS:
            if table not in existing_tables:
                # La table sera créée par create_all() plus tard ;
                # on log et on passe.
                logger.debug("Table %s absente, skip colonne %s", table, column)
                continue

            cols = {c["name"] for c in inspector.get_columns(table)}
            if column in cols:
                continue

            alter_sql = f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"
            logger.info("Migration légère : %s", alter_sql)
            try:
                conn.execute(text(alter_sql))
            except Exception as exc:  # noqa: BLE001
                # Si une autre instance a déjà ajouté la colonne, c'est OK
                logger.warning(
                    "Migration %s.%s a échoué (peut-être déjà appliquée) : %s",
                    table,
                    column,
                    exc,
                )
