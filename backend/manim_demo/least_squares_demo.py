"""Least Squares — 3Blue1Brown teaching version (strict non-overlapping layout)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, LEFT, UP, Create, DashedLine, Dot, FadeIn, FadeOut,
    MathTex, SurroundingRectangle, Text, Transform, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


LS = [(0, 1.2), (1, 1.6), (2, 2.9), (3, 3.1), (4, 4.6), (5, 4.8), (6, 5.9)]


def sums(data):
    n = len(data)
    Sx = sum(p[0] for p in data)
    Sy = sum(p[1] for p in data)
    Sxx = sum(p[0] * p[0] for p in data)
    Sxy = sum(p[0] * p[1] for p in data)
    return n, Sx, Sy, Sxx, Sxy


def normal_equations(data):
    n, Sx, Sy, Sxx, Sxy = sums(data)
    a = (n * Sxy - Sx * Sy) / (n * Sxx - Sx * Sx)
    b = (Sy - a * Sx) / n
    return a, b


TEXT = {
    "en": {
        "title": "Least Squares Fitting",
        "why1": "Real measurements are noisy, so no line passes through every point.",
        "why2": "We want the one straight line that fits the cloud of points best.",
        "motiv": "Here are seven measured points that roughly follow a line.",
        "resid": "For any line, the residual is the vertical gap to each point.",
        "bad": "This first line is a poor guess. The gaps are large.",
        "square": "We add the squares of these gaps and make that total as small as possible.",
        "why_sq": "Squaring punishes big errors more, and gives one unique best answer.",
        "best": "This is the best fit line. The gaps are now as small as they can be.",
        "calc": "The slope and intercept come from the normal equations.",
        "plug": "We plug in the sums of the data and divide.",
        "result": "So the best line is fixed by these two numbers.",
        "done": "That is least squares: the line closest to noisy data.",
    },
    "fr": {
        "title": "Ajustement par Moindres Carres",
        "why1": "Les mesures reelles sont bruitees, aucune droite ne passe par tous les points.",
        "why2": "On cherche la seule droite qui ajuste au mieux le nuage de points.",
        "motiv": "Voici sept points mesures qui suivent a peu pres une droite.",
        "resid": "Pour une droite, le residu est l'ecart vertical a chaque point.",
        "bad": "Cette premiere droite est un mauvais choix. Les ecarts sont grands.",
        "square": "On additionne les carres de ces ecarts et on rend ce total minimal.",
        "why_sq": "Le carre penalise plus les grandes erreurs et donne une seule meilleure reponse.",
        "best": "Voici la droite de meilleur ajustement. Les ecarts sont aussi petits que possible.",
        "calc": "La pente et l'ordonnee viennent des equations normales.",
        "plug": "On remplace par les sommes des donnees et on divise.",
        "result": "La meilleure droite est donc fixee par ces deux nombres.",
        "done": "C'est les moindres carres : la droite la plus proche de donnees bruitees.",
    },
}


class LeastSquaresDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def _residuals(self, axes, slope, intercept):
        segs = VGroup()
        for (x, y) in LS:
            yline = slope * x + intercept
            segs.add(DashedLine(axes.c2p(x, y), axes.c2p(x, yline),
                                color=STEPC, stroke_width=3))
        return segs

    def construct(self):
        self.title("title")

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
        self.wait(2.0)
        self.play(FadeOut(intro), run_time=0.7)

        axes = self.demo_axes(x_range=(0, 6.5, 1), y_range=(0, 7, 1))
        dots = VGroup(*[Dot(axes.c2p(x, y), color=PRIMARY, radius=0.07)
                        for (x, y) in LS])
        self.play(Create(axes), run_time=1.3)
        cap = self.subtitle(None, "motiv")
        self.play(FadeIn(dots, lag_ratio=0.2), run_time=1.6)

        # Panel: number of points n, objective, and the two normal equations.
        count = MathTex(rf"n = {len(LS)} \;\text{{points}}", color=MUTED).scale(0.6)
        objective = MathTex(r"S=\sum_{i}\,(y_i-(ax_i+b))^{2}", color=INK).scale(0.6)
        a_form = MathTex(
            r"a=\frac{n\sum x_iy_i-\sum x_i\sum y_i}"
            r"{n\sum x_i^{2}-(\sum x_i)^{2}}", color=STEPC).scale(0.6)
        b_form = MathTex(r"b=\frac{\sum y_i-a\sum x_i}{n}", color=STEPC).scale(0.6)
        pvg = VGroup(count, objective, a_form, b_form).arrange(
            DOWN, buff=0.4, aligned_edge=LEFT)
        self.panel(pvg, y=0.5)
        self.play(FadeIn(count), FadeIn(objective), run_time=1.2)

        a_bad, b_bad = 0.55, 2.4
        bad_line = axes.plot(lambda X: a_bad * X + b_bad,
                             x_range=[0, 6.5], color=STEPC, stroke_width=4)
        cap = self.subtitle(cap, "bad")
        self.play(Create(bad_line), run_time=1.4)

        cap = self.subtitle(cap, "resid")
        res_bad = self._residuals(axes, a_bad, b_bad)
        self.play(Create(res_bad), run_time=1.6)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "square")
        cap = self.subtitle(cap, "why_sq")

        a, b = normal_equations(LS)
        best_line = axes.plot(lambda X: a * X + b,
                              x_range=[0, 6.5], color=ROOT, stroke_width=5)
        res_best = self._residuals(axes, a, b)
        cap = self.subtitle(cap, "best")
        self.play(Transform(bad_line, best_line),
                  Transform(res_bad, res_best), run_time=2.0)
        self.wait(PAUSE)

        eqn = MathTex(rf"y={a:.2f}\,x+{b:.2f}", color=ROOT).scale(0.5)
        eqn.move_to(axes.c2p(1.3, 6.4))
        self.play(FadeIn(eqn), run_time=0.9)

        cap = self.subtitle(cap, "calc")
        self.play(FadeIn(a_form), run_time=1.2)
        self.play(FadeIn(b_form), run_time=1.0)

        n, Sx, Sy, Sxx, Sxy = sums(LS)
        cap = self.subtitle(cap, "plug")
        worked_a = self.work(MathTex(
            rf"a=\frac{{{n}\cdot {Sxy:.1f}-{Sx}\cdot {Sy:.1f}}}"
            rf"{{{n}\cdot {Sxx}-{Sx}^{{2}}}}={a:.2f}", color=ROOT).scale(0.7))
        self.play(FadeIn(worked_a), run_time=1.4)
        self.wait(PAUSE)
        worked_b = self.work(MathTex(
            rf"b=\frac{{{Sy:.1f}-{a:.2f}\cdot {Sx}}}{{{n}}}={b:.2f}",
            color=ROOT).scale(0.7))
        self.play(Transform(worked_a, worked_b), run_time=1.2)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "result")
        box = SurroundingRectangle(eqn, color=ROOT, buff=0.15)
        self.play(Create(box), run_time=0.9)
        self.wait(PAUSE)

        self.play(FadeOut(worked_a), run_time=0.4)
        cap = self.subtitle(cap, "done")
        self.wait(2.6)
        self.play(FadeOut(cap), run_time=0.6)


class LeastSquaresDemoFR(LeastSquaresDemo):
    lang = "fr"
