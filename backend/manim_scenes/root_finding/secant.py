"""Secant Method : like Newton-Raphson but using a chord (secant line)
through two consecutive iterates instead of the tangent.

Useful when f' is expensive or unavailable.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, RIGHT, UP, UR,
    Create, DashedLine, Dot, FadeIn, FadeOut, Line, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, ACCENT_GREEN, ACCENT_RED, BRAND_TEAL, NumeraScene,
    brand_axes, numera_caption,
)


def f(x: float) -> float:
    return x ** 3 - 2 * x - 5


class SecantMethod(NumeraScene):
    """4 iterations of the secant method on f(x) = x^3 - 2x - 5."""

    def construct(self):
        self.numera_intro(
            "Secant Method",
            "Tangent-free Newton-style iterations",
        )

        axes = brand_axes(x_range=(-0.5, 4.0, 1), y_range=(-8, 12, 4), width=8.5, height=5)
        axes.to_edge(DOWN, buff=0.5)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label(MathTex("f(x)")).set_color(BLACK).scale(0.7)
        curve = axes.plot(f, x_range=[0.1, 3.6], color=BRAND_TEAL, stroke_width=4)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.play(Create(curve), run_time=1.8)

        cap = numera_caption(r"Find x such that f(x) = x³ - 2x - 5 = 0").to_edge(UP, buff=0.35)
        self.play(FadeIn(cap), run_time=0.6)
        self.wait(0.6)

        # Two starting points : x_{-1} = 1, x_0 = 3
        cap2 = numera_caption("Need TWO starting points (no derivative required)").to_edge(UP, buff=0.35)
        self.play(Transform(cap, cap2), run_time=0.6)

        x_prev = 1.0
        x = 3.0
        all_artifacts = []
        for i in range(4):
            # Plot the two current dots
            d_prev = Dot(axes.coords_to_point(x_prev, f(x_prev)), color=ACCENT_AMBER, radius=0.10)
            d_curr = Dot(axes.coords_to_point(x, f(x)), color=ACCENT_AMBER, radius=0.10)
            self.play(FadeIn(d_prev, scale=1.4), FadeIn(d_curr, scale=1.4), run_time=0.6)

            # Draw the secant line through them, extended to the x-axis
            slope = (f(x) - f(x_prev)) / (x - x_prev)
            x_intercept = x - f(x) / slope
            y_at = lambda t, x=x, slope=slope, fx=f(x): slope * (t - x) + fx
            x_left = max(-0.4, x_intercept - 0.5)
            x_right = max(x, x_prev) + 0.4
            secant = Line(
                axes.coords_to_point(x_left, y_at(x_left)),
                axes.coords_to_point(x_right, y_at(x_right)),
                color=ACCENT_RED if i < 3 else ACCENT_GREEN,
                stroke_width=3,
            )
            self.play(Create(secant), run_time=1.2)

            # Mark intersection with x-axis
            intercept_dot = Dot(
                axes.coords_to_point(x_intercept, 0),
                color=ACCENT_GREEN if i == 3 else ACCENT_AMBER,
                radius=0.09,
            )
            self.play(FadeIn(intercept_dot, scale=1.3), run_time=0.5)
            self.wait(0.6)

            all_artifacts.extend([d_prev, d_curr, secant, intercept_dot])
            x_prev = x
            x = x_intercept

        cap3 = numera_caption(f"Converged : x ≈ {x:.4f}").to_edge(UP, buff=0.35)
        self.play(Transform(cap, cap3), run_time=0.6)
        self.wait(1.5)

        rule = MathTex(
            r"x_{n+1} \;=\; x_n \;-\; f(x_n) \cdot \frac{x_n - x_{n-1}}{f(x_n) - f(x_{n-1})}",
            color=BLACK,
        ).scale(0.6)
        rule.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(Write(rule), run_time=2.4)
        self.wait(3.0)

        self.play(FadeOut(VGroup(curve, *all_artifacts, axes, x_lab, y_lab, rule)), run_time=0.6)
        self.numera_outro("Secant Method  ·  numera")
