# ============================================================
# Service de Vérification Mathématique — SymPy
# ============================================================
# C'est quoi ce fichier ?
#
# Après que le LLM répond à l'étudiant, on VÉRIFIE que les
# formules mathématiques dans la réponse sont correctes.
#
# POURQUOI ? Les LLMs (le LLM, GPT...) peuvent "halluciner"
# des formules fausses. Par exemple :
#   - Dire que l'erreur d'Euler est O(h³) au lieu de O(h²)
#   - Écrire une mauvaise formule de Simpson
#   - Se tromper dans une dérivée
#
# COMMENT ? On utilise SymPy, une librairie Python de calcul
# symbolique. SymPy comprend les maths comme un humain :
#   - Il sait que la dérivée de x² est 2x
#   - Il peut simplifier des fractions
#   - Il peut vérifier si deux expressions sont équivalentes
#
# C'est l'architecture "NEURO-SYMBOLIQUE" de votre PFE :
#   Neuro = le LLM (génère du texte naturel)
#   Symbolique = SymPy (vérifie les maths, 100% fiable)
#
# Cette combinaison est ce qui rend votre projet publiable
# dans un journal scientifique (IEEE, etc.)
# ============================================================

import logging
import re
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# On importe SymPy seulement si la vérification est activée
# (pour ne pas ralentir le démarrage si on n'en a pas besoin)
try:
    from sympy import Symbol, diff, integrate, latex, oo, simplify
    from sympy.parsing.sympy_parser import (
        convert_xor,
        implicit_multiplication_application,
        parse_expr,
        standard_transformations,
    )
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    logger.warning("SymPy non installé — vérification mathématique désactivée")


# Symboles standards utilises dans nos validations math.
# On les declare une fois pour eviter de re-creer des Symbol() partout.
_DEFAULT_SYMBOLS: dict[str, "Symbol"] = {}
if SYMPY_AVAILABLE:
    for name in "abcdefghnstxyz":
        _DEFAULT_SYMBOLS[name] = Symbol(name)


def _is_inf(token: str) -> bool:
    """Heuristique : detecte si un bornage d'integrale represente l'infini."""
    if not token:
        return False
    cleaned = token.strip().lower().lstrip("-+")
    return cleaned in {"inf", "infty", "infinity", "oo", "\\infty"}


