"""Lagrange interpolation — 3Blue1Brown teaching version.

We have a few measured points and want one smooth curve through all of them.
The Lagrange idea: build a special basis curve for each node that equals one at
its own node and zero at every other node, then mix them with the data values.
Layout contract: graph on the LEFT (self.demo_axes), every formula/table/label
on the RIGHT through self.panel, every worked number through self.work, captions
through self.subtitle (plain words, no math glyphs). Real maths only in MathTex.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, Create, DashedLine, Dot, FadeIn, FadeOut, Flash,
    MathTex, SurroundingRectangle, Text, VGroup, Write,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, ACCENT2, PAUSE,
)


DATA = [(0, 12), (6, 18), (10, 24), (15, 28), (22, 14)]


def basis(points, i, x):
    """The i-th Lagrange basis polynomial, naive product of factors."""
    xi = points[i][0]
    num = 1.0
    den = 1.0
    for j, (xj, _) in enumerate(points):
        if j == i:
            continue
        num *= (x - xj)
        den *= (xi - xj)
    return num / den


def lagrange(points, x):
    """The full Lagrange interpolant evaluated at x."""
    total = 0.0
    for i, (_, yi) in enumerate(points):
        total += yi * basis(points, i, x)
    return total


TEXT = {
    "en": {
        "title": "Lagrange Interpolation",
        "why1": "We measured the temperature at a few separate hours of the day.",
        "why2": "We want one smooth curve that passes exactly through every point.",
        "motiv": "Here are the five measurements, hour against temperature.",
        "idea": "The trick: build one helper curve for each point.",
        "b1": "This helper rises to one at its own point and is zero at all the others.",
        "b3": "Each point gets its own helper, peaking at one only there.",
        "combine": "Now mix the helpers, each weighted by its measured value.",
        "build": "Adding the weighted helpers gives the curve through every point.",
        "read": "We can now read the temperature at hour sixteen, between two measurements.",
        "compute": "We just add up each value times its helper, evaluated at sixteen.",
        "done": "One smooth curve through all the data: that is Lagrange interpolation.",
    },
    "fr": {
        "title": "Interpolation de Lagrange",
        "why1": "On a mesure la temperature a quelques heures separees de la journee.",
        "why2": "On veut une seule courbe lisse passant exactement par chaque point.",
        "motiv": "Voici les cinq mesures, l'heure en face de la temperature.",
        "idea": "L'astuce : construire une courbe auxiliaire pour chaque point.",
        "b1": "Cette courbe vaut un en son propre point et zero en tous les autres.",
        "b3": "Chaque point a sa propre courbe, qui culmine a un seulement la.",
        "combine": "On melange les courbes auxiliaires, chacune ponderee par sa valeur mesuree.",
        "build": "La somme des courbes ponderees donne la courbe passant par chaque point.",
        "read": "On peut maintenant lire la temperature a l'heure seize, entre deux mesures.",
        "compute": "On additionne chaque valeur fois sa courbe auxiliaire, evaluee en seize.",
        "done": "Une seule courbe lisse par toutes les donnees : c'est l'interpolation de Lagrange.",
    },
}


class LagrangeDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def _table(self):
        header = r"x_i & y_i"
        body = r" \\ ".join(rf"{x} & {y}" for (x, y) in DATA)
        tex = r"\begin{array}{c c}" + header + r" \\ " + body + r"\end{array}"
        return MathTex(tex, color=INK)

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

        # --- The data points (graph LEFT) ---
        axes = self.demo_axes(x_range=(0, 24, 4), y_range=(0, 32, 8))
        self.play(Create(axes), run_time=1.3)
        cap = self.subtitle(None, "motiv")
        dots = VGroup(*[Dot(axes.c2p(x, y), color=ROOT, radius=0.08) for (x, y) in DATA])
        for d in dots:
            self.play(FadeIn(d, scale=1.4), run_time=0.4)
        self.wait(0.5)

        # --- The mixing formula and table on the RIGHT panel ---
        formula = self.panel(MathTex(r"P(x)=\sum_{i} y_i\, L_i(x)", color=INK), y=2.7)
        table = self.panel(self._table(), y=0.6)
        self.play(Write(formula), run_time=1.2)
        self.play(FadeIn(table), run_time=0.6)

        # --- The basis idea ---
        cap = self.subtitle(cap, "idea")
        cap = self.subtitle(cap, "b1")
        # L_1 scaled so peak fits the visible window (display only)
        l1 = axes.plot(lambda X: 28.0 * basis(DATA, 1, X),
                       x_range=[0, 22, 0.1], color=STEPC, stroke_width=4)
        # label in an empty corner of the graph (top-left), not on the curve
        l1lbl = MathTex(r"L_1(x)", color=STEPC).scale(0.55).move_to(axes.c2p(2, 30))
        self.play(Create(l1), Write(l1lbl), run_time=1.8)
        one_at = Dot(axes.c2p(6, 28.0), color=STEPC, radius=0.07)
        self.play(FadeIn(one_at, scale=1.4), run_time=0.6)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "b3")
        l3 = axes.plot(lambda X: 28.0 * basis(DATA, 3, X),
                       x_range=[0, 22, 0.1], color=ACCENT2, stroke_width=4)
        l3lbl = MathTex(r"L_3(x)", color=ACCENT2).scale(0.55).move_to(axes.c2p(20, 30))
        self.play(Create(l3), Write(l3lbl), run_time=1.8)
        one_at3 = Dot(axes.c2p(15, 28.0), color=ACCENT2, radius=0.07)
        self.play(FadeIn(one_at3, scale=1.4), run_time=0.6)
        self.wait(PAUSE)
        self.play(FadeOut(l1), FadeOut(l3), FadeOut(l1lbl), FadeOut(l3lbl),
                  FadeOut(one_at), FadeOut(one_at3), run_time=0.7)

        # --- The combined interpolant ---
        cap = self.subtitle(cap, "combine")
        cap = self.subtitle(cap, "build")
        curve = axes.plot(lambda X: lagrange(DATA, X),
                          x_range=[0, 22, 0.05], color=PRIMARY, stroke_width=5)
        plbl = MathTex(r"P(x)", color=PRIMARY).scale(0.55).move_to(axes.c2p(3, 30))
        self.play(Create(curve), Write(plbl), run_time=2.4)
        self.wait(PAUSE)

        # --- Read off the value at x = 16 (worked computation in the strip) ---
        cap = self.subtitle(cap, "read")
        xq = 16
        yq = lagrange(DATA, xq)
        drop = DashedLine(axes.c2p(xq, 0.0), axes.c2p(xq, yq), color=MUTED, stroke_width=2)
        qdot = Dot(axes.c2p(xq, yq), color=STEPC, radius=0.08)
        self.play(Create(drop), FadeIn(qdot, scale=1.4), run_time=1.0)

        cap = self.subtitle(cap, "compute")
        worked = self.work(MathTex(
            r"P(16)=\sum_i y_i\,L_i(16) \approx " + rf"{yq:.2f}",
            color=STEPC))
        self.play(Write(worked), run_time=1.6)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "done")
        box = SurroundingRectangle(table, color=ROOT, buff=0.15)
        self.play(Create(box), run_time=0.9)
        self.play(Flash(axes.c2p(xq, yq), color=STEPC, line_length=0.2,
                        num_lines=16, flash_radius=0.35), run_time=1.1)
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class LagrangeDemoFR(LagrangeDemo):
    lang = "fr"
