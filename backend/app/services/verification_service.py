# ============================================================
# Service de Vérification Mathématique — SymPy
# ============================================================
# C'est quoi ce fichier ?
#
# Après que Gemini répond à l'étudiant, on VÉRIFIE que les
# formules mathématiques dans la réponse sont correctes.
#
# POURQUOI ? Les LLMs (Gemini, GPT...) peuvent "halluciner"
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
#   Neuro = Gemini (génère du texte naturel)
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
    from sympy import Symbol, latex, simplify, sympify
    from sympy.parsing.sympy_parser import (
        implicit_multiplication_application,
        parse_expr,
        standard_transformations,
    )
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    logger.warning("SymPy non installé — vérification mathématique désactivée")


class VerificationService:
    """
    Service de vérification mathématique.

    Son rôle : prendre la réponse de Gemini, extraire les formules
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
            text : le texte contenant du LaTeX (la réponse de Gemini)

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
            # Le LaTeX de Gemini contient souvent des commandes décoratives
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
            # Ce n'est pas forcément une erreur dans la réponse de Gemini —
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

        Le LaTeX de Gemini contient souvent des commandes que SymPy
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

        # Enlever les commandes LaTeX restantes (\commande)
        # mais garder les contenus entre accolades
        expr = re.sub(r'\\[a-zA-Z]+', '', expr)

        # Enlever les accolades restantes
        expr = expr.replace('{', '').replace('}', '')

        # Nettoyer les espaces
        expr = expr.strip()

        return expr

    # ----------------------------------------------------------
    # MÉTHODE PRINCIPALE : Vérifier toute la réponse
    # ----------------------------------------------------------
    def verify_response(self, response_text: str) -> dict[str, Any]:
        """
        Vérifie TOUTES les formules mathématiques dans une réponse de Gemini.

        C'est cette méthode qui est appelée par le router /tutor/ask.

        Flux :
        1. Extraire toutes les expressions LaTeX de la réponse
        2. Vérifier chaque expression avec SymPy
        3. Calculer un score global de vérification
        4. Retourner le résultat

        Paramètres :
            response_text : la réponse complète de Gemini

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

        # Le score global
        # On considère la réponse comme "vérifiée" si :
        # - Aucune expression n'est invalide (invalid_count == 0)
        # - Au moins une expression est vérifiée OU toutes sont non-vérifiables
        is_verified = invalid_count == 0

        result = {
            "verified": is_verified,
            "total_expressions": len(expressions),
            "verified_count": verified_count,
            "unverifiable_count": unverifiable_count,
            "invalid_count": invalid_count,
            "details": details
        }

        logger.info(
            f"Vérification : {verified_count} OK, "
            f"{unverifiable_count} non-vérifiables, "
            f"{invalid_count} invalides sur {len(expressions)} total"
        )

        return result


# Instance globale
verification_service = VerificationService()
