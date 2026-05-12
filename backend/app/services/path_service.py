"""Source unique pour la generation du parcours d'apprentissage personnalise.

Pourquoi ce service ?
=====================
Avant le 12 mai 2026 deux versions de `generate_learning_path` coexistaient :

1. `services/graph_service.py:generate_learning_path` (la plus ancienne, sans
   support bilingue ni ordre pedagogique fixe).
2. `routers/graph.py:get_learning_path` (la version utilisee en production,
   avec `lang` parameter + `_MODULE_ORDER_CASE` + `_DIFFICULTY_ORDER_CASE`).

L'audit senior du 12/05/2026 a constate que la version 1 etait DEAD CODE
(zero caller dans tout le repo). Mais la duplication etait quand-meme un
risque : si la formule de recommandation evolue, on penserait peut-etre
mettre a jour la mauvaise version par habitude.

Ce module reprend la VERSION RICHE (avec bilingue + ordre pedagogique) en
service callable. Le router devient un simple thin wrapper. L'ancienne
methode de graph_service est supprimee.

Algorithme
==========
1. Recuperer la maitrise actuelle de l'etudiant (ConceptMastery sur Postgres).
2. Recuperer tous les concepts du graphe Neo4j (nommes dans la langue cible).
3. Pour chaque concept :
     - 0 < mastery < 70  -> `concepts_to_improve` (en cours)
     - mastery == 0      -> verifier les prerequis :
         - prerequis tous >= 70 -> `next_recommended` (debloque)
         - sinon -> ignore (encore trop tot)
4. Top 5 recommandes pour ne pas submerger l'etudiant.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.graph.neo4j_connection import neo4j_conn
from app.models.mastery import ConceptMastery

# ============================================================
# Constantes pedagogiques (memes valeurs que dans routers/graph.py)
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

# Seuil de maitrise (en %) au-dessus duquel un prerequis est considere
# comme acquis. Aligne avec settings.MASTERY_THRESHOLD = 70.0.
_MASTERY_THRESHOLD = 70.0

# Nombre max de concepts a recommander d'un coup (eviter de submerger).
_MAX_RECOMMENDATIONS = 5


def _normalize_lang(lang: str | None) -> str:
    """Normalise une langue arbitraire vers 'fr' ou 'en' (defaut: 'en')."""
    if not lang:
        return "en"
    lang = lang.lower().strip()
    return "fr" if lang.startswith("fr") else "en"


def generate_learning_path(
    db: Session,
    etudiant_id: int,
    lang: str = "en",
) -> dict[str, Any]:
    """Genere un parcours d'apprentissage personnalise (bilingue).

    Args:
        db: session SQLAlchemy (Postgres) pour lire ConceptMastery.
        etudiant_id: id de l'etudiant.
        lang: 'fr' ou 'en' (autre = fallback 'en').

    Returns:
        Dict serialisable JSON :
        {
            "etudiant_id": 42,
            "concepts_to_improve": [{id, name, mastery, status}, ...],
            "next_recommended": [{id, name, level, category}, ...] (max 5),
            "overall_progress": {total_concepts, mastered, in_progress},
        }
    """
    lang = _normalize_lang(lang)

    # 1. Lire la maitrise de l'etudiant depuis Postgres.
    mastery_rows = (
        db.query(ConceptMastery)
        .filter(ConceptMastery.etudiant_id == etudiant_id)
        .all()
    )
    mastery_dict = {m.concept_neo4j_id: m.niveau_maitrise for m in mastery_rows}

    # 2. Lire tous les concepts depuis Neo4j, dans la langue voulue.
    #    L'ordre pedagogique (module-id, difficulte) est applique cote Cypher
    #    pour rester stable independamment de la langue.
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

    # 3. Classer les concepts.
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
            # Verifier que tous les prerequis sont a >= seuil.
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

    return {
        "etudiant_id": etudiant_id,
        "concepts_to_improve": concepts_to_improve,
        "next_recommended": next_recommended[:_MAX_RECOMMENDATIONS],
        "overall_progress": {
            "total_concepts": len(all_concepts),
            "mastered": mastered,
            "in_progress": len(concepts_to_improve),
        },
    }
