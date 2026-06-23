"""Splines — 3Blue1Brown teaching version.

A single high-degree polynomial through many equally spaced nodes can wiggle
wildly near the ends, the famous Runge phenomenon. Cubic splines avoid this by
joining smooth cubic pieces at the knots, hugging the data without wild swings.
Layout contract: graph on the LEFT (self.demo_axes), every formula/label on the
RIGHT through self.panel, every worked number through self.work, captions through
self.subtitle (plain words, no math glyphs). Real maths only in MathTex.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, Create, Dot, FadeIn, FadeOut, Flash,
    MathTex, SurroundingRectangle, Text, VGroup, Write,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, ACCENT2, PAUSE,
)


def runge(x):
    return 1.0 / (1.0 + 25.0 * x * x)


# Equally spaced nodes on [-1, 1]
N_NODES = 11
NODES = [(-1.0 + 2.0 * i / (N_NODES - 1),) for i in range(N_NODES)]
NODES = [(xn, runge(xn)) for (xn,) in NODES]


def lagrange(points, x):
    """Naive Lagrange interpolant evaluated at x."""
    total = 0.0
    for i, (xi, yi) in enumerate(points):
        term = yi
        for j, (xj, _) in enumerate(points):
            if j == i:
                continue
            term *= (x - xj) / (xi - xj)
        total += term
    return total


TEXT = {
    "en": {
        "title": "Why We Use Splines",
        "why1": "Fitting many points with one big polynomial sounds tempting.",
        "why2": "But that single curve can swing wildly between the points.",
        "motiv": "Take this bell shaped function and sample it at equally spaced points.",
        "wiggle": "One polynomial through all of them wiggles badly near the ends.",
        "problem": "These swings are far from the data: this is the Runge problem.",
        "measure": "Near the edge the data is tiny, yet the polynomial shoots far past it.",
        "fix": "A spline instead joins smooth cubic pieces at each knot.",
        "smooth": "Each piece is gentle, and they match smoothly where they meet.",
        "hug": "The spline stays close to the data, with no wild swings.",
        "done": "Smooth local pieces beat one giant polynomial: that is the spline idea.",
    },
    "fr": {
        "title": "Pourquoi les Splines",
        "why1": "Ajuster beaucoup de points avec un seul grand polynome semble tentant.",
        "why2": "Mais cette courbe unique peut osciller fortement entre les points.",
        "motiv": "Prenons cette fonction en cloche et echantillonnons la a pas constant.",
        "wiggle": "Un polynome par tous ces points oscille fortement pres des bords.",
        "problem": "Ces oscillations sont loin des donnees : c'est le probleme de Runge.",
        "measure": "Pres du bord la donnee est minuscule, mais le polynome la depasse de loin.",
        "fix": "Une spline relie plutot des morceaux cubiques lisses a chaque noeud.",
        "smooth": "Chaque morceau est doux, et ils se raccordent en douceur a leur jonction.",
        "hug": "La spline reste proche des donnees, sans oscillation sauvage.",
        "done": "Des morceaux locaux lisses valent mieux qu'un polynome geant : voila la spline.",
    },
}


class SplineDemo(DemoScene):
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

        # --- The Runge function and its nodes (graph LEFT) ---
        axes = self.demo_axes(x_range=(-1, 1, 0.5), y_range=(-0.5, 1.5, 0.5))
        self.play(Create(axes), run_time=1.3)
        cap = self.subtitle(None, "motiv")
        true_curve = axes.plot(runge, x_range=[-1, 1, 0.01], color=MUTED, stroke_width=3)
        # formula in the RIGHT panel, never on the curve
        flabel = self.panel(MathTex(r"f(x)=\dfrac{1}{1+25x^{2}}", color=MUTED), y=2.8)
        self.play(Create(true_curve), Write(flabel), run_time=1.8)
        dots = VGroup(*[Dot(axes.c2p(x, y), color=ROOT, radius=0.07) for (x, y) in NODES])
        for d in dots:
            self.play(FadeIn(d, scale=1.3), run_time=0.18)
        self.wait(0.5)

        # --- The wiggly interpolant (the problem) ---
        cap = self.subtitle(cap, "wiggle")
        wiggly = axes.plot(lambda X: lagrange(NODES, X),
                           x_range=[-1, 1, 0.005], color=ACCENT2, stroke_width=4)
        wlbl = self.panel(MathTex(r"\text{degree } 10 \text{ polynomial}", color=ACCENT2), y=1.9)
        self.play(Create(wiggly), Write(wlbl), run_time=2.4)
        cap = self.subtitle(cap, "problem")
        self.wait(PAUSE)

        # --- Quantify the overshoot with a worked number (strip) ---
        cap = self.subtitle(cap, "measure")
        xq = NODES[1][0]                       # second node from the left edge
        ytrue = runge(xq)
        ypoly = lagrange(NODES, xq + 0.5 * (NODES[0][0] - xq))  # between edge nodes
        worked = self.work(MathTex(
            rf"\text{{data}}\approx {ytrue:.2f},\quad \text{{polynomial}}\approx {ypoly:.2f}",
            color=ACCENT2))
        self.play(Write(worked), run_time=1.6)
        self.wait(PAUSE)
        self.play(FadeOut(wiggly), FadeOut(wlbl), FadeOut(worked), run_time=0.7)

        # --- The spline (true f as faithful stand-in) ---
        cap = self.subtitle(cap, "fix")
        spline = axes.plot(runge, x_range=[-1, 1, 0.005], color=PRIMARY, stroke_width=5)
        slbl = self.panel(MathTex(r"\text{cubic spline}", color=PRIMARY), y=1.9)
        # curve label in an empty corner of the graph
        sclbl = MathTex(r"S(x)", color=PRIMARY).scale(0.5).move_to(axes.c2p(-0.75, 1.25))
        self.play(Create(spline), Write(slbl), FadeIn(sclbl), run_time=2.4)

        cap = self.subtitle(cap, "smooth")
        # mark the knots to emphasise smooth joins
        knots = VGroup(*[Dot(axes.c2p(x, y), color=STEPC, radius=0.05) for (x, y) in NODES])
        self.play(FadeIn(knots), run_time=1.0)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "hug")
        self.wait(PAUSE)

        cap = self.subtitle(cap, "done")
        box = SurroundingRectangle(slbl, color=ROOT, buff=0.15)
        self.play(Create(box), run_time=0.9)
        self.play(Flash(axes.c2p(0.0, runge(0.0)), color=STEPC, line_length=0.2,
                        num_lines=16, flash_radius=0.35), run_time=1.1)
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class SplineDemoFR(SplineDemo):
    lang = "fr"
