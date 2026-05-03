"""Fixed Point Iteration : x = g(x), visualized as a cobweb diagram.

We plot y = g(x) and y = x. Starting from x_0, we iterate x_{n+1} = g(x_n)
and trace the cobweb path showing convergence to the fixed point.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP,
    Create, Dot, FadeIn, FadeOut, Line, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, ACCENT_GREEN, BRAND_TEAL, NumeraScene, brand_axes, numera_caption,
)


def g(x: float) -> float:
    """g(x) = cos(x) — fixed point near 0.7390851."""
    return math.cos(x)


class FixedPointIteration(NumeraScene):
    """Cobweb diagram for x_{n+1} = cos(x_n), starting from x_0 = 0.2."""

    def construct(self):
        self.numera_intro(
            "Fixed Point Iteration",
            "Cobwebbing toward the solution of x = g(x)",
        )

        axes = brand_axes(x_range=(-0.2, 1.5, 0.5), y_range=(-0.2, 1.5, 0.5), width=7, height=5.5)
        axes.to_edge(DOWN, buff=0.5)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label("y").set_color(BLACK).scale(0.7)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)

        # y = g(x)
        g_curve = axes.plot(g, x_range=[-0.1, 1.4], color=BRAND_TEAL, stroke_width=4)
        # y = x (the bisecting line)
        line_yx = axes.plot(lambda x: x, x_range=[-0.1, 1.4], color=ACCENT_AMBER, stroke_width=3)
        self.play(Create(g_curve), run_time=1.4)
        self.play(Create(line_yx), run_time=1.0)

        cap = numera_caption("Solve x = g(x). Fixed point = where curves meet").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.6)
        self.wait(1.0)

        # Cobweb iteration starting at x_0 = 0.2
        cap2 = numera_caption("Iterate : x → g(x) → trace vertically + horizontally").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap2), run_time=0.6)

        x = 0.2
        cobweb = []
        for i in range(7):
            y_new = g(x)
            # Vertical : (x, x) -> (x, g(x))   [first step uses (x, 0) -> (x, g(x))]
            from_pt = axes.coords_to_point(x, x if i > 0 else 0)
            to_pt = axes.coords_to_point(x, y_new)
            v_line = Line(from_pt, to_pt, color=BLACK, stroke_width=2)
            self.play(Create(v_line), run_time=0.45)
            cobweb.append(v_line)

            # Horizontal : (x, g(x)) -> (g(x), g(x)) on the y=x line
            h_line = Line(
                axes.coords_to_point(x, y_new),
                axes.coords_to_point(y_new, y_new),
                color=BLACK, stroke_width=2,
            )
            self.play(Create(h_line), run_time=0.45)
            cobweb.append(h_line)

            x = y_new
            self.wait(0.2)

        # Highlight the fixed point
        fp_dot = Dot(axes.coords_to_point(x, x), color=ACCENT_GREEN, radius=0.12)
        self.play(FadeIn(fp_dot, scale=1.6), run_time=0.6)
        cap3 = numera_caption(f"Converged : x ≈ {x:.4f}").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap3), run_time=0.6)
        self.wait(1.5)

        rule = MathTex(r"x_{n+1} \;=\; g(x_n)", color=BLACK).scale(0.8)
        rule.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(Write(rule), run_time=1.6)
        self.wait(2.5)

        self.play(FadeOut(VGroup(g_curve, line_yx, *cobweb, fp_dot, axes, x_lab, y_lab, rule)), run_time=0.6)
        self.numera_outro("Fixed Point Iteration  ·  numera")
