"""Least Squares Approximation : the line that minimizes the sum of squared residuals.

Show 8 noisy data points, then animate the best-fit line appearing.
Visualize the residuals as vertical segments.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np  # noqa: E402

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP,
    Create, DashedLine, Dot, FadeIn, FadeOut, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, ACCENT_RED, BRAND_TEAL, NumeraScene, brand_axes, numera_caption,
)


class LeastSquaresApproximation(NumeraScene):
    """Show 8 data points and the best-fit line minimizing sum of squared residuals."""

    def construct(self):
        self.numera_intro(
            "Least Squares Approximation",
            "Best line through noisy data",
        )

        axes = brand_axes(x_range=(-0.5, 6.5, 1), y_range=(-0.5, 5, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label("y").set_color(BLACK).scale(0.7)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)

        # Hand-picked noisy linear data
        pts = [(0.5, 1.2), (1.0, 1.6), (1.7, 2.6), (2.4, 2.0),
               (3.2, 3.4), (4.0, 3.6), (4.8, 4.4), (5.6, 4.0)]
        dots = [Dot(axes.coords_to_point(x, y), color=ACCENT_AMBER, radius=0.09) for x, y in pts]

        cap = numera_caption("8 noisy measurements (x, y)").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.6)
        for d in dots:
            self.play(FadeIn(d, scale=1.4), run_time=0.25)
        self.wait(0.6)

        # Compute best fit line
        xs = np.array([p[0] for p in pts])
        ys = np.array([p[1] for p in pts])
        slope, intercept = np.polyfit(xs, ys, 1)

        # Show line
        cap2 = numera_caption("The line that minimises Σ(y_i - (mx_i+b))²").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap2), run_time=0.6)
        line = axes.plot(lambda x: slope * x + intercept, x_range=[0, 6.2],
                         color=BRAND_TEAL, stroke_width=4)
        self.play(Create(line), run_time=2.5)
        self.wait(0.6)

        # Show residuals (vertical dashed lines from each point to the line)
        cap3 = numera_caption("Each red segment is a residual : (y_i - prediction)").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap3), run_time=0.6)

        residuals = []
        for x, y in pts:
            pred = slope * x + intercept
            seg = DashedLine(
                axes.coords_to_point(x, y),
                axes.coords_to_point(x, pred),
                color=ACCENT_RED, stroke_width=2.5, dash_length=0.08,
            )
            residuals.append(seg)
            self.play(Create(seg), run_time=0.3)
        self.wait(2.0)

        # Equation
        eq = MathTex(
            r"\min_{m, b} \sum_{i=1}^{n} \big(\, y_i - (m \, x_i + b)\,\big)^2",
            color=BLACK,
        ).scale(0.65)
        eq.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(Write(eq), run_time=2.4)
        self.wait(3.0)

        self.play(FadeOut(VGroup(*dots, *residuals, line, axes, x_lab, y_lab, eq)), run_time=0.6)
        self.numera_outro("Least Squares  ·  numera")
