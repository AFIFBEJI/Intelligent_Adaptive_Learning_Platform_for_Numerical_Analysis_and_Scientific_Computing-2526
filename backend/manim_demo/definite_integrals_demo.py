"""Definite Integrals — 3Blue1Brown teaching version.

The definite integral is the exact shaded area under the curve. We shade the
area for a positive function, then show a function that dips below the axis and
explain the integral is the NET signed area (area above minus area below).
Graph on the LEFT, notation in the RIGHT panel (self.panel), a worked signed
sum in the strip under the graph (self.work). Captions are plain words; all
maths are LaTeX.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, Create, FadeIn, FadeOut, MathTex, Text, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, ROOT, ACCENT2, PAUSE,
)


def f(x):
    return 2.0 + 1.4 * math.sin(0.8 * x)


def g(x):
    return 1.5 * math.sin(0.9 * x)


TEXT = {
    "en": {
        "title": "Definite Integrals",
        "why1": "The definite integral is a single number.",
        "why2": "It measures the exact area trapped between the curve and the axis.",
        "motiv": "Here is a curve that stays above the axis on the whole interval.",
        "goal": "We shade the region from the left bound to the right bound.",
        "shade": "That shaded patch is the area, and the integral is exactly its size.",
        "notate": "We write it with the integral sign over the interval.",
        "signed1": "But what if the curve dips below the axis?",
        "signed2": "Above the axis the area counts as positive, shaded green.",
        "signed3": "Below the axis the area counts as negative, shaded red.",
        "net": "The integral is the net signed area: green area minus red area.",
        "compute": "So the value is the area above minus the area below.",
        "done": "So the definite integral is exact area, with a sign for each side.",
    },
    "fr": {
        "title": "Integrales Definies",
        "why1": "L'integrale definie est un seul nombre.",
        "why2": "Elle mesure l'aire exacte prise entre la courbe et l'axe.",
        "motiv": "Voici une courbe qui reste au-dessus de l'axe sur tout l'intervalle.",
        "goal": "On colore la region de la borne gauche a la borne droite.",
        "shade": "Cette zone coloree est l'aire, et l'integrale vaut exactement sa taille.",
        "notate": "On l'ecrit avec le signe integrale sur l'intervalle.",
        "signed1": "Mais que se passe-t-il si la courbe descend sous l'axe ?",
        "signed2": "Au-dessus de l'axe, l'aire compte comme positive, en vert.",
        "signed3": "Sous l'axe, l'aire compte comme negative, en rouge.",
        "net": "L'integrale est l'aire signee nette : aire verte moins aire rouge.",
        "compute": "La valeur est donc l'aire au-dessus moins l'aire en dessous.",
        "done": "L'integrale definie est donc une aire exacte, avec un signe de chaque cote.",
    },
}


class DefiniteIntegralsDemo(DemoScene):
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

        # --- Part 1: a positive function, exact area (graph LEFT) ---
        axes = self.demo_axes(x_range=(0, 8, 2), y_range=(0, 4, 1))
        curve = axes.plot(f, x_range=[0, 8, 0.02], color=PRIMARY, stroke_width=5)
        flabel = MathTex(r"f(x)=2+1.4\sin(0.8x)", color=PRIMARY).scale(0.5)
        flabel.move_to(axes.c2p(2.0, 3.7))
        self.play(Create(axes), run_time=1.3)
        self.play(Create(curve), run_time=1.8)
        self.play(FadeIn(flabel), run_time=0.9)
        cap = self.subtitle(None, "motiv")

        cap = self.subtitle(cap, "goal")
        area = axes.get_area(curve, x_range=(0, 8), color=ROOT, opacity=0.5)
        self.play(FadeIn(area), run_time=1.6)
        cap = self.subtitle(cap, "shade")
        self.wait(PAUSE)

        # --- Notation in the RIGHT panel ---
        cap = self.subtitle(cap, "notate")
        notation = self.panel(
            MathTex(r"\int_{a}^{b} f(x)\,dx", color=INK), y=2.4)
        self.play(FadeIn(notation), run_time=1.4)
        self.wait(PAUSE)
        self.play(FadeOut(area), FadeOut(curve), FadeOut(flabel),
                  FadeOut(notation), FadeOut(axes), run_time=0.8)

        # --- Part 2: a function that dips below, net signed area ---
        axes2 = self.demo_axes(x_range=(0, 7, 1), y_range=(-2, 2, 1))
        curve2 = axes2.plot(g, x_range=[0, 7, 0.02], color=PRIMARY, stroke_width=5)
        glabel = MathTex(r"g(x)=1.5\sin(0.9x)", color=PRIMARY).scale(0.5)
        glabel.move_to(axes2.c2p(1.6, 1.7))
        cap = self.subtitle(cap, "signed1")
        self.play(Create(axes2), run_time=1.2)
        self.play(Create(curve2), run_time=1.7)
        self.play(FadeIn(glabel), run_time=0.9)

        # g(x) >= 0 on [0, pi/0.9 ~= 3.49], < 0 after
        xcross = math.pi / 0.9
        cap = self.subtitle(cap, "signed2")
        area_pos = axes2.get_area(curve2, x_range=(0, xcross), color=ROOT, opacity=0.5)
        self.play(FadeIn(area_pos), run_time=1.4)
        plus = MathTex(r"+", color=ROOT).scale(0.9).move_to(axes2.c2p(1.7, 0.55))
        self.play(FadeIn(plus, scale=1.3), run_time=0.6)

        cap = self.subtitle(cap, "signed3")
        area_neg = axes2.get_area(curve2, x_range=(xcross, 7), color=ACCENT2, opacity=0.5)
        self.play(FadeIn(area_neg), run_time=1.4)
        minus = MathTex(r"-", color=ACCENT2).scale(0.9).move_to(axes2.c2p(5.2, -0.55))
        self.play(FadeIn(minus, scale=1.3), run_time=0.6)
        self.wait(PAUSE)

        # --- Net signed area: notation in panel, worked line in strip ---
        cap = self.subtitle(cap, "net")
        net = self.panel(
            MathTex(r"\int_{a}^{b} g(x)\,dx = A_{+} - A_{-}", color=INK), y=2.4)
        self.play(FadeIn(net), run_time=1.4)
        cap = self.subtitle(cap, "compute")
        worked = self.work(
            MathTex(r"\int_{a}^{b} g\,dx = A_{+} - A_{-}", color=ROOT))
        self.play(FadeIn(worked), run_time=1.2)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "done")
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class DefiniteIntegralsDemoFR(DefiniteIntegralsDemo):
    lang = "fr"
