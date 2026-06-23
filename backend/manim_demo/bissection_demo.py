"""Bisection Method — 3Blue1Brown teaching version (strict layout contract).

We trap the root of a continuous function between two points where the sign
changes, then halve the interval again and again. The midpoint's sign tells us
which half still holds the root; we keep that half. A braced interval on the
x-axis shrinks step by step while a LaTeX table (in the RIGHT panel) fills in
with the real numbers, and each worked computation appears in the clear strip
under the graph. Captions are plain words; all maths are LaTeX.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, UP, Create, DashedLine, Dot, FadeIn, FadeOut, Flash, Line,
    MathTex, SurroundingRectangle, Text, Transform, VGroup,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, ACCENT2, PAUSE,
)


def f(x):
    return x * x - 2.0


TEXT = {
    "en": {
        "title": "Bisection Method",
        "why1": "Many equations cannot be solved by an exact formula.",
        "why2": "Bisection finds the answer safely, by trapping the root and shrinking the trap.",
        "motiv": "Example: find the square root of two, the number whose square is two.",
        "goal": "We look for where the blue curve crosses zero.",
        "s1": "Step one: find two points where the curve changes sign, one below zero and one above.",
        "bracket": "Between these points the curve must cross zero, so the root is trapped here.",
        "s2": "Step two: look at the midpoint of the interval.",
        "calc": "Compute the midpoint, then test the sign of the function there.",
        "decide": "The midpoint value is positive, so the root sits in the lower half.",
        "keep": "We keep that half and forget the rest. The trap is now half as wide.",
        "again": "Same idea: take the midpoint, check its sign, keep the half with the root.",
        "stop": "We stop when the interval is tiny, because both ends now agree on the answer.",
        "done": "Bisection always works for a continuous function that changes sign.",
    },
    "fr": {
        "title": "Methode de Dichotomie",
        "why1": "Beaucoup d'equations n'ont pas de solution par formule exacte.",
        "why2": "La dichotomie trouve la reponse surement, en piegeant la racine et en retrecissant le piege.",
        "motiv": "Exemple : trouver la racine carree de deux, le nombre dont le carre vaut deux.",
        "goal": "On cherche ou la courbe bleue s'annule.",
        "s1": "Etape un : trouver deux points ou la courbe change de signe, un sous zero et un au-dessus.",
        "bracket": "Entre ces points la courbe doit traverser zero, donc la racine est piegee ici.",
        "s2": "Etape deux : on regarde le milieu de l'intervalle.",
        "calc": "On calcule le milieu, puis on teste le signe de la fonction a cet endroit.",
        "decide": "La valeur au milieu est positive, donc la racine est dans la moitie basse.",
        "keep": "On garde cette moitie et on oublie le reste. Le piege est deux fois plus etroit.",
        "again": "Meme idee : on prend le milieu, on teste son signe, on garde la moitie avec la racine.",
        "stop": "On s'arrete quand l'intervalle est minuscule, car les deux bords s'accordent sur la reponse.",
        "done": "La dichotomie marche toujours pour une fonction continue qui change de signe.",
    },
}


class BisectionDemo(DemoScene):
    lang = "en"
    strings = TEXT

    def _table(self, data):
        header = r"n & a & b & m"
        body = r" \\ ".join(
            rf"{n} & {a:.4f} & {b:.4f} & {m:.4f}" for (n, a, b, m) in data
        )
        tex = r"\begin{array}{c c c c}" + header
        if body:
            tex += r" \\ " + body
        tex += r"\end{array}"
        return MathTex(tex, color=INK)

    def _bracket(self, axes, a, b):
        """A bracket sitting just under the x-axis spanning [a, b]."""
        y = -0.18
        left = axes.c2p(a, 0.0)
        right = axes.c2p(b, 0.0)
        base = Line(axes.c2p(a, y), axes.c2p(b, y), color=STEPC, stroke_width=5)
        ltick = Line(axes.c2p(a, y), left, color=STEPC, stroke_width=5)
        rtick = Line(axes.c2p(b, y), right, color=STEPC, stroke_width=5)
        return VGroup(base, ltick, rtick)

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

        # --- Panel (RIGHT): formula, rule, table ---
        formula = self.panel(MathTex(r"m=\frac{a+b}{2}", color=INK), y=2.7)
        rule = self.panel(MathTex(r"f(a)\,f(b)<0", color=MUTED), y=1.85)
        self.play(FadeIn(formula), run_time=1.0)
        self.play(FadeIn(rule), run_time=0.5)
        data = []
        table = self.panel(self._table(data), y=0.1)
        self.play(FadeIn(table), run_time=0.5)

        # ---- Step 0, in full detail: bracket [1, 2] ----
        a, b = 1.0, 2.0
        cap = self.subtitle(cap, "s1")
        da = Dot(axes.c2p(a, f(a)), color=ACCENT2, radius=0.08)  # f(1) < 0
        db = Dot(axes.c2p(b, f(b)), color=ROOT, radius=0.08)     # f(2) > 0
        self.play(FadeIn(da, scale=1.4), FadeIn(db, scale=1.4), run_time=0.8)

        cap = self.subtitle(cap, "bracket")
        brace = self._bracket(axes, a, b)
        self.play(Create(brace), run_time=1.2)
        self.wait(0.6)

        cap = self.subtitle(cap, "s2")
        m = (a + b) / 2.0
        mid = Dot(axes.c2p(m, 0.0), color=STEPC, radius=0.08)
        mdrop = DashedLine(axes.c2p(m, 0.0), axes.c2p(m, f(m)), color=MUTED, stroke_width=2)
        self.play(FadeIn(mid, scale=1.5), run_time=0.7)
        self.play(Create(mdrop), run_time=0.8)

        # WORKED computation in the clear strip under the graph.
        cap = self.subtitle(cap, "calc")
        worked = self.work(MathTex(
            r"m=\frac{1+2}{2}=1.5,\quad f(1.5)=0.25>0", color=STEPC))
        self.play(FadeIn(worked), run_time=1.2)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "decide")
        data.append((0, a, b, m))
        self.play(Transform(table, self.panel(self._table(data), y=0.1)), run_time=0.7)

        # keep lower half [1, 1.5]
        cap = self.subtitle(cap, "keep")
        b = m
        brace2 = self._bracket(axes, a, b)
        self.play(Transform(brace, brace2), FadeOut(mdrop), FadeOut(db), run_time=1.0)
        self.wait(PAUSE)
        self.play(FadeOut(worked), FadeOut(mid), FadeOut(da), run_time=0.6)

        # ---- Steps 1..3, each briefly explained ----
        n = 1
        for _ in range(3):
            cap = self.subtitle(cap, "again")
            m = (a + b) / 2.0
            mid = Dot(axes.c2p(m, 0.0), color=STEPC, radius=0.07)
            self.play(FadeIn(mid, scale=1.3), run_time=0.5)
            data.append((n, a, b, m))
            self.play(Transform(table, self.panel(self._table(data), y=0.1)), run_time=0.6)
            # decide which half keeps the sign change
            if f(a) * f(m) < 0:
                b = m
            else:
                a = m
            brace_next = self._bracket(axes, a, b)
            self.play(Transform(brace, brace_next), run_time=1.0)
            self.wait(1.0)
            self.play(FadeOut(mid), run_time=0.4)
            n += 1

        cap = self.subtitle(cap, "stop")
        box = SurroundingRectangle(table, color=ROOT, buff=0.12)
        self.play(Create(box), run_time=0.8)
        self.play(Flash(axes.c2p(root_x, 0.0), color=ROOT, line_length=0.2,
                        num_lines=16, flash_radius=0.35), run_time=1.1)
        cap = self.subtitle(cap, "done")
        self.wait(2.6)
        self.play(FadeOut(cap), run_time=0.6)


class BisectionDemoFR(BisectionDemo):
    lang = "fr"
