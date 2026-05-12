# ADR-003: Lightweight boot-time migrations vs Alembic

**Status**: ✅ Accepted (with explicit debt)
**Date**: May 12, 2026
**Author**: Yassine Ben Nessib

## Context

PostgreSQL is the primary database (students, quizzes, mastery, tutor
sessions, user study). The schema evolves across project phases:

- Phase 1: `etudiants`, `quiz`, `quiz_resultats`, `concept_mastery`.
- Phase 2: `tutor_sessions`, `tutor_messages`.
- Phase 3: columns `is_verified`, `email_verified_at`,
  `verification_sent_at` on `etudiants`.
- Phase 4: `study_participants`, `study_events`.

Question: how to version these evolutions? The project is an academic
prototype, but must remain reproducible.

## Options considered

### Option A: Alembic (standard SQLAlchemy migration tool)
- **+** Structured versioning with revision hashes.
- **+** Rollback possible.
- **+** CI-compatible (auto-detect drift).
- **−** Initial setup (alembic init, env.py, migrations.py).
- **−** One migration = one commit = one extra file per ALTER.
- **−** Conflict risk in teams (two parallel migrations).
- **−** Learning required for future contributors.

### Option B: Lightweight boot-time migrations (pattern "ensure_columns")
- **+** No setup, just `ALTER TABLE IF NOT EXISTS ADD COLUMN ...`
  executed at FastAPI startup.
- **+** Code is self-healing: a dev who clones and starts has nothing to do.
- **+** No migration files to commit.
- **−** No automatic rollback.
- **−** Not ideal for large teams (race conditions at boot with
  multi-replicas).
- **−** Non-transactional ALTER on some DBs → downtime risk in production.

### Option C: Drop & recreate on each deployment (dev mode)
- **+** Ultra simple: `Base.metadata.drop_all()` + `create_all()`.
- **−** Loses user data. **Unacceptable** as soon as the user study starts.

## Decision

**Option B retained: lightweight migrations in `app/core/migrations.py`.**

**Main reason**: we are a 1-dev prototype, single-replica deployment
(Docker compose or Render). Race conditions don't exist. The gain in
simplicity is real.

**Implementation**: `backend/app/core/migrations.py`

```python
def ensure_columns(engine) -> None:
    """Idempotently adds columns added after the initial schema creation.
    Called at boot via main.py:lifespan."""
    with engine.connect() as conn:
        # Phase 3: email verification
        conn.execute(text("""
            ALTER TABLE etudiants
            ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE
        """))
        # ... other columns
```

Called in `main.py:lifespan`:
```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()        # Base.metadata.create_all (idempotent)
    ensure_columns(engine) # idempotent ALTER TABLE
    ...
```

## Consequences

### Positive

- **Zero setup**: `docker compose up` creates + migrates the schema
  without extra command. Excellent for IEEE paper reproducibility.
- **Readable code**: migration is just a native SQL ALTER, not an
  obfuscated Alembic revision.
- **No migration files** to commit/maintain.
- **No risk of "forgotten migration"**: the function is called on EVERY
  boot, so even a dev who pulls and starts cannot forget.

### Negative / accepted debt

- **No rollback**: if a migration introduces a bug, we must manually fix
  the DB. Acceptable in dev/PFE, **problematic in production**.
- **`migrations.py` grows linearly**: each new column = +3 lines. At ~50
  columns it becomes heavy. At that point, migrating to Alembic is a
  1-2 day project.
- **No history**: we don't know when each column was added. Solution:
  comments at the top of each block (`# Phase 3, 12/04/2026`).
- **Multi-replica race condition**: if we deploy on Kubernetes with 3
  replicas starting in parallel, they all try to ALTER simultaneously.
  `IF NOT EXISTS` makes the operation idempotent on Postgres but some
  DBs (older MySQL) don't support it. Acceptable because we are on
  Postgres with single-replica.

### Evolution plan

**When to migrate to Alembic**:

- When deploying in production multi-replica (Kubernetes, ECS, etc.).
- When the schema exceeds ~30 columns added after the initial creation.
- When we have > 1 backend contributor who can commit in parallel.

**Migration plan**:

1. Freeze `migrations.py` (status: "frozen, no more ALTERs to add").
2. `alembic init alembic/` then `alembic stamp head` on the current DB.
3. For each new schema change: `alembic revision --autogenerate -m "..."`.
4. `app/main.py`: replace `ensure_columns()` with `alembic upgrade head`
   (subprocess).
5. Estimate: 1-2 days of work + review.

## References

- Alembic docs: https://alembic.sqlalchemy.org
- Source file for this decision: `backend/app/core/migrations.py`
- Pattern "ensure schema at boot": Stripe article on schema evolution (2018).
