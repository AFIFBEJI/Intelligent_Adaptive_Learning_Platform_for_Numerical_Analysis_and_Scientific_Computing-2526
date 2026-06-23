"""Trapezoidal Rule - 3Blue1Brown teaching version.

Instead of flat-topped rectangles, use trapezoids whose slanted tops follow the
curve. The slanted tops hug the curve, so the error is much smaller. We build
the trapezoids as polygons. Graph on the LEFT, formula and target in the RIGHT
panel (self.panel), the worked trapezoid sum in the strip under the graph
(self.work). Captions are plain words; all maths are LaTeX.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, Create, FadeIn, FadeOut, MathTex, Polygon,
    SurroundingRectangle, Text, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


def f(x):
    return 0.4 * x * x + 1.0


def trapezoid_rule(a, b, n):
    dx = (b - a) / n
    xs = [a + i * dx for i in range(n + 1)]
    total = f(xs[0]) + f(xs[-1]) + 2.0 * sum(f(x) for x in xs[1:-1])
    return total * dx / 2.0


TRUE_AREA = 0.4 * 64.0 / 3.0 + 4.0  # 12.5333...


TEXT = {
    "en": {
        "title": "Trapezoidal Rule",
        "why1": "Flat-topped rectangles leave gaps or overshoot the curve.",
        "why2": "We can do better by letting the tops slant along the curve.",
        "motiv": "Same curve as before, on the same interval.",
        "goal": "Split the interval into a few equal pieces.",
        "s1": "On each piece, join the two curve heights with a straight slanted top.",
        "s2": "Each shape is a trapezoid that follows the curve far more closely.",
        "formula": "Add the trapezoid areas. This is the trapezoid rule.",
        "result": "The estimate is already very close to the true area.",
        "error": "The slanted tops hug the curve, so the error is much smaller than rectangles.",
        "done": "More trapezoids would shrink the small remaining error even further.",
    },
    "fr": {
        "title": "Methode des Trapezes",
        "why1": "Les rectangles a sommet plat laissent des trous ou depassent la courbe.",
        "why2": "On fait mieux en laissant les sommets s'incliner le long de la courbe.",
        "motiv": "Meme courbe qu'avant, sur le meme intervalle.",
        "goal": "On decoupe l'intervalle en quelques morceaux egaux.",
        "s1": "Sur chaque morceau, on relie les deux hauteurs par un sommet incline.",
        "s2": "Chaque forme est un trapeze qui suit la courbe de bien plus pres.",
        "formula": "On additionne les aires des trapezes. C'est la methode des trapezes.",
        "result": "L'estimation est deja tres proche de l'aire reelle.",
        "error": "Les sommets inclines epousent la courbe, l'erreur est bien plus petite que les rectangles.",
        "done": "Plus de trapezes reduiraient encore la petite erreur restante.",
    },
}


class TrapezoidalDemo(DemoScene):
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

        # --- The problem (graph LEFT) ---
        axes = self.demo_axes(x_range=(0, 4, 1), y_range=(0, 8, 2))
        curve = axes.plot(f, x_range=[0, 4, 0.02], color=PRIMARY, stroke_width=5)
        flabel = MathTex(r"f(x)=0.4\,x^{2}+1", color=PRIMARY).scale(0.55)
        flabel.move_to(axes.c2p(0.95, 7.2))
        self.play(Create(axes), run_time=1.3)
        self.play(Create(curve), run_time=1.8)
        self.play(FadeIn(flabel), run_time=0.9)
        cap = self.subtitle(None, "motiv")

        # --- The maths panel (RIGHT) ---
        formula = self.panel(
            MathTex(r"T=\frac{\Delta x}{2}\,(f_0+2f_1+\dots+f_n)", color=INK),
            y=2.6)
        target = self.panel(
            MathTex(rf"\int_{{0}}^{{4}} f(x)\,dx = {TRUE_AREA:.4f}", color=ROOT),
            y=1.5)
        self.play(FadeIn(formula), run_time=1.3)
        self.play(FadeIn(target), run_time=0.7)

        # --- Build trapezoids ---
        cap = self.subtitle(cap, "goal")
        n = 4
        a, b = 0.0, 4.0
        dx = (b - a) / n
        c2p = axes.coords_to_point

        cap = self.subtitle(cap, "s1")
        traps = VGroup()
        for i in range(n):
            xi = a + i * dx
            xj = xi + dx
            poly = Polygon(
                c2p(xi, 0), c2p(xi, f(xi)), c2p(xj, f(xj)), c2p(xj, 0),
                color=STEPC, stroke_width=1.5,
                fill_color=STEPC, fill_opacity=0.45,
            )
            traps.add(poly)
        self.play(Create(traps), run_time=2.2)
        cap = self.subtitle(cap, "s2")
        self.wait(PAUSE)

        # --- The result: value in panel, worked line in strip ---
        cap = self.subtitle(cap, "formula")
        est = trapezoid_rule(a, b, n)
        slabel = self.panel(
            MathTex(rf"T = {est:.4f}", color=STEPC), y=0.4)
        self.play(FadeIn(slabel), run_time=1.0)
        worked = self.work(
            MathTex(rf"T = \frac{{\Delta x}}{{2}}\,(f_0+2f_1+2f_2+2f_3+f_4)"
                    rf" = {est:.4f}", color=STEPC))
        self.play(FadeIn(worked), run_time=1.4)
        cap = self.subtitle(cap, "result")
        box = SurroundingRectangle(slabel, color=STEPC, buff=0.12)
        self.play(Create(box), run_time=0.9)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "error")
        self.wait(PAUSE)
        cap = self.subtitle(cap, "done")
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class TrapezoidalDemoFR(TrapezoidalDemo):
    lang = "fr"
