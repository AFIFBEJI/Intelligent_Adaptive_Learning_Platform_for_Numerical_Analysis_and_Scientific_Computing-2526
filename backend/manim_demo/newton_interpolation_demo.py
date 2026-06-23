"""Newton interpolation — 3Blue1Brown teaching version.

Newton's form of the interpolating polynomial is built one term at a time. We
start with a flat line through the first point, then add a linear term through
two points, a quadratic through three, and so on, watching the curve grab one
more point at every step.
Layout contract: graph on the LEFT (self.demo_axes), the nested form on the
RIGHT through self.panel, every worked number through self.work, captions through
self.subtitle (plain words, no math glyphs). Real maths only in MathTex.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, LEFT, Create, Dot, FadeIn, FadeOut, Flash,
    MathTex, SurroundingRectangle, Text, Transform, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


NEWT = [(0, 1), (1, 2), (2, 5), (3, 4)]


def divided_differences(points):
    xs = [p[0] for p in points]
    n = len(points)
    table = [[float(p[1]) for p in points]]
    for k in range(1, n):
        prev = table[-1]
        col = [(prev[i + 1] - prev[i]) / (xs[i + k] - xs[i]) for i in range(n - k)]
        table.append(col)
    return table


def newton_coeffs(points):
    return [col[0] for col in divided_differences(points)]


def partial_eval(points, coeffs, degree, x):
    """Evaluate the Newton polynomial truncated to the given degree."""
    xs = [p[0] for p in points]
    total = coeffs[0]
    prod = 1.0
    for k in range(1, degree + 1):
        prod *= (x - xs[k - 1])
        total += coeffs[k] * prod
    return total


TEXT = {
    "en": {
        "title": "Newton's Interpolating Form",
        "why1": "We want the polynomial passing through these four points.",
        "why2": "Newton builds it term by term, grabbing one more point each time.",
        "motiv": "Here are the four points to fit.",
        "p0": "Start with a flat line through the first point only.",
        "p1": "Add a linear term, and the line now passes through the first two points.",
        "p2": "Add a square term, and it bends through the first three points.",
        "p3": "Add the last term, and the curve passes through all four points.",
        "form": "Each term is added on top of the previous ones, in nested form.",
        "check": "Check it really hits the last point: put three in and add the terms.",
        "done": "One point at a time, until the curve fits them all.",
    },
    "fr": {
        "title": "Forme d'Interpolation de Newton",
        "why1": "On veut le polynome qui passe par ces quatre points.",
        "why2": "Newton le construit terme par terme, attrapant un point de plus a chaque fois.",
        "motiv": "Voici les quatre points a ajuster.",
        "p0": "On commence par une ligne plate passant par le premier point seulement.",
        "p1": "On ajoute un terme lineaire, et la ligne passe par les deux premiers points.",
        "p2": "On ajoute un terme carre, et elle se courbe par les trois premiers points.",
        "p3": "On ajoute le dernier terme, et la courbe passe par les quatre points.",
        "form": "Chaque terme s'ajoute aux precedents, sous forme imbriquee.",
        "check": "Verifions qu'elle atteint le dernier point : on met trois et on additionne.",
        "done": "Un point a la fois, jusqu'a ce que la courbe les ajuste tous.",
    },
}


class NewtonInterpolationDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def construct(self):
        self.title("title")

        # --- Real introduction: centred, slow ---
        intro = VGroup(
            Text(self.t("why1"), font="Arial", color=INK).scale(0.55),
            Text(self.t("why2"), font="Arial", color=MUTED).scale(0.5),
        ).arrange(DOWN, buff=0.5)
        for line in intro:
            if line.width > 11:
                line.scale_to_fit_width(11)
        intro.move_to(UP * 0.2)
        self.play(FadeIn(intro[0], shift=UP * 0.2), run_time=1.2)
        self.wait(1.4)
        self.play(FadeIn(intro[1], shift=UP * 0.2), run_time=1.2)
        self.wait(2.4)
        self.play(FadeOut(intro), run_time=0.7)

        # --- The points (graph LEFT) ---
        axes = self.demo_axes(x_range=(0, 3.5, 1), y_range=(0, 6, 1))
        self.play(Create(axes), run_time=1.3)
        cap = self.subtitle(None, "motiv")
        dots = VGroup(*[Dot(axes.c2p(x, y), color=ROOT, radius=0.08) for (x, y) in NEWT])
        for d in dots:
            self.play(FadeIn(d, scale=1.4), run_time=0.4)
        self.wait(0.5)

        coeffs = newton_coeffs(NEWT)

        # --- The nested Newton form on the RIGHT panel ---
        # Split the long nested polynomial into TWO readable stacked lines and
        # arrange them (with the four terms) in ONE VGroup so it never overlaps
        # the points on the left. Each term is revealed in order via FadeIn.
        terms = [
            MathTex(r"P(x)=a_0", color=INK).scale(0.6),
            MathTex(r"+\,a_1(x-x_0)", color=INK).scale(0.6),
            MathTex(r"+\,a_2(x-x_0)(x-x_1)", color=INK).scale(0.6),
            MathTex(r"+\,a_3(x-x_0)(x-x_1)", color=INK).scale(0.6),
            MathTex(r"\qquad\quad (x-x_2)", color=INK).scale(0.6),
        ]
        form = VGroup(*terms).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        self.panel(form, y=1.6)
        self.play(FadeIn(terms[0]), run_time=1.0)

        # --- P0: flat line ---
        cap = self.subtitle(cap, "p0")
        curve = axes.plot(lambda X: partial_eval(NEWT, coeffs, 0, X),
                          x_range=[0, 3, 0.02], color=PRIMARY, stroke_width=5)
        plbl = MathTex(r"P(x)", color=PRIMARY).scale(0.5).move_to(axes.c2p(0.45, 5.5))
        self.play(Create(curve), FadeIn(plbl), run_time=1.6)
        self.wait(PAUSE)

        # --- P1, P2, P3 by Transform; reveal the matching term(s) each time ---
        # Term index map: degree 1 -> terms[1], degree 2 -> terms[2],
        # degree 3 -> terms[3] and terms[4] (the second wrapped line).
        reveal = {1: [1], 2: [2], 3: [3, 4]}
        steps = [(1, "p1"), (2, "p2"), (3, "p3")]
        for degree, key in steps:
            cap = self.subtitle(cap, key)
            for idx in reveal[degree]:
                self.play(FadeIn(terms[idx]), run_time=0.9)
            new_curve = axes.plot(
                lambda X, d=degree: partial_eval(NEWT, coeffs, d, X),
                x_range=[0, 3, 0.02], color=PRIMARY, stroke_width=5)
            self.play(Transform(curve, new_curve), run_time=1.8)
            self.wait(PAUSE)

        # --- The coefficients (worked strip) ---
        cap = self.subtitle(cap, "form")
        coeff_tex = self.work(MathTex(
            r"a_0,a_1,a_2,a_3 = "
            + ",\\;".join(rf"{c:.2f}" for c in coeffs),
            color=STEPC))
        self.play(FadeIn(coeff_tex), run_time=1.4)
        self.wait(PAUSE)

        # --- A worked check at the last node x = 3 ---
        cap = self.subtitle(cap, "check")
        lastx, lasty = NEWT[-1]
        val = partial_eval(NEWT, coeffs, len(coeffs) - 1, lastx)
        check = self.work(MathTex(
            rf"P(3)={val:.2f}", color=STEPC))
        self.play(Transform(coeff_tex, check), run_time=1.2)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "done")
        box = SurroundingRectangle(coeff_tex, color=ROOT, buff=0.15)
        self.play(Create(box), run_time=0.9)
        self.play(Flash(axes.c2p(lastx, lasty), color=STEPC, line_length=0.2,
                        num_lines=16, flash_radius=0.35), run_time=1.1)
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class NewtonInterpolationDemoFR(NewtonInterpolationDemo):
    lang = "fr"
