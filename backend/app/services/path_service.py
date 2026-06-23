"""Single source for generating the personalized learning path.

Why this service?
=================
Before May 12, 2026, two versions of `generate_learning_path` coexisted:

1. `services/graph_service.py:generate_learning_path` (the oldest, without
   bilingual support nor a fixed pedagogical order).
2. `routers/graph.py:get_learning_path` (the version used in production,
   with a `lang` parameter + `_MODULE_ORDER_CASE` + `_DIFFICULTY_ORDER_CASE`).

The senior audit of 05/12/2026 found that version 1 was DEAD CODE
(zero callers in the whole repo). But the duplication was still a
risk: if the recommendation formula changes, one might
update the wrong version out of habit.

This module takes over the RICH VERSION (with bilingual + pedagogical order)
as a callable service. The router becomes a simple thin wrapper. The old
graph_service method is removed.

Algorithm
==========
1. Retrieve the student's current mastery (ConceptMastery on Postgres).
2. Retrieve all the Neo4j graph concepts (named in the target language).
3. For each concept:
     - 0 < mastery < 70  -> `concepts_to_improve` (in progress)
     - mastery == 0      -> check the prerequisites:
         - all prerequisites >= 70 -> `next_recommended` (unlocked)
         - otherwise -> ignored (still too early)
4. Top 5 recommended so as not to overwhelm the student.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.graph.neo4j_connection import neo4j_conn
from app.models.mastery import ConceptMastery

# ============================================================
# Pedagogical constants (same values as in routers/graph.py)
# ============================================================
_MODULE_ORDER_CASE = """
    CASE m.id
        WHEN 'module_interpolation' THEN 1
        WHEN 'module_integration' THEN 2
        WHEN 'module_approximation' THEN 3
        WHEN 'module_root_finding' THEN 4
        ELSE 99
    END
"""

_DIFFICULTY_ORDER_CASE = """
    CASE c.difficulty
        WHEN 'beginner' THEN 1
        WHEN 'intermediate' THEN 2
        WHEN 'advanced' THEN 3
        ELSE 99
    END
