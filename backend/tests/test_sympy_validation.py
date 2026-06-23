"""
Tests pour la validation SymPy de correctness mathematique.

Ces tests garantissent que verification_service ne se contente pas de
parser les expressions du LLM, mais detecte vraiment quand les maths sont
fausses (anti-hallucination par calcul symbolique).
"""
from __future__ import annotations

import pytest

# Le module pourrait planter sur l'import de SymPy si pas installe.
# Skip toute la suite dans ce cas.
sympy = pytest.importorskip("sympy")

from app.services.verification_service import verification_service  # noqa: E402


class TestVerifyEquation:
    """Tests pour verify_equation : LHS = RHS algebriquement vrai ?"""

    def test_correct_identity_passes(self):
        # (x+1)^2 = x^2 + 2x + 1 est une identite remarquable
        result = verification_service.verify_equation("(x+1)^2 = x^2 + 2*x + 1")
        assert result["status"] == "correct", result

    def test_correct_simple_equation(self):
        result = verification_service.verify_equation("2*x + 3*x = 5*x")
        assert result["status"] == "correct"

    def test_incorrect_equation_detected(self):
        # x^2 + 1 != 0 en general (l'enseignant peut se tromper)
        result = verification_service.verify_equation("x^2 + 1 = 0")
        assert result["status"] == "incorrect"
        assert "difference" in result

    def test_wrong_derivative_detected(self):
        # Une "regle de derivation" fausse comme la pourrait halluciner un LLM
        result = verification_service.verify_equation("(x^2 + 3*x) = 2*x + 3")
        # x^2 + 3x != 2x + 3, devrait etre signale incorrect
        assert result["status"] == "incorrect"

    def test_unverifiable_when_no_equals(self):
        result = verification_service.verify_equation("x^2 + 2")
        assert result["status"] == "unverifiable"


class TestVerifyDerivativeClaim:
    """Tests pour verify_derivative_claim : d/dx f = g ?"""

    def test_polynomial_derivative_correct(self):
        # d/dx (x^2) = 2x
        result = verification_service.verify_derivative_claim("x^2", "2*x")
        assert result["status"] == "correct"

    def test_sin_derivative_correct(self):
        result = verification_service.verify_derivative_claim("sin(x)", "cos(x)")
        assert result["status"] == "correct"

    def test_wrong_derivative_detected(self):
        # d/dx(x^2) != 3x — une hallucination tres plausible d'un LLM
        result = verification_service.verify_derivative_claim("x^2", "3*x")
        assert result["status"] == "incorrect"
        assert "expected" in result
        assert "claimed" in result


class TestVerifyIntegralClaim:
    """Tests pour verify_integral_claim : indefinie et definie."""

    def test_indefinite_integral_correct(self):
        # int x^2 dx = x^3/3 (constante d'integration toleree)
        result = verification_service.verify_integral_claim("x^2", "x^3/3")
        assert result["status"] == "correct"

    def test_definite_integral_zero_to_one(self):
        # int_0^1 x dx = 1/2
        result = verification_service.verify_integral_claim(
            "x", "1/2", a="0", b="1",
        )
        assert result["status"] == "correct"

    def test_wrong_integral_detected(self):
        # int x dx = x^3 (faux : devrait etre x^2/2)
        result = verification_service.verify_integral_claim("x", "x^3")
        assert result["status"] == "incorrect"


class TestExtractAndCheckEquations:
    """Tests pour la fonction qui scanne tout un texte LLM."""

    def test_finds_equation_in_latex_block(self):
        text = "On a la formule $\\sin^2(x) + \\cos^2(x) = 1$ qui marche partout."
        results = verification_service.extract_and_check_equations(text)
        assert len(results) >= 1
        # L'identite trigonometrique est correcte
        assert any(r["status"] == "correct" for r in results)

    def test_catches_hallucinated_equation(self):
        # Un LLM qui se trompe sur une egalite simple
        text = "Donc $x^2 = x$ pour tout x reel."  # FAUX
        results = verification_service.extract_and_check_equations(text)
        assert any(r["status"] == "incorrect" for r in results)

    def test_no_equations_found_returns_empty(self):
        text = "Voici une explication sans formule mathematique."
        results = verification_service.extract_and_check_equations(text)
        assert results == []


class TestVerifyResponseEndToEnd:
    """End-to-end : la methode top-level verify_response."""

    def test_correct_response_marked_verified(self):
        text = "L'identite $\\sin^2(x) + \\cos^2(x) = 1$ est fondamentale."
        result = verification_service.verify_response(text)
        assert result["verified"] is True
        # On doit avoir au moins une equation verifiee
        assert result.get("equations_correct", 0) >= 1

    def test_response_with_wrong_equation_marked_unverified(self):
        text = "On a $x^2 = x$ pour tous les x."  # equation fausse
        result = verification_service.verify_response(text)
        assert result["verified"] is False
        assert result.get("equations_incorrect", 0) >= 1

    def test_response_without_math_is_verified(self):
        text = "Ce texte ne contient aucune formule a verifier."
        result = verification_service.verify_response(text)
        assert result["verified"] is True
        assert result["total_expressions"] == 0
