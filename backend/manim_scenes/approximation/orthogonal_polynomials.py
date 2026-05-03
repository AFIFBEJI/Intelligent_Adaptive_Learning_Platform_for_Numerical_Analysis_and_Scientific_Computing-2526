"""Orthogonal Polynomials : the first Legendre polynomials P_0, P_1, P_2, P_3.

We show the curves on [-1, 1] and emphasize that they form an orthogonal
basis under the L2 inner product.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP,
    Create, FadeIn, FadeOut, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, ACCENT_GREEN, BRAND_TEAL, BRAND_TEAL_LIGHT, NumeraScene,
    brand_axes, numera_caption,
)

# First 4 Legendre polynomials
def P0(x): return 1.0
def P1(x): return x
def P2(x): return 0.5 * (3 * x ** 2 - 1)
def P3(x): return 0.5 * (5 * x ** 3 - 3 * x)


class OrthogonalPolynomials(NumeraScene):
    """Plot P_0, P_1, P_2, P_3 Legendre polynomials on [-1, 1]."""

    def construct(self):
        self.numera_intro(
            "Orthogonal Polynomials",
            "Legendre's basis for least-squares approximation",
        )

        axes = brand_axes(x_range=(-1.2, 1.2, 0.5), y_range=(-1.5, 1.5, 0.5), width=8, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label(MathTex("P_n(x)")).set_color(BLACK).scale(0.7)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)

        cap = numera_caption("First Legendre polynomials on [-1, 1]").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.6)
        self.wait(0.6)

        polys = [
            ("P_0(x) = 1",                P0, BRAND_TEAL),
            ("P_1(x) = x",                P1, ACCENT_AMBER),
            ("P_2(x) = ½(3x² - 1)",       P2, ACCENT_GREEN),
            ("P_3(x) = ½(5x³ - 3x)",      P3, BRAND_TEAL_LIGHT),
        ]
        curves = []
        for label, fn, color in polys:
            new_cap = numera_caption(label).to_edge(UP, buff=0.4)
            self.play(Transform(cap, new_cap), run_time=0.5)
            curve = axes.plot(fn, x_range=[-1.05, 1.05], color=color, stroke_width=4)
            self.play(Create(curve), run_time=1.6)
            curves.append(curve)
            self.wait(0.7)

        # All four together
        cap2 = numera_caption("The 4 polynomials together — they are orthogonal").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap2), run_time=0.6)
        self.wait(2.0)

        eq = MathTex(
            r"\int_{-1}^{1} P_m(x) \, P_n(x) \, dx \;=\; 0 \text{ if } m \neq n",
            color=BLACK,
        ).scale(0.6)
        eq.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(Write(eq), run_time=2.4)
        self.wait(3.0)

        self.play(FadeOut(VGroup(axes, x_lab, y_lab, *curves, eq)), run_time=0.6)
        self.numera_outro("Orthogonal Polynomials  ·  numera")
