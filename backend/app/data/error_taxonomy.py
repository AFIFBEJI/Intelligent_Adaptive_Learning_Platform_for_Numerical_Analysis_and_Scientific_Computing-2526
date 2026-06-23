"""Taxonomy of student errors for misconception detection.

Why ?
=====
The PFE proposal promises to "detect conceptual errors and trigger targeted
remediation". Before this module, the system only knew whether an answer
was CORRECT or WRONG. Not WHY it was wrong.

This taxonomy now allows classifying errors by type (conceptual,
computational, method, etc.) and proposing targeted remediation rather
than a "you are wrong, redo the quiz".

Inspired by the ITS literature :
- Smith et al. (1993) Misconceptions Reconceived (JLS).
- Carnegie Mellon Cognitive Tutor (Anderson, 1995) : 30+ error types.
- Nuthall (2007) The Hidden Lives of Learners.

Structure
=========
Each error has :
  - code   : stable identifier (used in the exports / paper)
  - label_fr / label_en : short label for the frontend
  - description_fr / description_en : pedagogical explanation
  - remediation_hint : action suggestion (read X, redo Y, etc.)
"""
from __future__ import annotations

# ============================================================
# Taxonomy of 12 common error types in numerical analysis
# ============================================================
ERROR_TAXONOMY: dict[str, dict[str, str]] = {
    # === CONCEPTUAL errors (wrong understanding of the principle) ===
    "concept_misidentification": {
        "category": "conceptual",
        "label_fr": "Confusion entre methodes",
        "label_en": "Method confusion",
        "description_fr": "L'etudiant confond deux methodes voisines (ex: "
                         "Newton-Raphson vs Newton-interpolation).",
        "description_en": "Student confuses two related methods (e.g., "
                         "Newton-Raphson vs Newton interpolation).",
        "remediation_hint": "Revoir la definition formelle des deux methodes "
                            "et leurs cas d'usage respectifs.",
    },
    "wrong_formula": {
        "category": "conceptual",
        "label_fr": "Mauvaise formule appliquee",
        "label_en": "Wrong formula applied",
        "description_fr": "L'etudiant utilise une formule incorrecte ou hors "
                         "domaine de validite.",
        "description_en": "Student uses an incorrect formula or one outside "
                         "its validity domain.",
        "remediation_hint": "Revoir la formule canonique et ses hypotheses.",
    },
    "prerequisite_gap": {
        "category": "conceptual",
        "label_fr": "Lacune sur un prerequis",
        "label_en": "Prerequisite gap",
        "description_fr": "L'erreur revele que l'etudiant n'a pas maitrise "
                         "un concept prerequis necessaire.",
        "description_en": "The error reveals an unmastered prerequisite concept.",
        "remediation_hint": "Reviser le concept prerequis avant de revenir.",
    },
    "boundary_confusion": {
        "category": "conceptual",
        "label_fr": "Confusion sur les bornes / limites",
        "label_en": "Boundary confusion",
        "description_fr": "L'etudiant confond les bornes d'integration, les "
                         "indices d'iteration, ou les conditions limites.",
        "description_en": "Student confuses integration bounds, iteration "
                         "indices, or boundary conditions.",
        "remediation_hint": "Refaire un exemple avec attention aux bornes.",
    },

    # === COMPUTATIONAL errors (the method is right, execution fails) ===
    "arithmetic_error": {
        "category": "computational",
        "label_fr": "Erreur arithmetique",
        "label_en": "Arithmetic error",
        "description_fr": "L'etudiant a la bonne methode mais commet une "
                         "erreur de calcul (signe, division, etc.).",
        "description_en": "Student has the right method but makes a "
                         "calculation error (sign, division, etc.).",
        "remediation_hint": "Refaire le calcul etape par etape, verifier "
                            "les signes.",
    },
    "off_by_one": {
        "category": "computational",
        "label_fr": "Erreur d'un cran",
        "label_en": "Off-by-one error",
        "description_fr": "L'etudiant decale d'un indice (ex: n vs n+1, "
                         "boucle de 0 a n vs 1 a n).",
        "description_en": "Student is off by one index (e.g., n vs n+1, "
                         "loop from 0 to n vs 1 to n).",
        "remediation_hint": "Verifier explicitement les indices de debut "
                            "et de fin.",
    },
    "sign_error": {
        "category": "computational",
        "label_fr": "Erreur de signe",
        "label_en": "Sign error",
        "description_fr": "Inversion d'un signe + / - dans le calcul.",
        "description_en": "Inversion of a + / - sign in the calculation.",
        "remediation_hint": "Refaire le calcul en mettant les signes en "
                            "couleur differente.",
    },

    # === METHOD errors (wrong tool for the right problem) ===
    "wrong_method": {
        "category": "method",
        "label_fr": "Methode inadaptee",
        "label_en": "Inappropriate method",
        "description_fr": "L'etudiant applique une methode qui ne convient "
                         "pas au probleme (ex: trapeze quand Simpson est requis).",
        "description_en": "Student applies a method ill-suited to the "
                         "problem (e.g., trapezoidal when Simpson required).",
        "remediation_hint": "Revoir le tableau des conditions d'application "
                            "de chaque methode.",
    },
    "convergence_misunderstanding": {
        "category": "method",
        "label_fr": "Conditions de convergence ignorees",
        "label_en": "Convergence conditions ignored",
        "description_fr": "L'etudiant applique une methode iterative sans "
                         "verifier ses conditions de convergence.",
        "description_en": "Student applies an iterative method without "
                         "checking convergence conditions.",
        "remediation_hint": "Verifier les hypotheses de convergence avant "
                            "d'iterer.",
    },

    # === PERCEPTION / reading errors ===
    "misread_problem": {
        "category": "perception",
        "label_fr": "Lecture incorrecte de l'enonce",
        "label_en": "Misread the problem",
        "description_fr": "L'etudiant a mal lu l'enonce (valeur, signe, "
                         "domaine).",
        "description_en": "Student misread the problem statement (value, "
                         "sign, domain).",
        "remediation_hint": "Relire l'enonce avant de commencer.",
    },
    "notation_confusion": {
        "category": "perception",
        "label_fr": "Confusion de notation",
        "label_en": "Notation confusion",
        "description_fr": "L'etudiant confond deux notations (ex: indices, "
                         "exposants, sommes).",
        "description_en": "Student confuses two notations (e.g., indices, "
                         "exponents, sums).",
        "remediation_hint": "Revoir la notation standard utilisee dans le "
                            "cours.",
    },

    # === Default case ===
    "unknown": {
        "category": "unknown",
        "label_fr": "Erreur non categorisee",
        "label_en": "Uncategorized error",
        "description_fr": "Le type d'erreur n'a pas pu etre identifie "
                         "automatiquement. Demander au tuteur.",
        "description_en": "Error type could not be auto-identified. Ask "
                         "the tutor for help.",
        "remediation_hint": "Discuter avec le tuteur IA pour clarifier.",
    },
}

