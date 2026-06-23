"""Divided differences — 3Blue1Brown teaching version.

Newton's divided-difference table turns a list of points into the coefficients
of an interpolating polynomial. We show HOW each number is obtained: the rule is
a difference of two neighbours divided by their gap in x. We work one entry by
hand so the origin of every value is clear, then fill the table column by column
and read the Newton coefficients off the top diagonal.
Layout contract: graph on the LEFT (self.demo_axes), every formula/table on the
RIGHT through self.panel, every worked number through self.work, captions through
self.subtitle (plain words, no math glyphs). Real maths only in MathTex.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, Create, Dot, FadeIn, FadeOut, Flash,
    MathTex, SurroundingRectangle, Text, Transform, VGroup, Write,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


DD = [(1, 1), (2, 4), (4, 16), (5, 25)]


def divided_differences(points):
    """Return the full triangular table as a list of columns (lists)."""
    xs = [p[0] for p in points]
    n = len(points)
    table = [[float(p[1]) for p in points]]  # column 0 = f[x_i]
    for k in range(1, n):
        prev = table[-1]
        col = []
        for i in range(n - k):
            val = (prev[i + 1] - prev[i]) / (xs[i + k] - xs[i])
            col.append(val)
        table.append(col)
    return table


def newton_coeffs(points):
    """Top diagonal entries = Newton coefficients."""
    table = divided_differences(points)
    return [col[0] for col in table]


def newton_eval(points, coeffs, x):
    xs = [p[0] for p in points]
    total = coeffs[0]
    prod = 1.0
    for k in range(1, len(coeffs)):
        prod *= (x - xs[k - 1])
        total += coeffs[k] * prod
    return total


TEXT = {
    "en": {
        "title": "Newton Divided Differences",
        "why1": "We have a handful of points and want the polynomial through them.",
        "why2": "Divided differences turn the data into that polynomial, step by step.",
        "motiv": "Here are the four points we will work with.",
        "rule": "Every new number is a difference of two neighbours over their gap in x.",
        "worked": "For the first two points: take four minus one, over two minus one.",
        "result": "So this first divided difference is three. That is how each value is made.",
        "col0": "First column: just the measured values at each point.",
        "col1": "Next column: apply the rule to every neighbouring pair, like we just did.",
        "col2": "We repeat, taking divided differences of the previous column the same way.",
        "col3": "One more pass leaves a single value at the bottom.",
        "diag": "The top entry of each column is a Newton coefficient.",
        "curve": "Those coefficients give the polynomial through every point.",
        "done": "From a small table to a full curve: that is divided differences.",
    },
    "fr": {
        "title": "Differences Divisees de Newton",
        "why1": "On a quelques points et on veut le polynome qui passe par eux.",
        "why2": "Les differences divisees transforment les donnees en ce polynome, pas a pas.",
        "motiv": "Voici les quatre points avec lesquels nous allons travailler.",
        "rule": "Chaque nouveau nombre est une difference de deux voisins sur leur ecart en x.",
        "worked": "Pour les deux premiers points : quatre moins un, sur deux moins un.",
        "result": "Cette premiere difference divisee vaut donc trois. Voila comment chaque valeur nait.",
        "col0": "Premiere colonne : simplement les valeurs mesurees en chaque point.",
        "col1": "Colonne suivante : on applique la regle a chaque paire voisine, comme a l'instant.",
        "col2": "On recommence, en prenant les differences divisees de la colonne precedente de meme.",
        "col3": "Un dernier passage laisse une seule valeur tout en bas.",
        "diag": "L'entree du haut de chaque colonne est un coefficient de Newton.",
        "curve": "Ces coefficients donnent le polynome passant par chaque point.",
        "done": "D'un petit tableau a une courbe complete : ce sont les differences divisees.",
    },
}


class DividedDifferencesDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def _table_tex(self, cols_shown):
        """Build the staggered divided-difference array, `cols_shown` value columns.

        A column with the x values plus one column per divided-difference order.
        The grid has 2n-1 rows; the j-th entry of difference column k sits on
        grid row k + 2j, so every value is shown and none collide.
        """
        table = divided_differences(DD)
        xs = [p[0] for p in DD]
        n = len(DD)
        ncols = cols_shown + 1            # 1 column for x, then the value columns
        nrows = 2 * n - 1
        grid = [["" for _ in range(ncols)] for _ in range(nrows)]
        # column of x values, one every two grid rows
        for i in range(n):
            grid[2 * i][0] = str(xs[i])
        # value columns
        for k in range(cols_shown):
            col = table[k]
            for j in range(len(col)):
                row = k + 2 * j
                grid[row][k + 1] = (rf"{col[j]:.0f}" if k == 0
                                    else rf"{col[j]:.2f}")
        col_spec = "c " * ncols
        body = r" \\ ".join(" & ".join(r) for r in grid)
        tex = r"\begin{array}{" + col_spec.strip() + "}" + body + r"\end{array}"
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

        # --- The points (graph LEFT) ---
        axes = self.demo_axes(x_range=(0, 6, 1), y_range=(0, 28, 7))
        self.play(Create(axes), run_time=1.3)
        cap = self.subtitle(None, "motiv")
        dots = VGroup(*[Dot(axes.c2p(x, y), color=ROOT, radius=0.08) for (x, y) in DD])
        for d in dots:
            self.play(FadeIn(d, scale=1.4), run_time=0.4)
        self.wait(0.5)

        # --- Explain HOW each number is obtained, BEFORE the table fills ---
        cap = self.subtitle(cap, "rule")
        rule = self.panel(
            MathTex(r"f[x_i,x_j]=\dfrac{f[x_j]-f[x_i]}{x_j-x_i}", color=INK), y=2.8)
        self.play(Write(rule), run_time=1.6)
        self.wait(PAUSE)

        # one fully worked entry, so the origin of every value is clear
        cap = self.subtitle(cap, "worked")
        worked = self.work(MathTex(
            r"f[x_0,x_1]=\dfrac{f(2)-f(1)}{2-1}=\dfrac{4-1}{2-1}", color=STEPC))
        self.play(Write(worked), run_time=1.8)
        self.wait(PAUSE)
        cap = self.subtitle(cap, "result")
        worked2 = self.work(MathTex(
            r"f[x_0,x_1]=\dfrac{4-1}{2-1}=3", color=STEPC))
        self.play(Transform(worked, worked2), run_time=1.2)
        self.wait(PAUSE)

        # --- Build the table column by column (RIGHT panel, under the rule) ---
        keys = ["col0", "col1", "col2", "col3"]
        cap = self.subtitle(cap, keys[0])
        table = self.panel(self._table_tex(1), y=0.4)
        self.play(FadeIn(table), run_time=1.0)
        self.wait(PAUSE)
        for k in range(1, len(DD)):
            cap = self.subtitle(cap, keys[k])
            self.play(Transform(table, self.panel(self._table_tex(k + 1), y=0.4)),
                      run_time=1.4)
            self.wait(PAUSE)
        self.play(FadeOut(worked), run_time=0.5)

        # --- The Newton coefficients on the diagonal (worked strip) ---
        cap = self.subtitle(cap, "diag")
        coeffs = newton_coeffs(DD)
        coeff_tex = self.work(MathTex(
            r"a_0,a_1,a_2,a_3 = "
            + ",\\;".join(rf"{c:.2f}" for c in coeffs),
            color=STEPC))
        self.play(Write(coeff_tex), run_time=1.6)
        self.wait(PAUSE)

        # --- The resulting polynomial ---
        cap = self.subtitle(cap, "curve")
        curve = axes.plot(lambda X: newton_eval(DD, coeffs, X),
                          x_range=[1, 5, 0.02], color=PRIMARY, stroke_width=5)
        plbl = MathTex(r"P(x)", color=PRIMARY).scale(0.55).move_to(axes.c2p(1.4, 26))
        self.play(Create(curve), Write(plbl), run_time=2.4)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "done")
        box = SurroundingRectangle(coeff_tex, color=ROOT, buff=0.15)
        self.play(Create(box), run_time=0.9)
        self.play(Flash(axes.c2p(3, newton_eval(DD, coeffs, 3)), color=STEPC,
                        line_length=0.2, num_lines=16, flash_radius=0.35), run_time=1.1)
        self.wait(3.0)
        self.play(FadeOut(cap), run_time=0.6)
        self.wait(0.3)


class DividedDifferencesDemoFR(DividedDifferencesDemo):
    lang = "fr"
