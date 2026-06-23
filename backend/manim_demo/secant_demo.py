"""Secant Method — 3Blue1Brown teaching version (strict layout contract).

Like Newton but with no derivative: draw the straight line through the last two
points on the curve and read off where it crosses the axis. That crossing is the
next guess. We march the secant lines toward the root, fading the older ones,
while a LaTeX table (in the RIGHT panel) fills in with the real values and the
worked x-intercept appears in the clear strip under the graph. Captions are
plain words; all maths are LaTeX.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, LEFT, UP, Create, DashedLine, Dot, FadeIn, FadeOut, Flash, MathTex,
    SurroundingRectangle, Text, Transform, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


def f(x):
    return x * x - 2.0


TEXT = {
    "en": {
        "title": "Secant Method",
        "why1": "Newton's method is fast, but it needs the derivative of the function.",
        "why2": "The secant method gets nearly the same speed using only the function itself.",
        "motiv": "Example: find the square root of two, the number whose square is two.",
        "goal": "We look for where the blue curve crosses zero.",
        "s1": "Step one: start from two guesses, two points on the curve.",
        "s2": "Step two: draw the straight line through those two points.",
        "cross": "Where does this line cross the axis? That crossing is the next guess.",
        "calc": "Plug the numbers into the formula to find the crossing.",
        "s3": "That value, about one point three three, is our next guess.",
        "closer": "It is already closer to the answer than either starting point was.",
        "again": "Now use the two most recent points, draw a new line, and read off the next guess.",
        "stop": "We stop when the guesses settle, because the value barely changes.",
        "done": "Nearly as fast as Newton, but it needs no derivative.",
    },
    "fr": {
        "title": "Methode de la Secante",
        "why1": "La methode de Newton est rapide, mais elle a besoin de la derivee de la fonction.",
        "why2": "La methode de la secante atteint presque la meme vitesse en n'utilisant que la fonction.",
        "motiv": "Exemple : trouver la racine carree de deux, le nombre dont le carre vaut deux.",
        "goal": "On cherche ou la courbe bleue s'annule.",
        "s1": "Etape un : on part de deux estimations, deux points sur la courbe.",
        "s2": "Etape deux : on trace la droite passant par ces deux points.",
        "cross": "Ou cette droite coupe-t-elle l'axe ? Ce point est l'estimation suivante.",
        "calc": "On remplace les nombres dans la formule pour trouver le croisement.",
        "s3": "Cette valeur, environ un virgule trois trois, est notre estimation suivante.",
        "closer": "Elle est deja plus proche de la reponse que chacun des points de depart.",
        "again": "On prend les deux points les plus recents, on trace une nouvelle droite, et on lit l'estimation suivante.",
        "stop": "On s'arrete quand les estimations se stabilisent, car la valeur change a peine.",
        "done": "Presque aussi rapide que Newton, mais sans aucune derivee.",
    },
}


class SecantDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def _table(self, data):
        header = r"n & x_n"
        body = r" \\ ".join(rf"{n} & {x:.4f}" for (n, x) in data)
        tex = r"\begin{array}{c c}" + header
        if body:
            tex += r" \\ " + body
        tex += r"\end{array}"
        return MathTex(tex, color=INK).scale(0.6)

    def _place_table(self, formula, table):
        """Place the (growing) table just below the fixed formula, both inside
        the RIGHT panel, so the two never overlap as the table grows down."""
        if table.width > 5.2:
            table.scale_to_fit_width(5.2)
        table.next_to(formula, DOWN, buff=0.4, aligned_edge=LEFT)
        return table

    def _secant(self, axes, x0, x1):
        """Full secant line through (x0,f(x0)) and (x1,f(x1)) and its x-intercept."""
        y0, y1 = f(x0), f(x1)
        slope = (y1 - y0) / (x1 - x0)
        xi = x1 - y1 / slope
        lo = max(0.25, min(x0, x1, xi) - 0.35)
        hi = min(2.55, max(x0, x1, xi) + 0.35)
        line = axes.plot(lambda X, x1=x1, y1=y1, slope=slope: y1 + slope * (X - x1),
                         x_range=[lo, hi], color=STEPC, stroke_width=4)
        return line, xi

    def construct(self):
        self.title("title")

        # --- Introduction: centred, slow ---
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

        # --- The problem (graph LEFT) ---
        axes = self.demo_axes(x_range=(0, 2.6, 0.5), y_range=(-2.5, 5, 1))
        curve = axes.plot(f, x_range=[0.2, 2.45, 0.02], color=PRIMARY, stroke_width=5)
        flabel = MathTex(r"f(x)=x^{2}-2", color=PRIMARY).scale(0.55)
        flabel.move_to(axes.c2p(0.9, 4.2))
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

        # --- Panel (RIGHT): formula on top, table below, never overlapping ---
        # Split the long secant rule into two readable stacked lines, kept in
        # ONE arranged VGroup pinned to the top of the panel; the table grows
        # underneath it (re-placed via _place_table on every Transform).
        formula = VGroup(
            MathTex(r"x_{n+1}=x_{n}", color=INK).scale(0.6),
            MathTex(r"-\,f(x_{n})\,\frac{x_{n}-x_{n-1}}{f(x_{n})-f(x_{n-1})}",
                    color=INK).scale(0.6),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        self.panel(formula, y=2.4)
        self.play(FadeIn(formula), run_time=1.2)
        data = []
        table = self._place_table(formula, self._table(data))
        self.play(FadeIn(table), run_time=0.5)

        # ---- First step in full detail: x0 = 2, x1 = 1 ----
        x0, x1 = 2.0, 1.0
        cap = self.subtitle(cap, "s1")
        p0 = Dot(axes.c2p(x0, f(x0)), color=STEPC, radius=0.08)
        p1 = Dot(axes.c2p(x1, f(x1)), color=STEPC, radius=0.08)
        self.play(FadeIn(p0, scale=1.4), FadeIn(p1, scale=1.4), run_time=0.8)
        data.append((0, x0))
        data.append((1, x1))
        self.play(Transform(table, self._place_table(formula, self._table(data))), run_time=0.6)

        cap = self.subtitle(cap, "s2")
        sec, xi = self._secant(axes, x0, x1)
        self.play(Create(sec), run_time=1.6)
        self.wait(0.6)

        cap = self.subtitle(cap, "cross")
        cap = self.subtitle(cap, "calc")
        # WORKED computation in the clear strip under the graph.
        worked = self.work(MathTex(
            r"x_{2}=1-(-1)\,\frac{1-2}{-1-2}=1.3333", color=STEPC))
        self.play(FadeIn(worked), run_time=1.2)
        self.wait(PAUSE)

        # only NOW reveal the next guess on the axis
        cap = self.subtitle(cap, "s3")
        inter = Dot(axes.c2p(xi, 0.0), color=ROOT, radius=0.08)
        drop = DashedLine(axes.c2p(xi, 0.0), axes.c2p(xi, f(xi)), color=MUTED, stroke_width=2)
        self.play(FadeIn(inter, scale=1.5), run_time=0.7)
        data.append((2, xi))
        self.play(Transform(table, self._place_table(formula, self._table(data))), run_time=0.7)
        cap = self.subtitle(cap, "closer")
        self.play(Create(drop), run_time=0.8)
        self.wait(PAUSE)
        self.play(FadeOut(worked), FadeOut(sec), FadeOut(drop),
                  FadeOut(p0), FadeOut(p1), run_time=0.6)

        # ---- Iterations using the last two points, fade older lines ----
        x0, x1 = x1, xi
        prev_sec = None
        n = 3
        for _ in range(3):
            cap = self.subtitle(cap, "again")
            pa = Dot(axes.c2p(x0, f(x0)), color=STEPC, radius=0.06)
            pb = Dot(axes.c2p(x1, f(x1)), color=STEPC, radius=0.06)
            self.play(FadeIn(pa, scale=1.3), FadeIn(pb, scale=1.3), run_time=0.5)
            sec, xi = self._secant(axes, x0, x1)
            if prev_sec is not None:
                self.play(FadeOut(prev_sec), Create(sec), run_time=1.2)
            else:
                self.play(Create(sec), run_time=1.2)
            inter = Dot(axes.c2p(xi, 0.0), color=ROOT, radius=0.06)
            self.play(FadeIn(inter, scale=1.3), run_time=0.5)
            data.append((n, xi))
            self.play(Transform(table, self._place_table(formula, self._table(data))), run_time=0.6)
            self.wait(1.0)
            self.play(FadeOut(pa), FadeOut(pb), run_time=0.4)
            prev_sec = sec
            x0, x1 = x1, xi
            n += 1

        cap = self.subtitle(cap, "stop")
        if prev_sec is not None:
            self.play(FadeOut(prev_sec), run_time=0.4)
        box = SurroundingRectangle(table, color=ROOT, buff=0.12)
        self.play(Create(box), run_time=0.8)
        self.play(Flash(axes.c2p(root_x, 0.0), color=ROOT, line_length=0.2,
                        num_lines=16, flash_radius=0.35), run_time=1.1)
        cap = self.subtitle(cap, "done")
        self.wait(2.6)
        self.play(FadeOut(cap), run_time=0.6)


class SecantDemoFR(SecantDemo):
    lang = "fr"
