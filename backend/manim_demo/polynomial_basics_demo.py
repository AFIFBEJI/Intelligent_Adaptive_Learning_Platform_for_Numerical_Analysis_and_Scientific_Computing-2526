"""Polynomial basics — 3Blue1Brown teaching version."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manim import (  # noqa: E402
    DOWN, LEFT, UP, Create, DashedLine, Dot, FadeIn, FadeOut, Flash,
    MathTex, SurroundingRectangle, Text, VGroup, Write,
)
from manim_demo._demo import (  # noqa: E402
    DemoScene, INK, MUTED, PRIMARY, STEPC, ROOT, ACCENT2, PAUSE,
)


def p(x):
    return 0.3 * x ** 3 - 1.2 * x ** 2 + x + 2.0


TEXT = {
    "en": {
        "title": "Polynomials, the Building Blocks",
        "why1": "Polynomials are sums of simple powers of x.",
        "why2": "They are flexible, and easy to evaluate, to differentiate and to integrate.",
        "motiv": "Let us first look at the powers on their own.",
        "m0": "The constant one is just a flat line.",
        "m1": "The first power is a straight slanted line.",
        "m2": "The square bends once into a smooth bowl.",
        "m3": "The cube can bend twice, turning up then down.",
        "combine": "A polynomial mixes these powers with chosen weights.",
        "plot": "Here is one such mix, drawn as a single smooth curve.",
        "degree": "The highest power is the degree, and it limits how many bends appear.",
        "eval": "We can evaluate it at any point, for example at two.",
        "compute": "Put two into every power, multiply by the weights, then add.",
        "done": "Powers in, one smooth curve out: that is a polynomial.",
    },
    "fr": {
        "title": "Les Polynomes, briques de base",
        "why1": "Les polynomes sont des sommes de puissances simples de x.",
        "why2": "Ils sont souples, et faciles a evaluer, a deriver et a integrer.",
        "motiv": "Regardons d'abord les puissances toutes seules.",
        "m0": "La constante un est simplement une ligne plate.",
        "m1": "La premiere puissance est une droite inclinee.",
        "m2": "Le carre se courbe une fois en une cuvette lisse.",
        "m3": "Le cube peut se courber deux fois, montant puis descendant.",
        "combine": "Un polynome melange ces puissances avec des poids choisis.",
        "plot": "Voici un tel melange, trace comme une seule courbe lisse.",
        "degree": "La plus haute puissance est le degre, et elle limite le nombre de courbures.",
        "eval": "On peut l'evaluer en tout point, par exemple en deux.",
        "compute": "On met deux dans chaque puissance, on multiplie par les poids, puis on additionne.",
        "done": "Des puissances en entree, une courbe lisse en sortie : c'est un polynome.",
    },
}


class PolynomialBasicsDemo(DemoScene):
    lang = "en"
    strings = TEXT

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

        axes = self.demo_axes(x_range=(-2.5, 2.5, 1), y_range=(-3, 4, 1))
        self.play(Create(axes), run_time=1.3)
        cap = self.subtitle(None, "motiv")

        monos = [
            (lambda X: 1.0 + 0 * X, r"y=1", MUTED, "m0"),
            (lambda X: X, r"y=x", STEPC, "m1"),
            (lambda X: X ** 2, r"y=x^{2}", ROOT, "m2"),
            (lambda X: X ** 3, r"y=x^{3}", ACCENT2, "m3"),
        ]
        power_lbls = VGroup(*[
            MathTex(tex, color=col).scale(0.6) for (_, tex, col, _) in monos
        ]).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        self.panel(power_lbls, y=1.7)
        for (fn, _, col, key), lbl in zip(monos, power_lbls):
            cap = self.subtitle(cap, key)
            g = axes.plot(fn, x_range=[-2.4, 2.4, 0.02], color=col, stroke_width=4)
            self.play(Create(g), FadeIn(lbl), run_time=1.4)
            self.wait(0.6)

        self.wait(PAUSE)

        cap = self.subtitle(cap, "combine")
        self.play(FadeOut(power_lbls), run_time=0.6)
        # Single-line polynomial equation (per request), plus the degree note.
        poly = MathTex(r"p(x)=0.3\,x^{3}-1.2\,x^{2}+x+2", color=PRIMARY).scale(0.6)
        deg = MathTex(r"\deg p = 3", color=MUTED).scale(0.6)
        deg2 = MathTex(r"\text{up to } 2 \text{ bends}", color=MUTED).scale(0.6)
        panel_vg = VGroup(poly, deg, deg2).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        self.panel(panel_vg, y=1.1)
        self.play(FadeIn(poly), run_time=1.0)

        cap = self.subtitle(cap, "plot")
        curve = axes.plot(p, x_range=[-2.4, 2.4, 0.02], color=PRIMARY, stroke_width=5)
        plbl = MathTex(r"p(x)", color=PRIMARY).scale(0.55).move_to(axes.c2p(-2.0, 3.6))
        self.play(Create(curve), FadeIn(plbl), run_time=2.2)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "degree")
        self.play(FadeIn(deg), FadeIn(deg2), run_time=0.8)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "eval")
        xq = 2.0
        yq = p(xq)
        drop = DashedLine(axes.c2p(xq, 0.0), axes.c2p(xq, yq), color=MUTED, stroke_width=2)
        qdot = Dot(axes.c2p(xq, yq), color=STEPC, radius=0.08)
        self.play(Create(drop), FadeIn(qdot, scale=1.4), run_time=1.0)

        cap = self.subtitle(cap, "compute")
        worked = self.work(MathTex(
            r"p(2)=0.3(8)-1.2(4)+2+2=" + rf"{yq:.1f}", color=STEPC))
        self.play(Write(worked), run_time=1.8)
        self.wait(PAUSE)

        cap = self.subtitle(cap, "done")
        box = SurroundingRectangle(worked, color=ROOT, buff=0.15)
        self.play(Create(box), run_time=0.9)
        self.play(Flash(axes.c2p(xq, yq), color=STEPC, line_length=0.2,
                        num_lines=16, flash_radius=0.35), run_time=1.1)
        self.wait(2.6)
        self.play(FadeOut(cap), run_time=0.6)


class PolynomialBasicsDemoFR(PolynomialBasicsDemo):
    lang = "fr"
