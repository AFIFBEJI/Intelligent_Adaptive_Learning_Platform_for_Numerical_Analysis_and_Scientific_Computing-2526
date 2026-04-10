from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.quiz import Quiz, QuizResult
from app.models.mastery import ConceptMastery
from app.schemas.quiz import (
    QuizCreate,
    QuizResponse,
    QuizResultCreate,
    QuizResultResponse,
)

router = APIRouter(prefix="/quiz", tags=["quiz"])

# ============================================================
# Neo4j concept → quiz module mapping
# ============================================================
MODULE_CONCEPT_MAP = {
    "Interpolation": [
        "concept_polynomial_basics", "concept_lagrange",
        "concept_divided_differences", "concept_newton_interpolation",
        "concept_spline_interpolation"
    ],
    "Numerical Integration": [
        "concept_riemann_sums", "concept_definite_integrals",
        "concept_trapezoidal", "concept_simpson",
        "concept_gaussian_quadrature"
    ],
    "ODEs": [
        "concept_initial_value", "concept_taylor_series",
        "concept_euler", "concept_improved_euler",
        "concept_rk4"
    ],
}

DIFFICULTY_CONCEPT_MAP = {
    "Interpolation": {
        "facile": "concept_polynomial_basics",
        "moyen": "concept_lagrange",
        "difficile": "concept_spline_interpolation",
    },
    "Numerical Integration": {
        "facile": "concept_riemann_sums",
        "moyen": "concept_trapezoidal",
        "difficile": "concept_gaussian_quadrature",
    },
    "ODEs": {
        "facile": "concept_initial_value",
        "moyen": "concept_euler",
        "difficile": "concept_rk4",
    },
}


def update_mastery(db: Session, etudiant_id: int, concept_id: str, score: float):
    """Update the mastery level of a concept for a student."""
    mastery = db.query(ConceptMastery).filter(
        ConceptMastery.etudiant_id == etudiant_id,
        ConceptMastery.concept_neo4j_id == concept_id
    ).first()

    if mastery:
        # Weighted average: 60% old + 40% new score
        mastery.niveau_maitrise = round(mastery.niveau_maitrise * 0.6 + score * 0.4, 1)
        mastery.derniere_mise_a_jour = datetime.now(timezone.utc)
    else:
        mastery = ConceptMastery(
            etudiant_id=etudiant_id,
            concept_neo4j_id=concept_id,
            niveau_maitrise=round(score, 1),
            derniere_mise_a_jour=datetime.now(timezone.utc)
        )
        db.add(mastery)


@router.post("/", response_model=QuizResponse)
def create_quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Create a new quiz."""
    nouveau_quiz = Quiz(
        titre=quiz_data.titre,
        module=quiz_data.module,
        difficulte=quiz_data.difficulte,
        questions=quiz_data.questions
    )
    db.add(nouveau_quiz)
    db.commit()
    db.refresh(nouveau_quiz)
    return nouveau_quiz


@router.get("/", response_model=List[QuizResponse])
def list_quiz(
    module: str = None,
    difficulte: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """List quizzes with optional filtering."""
    query = db.query(Quiz)
    if module:
        query = query.filter(Quiz.module == module)
    if difficulte:
        query = query.filter(Quiz.difficulte == difficulte)
    return query.offset(skip).limit(limit).all()


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Get a quiz by its ID."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
def submit_quiz(
    quiz_id: int,
    result_data: QuizResultCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Submit a quiz and update mastery automatically."""
    # 1. Check quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # 2. Save result
    quiz_result = QuizResult(
        etudiant_id=current_user_id,
        quiz_id=quiz_id,
        score=result_data.score,
        temps_reponse=result_data.temps_reponse,
        reponses=result_data.reponses
    )
    db.add(quiz_result)

    # 3. ADAPTIVE ALGORITHM: update mastery
    module = quiz.module
    difficulte = quiz.difficulte
    score = result_data.score

    # Find the primary concept linked to this quiz
    concept_id = DIFFICULTY_CONCEPT_MAP.get(module, {}).get(difficulte)
    if concept_id:
        update_mastery(db, current_user_id, concept_id, score)

    # If mixed quiz (difficult), update all concepts in the module
    if difficulte == "difficile" and module in MODULE_CONCEPT_MAP:
        for cid in MODULE_CONCEPT_MAP[module]:
            if cid != concept_id:
                # Reduced impact (50%) for non-targeted concepts
                update_mastery(db, current_user_id, cid, score * 0.5)

    db.commit()
    db.refresh(quiz_result)
    return quiz_result


@router.get("/results/{etudiant_id}", response_model=List[QuizResultResponse])
def get_student_results(
    etudiant_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Student results (own results only)."""
    if current_user_id != etudiant_id:
        raise HTTPException(status_code=403, detail="You can only view your own results")
    return db.query(QuizResult).filter(
        QuizResult.etudiant_id == etudiant_id
    ).offset(skip).limit(limit).all()


@router.get("/next/{etudiant_id}", response_model=QuizResponse)
def get_next_quiz(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """Recommend the next quiz adapted to the student's level."""
    if current_user_id != etudiant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get mastery records
    mastery_records = db.query(ConceptMastery).filter(
        ConceptMastery.etudiant_id == etudiant_id
    ).all()
    mastery_dict = {m.concept_neo4j_id: m.niveau_maitrise for m in mastery_records}

    # Find the best quiz to recommend
    all_quizzes = db.query(Quiz).filter(Quiz.module != "Prerequisites").all()

    # Priority 1: easy quiz from an unstarted module
    for quiz in all_quizzes:
        if quiz.difficulte == "facile":
            concepts = MODULE_CONCEPT_MAP.get(quiz.module, [])
            if concepts and all(mastery_dict.get(c, 0) == 0 for c in concepts):
                return quiz

    # Priority 2: medium quiz from a module with mastery 30-69%
    for quiz in all_quizzes:
        if quiz.difficulte == "moyen":
            concept_id = DIFFICULTY_CONCEPT_MAP.get(quiz.module, {}).get("facile")
            if concept_id and 30 <= mastery_dict.get(concept_id, 0) < 70:
                return quiz

    # Priority 3: hard quiz from a module with mastery >= 70%
    for quiz in all_quizzes:
        if quiz.difficulte == "difficile" and "Mixed" not in quiz.titre:
            concept_id = DIFFICULTY_CONCEPT_MAP.get(quiz.module, {}).get("moyen")
            if concept_id and mastery_dict.get(concept_id, 0) >= 70:
                return quiz

    # Fallback: diagnostic quiz
    diag = db.query(Quiz).filter(Quiz.module == "Prerequisites").first()
    if diag:
        return diag

    raise HTTPException(status_code=404, detail="No quiz available")