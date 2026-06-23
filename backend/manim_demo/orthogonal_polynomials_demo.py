"""Orthogonal Polynomials — 3Blue1Brown teaching version (strict layout).

A better basis. The monomials 1, x, x squared, x cubed look nearly the same on
[0,1], an unstable basis. The Legendre polynomials on [-1,1] point in clearly
different directions and are orthogonal, so each coefficient becomes independent
and the approximation is stable.

Layout: ONE set of axes is created (self.demo_axes) and reused for both the
monomials and the Legendre polynomials, so there is never a second repere; the
monomial list, the Legendre definitions P0..P3 and the orthogonality relation
are stacked in ONE VGroup in the RIGHT panel (self.panel) so they never overlap;
the worked integral check goes in the strip under the graph (self.work);
plain-word captions via self.subtitle. Maths in MathTex.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, LEFT, UP, Create, FadeIn, FadeOut, MathTex,
    SurroundingRectangle, Text, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, ACCENT2, PAUSE,
)


# Legendre polynomials
def P0(x):
    return 1.0


def P1(x):
    return x


def P2(x):
    return (3.0 * x * x - 1.0) / 2.0


def P3(x):
    return (5.0 * x ** 3 - 3.0 * x) / 2.0


TEXT = {
    "en": {
        "title": "Orthogonal Polynomials",
        "why1": "To approximate a function we write it as a sum of simpler building blocks.",
        "why2": "The choice of building blocks decides whether the answer is stable.",
        "monos": "Here are the plain powers: one, x, x squared, x cubed on the unit interval.",
        "bad": "On this range they nearly overlap. They are almost parallel directions.",
        "ill": "Such a near parallel basis is unstable, small data changes swing the answer.",
        "leg": "The Legendre polynomials instead point in clearly different directions.",
        "ortho": "They are orthogonal, each pair has zero overlap when integrated.",
        "check": "We can check one pair by integrating their product over the interval.",
        "ortho2": "Because of this, every coefficient can be found on its own.",
        "stable": "So the fit is stable, and Chebyshev polynomials further reduce oscillation.",
        "done": "A good basis makes approximation reliable.",
    },
    "fr": {
        "title": "Polynomes Orthogonaux",
        "why1": "Pour approcher une fonction on l'ecrit comme somme de briques simples.",
        "why2": "Le choix des briques decide si la reponse est stable.",
        "monos": "Voici les puissances simples : un, x, x au carre, x au cube sur l'intervalle unite.",
        "bad": "Sur cette plage elles se chevauchent presque. Ce sont des directions presque paralleles.",
        "ill": "Une base presque parallele est instable, un petit changement fait basculer la reponse.",
        "leg": "Les polynomes de Legendre pointent plutot dans des directions nettement differentes.",
        "ortho": "Ils sont orthogonaux, chaque paire a un recouvrement nul une fois integree.",
        "check": "On peut verifier une paire en integrant leur produit sur l'intervalle.",
        "ortho2": "Grace a cela, chaque coefficient se trouve independamment.",
        "stable": "L'ajustement est donc stable, et les polynomes de Chebyshev reduisent encore l'oscillation.",
        "done": "Une bonne base rend l'approximation fiable.",
    },
}


class OrthogonalPolynomialsDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def construct(self):
        self.title("title")

        # --- Introduction: why the basis matters (centred, slow) ---
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

        # --- ONE set of axes, reused for both bases (graph LEFT) ---
        axes = self.demo_axes(x_range=(-1, 1, 0.5), y_range=(-1, 1, 0.5))
        self.play(Create(axes), run_time=1.3)

        # --- The monomials on [0,1], drawn on the single axes ---
        cap = self.subtitle(None, "monos")
        mono_colors = [MUTED, PRIMARY, STEPC, ROOT]
        monos = VGroup()
        for k, col in enumerate(mono_colors):
            monos.add(axes.plot(lambda X, k=k: X ** k,
                                x_range=[0, 1, 0.01], color=col, stroke_width=4))
        self.play(Create(monos), run_time=2.0)

        # monomial list in the RIGHT panel
        mlabels = self.panel(
            MathTex(r"1,\; x,\; x^{2},\; x^{3}", color=INK).scale(0.6), y=2.5)
        self.play(FadeIn(mlabels), run_time=0.9)

        cap = self.subtitle(cap, "bad")
        self.wait(0.6)
        cap = self.subtitle(cap, "ill")
        self.wait(0.5)
        # clear the monomial curves but KEEP the same axes (no second repere)
        self.play(FadeOut(monos), FadeOut(mlabels), run_time=0.8)

        # --- The Legendre polynomials on [-1,1], on the SAME axes ---
        cap = self.subtitle(cap, "leg")
        leg_funcs = [P0, P1, P2, P3]
        leg_colors = [PRIMARY, STEPC, ROOT, ACCENT2]
        legs = VGroup()
        for fnc, col in zip(leg_funcs, leg_colors):
            legs.add(axes.plot(fnc, x_range=[-1, 1, 0.01], color=col, stroke_width=4))
        self.play(Create(legs), run_time=2.2)

        # --- Panel (RIGHT): definitions + orthogonality in ONE VGroup ---
        defs = MathTex(
            r"P_0=1",
            r"P_1=x",
            r"P_2=\tfrac{3x^{2}-1}{2}",
            r"P_3=\tfrac{5x^{3}-3x}{2}",
            color=INK).scale(0.6).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        defs[0].set_color(PRIMARY)
        defs[1].set_color(STEPC)
        defs[2].set_color(ROOT)
        defs[3].set_color(ACCENT2)

        ortho = MathTex(
            r"\int_{-1}^{1} P_i\,P_j\,dx = 0\quad(i\neq j)",
            color=ROOT).scale(0.6)

        pvg = VGroup(defs, ortho).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        self.panel(pvg, y=0.4)

        self.play(FadeIn(defs), run_time=1.6)
        cap = self.subtitle(cap, "ortho")
        self.play(FadeIn(ortho), run_time=1.4)
        self.wait(PAUSE)

        # --- One worked orthogonality check (strip under the graph) ---
        cap = self.subtitle(cap, "check")
        worked = self.work(MathTex(
            r"\int_{-1}^{1} x\cdot\tfrac{3x^{2}-1}{2}\,dx=0",
            color=STEPC).scale(0.72))
        self.play(FadeIn(worked), run_time=1.6)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "ortho2")
        self.wait(0.5)
        cap = self.subtitle(cap, "stable")
        box = SurroundingRectangle(ortho, color=ROOT, buff=0.12)
        self.play(Create(box), run_time=0.9)
        self.wait(PAUSE)

        self.play(FadeOut(worked), run_time=0.4)
        cap = self.subtitle(cap, "done")
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class OrthogonalPolynomialsDemoFR(OrthogonalPolynomialsDemo):
    lang = "fr"
