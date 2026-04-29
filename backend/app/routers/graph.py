from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.graph.neo4j_connection import neo4j_conn

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/health")
def graph_health():
    """Vérifie la connexion à Neo4j"""
    try:
        with neo4j_conn.get_session() as session:
            session.run("RETURN 1 AS ok").single()
        return {"status": "connected", "database": "neo4j"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Neo4j inaccessible: {str(e)}")


@router.get("/modules")
def get_modules():
    """Retourne tous les modules du knowledge graph"""
    with neo4j_conn.get_session() as session:
        result = session.run(
            "MATCH (m:Module) RETURN m.id AS id, m.name AS name, m.description AS description ORDER BY m.name"
        )
        return [dict(record) for record in result]


@router.get("/modules/{module_id}/concepts")
def get_module_concepts(module_id: str):
    """Retourne les concepts d'un module"""
    with neo4j_conn.get_session() as session:
        result = session.run(
            """
            MATCH (m:Module {id: $module_id})-[:COVERS]->(c:Concept)
            RETURN c.id AS id, c.name AS name, c.description AS description, c.difficulty AS difficulty
            ORDER BY c.difficulty, c.name
            """,
            module_id=module_id
        )
        concepts = [dict(record) for record in result]
        if not concepts:
            raise HTTPException(status_code=404, detail=f"Module '{module_id}' introuvable ou sans concepts")
        return concepts


@router.get("/concepts")
def get_all_concepts():
    """Retourne tous les concepts du knowledge graph"""
    with neo4j_conn.get_session() as session:
        result = session.run(
            """
            MATCH (m:Module)-[:COVERS]->(c:Concept)
            RETURN c.id AS id, c.name AS name, c.description AS description,
                   c.difficulty AS level, m.name AS category
            ORDER BY m.name, c.difficulty, c.name
            """
        )
        return [dict(record) for record in result]


@router.get("/concepts/{concept_id}/prerequisites")
def get_prerequisites(concept_id: str):
    """Retourne les prérequis d'un concept"""
    with neo4j_conn.get_session() as session:
        result = session.run(
            """
            MATCH (c:Concept {id: $concept_id})-[:REQUIRES]->(prereq:Concept)
            RETURN prereq.id AS id, prereq.name AS name, prereq.difficulty AS difficulty
            ORDER BY prereq.difficulty
            """,
            concept_id=concept_id
        )
        return [dict(record) for record in result]


@router.get("/concepts/{concept_id}/resources")
def get_concept_resources(concept_id: str):
    """Retourne les ressources pédagogiques d'un concept"""
    with neo4j_conn.get_session() as session:
        result = session.run(
            """
            MATCH (c:Concept {id: $concept_id})-[:REMEDIATES_TO]->(r:Resource)
            RETURN r.id AS id, r.name AS title, r.type AS type, r.url AS url
            """,
            concept_id=concept_id
        )
        resources = [dict(record) for record in result]
        if not resources:
            raise HTTPException(status_code=404, detail=f"Concept '{concept_id}' introuvable ou sans ressources")
        return resources


@router.get("/learning-path/{etudiant_id}")
def get_learning_path(
    etudiant_id: int,
    db: Session = Depends(get_db)
):
    """Génère un parcours d'apprentissage personnalisé"""
    from app.models.mastery import ConceptMastery

    # 1. Récupérer la maîtrise de l'étudiant depuis PostgreSQL
    mastery_records = db.query(ConceptMastery).filter(
        ConceptMastery.etudiant_id == etudiant_id
    ).all()
    mastery_dict = {m.concept_neo4j_id: m.niveau_maitrise for m in mastery_records}

    # 2. Récupérer tous les concepts depuis Neo4j
    with neo4j_conn.get_session() as session:
        result = session.run(
            """
            MATCH (m:Module)-[:COVERS]->(c:Concept)
            RETURN c.id AS id, c.name AS name, c.difficulty AS difficulty, m.name AS category
            ORDER BY m.name, c.difficulty
            """
        )
        all_concepts = [dict(r) for r in result]

    # 3. Calculer progression
    concepts_to_improve = []
    next_recommended = []

    for concept in all_concepts:
        cid = concept["id"]
        mastery = mastery_dict.get(cid, 0)

        if 0 < mastery < 70:
            concepts_to_improve.append({
                "id": cid, "name": concept["name"],
                "mastery": mastery, "status": "in_progress"
            })
        elif mastery == 0:
            # Vérifier prérequis dans Neo4j
            with neo4j_conn.get_session() as session:
                prereqs = session.run(
                    "MATCH (c:Concept {id: $cid})-[:REQUIRES]->(p:Concept) RETURN p.id AS id",
                    cid=cid
                )
                prereq_ids = [r["id"] for r in prereqs]

            prereqs_met = all(mastery_dict.get(pid, 0) >= 70 for pid in prereq_ids)
            if prereqs_met:
                next_recommended.append({
                    "id": cid, "name": concept["name"],
                    "level": concept["difficulty"], "category": concept["category"]
                })

    mastered = len([c for c in all_concepts if mastery_dict.get(c["id"], 0) >= 70])

    return {
        "etudiant_id": etudiant_id,
        "concepts_to_improve": concepts_to_improve,
        "next_recommended": next_recommended[:5],
        "overall_progress": {
            "total_concepts": len(all_concepts),
            "mastered": mastered,
            "in_progress": len(concepts_to_improve)
        }
    }


@router.get("/remediation/{concept_id}")
def get_remediation(concept_id: str):
    """Retourne les ressources de remédiation pour un concept"""
    with neo4j_conn.get_session() as session:
        result = session.run(
            """
            MATCH (c:Concept {id: $concept_id})-[:REMEDIATES_TO]->(r:Resource)
            RETURN r.id AS id, r.name AS title, r.type AS type, r.url AS url
            """,
            concept_id=concept_id
        )
        resources = [dict(record) for record in result]
        if not resources:
            raise HTTPException(status_code=404, detail=f"Pas de remédiation pour '{concept_id}'")
        return resources

@router.get("/concepts/{concept_id}/content")
def get_concept_content(
    concept_id: str,
    level: str = None,
    lang: str = "en",
    db: Session = Depends(get_db),
):
    """Retourne le contenu pédagogique adapté au niveau de l'étudiant"""
    lang = "fr" if lang == "fr" else "en"
    # Si pas de niveau spécifié, retourner les 3 niveaux
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
        raise HTTPException(status_code=404, detail=f"Pas de contenu pour '{concept_id}'")
    return contents


@router.get("/concepts/{concept_id}/adaptive-content")
def get_adaptive_content(concept_id: str, db: Session = Depends(get_db),
                         current_user_id: int = Depends(get_current_user)):
    """Retourne le contenu adapté automatiquement au niveau de maîtrise de l'étudiant"""
    from app.models.mastery import ConceptMastery

    # Récupérer la maîtrise de l'étudiant sur ce concept
    mastery = db.query(ConceptMastery).filter(
        ConceptMastery.etudiant_id == current_user_id,
        ConceptMastery.concept_neo4j_id == concept_id
    ).first()

    # Choisir le niveau selon la maîtrise
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
            RETURN ct.id AS id, ct.title AS title, ct.level AS level, ct.body AS body
            """,
            concept_id=concept_id, level=level
        )
        contents = [dict(r) for r in result]

    if not contents:
        raise HTTPException(status_code=404, detail=f"Pas de contenu pour '{concept_id}'")

    return {"mastery": niveau, "selected_level": level, "content": contents[0]}


@router.get("/stats")
def get_graph_stats():
    """Statistiques globales du knowledge graph"""
    with neo4j_conn.get_session() as session:
        stats = {}
        for label in ["Module", "Concept", "Resource"]:
            result = session.run(f"MATCH (n:{label}) RETURN count(n) AS count")
            stats[label.lower() + "s"] = result.single()["count"]
        for rel in ["COVERS", "REQUIRES", "REMEDIATES_TO"]:
            result = session.run(f"MATCH ()-[r:{rel}]->() RETURN count(r) AS count")
            stats[rel.lower()] = result.single()["count"]
        return stats
