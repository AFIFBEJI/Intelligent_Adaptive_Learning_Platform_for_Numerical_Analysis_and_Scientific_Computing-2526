"""Newton-Raphson — reference demo with the strict non-overlapping layout.

Graph on the LEFT, maths panel on the RIGHT (self.panel), worked computation in
the clear strip under the graph (self.work), bold-white caption band at the
bottom (self.subtitle). Real mechanism, real numbers, slow.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, Create, DashedLine, Dot, FadeIn, FadeOut, Flash,
    MathTex, SurroundingRectangle, Text, Transform, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


def f(x):
    return x * x - 2.0


def fp(x):
    return 2.0 * x


TEXT = {
    "en": {
        "title": "Newton-Raphson Method",
        "why1": "Many equations cannot be solved by an exact formula.",
        "why2": "Newton-Raphson finds the answer fast, by improving a guess step by step.",
        "motiv": "Example: find the square root of 2, the number whose square is 2.",
        "goal": "We look for where the blue curve crosses zero.",
        "s1": "Step 1: start from a first guess on the curve.",
        "s2": "Step 2: draw the tangent there. Its slope is the derivative.",
        "cross": "Where does this line cross the axis? Let us compute it.",
        "s3": "That value, 1.5, is our next guess.",
        "closer": "It is already much closer to the answer than 2 was.",
        "again": "Same idea at the new point, where f = {v:.4f}. Draw the tangent again.",
        "stop": "We stop at n = 3: f is almost 0, the guess no longer changes.",
        "done": "That is the square root of 2, how calculators compute roots.",
    },
    "fr": {
        "title": "Methode de Newton-Raphson",
        "why1": "Beaucoup d'equations n'ont pas de solution par formule exacte.",
        "why2": "Newton-Raphson trouve vite la reponse, en ameliorant une estimation pas a pas.",
        "motiv": "Exemple : trouver la racine carree de 2, le nombre dont le carre vaut 2.",
        "goal": "On cherche ou la courbe bleue s'annule.",
        "s1": "Etape 1 : on part d'une premiere estimation sur la courbe.",
        "s2": "Etape 2 : on trace la tangente. Sa pente est la derivee.",
        "cross": "Ou cette droite coupe-t-elle l'axe ? On le calcule.",
        "s3": "Cette valeur, 1,5, est notre estimation suivante.",
        "closer": "Elle est deja bien plus proche de la reponse que 2.",
        "again": "Meme idee au nouveau point, ou f = {v:.4f}. On retrace la tangente.",
        "stop": "On s'arrete a n = 3 : f est presque 0, la valeur ne change plus.",
        "done": "C'est la racine carree de 2, ainsi les calculatrices calculent.",
    },
}


class NewtonRaphsonDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def _table(self, data):
        header = r"n & x_n & f(x_n)"
        body = r" \\ ".join(rf"{n} & {x:.4f} & {fx:+.4f}" for (n, x, fx) in data)
        tex = r"\begin{array}{c c c}" + header
        if body:
            tex += r" \\ " + body
        tex += r"\end{array}"
        return MathTex(tex, color=INK)

    def _tangent(self, axes, x):
        from manim import Line
        m = fp(x)
        xi = x - f(x) / m
        lo = max(0.25, min(x, xi) - 0.45)
        hi = min(2.55, max(x, xi) + 0.45)
        line = axes.plot(lambda X, x=x, m=m: f(x) + m * (X - x),
                         x_range=[lo, hi], color=STEPC, stroke_width=4)
        return line, xi

    def construct(self):
        self.title("title")

        # Introduction (centred, slow).
        intro = VGroup(
            Text(self.t("why1"), font="Arial", color=INK).scale(0.55),
            Text(self.t("why2"), font="Arial", color=MUTED).scale(0.5),
        ).arrange(DOWN, buff=0.5)
        for line in intro:
            if line.width > 11:
                line.scale_to_fit_width(11)
        intro.move_to(UP * 0.2)
        self.play(FadeIn(intro[0], shift=UP * 0.2), run_time=1.2)
        self.wait(1.2)
        self.play(FadeIn(intro[1], shift=UP * 0.2), run_time=1.2)
        self.wait(2.0)
        self.play(FadeOut(intro), run_time=0.6)

        # Problem (graph LEFT).
        axes = self.demo_axes(x_range=(0, 2.6, 0.5), y_range=(-2.5, 5, 1))
        curve = axes.plot(f, x_range=[0.2, 2.45, 0.02], color=PRIMARY, stroke_width=5)
        flabel = MathTex(r"f(x)=x^{2}-2", color=PRIMARY).scale(0.55).move_to(axes.c2p(0.9, 4.2))
        self.play(Create(axes), run_time=1.2)
        self.play(Create(curve), run_time=1.6)
        self.play(FadeIn(flabel), run_time=0.7)
        cap = self.subtitle(None, "motiv")

        root_x = 2.0 ** 0.5
        root_mark = DashedLine(axes.c2p(root_x, -2.5), axes.c2p(root_x, 0),
                               color=ROOT, stroke_width=2)
        root_lbl = MathTex(r"\sqrt{2}", color=ROOT).scale(0.5)
        root_lbl.next_to(axes.c2p(root_x, -2.5), DOWN, buff=0.12)
        cap = self.subtitle(cap, "goal")
        self.play(Create(root_mark), FadeIn(root_lbl), run_time=0.9)

        # Panel (RIGHT): formula, derivative, table.
        formula = self.panel(MathTex(r"x_{n+1}=x_{n}-\frac{f(x_{n})}{f'(x_{n})}", color=INK), y=2.7)
        dlabel = self.panel(MathTex(r"f'(x)=2x", color=MUTED), y=1.85)
        self.play(FadeIn(formula), run_time=1.0)
        self.play(FadeIn(dlabel), run_time=0.5)
        data = []
        table = self.panel(self._table(data), y=0.1)
        self.play(FadeIn(table), run_time=0.5)

        # Iteration 0, in full detail.
        x = 2.0
        cap = self.subtitle(cap, "s1")
        pt = Dot(axes.c2p(x, f(x)), color=STEPC, radius=0.08)
        self.play(FadeIn(pt, scale=1.4), run_time=0.6)
        cap = self.subtitle(cap, "s2")
        tan, xi = self._tangent(axes, x)
        self.play(Create(tan), run_time=1.5)

        cap = self.subtitle(cap, "cross")
        worked = self.work(MathTex(r"x_{1}=2-\frac{f(2)}{f'(2)}=2-\frac{2}{4}=1.5", color=STEPC))
        self.play(FadeIn(worked), run_time=1.2)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "s3")
        inter = Dot(axes.c2p(xi, 0.0), color=ROOT, radius=0.08)
        self.play(FadeIn(inter, scale=1.5), run_time=0.6)
        data.append((0, x, f(x)))
        self.play(Transform(table, self.panel(self._table(data), y=0.1)), run_time=0.7)
        cap = self.subtitle(cap, "closer")
        self.wait(PAUSE)
        self.play(FadeOut(worked), FadeOut(tan), FadeOut(pt), run_time=0.6)

        # Iterations 1..3.
        x = xi
        for n in range(1, 4):
            cap = self.subtitle(cap, "again", v=f(x))
            pt = Dot(axes.c2p(x, f(x)), color=STEPC, radius=0.07)
            self.play(FadeIn(pt, scale=1.3), run_time=0.5)
            tan, xi = self._tangent(axes, x)
            self.play(Create(tan), run_time=1.3)
            data.append((n, x, f(x)))
            self.play(Transform(table, self.panel(self._table(data), y=0.1)), run_time=0.6)
            inter = Dot(axes.c2p(xi, 0.0), color=ROOT, radius=0.06)
            self.play(FadeIn(inter, scale=1.3), run_time=0.5)
            self.wait(0.9)
            self.play(FadeOut(tan), FadeOut(pt), run_time=0.4)
            x = xi

        cap = self.subtitle(cap, "stop")
        box = SurroundingRectangle(table, color=ROOT, buff=0.12)
        self.play(Create(box), run_time=0.8)
        self.play(Flash(axes.c2p(root_x, 0.0), color=ROOT, line_length=0.2,
                        num_lines=16, flash_radius=0.35), run_time=1.1)
        cap = self.subtitle(cap, "done")
        self.wait(2.6)
        self.play(FadeOut(cap), run_time=0.6)


class NewtonRaphsonDemoFR(NewtonRaphsonDemo):
    lang = "fr"
