"""Simpson's Rule : approximate the area using parabolas instead of trapezoids.

Show the curve, then fit a parabola through 3 sampled points,
shade the area under the parabola, and compare to the true integral.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np  # noqa: E402

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP,
    Create, Dot, FadeIn, FadeOut, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, BRAND_TEAL, BRAND_TEAL_LIGHT, NumeraScene, brand_axes, numera_caption,
)


def f(x: float) -> float:
    return 0.5 + 0.7 * math.sin(0.9 * x) + 0.2 * x


class SimpsonsRule(NumeraScene):
    """Show parabolic approximation through 3 points covering each pair of subintervals."""

    def construct(self):
        self.numera_intro(
            "Simpson's Rule",
            "Parabolas instead of trapezoids",
        )

        axes = brand_axes(x_range=(-0.3, 4.5, 1), y_range=(-0.5, 3, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label("f(x)").set_color(BLACK).scale(0.7)
        curve = axes.plot(f, x_range=[0, 4], color=BRAND_TEAL, stroke_width=4)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.play(Create(curve), run_time=2.0)

        cap = numera_caption(r"We approximate ∫₀⁴ f(x) dx with parabolas").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.6)
        self.wait(0.8)

        # Sample 3 points : a, midpoint, b for each pair (here just one parabola for clarity)
        a, m, b = 0.0, 2.0, 4.0
        sample_pts = [(a, f(a)), (m, f(m)), (b, f(b))]
        sample_dots = [Dot(axes.coords_to_point(x, y), color=ACCENT_AMBER, radius=0.10)
                       for x, y in sample_pts]
        for d in sample_dots:
            self.play(FadeIn(d, scale=1.4), run_time=0.6)

        cap2 = numera_caption("Fit a parabola through 3 points : (a, mid, b)").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap2), run_time=0.6)

        # Build the parabola through these 3 points
        xs = np.array([p[0] for p in sample_pts])
        ys = np.array([p[1] for p in sample_pts])
        coeffs = np.polyfit(xs, ys, 2)
        parabola = axes.plot(lambda x: float(np.polyval(coeffs, x)),
                             x_range=[a - 0.1, b + 0.1], color=ACCENT_AMBER, stroke_width=4.5)
        self.play(Create(parabola), run_time=2.0)
        self.wait(0.8)

        # Shade area under the parabola
        cap3 = numera_caption("The area under that parabola is our approximation").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap3), run_time=0.6)
        shaded = axes.get_area(parabola, x_range=(a, b), color=BRAND_TEAL_LIGHT, opacity=0.55)
        self.play(FadeIn(shaded), run_time=1.2)
        self.wait(1.6)

        formula = MathTex(
            r"\int_a^b f(x)\,dx \;\approx\; \frac{b-a}{6} \left[\, f(a) + 4f(\tfrac{a+b}{2}) + f(b) \right]",
            color=BLACK,
        ).scale(0.55)
        formula.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(Write(formula), run_time=2.4)
        self.wait(3.0)

        self.play(
            FadeOut(VGroup(curve, parabola, shaded, *sample_dots, axes, x_lab, y_lab, formula)),
            run_time=0.6,
        )
        self.numera_outro("Simpson's Rule  ·  numera")
