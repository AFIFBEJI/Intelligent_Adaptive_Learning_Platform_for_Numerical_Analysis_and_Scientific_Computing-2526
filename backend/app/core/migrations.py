# ============================================================
# Lightweight migrations — adding missing columns
# ============================================================
# This file complements Base.metadata.create_all() which can only
# create complete tables — it does NOT know how to add
# columns to an existing table.
#
# Here we inspect the real schema then run ALTER TABLE
# ADD COLUMN for each column declared in the models
# but missing from the database (idempotent, no effect if already OK).
#
# This is a pragmatic solution for a student project; in
# production we would use Alembic to track the history.
# ============================================================
from __future__ import annotations

import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


# ============================================================
# Columns to guarantee on existing tables
# ============================================================
# Each entry: (table, column, portable SQL DDL).
# The DDLs are compatible with PostgreSQL / SQLite / MySQL for the
# basic types (VARCHAR, INTEGER, JSON) that we use.
COLUMN_SPECS: list[tuple[str, str, str]] = [
    # Preferred language (default English)
    ("etudiants", "langue_preferee", "VARCHAR(2) NOT NULL DEFAULT 'en'"),
    # Phase 3 - email verification + reset password
    ("etudiants", "is_verified", "BOOLEAN NOT NULL DEFAULT FALSE"),
    ("etudiants", "email_verified_at", "TIMESTAMP"),
    ("etudiants", "verification_sent_at", "TIMESTAMP"),
    # New dynamic Quiz fields
    ("quiz", "source", "VARCHAR(20) NOT NULL DEFAULT 'static'"),
    ("quiz", "etudiant_generateur_id", "INTEGER"),
    ("quiz", "concept_neo4j_id", "VARCHAR(255)"),
    ("quiz", "seed", "VARCHAR(64)"),
    # Dual pedagogical mode:
    #   - "adaptive" (default) : updates the mastery
    #   - "practice"           : free training, no mastery impact
    ("quiz", "mode", "VARCHAR(20) NOT NULL DEFAULT 'adaptive'"),
    # New QuizResult fields (feedback)
    ("quiz_resultats", "evaluation_detaillee", "JSON"),
    ("quiz_resultats", "feedback_card", "JSON"),
]


def ensure_columns(engine: Engine) -> None:
    """Add the missing columns from COLUMN_SPECS.

    Called at FastAPI startup just after create_tables().
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table, column, ddl in COLUMN_SPECS:
            if table not in existing_tables:
                # The table will be created by create_all() later;
                # we log and skip.
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
                # If another instance has already added the column, that is OK
                logger.warning(
                    "Migration %s.%s a échoué (peut-être déjà appliquée) : %s",
                    table,
                    column,
                    exc,
                )
