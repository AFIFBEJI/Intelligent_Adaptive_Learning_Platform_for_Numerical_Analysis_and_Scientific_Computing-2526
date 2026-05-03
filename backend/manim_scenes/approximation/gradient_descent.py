"""Gradient Descent : iteratively walking downhill on a 1D loss curve.

We use a 1D animation (instead of a 3D surface) because :
  * It is more readable for a 30-second clip
  * The core intuition (each step moves opposite to the gradient) is the same
  * 1D animations render in seconds vs minutes for 3D surfaces

The animation shows :
  1. A bowl-shaped loss curve f(x) = (x-2)^2 + 0.4
  2. Starting point at x = -1.5
  3. 6 gradient-descent steps converging toward x = 2 (the minimum)
  4. The update rule appearing at the end

Render :
    cd backend
    manim -qm -o gradient_descent_en.mp4 manim_scenes/approximation/gradient_descent.py GradientDescent
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    MathTex,
    Transform,
    VGroup,
    Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER,
    ACCENT_GREEN,
    BRAND_TEAL,
    NumeraScene,
    brand_axes,
    numera_caption,
)


def loss(x: float) -> float:
    """Bowl-shaped loss : minimum at x=2, value 0.4."""
    return (x - 2.0) ** 2 + 0.4


def grad(x: float) -> float:
    """Derivative of the loss."""
    return 2.0 * (x - 2.0)


class GradientDescent(NumeraScene):
    """Show 6 steps of gradient descent converging to the minimum."""

    def construct(self):
        self.numera_intro(
            "Gradient Descent",
            "Walking downhill, one step at a time",
        )

        # ---------- Axes & loss curve ----------
        axes = brand_axes(x_range=(-2.5, 5.5, 1), y_range=(-0.5, 7, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label(MathTex("f(x)")).set_color(BLACK).scale(0.7)
        curve = axes.plot(loss, x_range=[-2.3, 5.3], color=BRAND_TEAL, stroke_width=4)

        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.play(Create(curve), run_time=1.8)
        self.wait(0.4)

        cap = numera_caption("Goal : find the x that minimises f(x)").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.7)
        self.wait(1.5)

        # ---------- Starting point ----------
        x0 = -1.5
        learning_rate = 0.25
        n_steps = 6
        path_dots = []

        first = Dot(axes.coords_to_point(x0, loss(x0)), color=ACCENT_AMBER, radius=0.10)
        first_lbl = MathTex("x_0", color=BLACK).scale(0.55).next_to(first, UP, buff=0.1)
        self.play(FadeIn(first, scale=1.4), Write(first_lbl), run_time=1.0)
        path_dots.append(first)
        self.wait(0.5)

        cap2 = numera_caption("Each step moves opposite to the gradient (slope)").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap2), run_time=0.8)
        self.wait(0.8)

        # ---------- Iterate ----------
        x = x0
        for i in range(n_steps):
            g = grad(x)
            x_next = x - learning_rate * g

            # Slope arrow at current x : direction of -gradient (downhill)
            arrow_start = axes.coords_to_point(x, loss(x))
            arrow_end = axes.coords_to_point(x_next, loss(x_next))
            arrow = Arrow(
                arrow_start,
                arrow_end,
                color=ACCENT_AMBER,
                buff=0.05,
                stroke_width=4,
                max_tip_length_to_length_ratio=0.18,
            )

            new_dot = Dot(
                arrow_end,
                color=ACCENT_GREEN if i == n_steps - 1 else ACCENT_AMBER,
                radius=0.09,
            )

            self.play(Create(arrow), run_time=0.7)
            self.play(FadeIn(new_dot, scale=1.3), FadeOut(arrow), run_time=0.7)
            path_dots.append(new_dot)
            x = x_next

        # Highlight final minimum
        cap3 = numera_caption("Converged to the minimum").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap3), run_time=0.7)
        self.play(path_dots[-1].animate.scale(1.6), run_time=0.7)
        self.play(path_dots[-1].animate.scale(1 / 1.6), run_time=0.7)
        self.wait(1.5)

        # ---------- Update rule ----------
        rule = MathTex(
            r"x_{n+1} \;=\; x_n \;-\; \eta \, \nabla f(x_n)",
            color=BLACK,
        ).scale(0.7)
        rule.to_edge(UP, buff=0.2)
        self.play(FadeOut(cap), run_time=0.5)
        self.play(Write(rule), run_time=1.8)
        self.wait(3.0)

        self.play(
            FadeOut(VGroup(curve, axes, x_lab, y_lab, first_lbl, *path_dots, rule)),
            run_time=0.6,
        )
        self.numera_outro("Gradient Descent  ·  numera")
