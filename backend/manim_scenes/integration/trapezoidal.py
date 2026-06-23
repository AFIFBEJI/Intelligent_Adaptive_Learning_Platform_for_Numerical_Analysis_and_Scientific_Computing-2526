"""Trapezoidal rule : approximating a definite integral by trapezoid sums.

The animation shows :
  1. The function f(x) = sin(x) + x/4 + 1 plotted on [0, 4]
  2. The "true" area shaded under the curve
  3. We approximate with N=4 then N=8 trapezoids — error visibly shrinks
  4. The approximation formula appears

Render :
    cd backend
    manim -qm -o trapezoidal_en.mp4 manim_scenes/integration/trapezoidal.py TrapezoidalRule
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK,
    DOWN,
    LEFT,
    UP,
    Create,
    FadeIn,
    FadeOut,
    MathTex,
    Polygon,
    Transform,
    VGroup,
    Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER,
    BRAND_TEAL,
    BRAND_TEAL_LIGHT,
    NumeraScene,
    brand_axes,
    numera_caption,
)


def f(x: float) -> float:
    """The function whose integral we approximate."""
    return math.sin(x) + 0.25 * x + 1.0


class TrapezoidalRule(NumeraScene):
    """Show how trapezoids approximate the area under f(x)."""

    def construct(self):
        self.numera_intro(
            "Trapezoidal Rule",
            "Approximating an integral by trapezoid sums",
        )

        # ---------- Axes & function ----------
        axes = brand_axes(x_range=(-0.3, 4.5, 1), y_range=(-0.3, 3.2, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label("f(x)").set_color(BLACK).scale(0.7)
        curve = axes.plot(f, x_range=[0, 4], color=BRAND_TEAL, stroke_width=4)

        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.play(Create(curve), run_time=2.2)
        self.wait(0.4)

        title = numera_caption(r"We want to compute  ∫₀⁴ f(x) dx").to_edge(UP, buff=0.4)
        self.play(FadeIn(title), run_time=0.7)
        self.wait(1.5)

        # ---------- "True" area shading ----------
        true_area = axes.get_area(curve, x_range=(0, 4), color=BRAND_TEAL, opacity=0.18)
        self.play(FadeIn(true_area), run_time=1.1)
        self.wait(1.5)

        # ---------- N=4 trapezoids ----------
        cap_n4 = numera_caption("Approximation with 4 trapezoids").to_edge(UP, buff=0.4)
        self.play(Transform(title, cap_n4), run_time=0.9)
        traps_4 = self._build_trapezoids(axes, n=4)
        self.play(FadeIn(traps_4), run_time=1.4)
        self.wait(2.0)

        # ---------- N=8 trapezoids -> tighter approx ----------
        cap_n8 = numera_caption("More trapezoids = smaller error").to_edge(UP, buff=0.4)
        self.play(Transform(title, cap_n8), run_time=0.9)
        traps_8 = self._build_trapezoids(axes, n=8)
        self.play(Transform(traps_4, traps_8), run_time=2.2)
        self.wait(2.0)

        # ---------- Formula ----------
        formula = MathTex(
            r"\int_a^b f(x)\,dx \;\approx\; \frac{h}{2} \left[\, f(x_0) + 2\sum_{i=1}^{n-1} f(x_i) + f(x_n) \right]",
            color=BLACK,
        ).scale(0.6)
        formula.to_edge(UP, buff=0.15)
        self.play(FadeOut(title), run_time=0.5)
        self.play(Write(formula), run_time=2.4)
        self.wait(3.0)

        self.play(
            FadeOut(VGroup(curve, true_area, traps_4, axes, x_lab, y_lab, formula)),
            run_time=0.6,
        )
        self.numera_outro("Trapezoidal Rule  ·  numera")

    def _build_trapezoids(self, axes, n: int) -> VGroup:
        """Return a VGroup of `n` filled trapezoids approximating the area under f on [0, 4]."""
        a, b = 0.0, 4.0
        h = (b - a) / n
        trapezoids = []
        for i in range(n):
            x0 = a + i * h
            x1 = a + (i + 1) * h
            p0 = axes.coords_to_point(x0, 0)
            p1 = axes.coords_to_point(x1, 0)
            p2 = axes.coords_to_point(x1, f(x1))
            p3 = axes.coords_to_point(x0, f(x0))
            poly = Polygon(
                p0,
                p1,
                p2,
                p3,
                color=ACCENT_AMBER,
                stroke_width=1.6,
                fill_color=BRAND_TEAL_LIGHT,
                fill_opacity=0.55,
            )
            trapezoids.append(poly)
        return VGroup(*trapezoids)
