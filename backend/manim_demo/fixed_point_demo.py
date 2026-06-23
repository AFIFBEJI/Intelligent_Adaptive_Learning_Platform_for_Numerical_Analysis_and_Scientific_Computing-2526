"""Fixed-Point Iteration — 3Blue1Brown teaching version (strict layout contract).

We rewrite a problem as "x equals g of x" and look for where the curve meets
the diagonal line. Starting from a first guess we cobweb: go up to the curve,
across to the diagonal, and repeat, spiralling into the meeting point. Here g is
the Babylonian average and the fixed point is the square root of two. The
iteration table lives in the RIGHT panel and grows by Transform; the worked
update appears in the clear strip under the graph. Captions are plain words; all
maths are LaTeX.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, Create, Dot, FadeIn, FadeOut, Flash, Line, MathTex,
    SurroundingRectangle, Text, Transform, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, PAUSE,
)


def g(x):
    return (x + 2.0 / x) / 2.0


TEXT = {
    "en": {
        "title": "Fixed-Point Iteration",
        "why1": "Some problems are easiest to solve by repeating one simple update.",
        "why2": "We rewrite the question as a rule, then apply that rule over and over.",
        "motiv": "Example: find the square root of two by averaging a guess with two over the guess.",
        "goal": "Rewrite the problem so the answer is where the curve meets the diagonal line.",
        "s1": "Plot the update rule as a curve, and the diagonal where input equals output.",
        "meet": "The answer is the point where the curve and the diagonal cross.",
        "s2": "Start from a first guess on the diagonal.",
        "up": "Go straight up to the curve. This gives the next value of the guess.",
        "calc": "Apply the rule once to find the first new guess.",
        "over": "Now go across to the diagonal, carrying that new value back as the next input.",
        "again": "Repeat: up to the curve, across to the diagonal. The path spirals inward.",
        "why_conv": "It converges because the curve is nearly flat at the crossing, so each step barely overshoots.",
        "stop": "The value stops changing, so we have reached the fixed point.",
        "done": "Many problems become repeat until the value stops changing.",
    },
    "fr": {
        "title": "Iteration de Point Fixe",
        "why1": "Certains problemes se resolvent le plus simplement en repetant une mise a jour.",
        "why2": "On reecrit la question en une regle, puis on applique cette regle encore et encore.",
        "motiv": "Exemple : trouver la racine carree de deux en moyennant une estimation avec deux sur l'estimation.",
        "goal": "Reecrire le probleme pour que la reponse soit ou la courbe rencontre la diagonale.",
        "s1": "Tracer la regle de mise a jour en courbe, et la diagonale ou l'entree egale la sortie.",
        "meet": "La reponse est le point ou la courbe et la diagonale se croisent.",
        "s2": "Partir d'une premiere estimation sur la diagonale.",
        "up": "Monter tout droit vers la courbe. Cela donne la valeur suivante de l'estimation.",
        "calc": "On applique la regle une fois pour trouver la premiere nouvelle estimation.",
        "over": "Aller maintenant vers la diagonale, en ramenant cette nouvelle valeur comme entree suivante.",
        "again": "Repeter : vers la courbe, vers la diagonale. Le chemin spirale vers l'interieur.",
        "why_conv": "Cela converge car la courbe est presque plate au croisement, donc chaque pas depasse a peine.",
        "stop": "La valeur ne change plus, donc on a atteint le point fixe.",
        "done": "Beaucoup de problemes deviennent repeter jusqu'a ce que la valeur ne change plus.",
    },
}


class FixedPointDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def _table(self, data):
        header = r"n & x_n"
        body = r" \\ ".join(rf"{n} & {x:.4f}" for (n, x) in data)
        tex = r"\begin{array}{c c}" + header
        if body:
            tex += r" \\ " + body
        tex += r"\end{array}"
        return MathTex(tex, color=INK)

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
        axes = self.demo_axes(x_range=(1, 2.2, 0.2), y_range=(1, 2.2, 0.2))
        curve = axes.plot(g, x_range=[1.05, 2.1, 0.01], color=PRIMARY, stroke_width=5)
        diag = axes.plot(lambda X: X, x_range=[1.05, 2.1, 0.01], color=MUTED, stroke_width=3)
        # curve label tucked into the empty top-left corner of the graph
        glabel = MathTex(r"y=g(x)", color=PRIMARY).scale(0.55)
        glabel.move_to(axes.c2p(1.25, 2.12))
        dlabel = MathTex(r"y=x", color=MUTED).scale(0.5)
        dlabel.move_to(axes.c2p(2.05, 1.9))
        self.play(Create(axes), run_time=1.2)
        cap = self.subtitle(None, "motiv")

        cap = self.subtitle(cap, "goal")
        cap = self.subtitle(cap, "s1")
        self.play(Create(curve), run_time=1.6)
        self.play(FadeIn(glabel), run_time=0.7)
        self.play(Create(diag), run_time=1.2)
        self.play(FadeIn(dlabel), run_time=0.6)

        root_x = 2.0 ** 0.5
        cap = self.subtitle(cap, "meet")
        meet = Dot(axes.c2p(root_x, root_x), color=ROOT, radius=0.08)
        root_lbl = MathTex(r"\sqrt{2}", color=ROOT).scale(0.5)
        root_lbl.next_to(meet, UP, buff=0.12)
        self.play(FadeIn(meet, scale=1.5), FadeIn(root_lbl), run_time=1.0)

        # --- Panel (RIGHT): formula, condition, table ---
        formula = self.panel(MathTex(r"x_{n+1}=g(x_{n})", color=INK), y=2.7)
        defin = self.panel(MathTex(r"g(x)=\frac{x+\frac{2}{x}}{2}", color=MUTED), y=1.7)
        cond = self.panel(MathTex(r"|g'|<1", color=MUTED), y=0.85)
        self.play(FadeIn(formula), run_time=1.0)
        self.play(FadeIn(defin), run_time=0.6)
        self.play(FadeIn(cond), run_time=0.5)
        data = []
        table = self.panel(self._table(data), y=-0.9)
        self.play(FadeIn(table), run_time=0.5)

        # ---- First step in full detail ----
        x = 2.0
        cap = self.subtitle(cap, "s2")
        start = Dot(axes.c2p(x, x), color=STEPC, radius=0.08)
        self.play(FadeIn(start, scale=1.4), run_time=0.7)
        data.append((0, x))
        self.play(Transform(table, self.panel(self._table(data), y=-0.9)), run_time=0.6)

        cap = self.subtitle(cap, "up")
        gx = g(x)
        up_line = Line(axes.c2p(x, x), axes.c2p(x, gx), color=STEPC, stroke_width=4)
        self.play(Create(up_line), run_time=1.2)

        # WORKED computation in the clear strip under the graph.
        cap = self.subtitle(cap, "calc")
        worked = self.work(MathTex(r"x_{1}=g(2)=\frac{2+\frac{2}{2}}{2}=1.5", color=STEPC))
        self.play(FadeIn(worked), run_time=1.2)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "over")
        over_line = Line(axes.c2p(x, gx), axes.c2p(gx, gx), color=STEPC, stroke_width=4)
        self.play(Create(over_line), run_time=1.2)
        x = gx
        data.append((1, x))
        self.play(Transform(table, self.panel(self._table(data), y=-0.9)), run_time=0.6)
        self.wait(PAUSE)
        self.play(FadeOut(worked), FadeOut(start), run_time=0.6)

        # ---- Further cobweb steps ----
        cap = self.subtitle(cap, "again")
        for n in range(2, 5):
            gx = g(x)
            up_line = Line(axes.c2p(x, x), axes.c2p(x, gx), color=STEPC, stroke_width=3)
            self.play(Create(up_line), run_time=0.9)
            over_line = Line(axes.c2p(x, gx), axes.c2p(gx, gx), color=STEPC, stroke_width=3)
            self.play(Create(over_line), run_time=0.9)
            x = gx
            data.append((n, x))
            self.play(Transform(table, self.panel(self._table(data), y=-0.9)), run_time=0.6)
            self.wait(0.9)

        cap = self.subtitle(cap, "why_conv")
        cap = self.subtitle(cap, "stop")
        box = SurroundingRectangle(table, color=ROOT, buff=0.12)
        self.play(Create(box), run_time=0.8)
        self.play(Flash(axes.c2p(root_x, root_x), color=ROOT, line_length=0.2,
                        num_lines=16, flash_radius=0.35), run_time=1.1)
        cap = self.subtitle(cap, "done")
        self.wait(2.6)
        self.play(FadeOut(cap), run_time=0.6)


class FixedPointDemoFR(FixedPointDemo):
    lang = "fr"
