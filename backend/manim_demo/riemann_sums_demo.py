"""Riemann Sums - 3Blue1Brown teaching version.

The area under the curve equals the accumulated total. We approximate it by
rectangles, then refine n = 4 -> 8 -> 16 and watch the left-Riemann sum approach
the true integral 12.5333. Graph on the LEFT, the running sum and formula in the
RIGHT panel (self.panel), the worked sum in the strip under the graph
(self.work). Captions are plain words; all maths are LaTeX.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, Create, FadeIn, FadeOut, MathTex, SurroundingRectangle,
    Text, Transform, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


def f(x):
    return 0.4 * x * x + 1.0


def left_riemann(a, b, n):
    dx = (b - a) / n
    return sum(f(a + i * dx) for i in range(n)) * dx


TRUE_AREA = 0.4 * 64.0 / 3.0 + 4.0  # 12.5333...


TEXT = {
    "en": {
        "title": "Riemann Sums",
        "why1": "How much area sits under a curve?",
        "why2": "That area is the accumulated total of the quantity the curve describes.",
        "motiv": "We cannot read the area off the picture, so we approximate it.",
        "goal": "The idea: cover the region with simple rectangles and add them up.",
        "s1": "First try: four rectangles, each as tall as the curve on its left edge.",
        "sum1": "Add the rectangle areas. This is the left Riemann sum.",
        "refine1": "Four rectangles are rough. Let us use eight thinner ones.",
        "sum2": "Eight rectangles already hug the curve more closely.",
        "refine2": "Thinner still: sixteen rectangles.",
        "sum3": "The running sum keeps creeping toward the true area.",
        "limit": "More rectangles, thinner each time, and the sum approaches the exact area.",
        "done": "In the limit of infinitely many rectangles, we get the exact integral.",
    },
    "fr": {
        "title": "Sommes de Riemann",
        "why1": "Quelle aire se trouve sous une courbe ?",
        "why2": "Cette aire est le total accumule de la quantite que decrit la courbe.",
        "motiv": "On ne peut pas lire l'aire sur le dessin, alors on l'approche.",
        "goal": "L'idee : recouvrir la region de rectangles simples et les additionner.",
        "s1": "Premier essai : quatre rectangles, hauts comme la courbe a leur bord gauche.",
        "sum1": "On additionne les aires des rectangles. C'est la somme de Riemann a gauche.",
        "refine1": "Quatre rectangles, c'est grossier. Prenons-en huit, plus fins.",
        "sum2": "Huit rectangles epousent deja mieux la courbe.",
        "refine2": "Encore plus fins : seize rectangles.",
        "sum3": "La somme courante se rapproche peu a peu de l'aire reelle.",
        "limit": "Plus de rectangles, toujours plus fins, et la somme tend vers l'aire exacte.",
        "done": "A la limite d'une infinite de rectangles, on obtient l'integrale exacte.",
    },
}


class RiemannSumsDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def _rects(self, axes, graph, n):
        return axes.get_riemann_rectangles(
            graph, x_range=[0, 4], dx=4.0 / n, input_sample_type="left",
            stroke_width=0.6, stroke_color=INK, fill_opacity=0.55,
            color=[STEPC, ROOT],
        )

    def _sum_label(self, n):
        s = left_riemann(0.0, 4.0, n)
        return self.panel(
            MathTex(rf"S_{{{n}}} = {s:.4f}", color=STEPC), y=0.2)

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
        axes = self.demo_axes(x_range=(0, 4, 1), y_range=(0, 8, 2))
        curve = axes.plot(f, x_range=[0, 4, 0.02], color=PRIMARY, stroke_width=5)
        flabel = MathTex(r"f(x)=0.4\,x^{2}+1", color=PRIMARY).scale(0.55)
        flabel.move_to(axes.c2p(0.95, 7.2))
        self.play(Create(axes), run_time=1.3)
        self.play(Create(curve), run_time=1.8)
        self.play(FadeIn(flabel), run_time=0.9)
        cap = self.subtitle(None, "motiv")
        cap = self.subtitle(cap, "goal")

        # --- The maths panel (RIGHT): formula + true-area target ---
        formula = self.panel(
            MathTex(r"S=\sum_{i} f(x_i)\,\Delta x", color=INK), y=2.6)
        target = self.panel(
            MathTex(rf"\int_{{0}}^{{4}} f(x)\,dx = {TRUE_AREA:.4f}", color=ROOT),
            y=1.5)
        self.play(FadeIn(formula), run_time=1.2)
        self.play(FadeIn(target), run_time=0.7)

        # ---- n = 4, in full detail ----
        cap = self.subtitle(cap, "s1")
        rects = self._rects(axes, curve, 4)
        self.play(Create(rects), run_time=2.0)
        cap = self.subtitle(cap, "sum1")
        slabel = self._sum_label(4)
        self.play(FadeIn(slabel), run_time=1.0)
        worked = self.work(
            MathTex(rf"S_{{4}} = \sum_{{i=0}}^{{3}} f(x_i)\,\Delta x"
                    rf" = {left_riemann(0.0, 4.0, 4):.4f}", color=STEPC))
        self.play(FadeIn(worked), run_time=1.4)
        self.wait(PAUSE)

        # ---- refine to n = 8 ----
        cap = self.subtitle(cap, "refine1")
        rects8 = self._rects(axes, curve, 8)
        self.play(Transform(rects, rects8), run_time=1.8)
        cap = self.subtitle(cap, "sum2")
        self.play(Transform(slabel, self._sum_label(8)), run_time=1.0)
        self.play(Transform(worked, self.work(
            MathTex(rf"S_{{8}} = {left_riemann(0.0, 4.0, 8):.4f}",
                    color=STEPC))), run_time=0.9)
        self.wait(PAUSE)

        # ---- refine to n = 16 ----
        cap = self.subtitle(cap, "refine2")
        rects16 = self._rects(axes, curve, 16)
        self.play(Transform(rects, rects16), run_time=1.8)
        cap = self.subtitle(cap, "sum3")
        self.play(Transform(slabel, self._sum_label(16)), run_time=1.0)
        self.play(Transform(worked, self.work(
            MathTex(rf"S_{{16}} = {left_riemann(0.0, 4.0, 16):.4f}",
                    color=STEPC))), run_time=0.9)
        self.wait(PAUSE)

        # ---- the limit ----
        cap = self.subtitle(cap, "limit")
        box = SurroundingRectangle(target, color=ROOT, buff=0.15)
        self.play(Create(box), run_time=0.9)
        cap = self.subtitle(cap, "done")
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class RiemannSumsDemoFR(RiemannSumsDemo):
    lang = "fr"
