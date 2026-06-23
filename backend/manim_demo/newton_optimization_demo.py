"""Newton Optimisation — 3Blue1Brown teaching version (strict layout).

Use curvature to jump straight to the minimum. Newton's method for optimisation
fits a parabola using the second derivative and lands at its vertex. For this
bowl it reaches the exact minimum in a single step. We contrast this with
gradient descent, which needed many small steps.

Layout: bowl in the LEFT half (self.demo_axes), with its name in an empty graph
corner via c2p; the update rule, the derivatives and the iteration table live in
the RIGHT panel (self.panel, stacked); the worked single step goes in the strip
under the graph (self.work); plain-word captions via self.subtitle. Maths in
MathTex.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, Arrow, Create, DashedLine, Dot, FadeIn, FadeOut,
    Flash, MathTex, SurroundingRectangle, Text, Transform, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


def f(x):
    return (x - 2.0) ** 2 + 1.0


def fp(x):
    return 2.0 * (x - 2.0)


def fpp(x):
    return 2.0


X0 = 4.0


TEXT = {
    "en": {
        "title": "Newton Optimisation",
        "why1": "Gradient descent walks downhill in many small steps.",
        "why2": "Newton uses the curvature to jump straight toward the minimum.",
        "motiv": "Same bowl as before, with its minimum at the centre. We start to the right.",
        "curv": "The second derivative measures how the slope itself is changing.",
        "rule": "Newton divides the slope by the curvature.",
        "fit": "It fits a parabola at the start point, which here matches the bowl exactly.",
        "step": "One worked step lands exactly on the minimum.",
        "jump": "The arrow goes straight from the start to the vertex in a single move.",
        "contrast": "Gradient descent needed many steps, Newton needs only one here.",
        "cost": "The price is that Newton also needs the second derivative.",
        "done": "Newton trades extra information for far faster convergence.",
    },
    "fr": {
        "title": "Optimisation de Newton",
        "why1": "La descente de gradient descend en beaucoup de petits pas.",
        "why2": "Newton utilise la courbure pour sauter droit vers le minimum.",
        "motiv": "Le meme bol qu'avant, avec son minimum au centre. On part vers la droite.",
        "curv": "La derivee seconde mesure comment la pente elle-meme change.",
        "rule": "Newton divise la pente par la courbure.",
        "fit": "Il ajuste une parabole au point de depart, qui ici epouse exactement le bol.",
        "step": "Un seul pas calcule tombe pile sur le minimum.",
        "jump": "La fleche va droit du depart au sommet en un seul mouvement.",
        "contrast": "La descente de gradient demandait beaucoup de pas, Newton n'en demande qu'un ici.",
        "cost": "Le prix est que Newton a aussi besoin de la derivee seconde.",
        "done": "Newton echange une information en plus contre une convergence bien plus rapide.",
    },
}


class NewtonOptimizationDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def _table(self, data, y=-0.4):
        header = r"n & x_n & f(x_n)"
        body = r" \\ ".join(rf"{n} & {x:.4f} & {fx:.4f}" for (n, x, fx) in data)
        tex = r"\begin{array}{c c c}" + header
        if body:
            tex += r" \\ " + body
        tex += r"\end{array}"
        return self.panel(MathTex(tex, color=INK), y=y)

    def construct(self):
        self.title("title")

        # --- Introduction: why curvature (centred, slow) ---
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

        # --- The bowl (graph LEFT) ---
        axes = self.demo_axes(x_range=(0, 4.5, 1), y_range=(0, 6, 1))
        curve = axes.plot(f, x_range=[0.2, 4.3, 0.02], color=PRIMARY, stroke_width=5)
        flabel = MathTex(r"f(x)=(x-2)^{2}+1", color=PRIMARY).scale(0.5)
        flabel.move_to(axes.c2p(1.0, 5.5))
        self.play(Create(axes), run_time=1.3)
        self.play(Create(curve), run_time=1.6)
        self.play(FadeIn(flabel), run_time=0.9)
        cap = self.subtitle(None, "motiv")

        min_mark = DashedLine(axes.c2p(2.0, 0), axes.c2p(2.0, f(2.0)),
                              color=ROOT, stroke_width=2)
        self.play(Create(min_mark), run_time=0.8)

        # --- Maths panel (RIGHT): rule, derivatives, iteration table ---
        rule = self.panel(MathTex(
            r"x_{n+1}=x_{n}-\frac{f'(x_{n})}{f''(x_{n})}", color=INK), y=2.8)
        dlabel = self.panel(MathTex(
            r"f'(x)=2(x-2),\;f''(x)=2", color=MUTED), y=1.9)
        cap = self.subtitle(cap, "curv")
        self.play(FadeIn(rule), run_time=1.0)
        cap = self.subtitle(cap, "rule")
        self.play(FadeIn(dlabel), run_time=0.6)

        data = [(0, X0, f(X0))]
        table = self._table(data)
        self.play(FadeIn(table), run_time=0.5)

        # --- Starting dot ---
        x = X0
        dot = Dot(axes.c2p(x, f(x)), color=STEPC, radius=0.09)
        self.play(FadeIn(dot, scale=1.4), run_time=0.7)

        # --- The fitted parabola (here equals f) ---
        cap = self.subtitle(cap, "fit")
        parab = axes.plot(f, x_range=[0.2, 4.3, 0.02], color=STEPC, stroke_width=3)
        self.play(Create(parab), run_time=1.5)
        self.wait(0.6)

        # --- One worked step (strip under the graph) ---
        cap = self.subtitle(cap, "step")
        worked = self.work(MathTex(
            r"x_{1}=4-\frac{f'(4)}{f''(4)}=4-\frac{4}{2}=2", color=STEPC))
        self.play(FadeIn(worked), run_time=1.6)

        # update the iteration table live (panel)
        x_new = x - fp(x) / fpp(x)
        data.append((1, x_new, f(x_new)))
        self.play(Transform(table, self._table(data)), run_time=0.6)
        self.wait(PAUSE)

        # --- The jump arrow from start to vertex ---
        cap = self.subtitle(cap, "jump")
        vertex = Dot(axes.c2p(x_new, f(x_new)), color=ROOT, radius=0.09)
        arrow = Arrow(axes.c2p(x, f(x)), axes.c2p(x_new, f(x_new)),
                      color=ROOT, buff=0.1, stroke_width=4)
        self.play(Create(arrow), run_time=1.3)
        self.play(FadeIn(vertex, scale=1.5), run_time=0.7)
        self.play(Flash(axes.c2p(x_new, f(x_new)), color=ROOT, line_length=0.2,
                        num_lines=16, flash_radius=0.35), run_time=1.1)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "contrast")
        box = SurroundingRectangle(table, color=ROOT, buff=0.12)
        self.play(Create(box), run_time=0.9)
        self.wait(0.6)
        cap = self.subtitle(cap, "cost")
        self.wait(0.6)

        cap = self.subtitle(cap, "done")
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class NewtonOptimizationDemoFR(NewtonOptimizationDemo):
    lang = "fr"
