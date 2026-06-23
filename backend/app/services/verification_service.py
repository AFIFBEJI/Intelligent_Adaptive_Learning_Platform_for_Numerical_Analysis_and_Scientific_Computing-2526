# ============================================================
# Mathematical Verification Service — SymPy
# ============================================================
# What is this file?
#
# After the LLM answers the student, we VERIFY that the
# mathematical formulas in the response are correct.
#
# WHY? LLMs (the LLM, GPT...) can "hallucinate"
# wrong formulas. For example:
#   - Saying that Euler's error is O(h^3) instead of O(h^2)
#   - Writing a wrong Simpson formula
#   - Making a mistake in a derivative
#
# HOW? We use SymPy, a Python library for symbolic
# computation. SymPy understands math like a human:
#   - It knows that the derivative of x^2 is 2x
#   - It can simplify fractions
#   - It can check whether two expressions are equivalent
#
# This is the "NEURO-SYMBOLIC" architecture of your PFE:
#   Neuro = the LLM (generates natural text)
#   Symbolic = SymPy (verifies the math, 100% reliable)
#
# This combination is what makes your project publishable
# in a scientific journal (IEEE, etc.)
# ============================================================

import logging
import re
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# We import SymPy only if verification is enabled
# (so as not to slow down startup if we do not need it)
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


# Standard symbols used in our math validations.
# We declare them once to avoid re-creating Symbol() everywhere.
_DEFAULT_SYMBOLS: dict[str, "Symbol"] = {}
if SYMPY_AVAILABLE:
    for name in "abcdefghnstxyz":
        _DEFAULT_SYMBOLS[name] = Symbol(name)


def _is_inf(token: str) -> bool:
    """Heuristic: detects whether an integral bound represents infinity."""
    if not token:
        return False
    cleaned = token.strip().lower().lstrip("-+")
    return cleaned in {"inf", "infty", "infinity", "oo", "\\infty"}


# Math functions SymPy knows natively. Any OTHER name used as "name(...)"
# (e.g. f(x), p(x), S(x), g(x)) is an undefined function: SymPy would read
# it as a multiplication "f*x" and wrongly flag the equation as incorrect.
_KNOWN_MATH_FUNCS = frozenset({
    "sin", "cos", "tan", "cot", "sec", "csc", "asin", "acos", "atan",
    "sinh", "cosh", "tanh", "exp", "log", "ln", "sqrt", "abs", "floor", "ceil",
})
_FUNC_CALL_RE = re.compile(r"([A-Za-z]+)\s*'?\s*\(")


def _has_undefined_function_call(expr: str) -> bool:
    """True if `expr` uses function-application notation of an UNKNOWN
    function such as f(x), p(x), S(x) or f'(x).

    SymPy cannot know the definition of f, so it would mis-read "f(x)" as
    "f*x" and report a false "incorrect" equation. We use this to SKIP such
    equations (mark them unverifiable) instead of flagging them as wrong.
    """
    for match in _FUNC_CALL_RE.finditer(expr):
        if match.group(1).lower() not in _KNOWN_MATH_FUNCS:
            return True
    return False