# ============================================================
# Categories (for aggregation and statistics)
# ============================================================
CATEGORIES = {
    "conceptual": "Comprehension du concept",
    "computational": "Execution du calcul",
    "method": "Choix de la methode",
    "perception": "Lecture / notation",
    "unknown": "Non categorise",
}


def get_error_info(code: str, lang: str = "en") -> dict[str, str]:
    """Returns the localized labels of an error code."""
    entry = ERROR_TAXONOMY.get(code, ERROR_TAXONOMY["unknown"])
    label_key = f"label_{lang}" if f"label_{lang}" in entry else "label_en"
    desc_key = f"description_{lang}" if f"description_{lang}" in entry else "description_en"
    return {
        "code": code,
        "category": entry["category"],
        "label": entry[label_key],
        "description": entry[desc_key],
        "remediation_hint": entry["remediation_hint"],
    }


def analyze_error_distribution(error_codes: list[str]) -> dict[str, int]:
    """Counts the errors per category. Useful to identify a student's
    dominant error profile.

    E.g.: {"conceptual": 5, "computational": 2, "method": 1} ->
    the student mostly has comprehension problems, not computation.
    """
    counts: dict[str, int] = {cat: 0 for cat in CATEGORIES}
    for code in error_codes:
        entry = ERROR_TAXONOMY.get(code, ERROR_TAXONOMY["unknown"])
        cat = entry["category"]
        counts[cat] = counts.get(cat, 0) + 1
    return counts
