"""Gaussian Quadrature : non-uniform sample points for higher accuracy.

We show that with the SAME number of nodes (4 here), Gauss-Legendre
nodes (chosen optimally) give a much better approximation than evenly
spaced ones.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP,
    Create, Dot, FadeIn, FadeOut, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, ACCENT_GREEN, BRAND_TEAL, NumeraScene, brand_axes, numera_caption,
)


def f(x: float) -> float:
    return 0.6 + math.cos(x) + 0.15 * x


class GaussianQuadrature(NumeraScene):
    """Visualize uniform vs Gauss-Legendre node placement on [0, 4]."""

    def construct(self):
        self.numera_intro(
            "Gaussian Quadrature",
            "Smart node placement for higher accuracy",
        )

        axes = brand_axes(x_range=(-0.3, 4.5, 1), y_range=(-0.5, 3, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label("f(x)").set_color(BLACK).scale(0.7)
        curve = axes.plot(f, x_range=[0, 4], color=BRAND_TEAL, stroke_width=4)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.play(Create(curve), run_time=2.0)

        # ---------- Uniform sampling (4 nodes) ----------
        cap = numera_caption("Uniform nodes : 4 evenly spaced samples").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.6)
        uniform_xs = [0.5, 1.5, 2.5, 3.5]
        uniform_dots = [Dot(axes.coords_to_point(x, f(x)), color=ACCENT_AMBER, radius=0.10)
                        for x in uniform_xs]
        for d in uniform_dots:
            self.play(FadeIn(d, scale=1.4), run_time=0.4)
        self.wait(1.0)

        # ---------- Gauss-Legendre nodes (4-point on [0, 4]) ----------
        # Standard 4-point Gauss-Legendre nodes on [-1, 1] are approximately :
        #   ±0.339981, ±0.861136
        # Mapped to [0, 4] : x_i = (b - a)/2 * t_i + (a + b)/2 = 2 * t_i + 2.
        cap2 = numera_caption("Gauss-Legendre nodes : optimally chosen, NOT evenly spaced").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap2), run_time=0.6)

        gauss_t = [-0.861136, -0.339981, 0.339981, 0.861136]
        gauss_xs = [2 * t + 2 for t in gauss_t]
        gauss_dots = [Dot(axes.coords_to_point(x, f(x)), color=ACCENT_GREEN, radius=0.10)
                      for x in gauss_xs]

        # Animate the transition : uniform -> Gauss
        for ud, gd in zip(uniform_dots, gauss_dots):
            self.play(Transform(ud, gd), run_time=0.6)
        self.wait(1.5)

        cap3 = numera_caption("Same N = 4, but exact for any polynomial of degree ≤ 7").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap3), run_time=0.6)
        self.wait(2.0)

        formula = MathTex(
            r"\int_a^b f(x)\,dx \;\approx\; \sum_{i=1}^{n} w_i \, f(x_i)",
            color=BLACK,
        ).scale(0.7)
        formula.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(Write(formula), run_time=2.0)
        self.wait(3.0)

        self.play(FadeOut(VGroup(curve, *uniform_dots, axes, x_lab, y_lab, formula)), run_time=0.6)
        self.numera_outro("Gaussian Quadrature  ·  numera")
