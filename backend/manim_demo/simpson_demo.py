"""Simpson's Rule — 3Blue1Brown teaching version.

Instead of straight lines, Simpson fits a PARABOLA through each pair of
sub-intervals: three points give one parabola. The parabola hugs the curve, so
the rule is very accurate. We fit the quadratic through three points in python
and draw it. Graph on the LEFT, formula in the RIGHT panel (self.panel), the
worked three-point estimate in the strip under the graph (self.work). Captions
are plain words; all maths are LaTeX.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, Create, Dot, FadeIn, FadeOut, MathTex, Text, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


def f(x):
    return 1.0 + 0.6 * math.sin(0.9 * x) + 0.3 * math.cos(1.3 * x)


def quad_through(x0, y0, x1, y1, x2, y2):
    """Coefficients (a, b, c) of the parabola y = a x^2 + b x + c through 3 points."""
    d0 = (x0 - x1) * (x0 - x2)
    d1 = (x1 - x0) * (x1 - x2)
    d2 = (x2 - x0) * (x2 - x1)
    a = y0 / d0 + y1 / d1 + y2 / d2
    b = (-y0 * (x1 + x2) / d0 - y1 * (x0 + x2) / d1 - y2 * (x0 + x1) / d2)
    c = (y0 * x1 * x2 / d0 + y1 * x0 * x2 / d1 + y2 * x0 * x1 / d2)
    return a, b, c


def simpson_one(x0, x2, y0, y1, y2):
    """Simpson estimate over one panel [x0, x2] with midpoint height y1."""
    h = (x2 - x0) / 2.0
    return h / 3.0 * (y0 + 4.0 * y1 + y2)


TEXT = {
    "en": {
        "title": "Simpson's Rule",
        "why1": "Straight tops follow the curve well, but not perfectly.",
        "why2": "Curved pieces can match a bending curve far more faithfully.",
        "motiv": "Here is a gently waving curve to approximate.",
        "goal": "Take three neighbouring points on the curve.",
        "s1": "Three points fix exactly one parabola.",
        "s2": "Draw that parabola: it bends to match the curve almost perfectly.",
        "idea": "Simpson repeats this across the whole interval, two pieces at a time.",
        "formula": "Weight the heights one, four, two, four, and so on, then scale.",
        "compute": "For this panel we weight the three heights one, four, one.",
        "accurate": "Because parabolas bend with the curve, the rule is very accurate.",
        "done": "Simpson often beats trapezoids by a wide margin for smooth curves.",
    },
    "fr": {
        "title": "Methode de Simpson",
        "why1": "Les sommets droits suivent bien la courbe, mais pas parfaitement.",
        "why2": "Des morceaux courbes epousent une courbe ondulee bien plus fidelement.",
        "motiv": "Voici une courbe qui ondule doucement a approcher.",
        "goal": "On prend trois points voisins sur la courbe.",
        "s1": "Trois points fixent exactement une parabole.",
        "s2": "On trace cette parabole : elle se plie pour coller a la courbe presque parfaitement.",
        "idea": "Simpson repete cela sur tout l'intervalle, deux morceaux a la fois.",
        "formula": "On pondere les hauteurs par un, quatre, deux, quatre, puis on met a l'echelle.",
        "compute": "Pour ce morceau on pondere les trois hauteurs par un, quatre, un.",
        "accurate": "Comme les paraboles se plient avec la courbe, la methode est tres precise.",
        "done": "Simpson surpasse souvent les trapezes nettement pour les courbes lisses.",
    },
}


class SimpsonDemo(DemoScene):
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

        # --- The problem (graph LEFT) ---
        axes = self.demo_axes(x_range=(0, 4, 1), y_range=(0, 2.5, 0.5))
        curve = axes.plot(f, x_range=[0, 4, 0.02], color=PRIMARY, stroke_width=5)
        flabel = MathTex(r"f(x)=1+0.6\sin(0.9x)+0.3\cos(1.3x)",
                         color=PRIMARY).scale(0.4)
        flabel.move_to(axes.c2p(1.7, 2.3))
        self.play(Create(axes), run_time=1.3)
        self.play(Create(curve), run_time=1.8)
        self.play(FadeIn(flabel), run_time=0.9)
        cap = self.subtitle(None, "motiv")

        # --- Pick three points x0, x1, x2 ---
        cap = self.subtitle(cap, "goal")
        x0, x1, x2 = 0.0, 2.0, 4.0
        y0, y1, y2 = f(x0), f(x1), f(x2)
        dots = VGroup(
            Dot(axes.c2p(x0, y0), color=STEPC, radius=0.08),
            Dot(axes.c2p(x1, y1), color=STEPC, radius=0.08),
            Dot(axes.c2p(x2, y2), color=STEPC, radius=0.08),
        )
        self.play(FadeIn(dots, scale=1.4), run_time=1.0)
        cap = self.subtitle(cap, "s1")
        self.wait(PAUSE)

        # --- Fit the parabola and draw it ---
        cap = self.subtitle(cap, "s2")
        a, b, c = quad_through(x0, y0, x1, y1, x2, y2)
        parab = axes.plot(lambda X: a * X * X + b * X + c,
                          x_range=[x0, x2, 0.02], color=ROOT, stroke_width=4)
        self.play(Create(parab), run_time=2.0)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "idea")
        self.wait(PAUSE)

        # --- The formula in the RIGHT panel ---
        cap = self.subtitle(cap, "formula")
        formula = self.panel(
            MathTex(r"S=\frac{\Delta x}{3}\,(f_0+4f_1+2f_2+\dots)", color=INK),
            y=2.5)
        self.play(FadeIn(formula), run_time=1.4)

        # --- The worked three-point estimate in the strip ---
        cap = self.subtitle(cap, "compute")
        est = simpson_one(x0, x2, y0, y1, y2)
        worked = self.work(
            MathTex(rf"S = \frac{{\Delta x}}{{3}}\,(f_0+4f_1+f_2) = {est:.4f}",
                    color=STEPC))
        self.play(FadeIn(worked), run_time=1.6)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "accurate")
        self.wait(PAUSE)
        cap = self.subtitle(cap, "done")
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class SimpsonDemoFR(SimpsonDemo):
    lang = "fr"
