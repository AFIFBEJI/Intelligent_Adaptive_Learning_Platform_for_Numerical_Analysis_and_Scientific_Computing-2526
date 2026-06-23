from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.i18n import http_msg
from app.core.security import get_current_user
from app.graph.neo4j_connection import neo4j_conn

router = APIRouter(prefix="/graph", tags=["graph"])


def _normalize_lang(lang: str | None) -> str:
    """Restricts the value to 'en' or 'fr'. Default = 'en'."""
    return "fr" if (lang or "").lower() == "fr" else "en"


# Fixed pedagogical order of modules (independent of the display language).
# Used as the primary sort key for concept/module lists
# so that the order is identical in FR and EN.
_MODULE_ORDER_CASE = """CASE m.id
    WHEN 'module_interpolation' THEN 1
    WHEN 'module_integration'   THEN 2
    WHEN 'module_approximation' THEN 3
    WHEN 'module_root_finding'  THEN 4
    ELSE 99
END"""

# Fixed pedagogical order of difficulties (beginner -> intermediate -> advanced).
# Used to keep the same order regardless of the language.
_DIFFICULTY_ORDER_CASE = """CASE c.difficulty
    WHEN 'beginner'     THEN 1
    WHEN 'intermediate' THEN 2
    WHEN 'advanced'     THEN 3
    ELSE 99
END"""


@router.get("/health")
def graph_health(lang: str = "en"):
    """Check the connection to Neo4j"""
    lang = _normalize_lang(lang)
    try:
        with neo4j_conn.get_session() as session:
            session.run("RETURN 1 AS ok").single()
        return {"status": "connected", "database": "neo4j"}
    except Exception as e:
        # Log the real error server-side, return a generic message (no leak).
        import logging
        logging.getLogger(__name__).warning("Neo4j unavailable: %s", e)
        raise HTTPException(
            status_code=503,
            detail=http_msg("graph.neo4j_unavailable", lang, error="unavailable"),
        ) from e


@router.get("/modules")
def get_modules(lang: str = "en"):
    """Return all the knowledge graph modules in the requested language.
    Fixed pedagogical order (Module 1 -> 2 -> 3), regardless of the language."""
    lang = _normalize_lang(lang)
    with neo4j_conn.get_session() as session:
        result = session.run(
            f"""
            MATCH (m:Module)
            RETURN m.id AS id,
                   CASE WHEN $lang = 'fr' THEN coalesce(m.name_fr, m.name) ELSE m.name END AS name,
                   CASE WHEN $lang = 'fr' THEN coalesce(m.description_fr, m.description) ELSE m.description END AS description
            ORDER BY {_MODULE_ORDER_CASE}, m.id
            """,
            lang=lang,
        )
        return [dict(record) for record in result]


@router.get("/modules/{module_id}/concepts")
def get_module_concepts(module_id: str, lang: str = "en"):
    """Return the concepts of a module in the requested language.
    Order: ascending difficulty then name (independent of the display language)."""
    lang = _normalize_lang(lang)
    with neo4j_conn.get_session() as session:
        result = session.run(
            f"""
            MATCH (m:Module {{id: $module_id}})-[:COVERS]->(c:Concept)
            RETURN c.id AS id,
                   CASE WHEN $lang = 'fr' THEN coalesce(c.name_fr, c.name) ELSE c.name END AS name,
                   CASE WHEN $lang = 'fr' THEN coalesce(c.description_fr, c.description) ELSE c.description END AS description,
                   c.difficulty AS difficulty
            ORDER BY {_DIFFICULTY_ORDER_CASE}, c.id
            """,
            module_id=module_id,
            lang=lang,
        )
        concepts = [dict(record) for record in result]
        if not concepts:
            raise HTTPException(status_code=404, detail=http_msg("graph.module_not_found", lang, id=module_id))
        return concepts


@router.get("/concepts")
def get_all_concepts(lang: str = "en"):
    """Return all the knowledge graph concepts in the requested language.

    `lang=fr` -> `name_fr`/`description_fr` (fallback `name`/`description`).
    `lang=en` -> `name`/`description` (English is the default seeded value).

    Fixed pedagogical order (M1 Interpolation -> M2 Integration -> M3 Approximation),
    independent of the language: we sort on the module's identifier, not on its
    translated name, to keep the same order in EN and FR.
    """
    lang = _normalize_lang(lang)
    with neo4j_conn.get_session() as session:
        result = session.run(
            f"""
            MATCH (m:Module)-[:COVERS]->(c:Concept)
            RETURN c.id AS id,
                   CASE WHEN $lang = 'fr' THEN coalesce(c.name_fr, c.name) ELSE c.name END AS name,
                   CASE WHEN $lang = 'fr' THEN coalesce(c.description_fr, c.description) ELSE c.description END AS description,
                   c.difficulty AS level,
                   CASE WHEN $lang = 'fr' THEN coalesce(m.name_fr, m.name) ELSE m.name END AS category
            ORDER BY {_MODULE_ORDER_CASE}, {_DIFFICULTY_ORDER_CASE}, c.id
            """,
            lang=lang,
        )
        return [dict(record) for record in result]