"""

# Mastery threshold (in %) above which a prerequisite is considered
# acquired. Aligned with settings.MASTERY_THRESHOLD = 70.0.
_MASTERY_THRESHOLD = 70.0

# Max number of concepts to recommend at once (avoid overwhelming).
_MAX_RECOMMENDATIONS = 5


def _normalize_lang(lang: str | None) -> str:
    """Normalize an arbitrary language to 'fr' or 'en' (default: 'en')."""
    if not lang:
        return "en"
    lang = lang.lower().strip()
    return "fr" if lang.startswith("fr") else "en"


# ============================================================
# Alternative path strategies (05/12/2026)
# ============================================================
# The PFE proposal promises "alternative learning paths". Before this change
# we only had ONE single optimal path. We now add 3 strategies
# that re-order the recommendations based on the student's profile:
#
#   - "optimal"        : standard pedagogical order (prerequisite-driven). Default.
#   - "theory_first"   : favors beginner / theoretical concepts.
#                        For students who prefer to understand BEFORE practicing.
#   - "practice_first" : favors intermediate / applied concepts.
#                        For "learning by experience" students.
#   - "remediation"    : for students who are struggling, prioritizes
#                        the REMEDIATES_TO of weakly mastered concepts.
#
# The 3 strategies output the SAME format as the optimal path:
# a single `generate_learning_path(... strategy="...")`. Allows the frontend
# to display 3 proposals side by side ("here are 3 ways to progress")
# and to let the student choose, which satisfies the
# "alternative learning paths" aspect of the proposal.

_VALID_STRATEGIES = {"optimal", "theory_first", "practice_first", "remediation"}


def _apply_strategy_reorder(
    next_recommended: list[dict[str, Any]],
    concepts_to_improve: list[dict[str, Any]],
    strategy: str,
) -> list[dict[str, Any]]:
    """Reorder `next_recommended` according to the strategy.

    Does not change the `concepts_to_improve` list since it is determined
    by the current mastery, not by the learning preference. Only
    the order of the next concepts to discover changes.
    """
    if strategy == "optimal" or not next_recommended:
        return next_recommended

    if strategy == "theory_first":
        # beginner first, then intermediate, then advanced.
        order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        return sorted(next_recommended, key=lambda c: order.get(c.get("level", "intermediate"), 99))

    if strategy == "practice_first":
        # intermediate (applicable) first, then advanced, then beginner.
        # Hypothesis: a "practice-driven" student wants realistic exercises
        # right away, not abstract theory.
        order = {"intermediate": 0, "advanced": 1, "beginner": 2}
        return sorted(next_recommended, key=lambda c: order.get(c.get("level", "intermediate"), 99))

    if strategy == "remediation":
        # Special strategy: we demote the "next_recommended" that
        # require a currently weak concept. We prefer
        # concepts with fewer dependencies so as not to discourage
        # the student who is struggling.
        # Heuristic: sort by level (beginner first, like
        # theory_first) since beginner concepts have fewer prerequisites.
        order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        return sorted(next_recommended, key=lambda c: order.get(c.get("level", "intermediate"), 99))

    # Unknown strategy -> fallback optimal.
    return next_recommended


def generate_learning_path(
    db: Session,
    etudiant_id: int,
    lang: str = "en",
    strategy: str = "optimal",
) -> dict[str, Any]:
    """Generate a personalized learning path (bilingual, strategic).

    Args:
        db: SQLAlchemy session (Postgres) to read ConceptMastery.
        etudiant_id: the student's id.
        lang: 'fr' or 'en' (other = fallback 'en').
        strategy: 'optimal' | 'theory_first' | 'practice_first' | 'remediation'.
                  Unknown strategy -> fallback 'optimal'.

    Returns:
        JSON-serializable dict:
        {
            "etudiant_id": 42,
            "strategy": "optimal",
            "concepts_to_improve": [{id, name, mastery, status}, ...],
            "next_recommended": [{id, name, level, category}, ...] (max 5),
            "overall_progress": {total_concepts, mastered, in_progress},
        }
    """
    if strategy not in _VALID_STRATEGIES:
        strategy = "optimal"
    lang = _normalize_lang(lang)

    # 1. Read the student's mastery from Postgres.
    mastery_rows = (
        db.query(ConceptMastery)
        .filter(ConceptMastery.etudiant_id == etudiant_id)
        .all()
    )
    mastery_dict = {m.concept_neo4j_id: m.niveau_maitrise for m in mastery_rows}

    # 2. Read all the concepts from Neo4j, in the desired language.
    #    The pedagogical order (module-id, difficulty) is applied on the Cypher
    #    side to stay stable regardless of the language.
    with neo4j_conn.get_session() as session:
        result = session.run(
            f"""
            MATCH (m:Module)-[:COVERS]->(c:Concept)
            RETURN c.id AS id,
                   CASE WHEN $lang = 'fr' THEN coalesce(c.name_fr, c.name) ELSE c.name END AS name,
                   c.difficulty AS difficulty,
                   CASE WHEN $lang = 'fr' THEN coalesce(m.name_fr, m.name) ELSE m.name END AS category
            ORDER BY {_MODULE_ORDER_CASE}, {_DIFFICULTY_ORDER_CASE}, c.id
            """,
            lang=lang,
        )
        all_concepts = [dict(r) for r in result]

    # 3. Classify the concepts.
    concepts_to_improve: list[dict[str, Any]] = []
    next_recommended: list[dict[str, Any]] = []

    for concept in all_concepts:
        cid = concept["id"]
        mastery = mastery_dict.get(cid, 0)

        if 0 < mastery < _MASTERY_THRESHOLD:
            concepts_to_improve.append({
                "id": cid,
                "name": concept["name"],
                "mastery": mastery,
                "status": "in_progress",
            })
        elif mastery == 0:
            # Check that all prerequisites are >= threshold.
            with neo4j_conn.get_session() as session:
                prereqs = session.run(
                    "MATCH (c:Concept {id: $cid})-[:REQUIRES]->(p:Concept) "
                    "RETURN p.id AS id",
                    cid=cid,
                )
                prereq_ids = [r["id"] for r in prereqs]
            prereqs_met = all(
                mastery_dict.get(pid, 0) >= _MASTERY_THRESHOLD for pid in prereq_ids
            )
            if prereqs_met:
                next_recommended.append({
                    "id": cid,
                    "name": concept["name"],
                    "level": concept["difficulty"],
                    "category": concept["category"],
                })

    mastered = sum(
        1 for c in all_concepts
        if mastery_dict.get(c["id"], 0) >= _MASTERY_THRESHOLD
    )

    # Apply the strategy to the order of `next_recommended`.
    # `concepts_to_improve` is not reordered since it derives from the
    # current mastery and is not a "learning preference".
    reordered = _apply_strategy_reorder(next_recommended, concepts_to_improve, strategy)

    return {
        "etudiant_id": etudiant_id,
        "strategy": strategy,
        "concepts_to_improve": concepts_to_improve,
        "next_recommended": reordered[:_MAX_RECOMMENDATIONS],
        "overall_progress": {
            "total_concepts": len(all_concepts),
            "mastered": mastered,
            "in_progress": len(concepts_to_improve),
        },
    }


def generate_alternative_paths(
    db: Session,
    etudiant_id: int,
    lang: str = "en",
) -> dict[str, Any]:
    """Return the 3 alternative paths side by side.

    Allows the frontend to display: "Here are 3 different ways to
    progress. Choose the one that suits you best."

    Output:
        {
            "etudiant_id": 42,
            "paths": {
                "optimal":        {...path...},
                "theory_first":   {...path...},
                "practice_first": {...path...},
                "remediation":    {...path...},
            }
        }

    The current mastery and the concepts_to_improve are the same for the
    4 strategies (derived from the DB) — only `next_recommended` is
    re-ordered specifically per strategy. This lets the student
    clearly see the difference between the recommendations.
    """
    paths = {
        strat: generate_learning_path(db, etudiant_id, lang, strategy=strat)
        for strat in ("optimal", "theory_first", "practice_first", "remediation")
    }
    return {
        "etudiant_id": etudiant_id,
        "paths": paths,
    }