def _safe_parse(expr_str: str) -> "object | None":
    """Parse une expression nettoyee en object SymPy. Retourne None si echec.

    On encapsule dans un helper pour ne pas dupliquer la logique try/except
    + transformations dans chaque methode de validation.
    """
    if not SYMPY_AVAILABLE:
        return None
    try:
        # SECURITY/UX (12/05/2026) : on ajoute `convert_xor` pour traduire
        # le `^` (XOR en Python pur) vers `**` (puissance) au parsing. Sans
        # cette transformation, "x^2" est interprete comme un XOR bit-a-bit
        # et fait planter la verification. C'est le format LaTeX/scolaire
        # que produisent les LLMs et les enseignants, on doit l'accepter.
        transformations = standard_transformations + (
            implicit_multiplication_application,
            convert_xor,
        )
        return parse_expr(
            expr_str,
            transformations=transformations,
            local_dict=_DEFAULT_SYMBOLS,
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("safe_parse failed for %r : %s", expr_str, exc)
        return None


class VerificationService:
    """
    Service de vérification mathématique.

    Son rôle : prendre la réponse de le LLM, extraire les formules
    LaTeX, et vérifier qu'elles sont syntaxiquement et mathématiquement
    correctes avec SymPy.

    Le résultat est un badge "✅ Vérifié" ou "⚠️ Non vérifié"
    affiché à côté de chaque message du tuteur.
    """

    def __init__(self):
        r"""
        Initialise les patterns regex pour détecter le LaTeX.

        C'est quoi une regex ?
        Une "expression régulière" — un langage de recherche de texte.
        Par exemple, le pattern \$(.+?)\$ cherche tout texte
        entre deux signes $...$ (c'est la syntaxe LaTeX inline).

        On a 3 patterns car LaTeX peut être écrit de 3 façons :
        1. $formule$     → LaTeX inline (dans le texte)
        2. $$formule$$   → LaTeX en bloc (centré, sur sa propre ligne)
        3. \[formule\]   → Autre syntaxe LaTeX en bloc
        """
        # Pattern pour le LaTeX inline : $x^2 + y^2$
        # \$ = un signe dollar littéral
        # (.+?) = capture tout texte entre les $ (le ? = le minimum possible)
        self.inline_pattern = r'\$([^\$]+?)\$'

        # Pattern pour le LaTeX en bloc : $$\int_a^b f(x)dx$$
        self.block_pattern = r'\$\$(.+?)\$\$'

        # Pattern pour \[...\]
        self.bracket_pattern = r'\\\[(.+?)\\\]'

    # ----------------------------------------------------------
    # MÉTHODE 1 : Extraire les expressions LaTeX
    # ----------------------------------------------------------
    def extract_latex(self, text: str) -> list[str]:
        """
        Extrait toutes les expressions LaTeX d'un texte.

        Exemple :
        Input:  "La formule est $x^2 + 1$ et aussi $$\\int_0^1 x dx$$"
        Output: ["x^2 + 1", "\\int_0^1 x dx"]

        Paramètres :
            text : le texte contenant du LaTeX (la réponse de le LLM)

        Retourne :
            Liste de strings LaTeX (sans les $)
        """
        expressions = []

        # D'abord les blocs $$ (pour ne pas les confondre avec les $ inline)
        # re.DOTALL = le "." matche aussi les sauts de ligne
        block_matches = re.findall(self.block_pattern, text, re.DOTALL)
        expressions.extend(block_matches)

        # Puis les \[...\]
        bracket_matches = re.findall(self.bracket_pattern, text, re.DOTALL)
        expressions.extend(bracket_matches)

        # Enlever les blocs $$ du texte avant de chercher les $ inline
        # Sinon, $$x^2$$ serait aussi capturé comme $x^2$
        text_without_blocks = re.sub(self.block_pattern, '', text)
        text_without_blocks = re.sub(self.bracket_pattern, '', text_without_blocks)

        # Enfin les inline $...$
        inline_matches = re.findall(self.inline_pattern, text_without_blocks)
        expressions.extend(inline_matches)

        # Nettoyer : enlever les espaces en trop
        expressions = [expr.strip() for expr in expressions if expr.strip()]

        logger.info(f"Extrait {len(expressions)} expressions LaTeX")
        return expressions

    # ----------------------------------------------------------
    # MÉTHODE 2 : Vérifier une expression LaTeX
    # ----------------------------------------------------------
    def verify_expression(self, latex_expr: str) -> dict[str, Any]:
        """
        Vérifie si une expression LaTeX est mathématiquement valide.

        Comment ça marche ?
        1. On nettoie l'expression LaTeX (enlever les commandes décoratives)
        2. On essaie de la parser avec SymPy
        3. Si SymPy comprend → l'expression est valide
        4. Si SymPy échoue → il y a probablement une erreur

        Attention : SymPy ne peut pas vérifier TOUTES les expressions.
        Les notations comme O(h²) ou des formules très complexes
        peuvent ne pas être parsées. Dans ce cas, on retourne "unverifiable"
        (pas "invalid" — on ne sait juste pas vérifier).

        Paramètres :
            latex_expr : l'expression LaTeX à vérifier (ex: "x^2 + 2x + 1")

        Retourne :
            Un dictionnaire avec :
            - valid : True/False/None (None = pas vérifiable)
            - expression : l'expression originale
            - parsed : la version SymPy (si réussie)
            - error : le message d'erreur (si échec)
        """
        if not SYMPY_AVAILABLE:
            return {
                "valid": None,
                "expression": latex_expr,
                "note": "SymPy non disponible"
            }

        try:
            # --- Étape 1 : Nettoyer le LaTeX ---
            # Le LaTeX de le LLM contient souvent des commandes décoratives
            # que SymPy ne comprend pas. On les enlève.
            cleaned = self._clean_latex(latex_expr)

            # Si l'expression est trop courte ou juste du texte, on skip
            if len(cleaned) < 2 or cleaned.isalpha():
                return {
                    "valid": None,
                    "expression": latex_expr,
                    "note": "Expression trop simple pour vérification"
                }

            # --- Étape 2 : Parser avec SymPy ---
            # parse_expr() essaie de comprendre l'expression mathématique
            # standard_transformations = règles de base (2x → 2*x)
            # implicit_multiplication = "xy" → "x*y"
            transformations = standard_transformations + (
                implicit_multiplication_application,
            )

            parsed = parse_expr(
                cleaned,
                transformations=transformations,
                local_dict={
                    'x': Symbol('x'),
                    'y': Symbol('y'),
                    'h': Symbol('h'),
                    'n': Symbol('n'),
                    't': Symbol('t'),
                    'a': Symbol('a'),
                    'b': Symbol('b'),
                }
            )

            return {
                "valid": True,
                "expression": latex_expr,
                "parsed": str(parsed),
                "sympy_latex": latex(parsed),  # Version LaTeX propre par SymPy
            }

        except Exception as e:
            # SymPy n'a pas réussi à parser l'expression
            # Ce n'est pas forcément une erreur dans la réponse de le LLM —
            # c'est peut-être une notation que SymPy ne comprend pas
            # (comme O(h²), \text{...}, etc.)
            return {
                "valid": None,  # None = pas vérifiable (pas False = faux)
                "expression": latex_expr,
                "note": f"Non vérifiable par SymPy : {str(e)[:100]}"
            }

    # ----------------------------------------------------------
    # MÉTHODE 3 : Nettoyer le LaTeX pour SymPy
    # ----------------------------------------------------------
    def _clean_latex(self, expr: str) -> str:
        """
        Nettoie une expression LaTeX pour la rendre parsable par SymPy.

        Le LaTeX de le LLM contient souvent des commandes que SymPy
        ne comprend pas. Cette méthode les enlève ou les remplace.

        Exemples :
        - "\\frac{a}{b}" → "a/b"       (SymPy préfère la notation /)
        - "\\cdot" → "*"                (point de multiplication → *)
        - "\\text{erreur}" → ""         (enlever le texte)
        - "\\approx" → ""               (enlever ≈)
        """
        # Remplacer \frac{a}{b} par (a)/(b)
        expr = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', expr)

        # Remplacer les commandes LaTeX courantes
        replacements = {
            '\\cdot': '*',
            '\\times': '*',
            '\\div': '/',
            '\\pm': '+',
            '\\mp': '-',
            '\\leq': '<=',
            '\\geq': '>=',
            '\\neq': '!=',
            '\\left': '',
            '\\right': '',
            '\\,': ' ',
            '\\;': ' ',
            '\\quad': ' ',
            '\\qquad': ' ',
            '\\approx': '',
            '\\sim': '',
            '\\rightarrow': '',
            '\\Rightarrow': '',
            '\\infty': 'oo',  # SymPy utilise "oo" pour l'infini
        }

        for latex_cmd, replacement in replacements.items():
            expr = expr.replace(latex_cmd, replacement)

        # Enlever \text{...} (texte dans les formules)
        expr = re.sub(r'\\text\{[^}]*\}', '', expr)

        # (12/05/2026) Avant de stripper les `\commande` restantes, on
        # convertit les fonctions standard SymPy connues : `\sin` -> `sin`,
        # `\cos` -> `cos`, `\tan` -> `tan`, `\log`, `\ln`, `\exp`, `\sqrt`.
        # Sinon `\sin^2(x)` devient `^2(x)` (vide), et le parser plante.
        # SymPy connait ces noms en local_dict, donc on les preserve.
        _SYMPY_FUNCTIONS = (
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
            'sinh', 'cosh', 'tanh',
            'log', 'ln', 'exp', 'sqrt', 'abs',
        )
        for fn in _SYMPY_FUNCTIONS:
            expr = re.sub(rf'\\{fn}\b', fn, expr)

        # (12/05/2026) Convertir la notation trigonometrique LaTeX
        # `sin^2(x)`, `cos^{3}(x)`, `tan^2(x)` -> `sin(x)**2`, etc.
        # SymPy n'accepte PAS `sin**2(x)` (qui voudrait dire la fonction sin
        # elevee a la puissance 2, puis appliquee a x — mathematiquement
        # absurde). La convention scolaire est `sin^n(x) = (sin(x))^n`.
        #
        # Pattern : `<fn>^<exposant>(<arg>)` ou exposant = nombre OU `{...}`.
        # On lit-back vers une forme parsable : `(<fn>(<arg>))**<exposant>`.
        for fn in _SYMPY_FUNCTIONS:
            # Cas 1 : exposant entre accolades — sin^{2}(x)
            expr = re.sub(
                rf'{fn}\^\{{([^}}]+)\}}\(([^)]+)\)',
                rf'({fn}(\2))**(\1)',
                expr,
            )
            # Cas 2 : exposant numerique direct — sin^2(x) ou sin^-1(x)
            expr = re.sub(
                rf'{fn}\^(-?\d+)\(([^)]+)\)',
                rf'({fn}(\2))**(\1)',
                expr,
            )

        # Enlever les commandes LaTeX restantes (\commande) inconnues
        # mais garder les contenus entre accolades.
        expr = re.sub(r'\\[a-zA-Z]+', '', expr)

        # Enlever les accolades restantes
        expr = expr.replace('{', '').replace('}', '')

        # Nettoyer les espaces
        expr = expr.strip()

        return expr

    # ==========================================================
    # VALIDATION DE CORRECTNESS (au-dela du parsing syntaxique)
    # ==========================================================
    # Les methodes ci-dessous verifient que les maths sont VRAIES,
    # pas juste qu'elles compilent. C'est ce qui anti-hallucine
    # vraiment le tuteur LLM, comme demande par le cahier des
    # charges (section 7).
    # ==========================================================

    def verify_equation(self, latex_expr: str) -> dict[str, Any]:
        """Verifie si une equation LaTeX 'LHS = RHS' est mathematiquement vraie.

        Approche : on simplifie LHS - RHS avec SymPy. Si le resultat est
        identiquement 0, l'equation est vraie. Sinon elle est fausse.

        Exemple :
            "(x+1)^2 = x^2 + 2x + 1" -> True (correct)
            "x^2 + 1 = 0"            -> False (faux en general)

        Retourne un dict avec :
            - status : "correct" | "incorrect" | "unverifiable"
            - reason : explication courte
        """
        if not SYMPY_AVAILABLE:
            return {"status": "unverifiable", "reason": "SymPy indisponible"}

        cleaned = self._clean_latex(latex_expr)
        if "=" not in cleaned:
            return {"status": "unverifiable", "reason": "Pas une equation (pas de '=')"}

        # On split sur le PREMIER signe egal seulement (pour gerer les cas
        # comme "a = b = c" ou les operateurs comme '<=' / '>=').
        lhs_str, _, rhs_str = cleaned.partition("=")
        lhs = _safe_parse(lhs_str.strip())
        rhs = _safe_parse(rhs_str.strip())
        if lhs is None or rhs is None:
            return {
                "status": "unverifiable",
                "reason": "Impossible de parser les deux cotes de l'equation",
            }

        try:
            diff_simplified = simplify(lhs - rhs)
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "unverifiable",
                "reason": f"Echec simplify : {str(exc)[:80]}",
            }

        if diff_simplified == 0:
            return {
                "status": "correct",
                "reason": f"{lhs} = {rhs} (verifie symboliquement)",
                "lhs": str(lhs),
                "rhs": str(rhs),
            }
        return {
            "status": "incorrect",
            "reason": f"LHS - RHS = {diff_simplified}, devrait etre 0",
            "lhs": str(lhs),
            "rhs": str(rhs),
            "difference": str(diff_simplified),
        }

    def verify_derivative_claim(self, function_expr: str, claimed_derivative: str,
                                  variable: str = "x") -> dict[str, Any]:
        """Verifie une affirmation de derivee : 'd/dx f = g' ?

        Exemple :
            verify_derivative_claim('x^2', '2*x') -> correct
            verify_derivative_claim('sin(x)', 'cos(x)') -> correct
            verify_derivative_claim('x^2', '3*x') -> incorrect
        """
        if not SYMPY_AVAILABLE:
            return {"status": "unverifiable", "reason": "SymPy indisponible"}

        f = _safe_parse(self._clean_latex(function_expr))
        g = _safe_parse(self._clean_latex(claimed_derivative))
        if f is None or g is None:
            return {"status": "unverifiable", "reason": "Parsing impossible"}

        try:
            actual = diff(f, _DEFAULT_SYMBOLS.get(variable, Symbol(variable)))
            ok = simplify(actual - g) == 0
        except Exception as exc:  # noqa: BLE001
            return {"status": "unverifiable", "reason": f"diff failed : {exc}"}

        if ok:
            return {
                "status": "correct",
                "reason": f"d/d{variable} ({f}) = {g} verifie",
            }
        return {
            "status": "incorrect",
            "reason": f"d/d{variable} ({f}) = {actual}, mais le tuteur dit {g}",
            "expected": str(actual),
            "claimed": str(g),
        }

    def verify_integral_claim(self, function_expr: str, claimed_integral: str,
                                a: str | None = None, b: str | None = None,
                                variable: str = "x") -> dict[str, Any]:
        """Verifie une integrale (definie ou indefinie).

        - Si a et b sont donnes : integrale definie de f de a a b == claimed ?
        - Sinon : integrale indefinie de f == claimed (modulo constante) ?
        """
        if not SYMPY_AVAILABLE:
            return {"status": "unverifiable", "reason": "SymPy indisponible"}

        var = _DEFAULT_SYMBOLS.get(variable, Symbol(variable))
        f = _safe_parse(self._clean_latex(function_expr))
        claimed = _safe_parse(self._clean_latex(claimed_integral))
        if f is None or claimed is None:
            return {"status": "unverifiable", "reason": "Parsing impossible"}

        try:
            if a is not None and b is not None:
                # Integrale definie
                a_expr = _safe_parse(a) if not _is_inf(a) else (-oo if "-" in a else oo)
                b_expr = _safe_parse(b) if not _is_inf(b) else (-oo if "-" in b else oo)
                actual = integrate(f, (var, a_expr, b_expr))
                # Compare numerically (the LLM might claim a decimal value)
                ok = simplify(actual - claimed) == 0 or (
                    hasattr(actual, "is_number") and actual.is_number
                    and hasattr(claimed, "is_number") and claimed.is_number
                    and abs(float(actual) - float(claimed)) < 1e-6
                )
            else:
                # Integrale indefinie : on accepte une constante d'integration de difference
                actual = integrate(f, var)
                d = simplify(actual - claimed)
                ok = (d == 0) or (d.is_constant() if hasattr(d, "is_constant") else False)
        except Exception as exc:  # noqa: BLE001
            return {"status": "unverifiable", "reason": f"integrate failed : {exc}"}

        if ok:
            return {"status": "correct", "reason": "Integrale verifiee"}
        return {
            "status": "incorrect",
            "reason": f"Resultat attendu : {actual}, claim : {claimed}",
            "expected": str(actual),
            "claimed": str(claimed),
        }

    def extract_and_check_equations(self, text: str) -> list[dict[str, Any]]:
        """Trouve toutes les equations 'LHS = RHS' dans le texte (LaTeX ou pas)
        et essaie de verifier leur correction symbolique.

        On ignore les `=` qui font partie d'operateurs comme `<=`, `>=`, `:=`,
        et les `=` qui apparaissent dans des phrases en langage naturel
        (heuristique : on n'examine que ce qui est dans des blocs LaTeX `$...$`).
        """
        results: list[dict[str, Any]] = []
        latex_blocks = self.extract_latex(text)
        for block in latex_blocks:
            # On ne considere que les blocs qui contiennent un signe '='
            # entoure d'autre chose qu'un autre symbole de comparaison.
            if "=" not in block:
                continue
            if any(op in block for op in ("<=", ">=", "!=", ":=", "==")):
                # On simplifie et on continue sans valider — trop ambigu
                continue
            check = self.verify_equation(block)
            check["source"] = block
            results.append(check)
        return results

    # ----------------------------------------------------------
    # MÉTHODE PRINCIPALE : Vérifier toute la réponse
    # ----------------------------------------------------------
    def verify_response(self, response_text: str) -> dict[str, Any]:
        """
        Vérifie TOUTES les formules mathématiques dans une réponse de le LLM.

        C'est cette méthode qui est appelée par le router /tutor/ask.

        Flux :
        1. Extraire toutes les expressions LaTeX de la réponse
        2. Vérifier chaque expression avec SymPy
        3. Calculer un score global de vérification
        4. Retourner le résultat

        Paramètres :
            response_text : la réponse complète de le LLM

        Retourne :
            Un dictionnaire avec :
            - verified : True si TOUT est vérifié, False sinon
            - total_expressions : nombre de formules trouvées
            - verified_count : nombre de formules vérifiées OK
            - unverifiable_count : nombre de formules non vérifiables
            - invalid_count : nombre de formules invalides
            - details : liste détaillée de chaque vérification
        """
        # Si la vérification est désactivée dans .env
        if not settings.ENABLE_SYMPY_VERIFICATION:
            return {
                "verified": True,
                "total_expressions": 0,
                "note": "Vérification désactivée dans la configuration"
            }

        # Extraire les expressions LaTeX
        expressions = self.extract_latex(response_text)

        if not expressions:
            return {
                "verified": True,
                "total_expressions": 0,
                "note": "Aucune expression LaTeX trouvée"
            }

        # Vérifier chaque expression
        details = []
        verified_count = 0
        unverifiable_count = 0
        invalid_count = 0

        for expr in expressions:
            result = self.verify_expression(expr)
            details.append(result)

            if result["valid"] is True:
                verified_count += 1
            elif result["valid"] is None:
                unverifiable_count += 1
            else:
                invalid_count += 1

        # ----- Validation de CORRECTNESS (au-dela du parse syntaxique) -----
        # On cherche les equations 'LHS = RHS' dans les blocs LaTeX
        # et on verifie que LHS - RHS == 0 symboliquement.
        equation_checks = self.extract_and_check_equations(response_text)
        equations_correct = sum(1 for c in equation_checks if c["status"] == "correct")
        equations_incorrect = sum(1 for c in equation_checks if c["status"] == "incorrect")

        # Le score global
        # On considère la réponse comme "vérifiée" si :
        # - Aucune expression syntaxiquement invalide
        # - Aucune equation incorrecte detectee par SymPy
        is_verified = invalid_count == 0 and equations_incorrect == 0

        result = {
            "verified": is_verified,
            "total_expressions": len(expressions),
            "verified_count": verified_count,
            "unverifiable_count": unverifiable_count,
            "invalid_count": invalid_count,
            "details": details,
            # Nouveau : validation de correctness des equations
            "equations_checked": len(equation_checks),
            "equations_correct": equations_correct,
            "equations_incorrect": equations_incorrect,
            "equations_details": equation_checks,
        }

        logger.info(
            f"Vérification : {verified_count} OK, "
            f"{unverifiable_count} non-vérifiables, "
            f"{invalid_count} invalides sur {len(expressions)} total"
        )

        return result


# Instance globale
verification_service = VerificationService()
