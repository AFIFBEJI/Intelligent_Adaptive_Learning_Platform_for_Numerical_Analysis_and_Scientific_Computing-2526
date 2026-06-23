"""Gaussian Quadrature — 3Blue1Brown teaching version.

Instead of many equally spaced points, choose a FEW clever ones. The two-point
Gauss-Legendre rule samples at plus and minus one over root three, with equal
weights, and is EXACT for cubics. Graph on the LEFT, the rule, the node/weight
table and the exact value in stacked RIGHT panels (self.panel) so nothing is cut
off, and the worked Gauss computation in the strip under the graph (self.work).
Captions are plain words; maths are LaTeX.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, LEFT, UP, Create, DashedLine, Dot, FadeIn, FadeOut, MathTex,
    Text, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


def f(x):
    return x ** 3 + 2.0 * x * x - x + 1.0


NODE = 1.0 / math.sqrt(3.0)  # 0.5773502...
EXACT = 10.0 / 3.0           # exact integral on [-1, 1]
GAUSS = f(-NODE) + f(NODE)   # weights are both 1


TEXT = {
    "en": {
        "title": "Gaussian Quadrature",
        "why1": "Most rules use many equally spaced sample points.",
        "why2": "Gaussian quadrature picks a few clever points instead, and wins.",
        "motiv": "Here is a cubic curve to integrate on the interval from minus one to one.",
        "goal": "We will use just two sample points, chosen with great care.",
        "s1": "The two nodes sit at minus and plus one over root three.",
        "s2": "That is about minus zero point five eight and plus zero point five eight.",
        "rule": "The rule is a weighted sum of the curve heights at those nodes.",
        "compute": "With both weights equal to one, we just add the two heights.",
        "exact": "The two-point result matches the exact integral, ten over three.",
        "magic": "Two clever points are exact for any cubic, no error at all.",
        "done": "Far fewer evaluations for the same accuracy: that is the payoff.",
    },
    "fr": {
        "title": "Quadrature de Gauss",
        "why1": "La plupart des methodes utilisent beaucoup de points equidistants.",
        "why2": "La quadrature de Gauss choisit plutot quelques points malins, et gagne.",
        "motiv": "Voici une courbe cubique a integrer sur l'intervalle de moins un a un.",
        "goal": "On va utiliser seulement deux points, choisis avec grand soin.",
        "s1": "Les deux noeuds sont a moins et plus un sur racine de trois.",
        "s2": "C'est environ moins zero virgule cinquante-huit et plus zero virgule cinquante-huit.",
        "rule": "La regle est une somme ponderee des hauteurs de la courbe a ces noeuds.",
        "compute": "Les deux poids valant un, il suffit d'additionner les deux hauteurs.",
        "exact": "Le resultat a deux points egale l'integrale exacte, dix tiers.",
        "magic": "Deux points malins sont exacts pour toute cubique, aucune erreur.",
        "done": "Bien moins d'evaluations pour la meme precision : c'est le benefice.",
    },
}


class GaussianQuadratureDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def _node_table(self):
        tex = (
            r"\begin{array}{c c}"
            r"x_i & w_i \\ "
            r"-0.5774 & 1 \\ "
            r"+0.5774 & 1"
            r"\end{array}"
        )
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

        # --- The problem (graph LEFT) ---
        axes = self.demo_axes(x_range=(-1, 1, 0.5), y_range=(0, 4, 1))
        curve = axes.plot(f, x_range=[-1, 1, 0.02], color=PRIMARY, stroke_width=5)
        flabel = MathTex(r"f(x)=x^{3}+2x^{2}-x+1", color=PRIMARY).scale(0.45)
        flabel.move_to(axes.c2p(-0.4, 3.6))
        self.play(Create(axes), run_time=1.3)
        self.play(Create(curve), run_time=1.8)
        self.play(FadeIn(flabel), run_time=0.9)
        cap = self.subtitle(None, "motiv")

        # --- Mark the two nodes (labels kept clear of axis ticks) ---
        cap = self.subtitle(cap, "goal")
        cap = self.subtitle(cap, "s1")
        nodes = VGroup()
        drops = VGroup()
        for xn in (-NODE, NODE):
            nodes.add(Dot(axes.c2p(xn, f(xn)), color=STEPC, radius=0.08))
            drops.add(DashedLine(axes.c2p(xn, 0), axes.c2p(xn, f(xn)),
                                 color=MUTED, stroke_width=2))
        self.play(FadeIn(nodes, scale=1.4), Create(drops), run_time=1.4)
        # Short node tags placed near each node, above the axis numbers.
        nl_left = MathTex(r"-0.58", color=STEPC).scale(0.4)
        nl_left.next_to(axes.c2p(-NODE, f(-NODE)), UP, buff=0.12)
        nl_right = MathTex(r"+0.58", color=STEPC).scale(0.4)
        nl_right.next_to(axes.c2p(NODE, f(NODE)), UP, buff=0.12)
        self.play(FadeIn(nl_left), FadeIn(nl_right), run_time=1.0)
        cap = self.subtitle(cap, "s2")
        self.wait(PAUSE)

        # --- The rule, the small node/weight table and the exact value, all
        # arranged together in ONE VGroup on the RIGHT panel so nothing
        # overlaps. Each member is revealed in order via FadeIn. ---
        cap = self.subtitle(cap, "rule")
        rule = MathTex(r"\int_{-1}^{1} f \approx \sum_i w_i\,f(x_i)",
                       color=INK).scale(0.6)
        table = self._node_table().scale(0.6)
        exact = MathTex(r"\int_{-1}^{1} f\,dx = \frac{10}{3}", color=ROOT).scale(0.6)
        exact2 = MathTex(rf"= {EXACT:.4f}", color=ROOT).scale(0.6)
        panel_vg = VGroup(rule, table, exact, exact2).arrange(
            DOWN, buff=0.4, aligned_edge=LEFT)
        self.panel(panel_vg, y=0.8)
        self.play(FadeIn(rule), run_time=1.4)
        self.play(FadeIn(table), run_time=1.0)

        # --- The worked Gauss computation in the strip ONLY ---
        cap = self.subtitle(cap, "compute")
        worked = self.work(
            MathTex(rf"f(-0.5774)+f(0.5774) = {GAUSS:.4f}", color=STEPC))
        self.play(FadeIn(worked), run_time=1.6)
        self.wait(PAUSE)

        # --- The exact value, revealed in the same panel VGroup ---
        cap = self.subtitle(cap, "exact")
        self.play(FadeIn(exact), FadeIn(exact2), run_time=1.4)
        cap = self.subtitle(cap, "magic")
        self.wait(PAUSE)

        cap = self.subtitle(cap, "done")
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class GaussianQuadratureDemoFR(GaussianQuadratureDemo):
    lang = "fr"
