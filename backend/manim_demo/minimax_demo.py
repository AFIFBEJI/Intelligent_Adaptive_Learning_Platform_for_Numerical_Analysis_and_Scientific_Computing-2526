"""Minimax Approximation — 3Blue1Brown teaching version (strict layout).

Minimise the worst error, not the average. We compare two error curves of two
different fits. One is small in the middle but spikes near the ends; the minimax
error instead equioscillates, with equal-amplitude peaks, so its worst case is
smaller. The error curves are illustrative.

Layout: error curves in the LEFT half (self.demo_axes), with their names in an
empty graph corner via c2p; the minimax goal and the worst-error readings are
stacked in ONE VGroup in the RIGHT panel (self.panel), so they never overlap;
the worked peak value (pure maths) goes in the strip under the graph
(self.work); all wording is bilingual via self.subtitle.
"""
import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, LEFT, UP, Create, DashedLine, Dot, FadeIn, FadeOut,
    MathTex, SurroundingRectangle, Text, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, ROOT, ACCENT2, PAUSE,
)


# Illustrative error curves (the error of two different fits)
def e_ls(x):
    return 0.3 * x ** 4 - 0.04 * x


def e_mm(x):
    return 0.12 * math.cos(4.0 * math.pi * x)


TEXT = {
    "en": {
        "title": "Minimax Approximation",
        "why1": "We replace a function by a simple polynomial, but some error always remains.",
        "why2": "Minimax asks for the smallest possible worst error across the whole range.",
        "motiv": "Look at the error of a fit: how far the polynomial is from the true function.",
        "ls": "This first error is tiny in the middle but spikes badly near the ends.",
        "lsmax": "Its worst error is large, sitting at the right end of the range.",
        "mm": "Here is the error of a different fit. The peaks all have the same height.",
        "equi": "This equal bouncing behaviour is the sign of the minimax solution.",
        "mmmax": "Its worst error is smaller, and it is shared evenly across the range.",
        "goal": "Minimax makes the largest error as small as possible.",
        "use": "Useful where the worst case matters, like hardware function tables.",
        "done": "Minimax controls the worst error, not just the average.",
    },
    "fr": {
        "title": "Approximation Minimax",
        "why1": "On remplace une fonction par un polynome simple, mais une erreur subsiste toujours.",
        "why2": "Le minimax demande la plus petite erreur maximale sur toute la plage.",
        "motiv": "Regardons l'erreur d'un ajustement : l'ecart du polynome a la vraie fonction.",
        "ls": "Cette premiere erreur est minuscule au centre mais explose pres des bords.",
        "lsmax": "Son erreur maximale est grande, situee au bord droit de la plage.",
        "mm": "Voici l'erreur d'un autre ajustement. Les pics ont tous la meme hauteur.",
        "equi": "Ce rebond egal est le signe de la solution minimax.",
        "mmmax": "Son erreur maximale est plus petite et repartie egalement sur la plage.",
        "goal": "Le minimax rend la plus grande erreur aussi petite que possible.",
        "use": "Utile quand le pire cas compte, comme les tables de fonctions materielles.",
        "done": "Le minimax controle l'erreur maximale, pas seulement la moyenne.",
    },
}


class MinimaxDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def construct(self):
        self.title("title")

        # --- Introduction: why minimax (centred, slow) ---
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

        # --- The axes (graph LEFT) ---
        axes = self.demo_axes(x_range=(-1, 1, 0.5), y_range=(-0.35, 0.35, 0.1))
        self.play(Create(axes), run_time=1.3)
        cap = self.subtitle(None, "motiv")

        # --- Maths panel (RIGHT): goal + worst-error readings in ONE VGroup ---
        amp = 0.12
        ls_peak = e_ls(1.0)
        goal = MathTex(
            r"\min_{p}\;\max_{x}\;\lvert f(x)-p(x)\rvert", color=ROOT).scale(0.6)
        read_ls = MathTex(
            rf"\max\lvert e_{{\mathrm{{ls}}}}\rvert={ls_peak:.2f}",
            color=ACCENT2).scale(0.6)
        read_mm = MathTex(
            rf"\max\lvert e_{{\mathrm{{mm}}}}\rvert={amp:.2f}",
            color=PRIMARY).scale(0.6)

        pvg = VGroup(goal, read_ls, read_mm).arrange(
            DOWN, buff=0.4, aligned_edge=LEFT)
        self.panel(pvg, y=0.4)
        self.play(FadeIn(goal), run_time=1.4)

        # --- The least-squares-style error curve (graph LEFT) ---
        ls_curve = axes.plot(e_ls, x_range=[-1, 1, 0.01], color=ACCENT2, stroke_width=5)
        ls_label = MathTex(r"e_{\mathrm{ls}}(x)", color=ACCENT2).scale(0.55)
        ls_label.move_to(axes.c2p(-0.55, 0.30))
        cap = self.subtitle(cap, "ls")
        self.play(Create(ls_curve), run_time=1.8)
        self.play(FadeIn(ls_label), run_time=0.8)

        # mark its large maximum at the end x=1
        ls_dot = Dot(axes.c2p(1.0, ls_peak), color=ACCENT2, radius=0.08)
        ls_bound = DashedLine(axes.c2p(-1, ls_peak), axes.c2p(1, ls_peak),
                              color=ACCENT2, stroke_width=2)
        cap = self.subtitle(cap, "lsmax")
        self.play(FadeIn(ls_dot, scale=1.4), Create(ls_bound), run_time=1.2)
        self.play(FadeIn(read_ls), run_time=1.0)
        self.wait(PAUSE)
        self.play(FadeOut(ls_curve), FadeOut(ls_dot), FadeOut(ls_bound),
                  FadeOut(ls_label), run_time=0.7)

        # --- The minimax error curve, equioscillating (graph LEFT) ---
        mm_curve = axes.plot(e_mm, x_range=[-1, 1, 0.005], color=PRIMARY, stroke_width=5)
        mm_label = MathTex(r"e_{\mathrm{mm}}(x)", color=PRIMARY).scale(0.55)
        mm_label.move_to(axes.c2p(-0.55, 0.30))
        cap = self.subtitle(cap, "mm")
        self.play(Create(mm_curve), run_time=1.8)
        self.play(FadeIn(mm_label), run_time=0.8)

        # equal-amplitude dashed bounds
        up_bound = DashedLine(axes.c2p(-1, amp), axes.c2p(1, amp),
                              color=PRIMARY, stroke_width=2)
        dn_bound = DashedLine(axes.c2p(-1, -amp), axes.c2p(1, -amp),
                              color=PRIMARY, stroke_width=2)
        peaks = VGroup(*[Dot(axes.c2p(xp, e_mm(xp)), color=PRIMARY, radius=0.06)
                         for xp in (-1.0, -0.5, 0.0, 0.5, 1.0)])
        cap = self.subtitle(cap, "equi")
        self.play(Create(up_bound), Create(dn_bound), run_time=1.0)
        self.play(FadeIn(peaks, lag_ratio=0.2), run_time=1.2)

        # worked equal-peak reading: pure maths in the strip (equal amplitude)
        worked_mm = self.work(MathTex(
            rf"\lvert e_{{\mathrm{{mm}}}}(x_k)\rvert={amp:.2f}",
            color=PRIMARY).scale(0.72))
        self.play(FadeIn(worked_mm), run_time=1.2)
        self.play(FadeIn(read_mm), run_time=1.0)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "mmmax")
        self.wait(0.5)

        # --- The minimax goal highlighted (panel, RIGHT) ---
        cap = self.subtitle(cap, "goal")
        box = SurroundingRectangle(goal, color=ROOT, buff=0.15)
        self.play(Create(box), run_time=0.9)
        self.wait(PAUSE)

        self.play(FadeOut(worked_mm), run_time=0.4)
        cap = self.subtitle(cap, "use")
        self.wait(0.6)
        cap = self.subtitle(cap, "done")
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class MinimaxDemoFR(MinimaxDemo):
    lang = "fr"