@router.get("/concepts/{concept_id}/prerequisites")
def get_prerequisites(concept_id: str, lang: str = "en"):
    """Return the prerequisites of a concept in the requested language."""
    lang = _normalize_lang(lang)
    with neo4j_conn.get_session() as session:
        result = session.run(
            """
            MATCH (c:Concept {id: $concept_id})-[:REQUIRES]->(prereq:Concept)
            RETURN prereq.id AS id,
                   CASE WHEN $lang = 'fr' THEN coalesce(prereq.name_fr, prereq.name) ELSE prereq.name END AS name,
                   prereq.difficulty AS difficulty
            ORDER BY prereq.difficulty
            """,
            concept_id=concept_id,
            lang=lang,
        )
        return [dict(record) for record in result]


@router.get("/concepts/{concept_id}/resources")
def get_concept_resources(concept_id: str, lang: str = "en"):
    """Return the educational resources of a concept in the requested language."""
    lang = _normalize_lang(lang)
    with neo4j_conn.get_session() as session:
        result = session.run(
            """
            MATCH (c:Concept {id: $concept_id})-[:REMEDIATES_TO]->(r:Resource)
            RETURN r.id AS id,
                   CASE WHEN $lang = 'fr' THEN coalesce(r.name_fr, r.name) ELSE r.name END AS title,
                   r.type AS type,
                   r.url AS url
            """,
            concept_id=concept_id,
            lang=lang,
        )
        resources = [dict(record) for record in result]
        if not resources:
            raise HTTPException(status_code=404, detail=http_msg("graph.concept_not_found", lang, id=concept_id))
        return resources


