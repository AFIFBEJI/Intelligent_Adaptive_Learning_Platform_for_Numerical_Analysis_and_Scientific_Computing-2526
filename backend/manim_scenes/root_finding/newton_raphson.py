"""Newton-Raphson method : iteratively converging to a root via tangent lines.

Iconic example for the root-finding module. The animation shows :
  1. f(x) = x^3 - 2x - 5 with its true root near x ≈ 2.094
  2. Starting at x_0 = 3, we draw the tangent at (x_0, f(x_0))
  3. The tangent crosses the x-axis at x_1 ; we drop a vertical line and recurse
  4. After 4 iterations we are visibly on the root
  5. The update rule appears at the end

Render :
    cd backend
    manim -qm -o newton_raphson_en.mp4 manim_scenes/root_finding/newton_raphson.py NewtonRaphson
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
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    Transform,
    VGroup,
    Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER,
    ACCENT_GREEN,
    ACCENT_RED,
    BRAND_TEAL,
    NumeraScene,
    brand_axes,
    numera_caption,
)


def f(x: float) -> float:
    return x ** 3 - 2 * x - 5


def fprime(x: float) -> float:
    return 3 * x ** 2 - 2


class NewtonRaphson(NumeraScene):
    """Show 4 Newton-Raphson iterations converging to the root of x^3 - 2x - 5."""

    def construct(self):
        self.numera_intro(
            "Newton-Raphson Method",
            "Tangent lines that race to the root",
        )

        # ---------- Axes & function ----------
        axes = brand_axes(x_range=(-0.5, 4.0, 1), y_range=(-8, 12, 4), width=8.5, height=5)
        axes.to_edge(DOWN, buff=0.5)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label(MathTex("f(x)")).set_color(BLACK).scale(0.7)
        curve = axes.plot(f, x_range=[0.1, 3.6], color=BRAND_TEAL, stroke_width=4)

        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.play(Create(curve), run_time=1.8)
        self.wait(0.4)

        cap = numera_caption(r"Find x such that f(x) = x³ - 2x - 5 = 0").to_edge(UP, buff=0.35)
        self.play(FadeIn(cap), run_time=0.7)
        self.wait(1.5)

        # ---------- Newton iterations ----------
        x = 3.0
        n_iter = 4
        all_to_fade = []

        for i in range(n_iter):
            fx = f(x)
            slope = fprime(x)
            x_next = x - fx / slope

            # Dot at current point on the curve
            cur_dot = Dot(axes.coords_to_point(x, fx), color=ACCENT_AMBER, radius=0.10)
            cur_label = MathTex(f"x_{i}", color=BLACK).scale(0.5).next_to(cur_dot, UR := UP + RIGHT, buff=0.1)
            self.play(FadeIn(cur_dot, scale=1.4), Write(cur_label), run_time=0.8)

            # Vertical dashed line from x-axis to (x, f(x))
            v_line = DashedLine(
                axes.coords_to_point(x, 0),
                axes.coords_to_point(x, fx),
                color=ACCENT_AMBER,
                stroke_width=2,
                dash_length=0.1,
            )
            self.play(Create(v_line), run_time=0.6)

            # Tangent line that intersects x-axis at x_next
            x_left = max(x_next - 0.6, -0.4)
            x_right = x + 0.4
            y_at = lambda t, _x=x, _slope=slope, _fx=fx: _slope * (t - _x) + _fx
            tangent = Line(
                axes.coords_to_point(x_left, y_at(x_left)),
                axes.coords_to_point(x_right, y_at(x_right)),
                color=ACCENT_RED if i < n_iter - 1 else ACCENT_GREEN,
                stroke_width=3,
            )
            self.play(Create(tangent), run_time=1.2)

            # Where the tangent crosses x-axis = x_next
            x_axis_dot = Dot(
                axes.coords_to_point(x_next, 0),
                color=ACCENT_GREEN if i == n_iter - 1 else ACCENT_AMBER,
                radius=0.09,
            )
            self.play(FadeIn(x_axis_dot, scale=1.3), run_time=0.6)
            self.wait(0.7)  # pause to let viewer see each iteration

            all_to_fade.extend([cur_dot, cur_label, v_line, tangent, x_axis_dot])
            x = x_next

        # ---------- Highlight convergence ----------
        cap2 = numera_caption(f"Converged to root x ≈ {x:.4f}").to_edge(UP, buff=0.35)
        self.play(Transform(cap, cap2), run_time=0.9)
        self.wait(2.0)

        # ---------- Update rule ----------
        rule = MathTex(
            r"x_{n+1} \;=\; x_n \;-\; \frac{f(x_n)}{f'(x_n)}",
            color=BLACK,
        ).scale(0.75)
        rule.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.5)
        self.play(Write(rule), run_time=1.8)
        self.wait(3.0)

        self.play(
            FadeOut(VGroup(curve, axes, x_lab, y_lab, *all_to_fade, rule)),
            run_time=0.6,
        )
        self.numera_outro("Newton-Raphson  ·  numera")
