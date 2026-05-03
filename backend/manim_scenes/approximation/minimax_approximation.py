"""Minimax Approximation : minimize the MAXIMUM error (Chebyshev approximation).

Show f(x) and a polynomial p(x) approximating it. Highlight the error
e(x) = f(x) - p(x) and the equioscillation property.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP,
    Create, DashedLine, FadeIn, FadeOut, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, ACCENT_RED, BRAND_TEAL, NumeraScene, brand_axes, numera_caption,
)


def f(x: float) -> float:
    return math.sin(x) + 0.3 * x ** 2 / 4


# Chebyshev-like degree-2 approximation (hand-tuned for the demo)
def p(x: float) -> float:
    return 0.32 * x ** 2 + 0.22 * x + 0.05


class MinimaxApproximation(NumeraScene):
    """Show f(x), p(x) and the error e(x) with equioscillation hint."""

    def construct(self):
        self.numera_intro(
            "Minimax Approximation",
            "Minimize the worst-case error",
        )

        axes = brand_axes(x_range=(-2.5, 2.5, 1), y_range=(-1.5, 2.5, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label("y").set_color(BLACK).scale(0.7)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)

        # Plot the target function
        cap = numera_caption("Target function f(x) we want to approximate").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.6)
        f_curve = axes.plot(f, x_range=[-2.3, 2.3], color=BRAND_TEAL, stroke_width=4)
        self.play(Create(f_curve), run_time=2.0)
        self.wait(1.0)

        # Plot the approximation
        cap2 = numera_caption("Polynomial approximation p(x)").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap2), run_time=0.5)
        p_curve = axes.plot(p, x_range=[-2.3, 2.3], color=ACCENT_AMBER, stroke_width=4)
        self.play(Create(p_curve), run_time=2.0)
        self.wait(1.0)

        # Show the error e(x) = f(x) - p(x), shifted to be visible separately
        cap3 = numera_caption("Error e(x) = f(x) - p(x) oscillates between extrema").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap3), run_time=0.5)

        # Highlight extrema where the error reaches its max in absolute value
        extrema_x = [-2.0, -0.6, 0.7, 2.0]
        extrema_lines = []
        for x in extrema_x:
            seg = DashedLine(
                axes.coords_to_point(x, p(x)),
                axes.coords_to_point(x, f(x)),
                color=ACCENT_RED, stroke_width=3,
            )
            extrema_lines.append(seg)
            self.play(Create(seg), run_time=0.45)
        self.wait(2.0)

        eq = MathTex(
            r"\min_{p \in \mathcal{P}_n} \;\; \max_{x \in [a,b]} \;\big| f(x) - p(x) \big|",
            color=BLACK,
        ).scale(0.65)
        eq.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(Write(eq), run_time=2.4)
        self.wait(3.0)

        self.play(FadeOut(VGroup(f_curve, p_curve, *extrema_lines, axes, x_lab, y_lab, eq)), run_time=0.6)
        self.numera_outro("Minimax Approximation  ·  numera")
