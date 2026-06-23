"""Gradient Descent — 3Blue1Brown teaching version (strict layout).

Follow the slope downhill. We minimise a bowl by repeatedly stepping against the
derivative, scaled by a learning rate. A dot walks down the bowl toward the
minimum while a table fills in with the real numbers, and the update for each
step is worked out with the real numbers in the strip under the graph.

Layout: bowl in the LEFT half (self.demo_axes); the update rule, the derivative
and the live iteration table are stacked in ONE VGroup in the RIGHT panel
(self.panel), so they can never overlap; each worked step replaces the previous
worked line via self.work; plain-word captions via self.subtitle. Real maths
only in MathTex.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, LEFT, UP, Create, DashedLine, Dot, FadeIn, FadeOut, Flash,
    MathTex, SurroundingRectangle, Text, Transform, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


def f(x):
    return (x - 2.0) ** 2 + 1.0


def fp(x):
    return 2.0 * (x - 2.0)


ETA = 0.3
X0 = 4.0
N_STEPS = 5


TEXT = {
    "en": {
        "title": "Gradient Descent",
        "why1": "To find the lowest point of a curve, we can simply walk downhill.",
        "why2": "At each step we move against the slope, and the bottom comes closer.",
        "motiv": "This bowl has its minimum at the centre. We start off to the right.",
        "slope": "The derivative tells us the slope under our feet.",
        "rule": "We step against the slope, scaled by the learning rate.",
        "step1": "First step from the start point, worked out with real numbers.",
        "walk": "Repeating the rule, the dot walks steadily down toward the minimum.",
        "eta": "The learning rate sets the step size: too big overshoots, too small crawls.",
        "stop": "After a few steps we are essentially at the bottom.",
        "done": "That is gradient descent: many small steps guided by the slope.",
    },
    "fr": {
        "title": "Descente de Gradient",
        "why1": "Pour trouver le point le plus bas d'une courbe, on peut simplement descendre.",
        "why2": "A chaque pas on avance contre la pente, et le fond se rapproche.",
        "motiv": "Ce bol a son minimum au centre. On demarre vers la droite.",
        "slope": "La derivee nous donne la pente sous nos pieds.",
        "rule": "On avance contre la pente, mise a l'echelle par le taux d'apprentissage.",
        "step1": "Premier pas depuis le depart, calcule avec de vrais nombres.",
        "walk": "En repetant la regle, le point descend regulierement vers le minimum.",
        "eta": "Le taux d'apprentissage fixe la taille du pas : trop grand depasse, trop petit rampe.",
        "stop": "Apres quelques pas on est pratiquement au fond.",
        "done": "C'est la descente de gradient : beaucoup de petits pas guides par la pente.",
    },
}


class GradientDescentDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def _table_tex(self, data):
        """The iteration table as ONE MathTex array (replaced via Transform)."""
        header = r"n & x_n & f(x_n)"
        body = r" \\ ".join(rf"{n} & {x:.3f} & {fx:.3f}" for (n, x, fx) in data)
        tex = r"\begin{array}{c c c}" + header
        if body:
            tex += r" \\ " + body
        tex += r"\end{array}"
        return MathTex(tex, color=INK).scale(0.6)

    def _worked_tex(self, n, x):
        """The update computed at this step, with the real numbers."""
        g = fp(x)
        x_new = x - ETA * g
        return MathTex(
            rf"x_{{{n}}}={x:.3f}-0.3\cdot f'({x:.3f})"
            rf"={x:.3f}-0.3\cdot {g:.3f}={x_new:.3f}",
            color=STEPC).scale(0.62)

    def construct(self):
        self.title("title")

        # --- Introduction: why walk downhill (centred, slow) ---
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

        # mark the minimum at x=2
        min_mark = DashedLine(axes.c2p(2.0, 0), axes.c2p(2.0, f(2.0)),
                              color=ROOT, stroke_width=2)
        self.play(Create(min_mark), run_time=0.8)

        # --- Maths panel (RIGHT): rule, derivative, live table in ONE VGroup ---
        rule = MathTex(r"x_{n+1}=x_{n}-\eta\,f'(x_{n})", color=INK).scale(0.6)
        dlabel = MathTex(r"f'(x)=2(x-2)", r"\eta=0.3", color=MUTED).scale(0.6)
        dlabel.arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        data = [(0, X0, f(X0))]
        table = self._table_tex(data)

        pvg = VGroup(rule, dlabel, table).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        self.panel(pvg, y=0.4)

        cap = self.subtitle(cap, "slope")
        self.play(FadeIn(rule), run_time=1.0)
        cap = self.subtitle(cap, "rule")
        self.play(FadeIn(dlabel), run_time=0.6)
        self.play(FadeIn(table), run_time=0.5)

        # keep a fixed anchor for re-placing the growing table
        table_y = table.get_center()[1]

        def place_table(tex):
            tex.scale_to_fit_width(min(tex.width, 5.2))
            tex.move_to([3.7, table_y, 0])
            tex.align_to(rule, LEFT)
            return tex

        place_table(table)

        # --- Starting dot ---
        x = X0
        dot = Dot(axes.c2p(x, f(x)), color=STEPC, radius=0.09)
        self.play(FadeIn(dot, scale=1.4), run_time=0.7)

        # --- Worked first step (strip under the graph, real numbers) ---
        cap = self.subtitle(cap, "step1")
        worked = self.work(self._worked_tex(1, x))
        self.play(FadeIn(worked), run_time=1.6)
        self.wait(PAUSE)

        # --- Walk down the bowl; table + worked line update live ---
        cap = self.subtitle(cap, "walk")
        for n in range(1, N_STEPS + 1):
            new_worked = self.work(self._worked_tex(n, x))
            self.play(Transform(worked, new_worked), run_time=0.8)
            x_new = x - ETA * fp(x)
            new_dot = Dot(axes.c2p(x_new, f(x_new)), color=STEPC, radius=0.09)
            self.play(Transform(dot, new_dot), run_time=1.0)
            data.append((n, x_new, f(x_new)))
            self.play(Transform(table, place_table(self._table_tex(data))),
                      run_time=0.6)
            self.wait(0.7)
            x = x_new

        self.play(FadeOut(worked), run_time=0.4)
        cap = self.subtitle(cap, "eta")
        self.wait(0.6)

        cap = self.subtitle(cap, "stop")
        box = SurroundingRectangle(table, color=ROOT, buff=0.12)
        self.play(Create(box), run_time=0.9)
        self.play(Flash(axes.c2p(2.0, f(2.0)), color=ROOT, line_length=0.2,
                        num_lines=16, flash_radius=0.35), run_time=1.1)
        cap = self.subtitle(cap, "done")
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class GradientDescentDemoFR(GradientDescentDemo):
    lang = "fr"