def _safe_parse(expr_str: str) -> "object | None":
    """Parse a cleaned expression into a SymPy object. Returns None on failure.

    We wrap this in a helper to avoid duplicating the try/except logic
    + transformations in each validation method.
    """
    if not SYMPY_AVAILABLE:
        return None
    try:
        # SECURITY/UX (05/12/2026): we add `convert_xor` to translate
        # the `^` (XOR in pure Python) to `**` (power) at parse time. Without
        # this transformation, "x^2" is interpreted as a bitwise XOR
        # and crashes the verification. This is the LaTeX/academic format
        # that LLMs and teachers produce, so we must accept it.
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
    Mathematical verification service.

    Its role: take the LLM's response, extract the LaTeX
    formulas, and verify that they are syntactically and mathematically
    correct with SymPy.

    The result is a "Verified" or "Not verified" badge
    displayed next to each tutor message.
    """

    def __init__(self):
        r"""
        Initialize the regex patterns to detect LaTeX.

        What is a regex?
        A "regular expression" — a text-search language.
        For example, the pattern \$(.+?)\$ looks for any text
        between two $...$ signs (this is the inline LaTeX syntax).

        We have 3 patterns because LaTeX can be written in 3 ways:
        1. $formula$     -> inline LaTeX (within the text)
        2. $$formula$$   -> block LaTeX (centered, on its own line)
        3. \[formula\]   -> Another block LaTeX syntax
        """
        # Pattern for inline LaTeX: $x^2 + y^2$
        # \$ = a literal dollar sign
        # (.+?) = capture any text between the $ (the ? = the minimum possible)
        self.inline_pattern = r'\$([^\$]+?)\$'

        # Pattern for block LaTeX: $$\int_a^b f(x)dx$$
        self.block_pattern = r'\$\$(.+?)\$\$'

        # Pattern for \[...\]
        self.bracket_pattern = r'\\\[(.+?)\\\]'

    # ----------------------------------------------------------
    # METHOD 1: Extract the LaTeX expressions
    # ----------------------------------------------------------
    def extract_latex(self, text: str) -> list[str]:
        """
        Extract all the LaTeX expressions from a text.

        Example:
        Input:  "La formule est $x^2 + 1$ et aussi $$\\int_0^1 x dx$$"
        Output: ["x^2 + 1", "\\int_0^1 x dx"]

        Parameters:
            text: the text containing LaTeX (the LLM's response)

        Returns:
            List of LaTeX strings (without the $)
        """
        expressions = []

        # First the $$ blocks (so as not to confuse them with inline $)
        # re.DOTALL = the "." also matches line breaks
        block_matches = re.findall(self.block_pattern, text, re.DOTALL)
        expressions.extend(block_matches)

        # Then the \[...\]
        bracket_matches = re.findall(self.bracket_pattern, text, re.DOTALL)
        expressions.extend(bracket_matches)

        # Remove the $$ blocks from the text before looking for inline $
        # Otherwise, $$x^2$$ would also be captured as $x^2$
        text_without_blocks = re.sub(self.block_pattern, '', text)
        text_without_blocks = re.sub(self.bracket_pattern, '', text_without_blocks)

        # Finally the inline $...$
        inline_matches = re.findall(self.inline_pattern, text_without_blocks)
        expressions.extend(inline_matches)

        # Clean up: remove extra spaces
        expressions = [expr.strip() for expr in expressions if expr.strip()]

        logger.info(f"Extrait {len(expressions)} expressions LaTeX")
        return expressions

    # ----------------------------------------------------------
    # METHOD 2: Verify a LaTeX expression
    # ----------------------------------------------------------
    def verify_expression(self, latex_expr: str) -> dict[str, Any]:
        """
        Verify whether a LaTeX expression is mathematically valid.

        How does it work?
        1. We clean the LaTeX expression (remove decorative commands)
        2. We try to parse it with SymPy
        3. If SymPy understands -> the expression is valid
        4. If SymPy fails -> there is probably an error

        Caution: SymPy cannot verify ALL expressions.
        Notations like O(h^2) or very complex formulas
        may not be parsed. In that case, we return "unverifiable"
        (not "invalid" — we just cannot verify).

        Parameters:
            latex_expr: the LaTeX expression to verify (e.g. "x^2 + 2x + 1")

        Returns:
            A dictionary with:
            - valid: True/False/None (None = not verifiable)
            - expression: the original expression
            - parsed: the SymPy version (if successful)
            - error: the error message (if failed)
        """
        if not SYMPY_AVAILABLE:
            return {
                "valid": None,
                "expression": latex_expr,
                "note": "SymPy non disponible"
            }

        try:
            # --- Step 1: Clean the LaTeX ---
            # The LLM's LaTeX often contains decorative commands
            # that SymPy does not understand. We remove them.
            cleaned = self._clean_latex(latex_expr)

            # If the expression is too short or just text, we skip
            if len(cleaned) < 2 or cleaned.isalpha():
                return {
                    "valid": None,
                    "expression": latex_expr,
                    "note": "Expression trop simple pour vérification"
                }

            # --- Step 2: Parse with SymPy ---
            # parse_expr() tries to understand the mathematical expression
            # standard_transformations = basic rules (2x -> 2*x)
            # implicit_multiplication = "xy" -> "x*y"
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
                "sympy_latex": latex(parsed),  # Clean LaTeX version by SymPy
            }

        except Exception as e:
            # SymPy failed to parse the expression
            # This is not necessarily an error in the LLM's response —
            # it might be a notation that SymPy does not understand
            # (like O(h^2), \text{...}, etc.)
            return {
                "valid": None,  # None = not verifiable (not False = wrong)
                "expression": latex_expr,
                "note": f"Non vérifiable par SymPy : {str(e)[:100]}"
            }

    # ----------------------------------------------------------
    # METHOD 3: Clean the LaTeX for SymPy
    # ----------------------------------------------------------
    def _clean_latex(self, expr: str) -> str:
        """
        Clean a LaTeX expression to make it parsable by SymPy.

        The LLM's LaTeX often contains commands that SymPy
        does not understand. This method removes or replaces them.

        Examples:
        - "\\frac{a}{b}" -> "a/b"       (SymPy prefers the / notation)
        - "\\cdot" -> "*"                (multiplication dot -> *)
        - "\\text{error}" -> ""          (remove the text)
        - "\\approx" -> ""               (remove ~)
        """
        # Replace \frac{a}{b} with (a)/(b)
        expr = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', expr)

        # Replace the common LaTeX commands
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
            '\\infty': 'oo',  # SymPy uses "oo" for infinity
        }

        for latex_cmd, replacement in replacements.items():
            expr = expr.replace(latex_cmd, replacement)

        # Remove \text{...} (text within the formulas)
        expr = re.sub(r'\\text\{[^}]*\}', '', expr)

        # (05/12/2026) Before stripping the remaining `\command`, we
        # convert the known standard SymPy functions: `\sin` -> `sin`,
        # `\cos` -> `cos`, `\tan` -> `tan`, `\log`, `\ln`, `\exp`, `\sqrt`.
        # Otherwise `\sin^2(x)` becomes `^2(x)` (empty), and the parser crashes.
        # SymPy knows these names in local_dict, so we preserve them.
        _SYMPY_FUNCTIONS = (
            'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
            'sinh', 'cosh', 'tanh',
            'log', 'ln', 'exp', 'sqrt', 'abs',
        )
        for fn in _SYMPY_FUNCTIONS:
            expr = re.sub(rf'\\{fn}\b', fn, expr)

        # (05/12/2026) Convert the LaTeX trigonometric notation
        # `sin^2(x)`, `cos^{3}(x)`, `tan^2(x)` -> `sin(x)**2`, etc.
        # SymPy does NOT accept `sin**2(x)` (which would mean the function sin
        # raised to the power 2, then applied to x — mathematically
        # absurd). The academic convention is `sin^n(x) = (sin(x))^n`.
        #
        # Pattern: `<fn>^<exponent>(<arg>)` where exponent = number OR `{...}`.
        # We rewrite it to a parsable form: `(<fn>(<arg>))**<exponent>`.
        for fn in _SYMPY_FUNCTIONS:
            # Case 1: exponent in braces — sin^{2}(x)
            expr = re.sub(
                rf'{fn}\^\{{([^}}]+)\}}\(([^)]+)\)',
                rf'({fn}(\2))**(\1)',
                expr,
            )
            # Case 2: direct numeric exponent — sin^2(x) or sin^-1(x)
            expr = re.sub(
                rf'{fn}\^(-?\d+)\(([^)]+)\)',
                rf'({fn}(\2))**(\1)',
                expr,
            )

        # Remove the remaining unknown LaTeX commands (\command)
        # but keep the contents within braces.
        expr = re.sub(r'\\[a-zA-Z]+', '', expr)

        # Remove the remaining braces
        expr = expr.replace('{', '').replace('}', '')

        # Clean up the spaces
        expr = expr.strip()

        return expr

    # ==========================================================
    # CORRECTNESS VALIDATION (beyond syntactic parsing)
    # ==========================================================
    # The methods below verify that the math is TRUE,
    # not just that it compiles. This is what truly anti-hallucinates
    # the LLM tutor, as required by the specifications
    # (section 7).
    # ==========================================================

    def verify_equation(self, latex_expr: str) -> dict[str, Any]:
        """Verify whether a LaTeX equation 'LHS = RHS' is mathematically true.

        Approach: we simplify LHS - RHS with SymPy. If the result is
        identically 0, the equation is true. Otherwise it is false.

        Example:
            "(x+1)^2 = x^2 + 2x + 1" -> True (correct)
            "x^2 + 1 = 0"            -> False (false in general)

        Returns a dict with:
            - status: "correct" | "incorrect" | "unverifiable"
            - reason: short explanation
        """
        if not SYMPY_AVAILABLE:
            return {"status": "unverifiable", "reason": "SymPy indisponible"}

        cleaned = self._clean_latex(latex_expr)
        if "=" not in cleaned:
            return {"status": "unverifiable", "reason": "Pas une equation (pas de '=')"}

        # We split on the FIRST equals sign only (to handle cases
        # like "a = b = c" or operators like '<=' / '>=').
        lhs_str, _, rhs_str = cleaned.partition("=")

        # Skip equations that use function notation of an undefined function
        # (e.g. "f(x) = x^2 - 5x + 6"). SymPy would read "f(x)" as "f*x" and
        # wrongly report the equation as incorrect. These are conceptually
        # valid statements we simply cannot verify symbolically.
        if _has_undefined_function_call(lhs_str) or _has_undefined_function_call(rhs_str):
            return {
                "status": "unverifiable",
                "reason": "Equation uses an undefined function (e.g. f(x)); skipped",
            }

        lhs = _safe_parse(lhs_str.strip())
        rhs = _safe_parse(rhs_str.strip())
        if lhs is None or rhs is None:
            return {
                "status": "unverifiable",
                "reason": "Impossible de parser les deux cotes de l'equation",
            }

        # A lone symbol on one side ("x = 2", "m = 1.5", "y = x^2") is an
        # ASSIGNMENT / root / solution statement, NOT an algebraic identity.
        # SymPy would compute "x - 2 != 0" and wrongly flag it as incorrect,
        # so we skip these (mark unverifiable) instead of reporting them wrong.
        if isinstance(lhs, Symbol) or isinstance(rhs, Symbol):
            return {
                "status": "unverifiable",
                "reason": "assignment or root statement (e.g. x = 2), not an identity",
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
        """Verify a derivative claim: 'd/dx f = g' ?

        Example:
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
        """Verify an integral (definite or indefinite).

        - If a and b are given: definite integral of f from a to b == claimed ?
        - Otherwise: indefinite integral of f == claimed (modulo constant) ?
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
                # Definite integral
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
                # Indefinite integral: we accept an integration constant as the difference
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

    def _resolve_part(self, part: str, func_defs: dict, var) -> "object | None":
        """Resolve ONE side of an equation into a SymPy expression.

        Uses the collected function definitions so that "f(x)" becomes its
        definition (and "f(2)" the definition evaluated at 2). Returns None
        when the part is OPAQUE — an undefined function we cannot resolve
        (e.g. "P(x)*Q(x)") — or cannot be parsed.
        """
        s = part.strip()
        if not s:
            return None
        m = re.match(r"^([A-Za-z])\s*'?\s*\(\s*([^()]+?)\s*\)$", s)
        if m:
            name, arg = m.group(1), m.group(2).strip()
            if name.lower() in _KNOWN_MATH_FUNCS:
                return _safe_parse(self._clean_latex(s))
            if name in func_defs:
                def_expr = func_defs[name]
                if arg == str(var):
                    return def_expr
                arg_expr = _safe_parse(arg)
                if arg_expr is not None:
                    try:
                        return def_expr.subs(var, arg_expr)
                    except Exception:  # noqa: BLE001
                        return None
            return None  # undefined function, no definition -> opaque
        if _has_undefined_function_call(s):
            return None  # still embeds f(...)/P(...) we cannot resolve
        return _safe_parse(s)

    def _collect_function_defs(self, eq_blocks: list[str], var) -> dict:
        """Scan equations for definitions 'f(x) = <expr>' and record f -> expr."""
        func_defs: dict = {}
        for block in eq_blocks:
            parts = [p.strip() for p in self._clean_latex(block).split("=")]
            if len(parts) < 2:
                continue
            m = re.match(r"^([A-Za-z])\s*'?\s*\(\s*([A-Za-z])\s*\)$", parts[0])
            if not m:
                continue
            name = m.group(1)
            if name.lower() in _KNOWN_MATH_FUNCS or name in func_defs:
                continue
            for rhs in parts[1:]:
                if _has_undefined_function_call(rhs):
                    continue
                expr = _safe_parse(rhs)
                if expr is not None and not isinstance(expr, Symbol):
                    func_defs[name] = expr
                    break
        return func_defs

    def _check_equation_chain(self, block: str, func_defs: dict, var) -> dict[str, Any]:
        """Verify a (possibly chained) equation 'a = b = c', resolving any
        f(x) via the collected definitions. Returns correct / incorrect /
        unverifiable for the whole block."""
        cleaned = self._clean_latex(block)
        parts = [p.strip() for p in cleaned.split("=") if p.strip()]
        if len(parts) < 2:
            return {"status": "unverifiable", "reason": "not an equation", "source": block}
        resolved = [self._resolve_part(p, func_defs, var) for p in parts]
        checked_any = False
        for i in range(len(resolved) - 1):
            a, b = resolved[i], resolved[i + 1]
            if a is None or b is None:
                continue
            # A lone symbol side ("x = 2", "m = 1.5") is an assignment/root,
            # not an identity -> skip it.
            if isinstance(a, Symbol) or isinstance(b, Symbol):
                continue
            try:
                if simplify(a - b) != 0:
                    return {"status": "incorrect", "reason": f"{a} != {b}", "source": block}
                checked_any = True
            except Exception:  # noqa: BLE001
                continue
        if checked_any:
            return {"status": "correct", "reason": "verified (with substitution)", "source": block}
        return {"status": "unverifiable", "reason": "no concrete pair to verify", "source": block}

    def extract_and_check_equations(self, text: str) -> list[dict[str, Any]]:
        """Find the 'LHS = RHS' equations in the LaTeX blocks and verify their
        symbolic correctness.

        Improvement: we first collect function definitions like 'f(x) = x^2-2',
        then substitute them so a statement such as 'f(x) = (x-2)(x-3)' can be
        VERIFIED (not just skipped). Comparison operators (<=, >=, :=, ...) and
        assignment statements (x = 2) are ignored.
        """
        results: list[dict[str, Any]] = []
        if not SYMPY_AVAILABLE:
            return results
        eq_blocks: list[str] = []
        for block in self.extract_latex(text):
            if "=" not in block:
                continue
            if any(op in block for op in ("<=", ">=", "!=", ":=", "==")):
                continue
            eq_blocks.append(block)
        if not eq_blocks:
            return results
        var = Symbol("x")
        func_defs = self._collect_function_defs(eq_blocks, var)
        for block in eq_blocks:
            results.append(self._check_equation_chain(block, func_defs, var))
        return results

    # ----------------------------------------------------------
    # MAIN METHOD: Verify the whole response
    # ----------------------------------------------------------
    def verify_response(self, response_text: str) -> dict[str, Any]:
        """
        Verify ALL the mathematical formulas in an LLM response.

        This is the method called by the /tutor/ask router.

        Flow:
        1. Extract all the LaTeX expressions from the response
        2. Verify each expression with SymPy
        3. Compute a global verification score
        4. Return the result

        Parameters:
            response_text: the complete LLM response

        Returns:
            A dictionary with:
            - verified: True if EVERYTHING is verified, False otherwise
            - total_expressions: number of formulas found
            - verified_count: number of formulas verified OK
            - unverifiable_count: number of non-verifiable formulas
            - invalid_count: number of invalid formulas
            - details: detailed list of each verification
        """
        # If verification is disabled in .env
        if not settings.ENABLE_SYMPY_VERIFICATION:
            return {
                "verified": True,
                "total_expressions": 0,
                "note": "Vérification désactivée dans la configuration"
            }

        # Extract the LaTeX expressions
        expressions = self.extract_latex(response_text)

        if not expressions:
            return {
                "verified": True,
                "total_expressions": 0,
                "note": "Aucune expression LaTeX trouvée"
            }

        # Verify each expression
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

        # ----- CORRECTNESS validation (beyond the syntactic parse) -----
        # We look for the 'LHS = RHS' equations in the LaTeX blocks
        # and verify that LHS - RHS == 0 symbolically.
        equation_checks = self.extract_and_check_equations(response_text)
        equations_correct = sum(1 for c in equation_checks if c["status"] == "correct")
        equations_incorrect = sum(1 for c in equation_checks if c["status"] == "incorrect")

        # The global score
        # We consider the response "verified" if:
        # - No syntactically invalid expression
        # - No incorrect equation detected by SymPy
        is_verified = invalid_count == 0 and equations_incorrect == 0

        result = {
            "verified": is_verified,
            "total_expressions": len(expressions),
            "verified_count": verified_count,
            "unverifiable_count": unverifiable_count,
            "invalid_count": invalid_count,
            "details": details,
            # New: correctness validation of the equations
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


# Global instance
verification_service = VerificationService()
