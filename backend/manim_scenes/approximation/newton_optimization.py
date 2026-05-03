"""Newton's Method for Optimization : at each step, fit a parabola
(2nd-order Taylor) and jump to its minimum.

Faster than gradient descent for smooth problems but requires the second
derivative.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP,
    Create, DashedLine, Dot, FadeIn, FadeOut, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, ACCENT_GREEN, ACCENT_RED, BRAND_TEAL, NumeraScene,
    brand_axes, numera_caption,
)


def fobj(x: float) -> float:
    return 0.25 * x ** 4 - 1.5 * x ** 2 + x + 3


def fp(x: float) -> float:
    return x ** 3 - 3 * x + 1


def fpp(x: float) -> float:
    return 3 * x ** 2 - 3


class NewtonOptimization(NumeraScene):
    """Show 4 Newton steps converging on a local minimum."""

    def construct(self):
        self.numera_intro(
            "Newton's Method (Optimization)",
            "Use the curvature for faster convergence",
        )

        axes = brand_axes(x_range=(-3, 3, 1), y_range=(-1, 6, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label(MathTex("f(x)")).set_color(BLACK).scale(0.7)
        curve = axes.plot(fobj, x_range=[-2.7, 2.7], color=BRAND_TEAL, stroke_width=4)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.play(Create(curve), run_time=2.0)

        cap = numera_caption("Goal : find a local minimum of f(x)").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.6)
        self.wait(0.6)

        cap2 = numera_caption("Each step uses 2nd-order Taylor approximation").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap2), run_time=0.5)

        # Iterations starting from x_0 = 2.4
        x = 2.4
        path_dots = []
        all_artifacts = []
        for i in range(4):
            cur_dot = Dot(axes.coords_to_point(x, fobj(x)), color=ACCENT_AMBER, radius=0.10)
            v_line = DashedLine(
                axes.coords_to_point(x, 0),
                axes.coords_to_point(x, fobj(x)),
                color=ACCENT_AMBER, stroke_width=2, dash_length=0.1,
            )
            self.play(FadeIn(cur_dot, scale=1.4), run_time=0.6)
            self.play(Create(v_line), run_time=0.4)

            # Local quadratic approximation : q(t) = f(x) + f'(x)(t-x) + 0.5 f''(x)(t-x)^2
            fx, fpx, fppx = fobj(x), fp(x), fpp(x)
            q = lambda t, x=x, fx=fx, fpx=fpx, fppx=fppx: fx + fpx * (t - x) + 0.5 * fppx * (t - x) ** 2
            # Plot the parabola in a small range around x
            x_left = max(-2.7, x - 1.5)
            x_right = min(2.7, x + 1.5)
            parabola = axes.plot(q, x_range=[x_left, x_right],
                                 color=ACCENT_RED if i < 3 else ACCENT_GREEN,
                                 stroke_width=3)
            self.play(Create(parabola), run_time=1.0)

            # Newton step : x_next = x - f'(x) / f''(x)
            x_next = x - fpx / fppx if fppx != 0 else x
            x_next = max(-2.7, min(2.7, x_next))  # clamp to plot range
            next_dot = Dot(
                axes.coords_to_point(x_next, fobj(x_next)),
                color=ACCENT_GREEN if i == 3 else ACCENT_AMBER,
                radius=0.10,
            )
            self.play(FadeIn(next_dot, scale=1.4), run_time=0.5)
            self.wait(0.5)

            all_artifacts.extend([cur_dot, v_line, parabola, next_dot])
            path_dots.append(next_dot)
            x = x_next

        cap3 = numera_caption(f"Converged to a local minimum near x ≈ {x:.3f}").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap3), run_time=0.6)
        self.wait(1.5)

        rule = MathTex(
            r"x_{n+1} \;=\; x_n - \frac{f'(x_n)}{f''(x_n)}",
            color=BLACK,
        ).scale(0.7)
        rule.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(Write(rule), run_time=2.0)
        self.wait(3.0)

        self.play(FadeOut(VGroup(curve, *all_artifacts, axes, x_lab, y_lab, rule)), run_time=0.6)
        self.numera_outro("Newton Optimization  ·  numera")