@router.get("/learning-path/{etudiant_id}")
def get_learning_path(
    etudiant_id: int,
    lang: str = "en",
    strategy: str = "optimal",
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Generate ONE personalized learning path according to the strategy.

    Query params:
        lang     : 'fr' | 'en' (default 'en')
        strategy : 'optimal' | 'theory_first' | 'practice_first' | 'remediation'

    Thin wrapper over `path_service.generate_learning_path`.
    To GET THE 3 ALTERNATIVES in one call: see
    GET /graph/learning-paths/{etudiant_id} (note the plural).
    """
    # IDOR protection: a student can only read THEIR OWN learning path.
    if etudiant_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    from app.services.path_service import generate_learning_path
    return generate_learning_path(db, etudiant_id, lang, strategy=strategy)


@router.get("/learning-paths/{etudiant_id}")
def get_alternative_learning_paths(
    etudiant_id: int,
    lang: str = "en",
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """Return the 4 alternative paths side-by-side for comparison.

    The frontend can display 4 cards: optimal, theory-first,
    practice-first, remediation. The student clicks the one that speaks
    to them the most, which fulfills the 'alternative learning paths'
    promise of the PFE proposal.
    """
    # IDOR protection: a student can only read THEIR OWN learning paths.
    if etudiant_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    from app.services.path_service import generate_alternative_paths
    return generate_alternative_paths(db, etudiant_id, lang)


@router.get("/remediation/{concept_id}")
def get_remediation(concept_id: str, lang: str = "en"):
    """Return the remediation resources for a concept in the requested language."""
    lang = _normalize_lang(lang)
    with neo4j_conn.get_session() as session:
        result = session.run(
            """
            MATCH (c:Concept {id: $concept_id})-[:REMEDIATES_TO]->(r:Resource)
            RETURN r.id AS id,
                   CASE WHEN $lang = 'fr' THEN coalesce(r.name_fr, r.name) ELSE r.name END AS title,
                   r.type AS type,
                   r.url AS url
            """,
            concept_id=concept_id,
            lang=lang,
        )
        resources = [dict(record) for record in result]
        if not resources:
            raise HTTPException(status_code=404, detail=http_msg("graph.no_remediation", lang, id=concept_id))
        return resources

@router.get("/concepts/{concept_id}/content")
def get_concept_content(
    concept_id: str,
    level: str = None,
    lang: str = "en",
    db: Session = Depends(get_db),
):
    """Return the educational content adapted to the student's level.

    The content is served in the requested language:
      - lang=fr -> title_fr / body_fr (fallback title/body if not available)
      - lang=en -> title_en / body_en (fallback title/body if not available)
    """
    lang = _normalize_lang(lang)
    # If no level specified, return the 3 levels
    if level:
        with neo4j_conn.get_session() as session:
            result = session.run(
                """
                MATCH (c:Concept {id: $concept_id})-[:HAS_CONTENT]->(ct:Content {level: $level})
                RETURN ct.id AS id,
                       CASE WHEN $lang = 'fr' THEN coalesce(ct.title_fr, ct.title) ELSE coalesce(ct.title_en, ct.title) END AS title,
                       ct.level AS level,
                       CASE WHEN $lang = 'fr' THEN coalesce(ct.body_fr, ct.body) ELSE coalesce(ct.body_en, ct.body) END AS body
                """,
                concept_id=concept_id, level=level, lang=lang
            )
            contents = [dict(r) for r in result]
    else:
        with neo4j_conn.get_session() as session:
            result = session.run(
                """
                MATCH (c:Concept {id: $concept_id})-[:HAS_CONTENT]->(ct:Content)
                RETURN ct.id AS id,
                       CASE WHEN $lang = 'fr' THEN coalesce(ct.title_fr, ct.title) ELSE coalesce(ct.title_en, ct.title) END AS title,
                       ct.level AS level,
                       CASE WHEN $lang = 'fr' THEN coalesce(ct.body_fr, ct.body) ELSE coalesce(ct.body_en, ct.body) END AS body
                ORDER BY CASE ct.level
                    WHEN 'simplified' THEN 1
                    WHEN 'standard' THEN 2
                    WHEN 'rigorous' THEN 3
                END
                """,
                concept_id=concept_id, lang=lang
            )
            contents = [dict(r) for r in result]

    if not contents:
        raise HTTPException(status_code=404, detail=http_msg("graph.no_content", lang, id=concept_id))
    return contents


@router.get("/concepts/{concept_id}/adaptive-content")
def get_adaptive_content(concept_id: str, lang: str = "en",
                         db: Session = Depends(get_db),
                         current_user_id: int = Depends(get_current_user)):
    """Return the content automatically adapted to the student's mastery level
    and localized according to `lang`."""
    from app.models.mastery import ConceptMastery

    lang = _normalize_lang(lang)

    # Retrieve the student's mastery of this concept
    mastery = db.query(ConceptMastery).filter(
        ConceptMastery.etudiant_id == current_user_id,
        ConceptMastery.concept_neo4j_id == concept_id
    ).first()

    # Choose the level according to the mastery
    niveau = mastery.niveau_maitrise if mastery else 0
    if niveau < 40:
        level = "simplified"
    elif niveau < 75:
        level = "standard"
    else:
        level = "rigorous"

    with neo4j_conn.get_session() as session:
        result = session.run(
            """
            MATCH (c:Concept {id: $concept_id})-[:HAS_CONTENT]->(ct:Content {level: $level})
            RETURN ct.id AS id,
                   CASE WHEN $lang = 'fr' THEN coalesce(ct.title_fr, ct.title) ELSE coalesce(ct.title_en, ct.title) END AS title,
                   ct.level AS level,
                   CASE WHEN $lang = 'fr' THEN coalesce(ct.body_fr, ct.body) ELSE coalesce(ct.body_en, ct.body) END AS body
            """,
            concept_id=concept_id, level=level, lang=lang,
        )
        contents = [dict(r) for r in result]

    if not contents:
        raise HTTPException(status_code=404, detail=http_msg("graph.no_content", lang, id=concept_id))

    return {"mastery": niveau, "selected_level": level, "content": contents[0]}


@router.get("/stats")
def get_graph_stats():
    """Global statistics of the knowledge graph"""
    with neo4j_conn.get_session() as session:
        stats = {}
        for label in ["Module", "Concept", "Resource"]:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) AS count")
            stats[label.lower() + "s"] = result.single()["count"]
        for rel in ["COVERS", "REQUIRES", "REMEDIATES_TO"]:
            result = session.run(f"MATCH ()-[r:{rel}]->() RETURN count(r) AS count")
            stats[rel.lower()] = result.single()["count"]
        return stats
