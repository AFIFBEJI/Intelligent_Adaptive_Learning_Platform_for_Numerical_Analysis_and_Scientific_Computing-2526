"""Riemann Sums : approximating an integral by left rectangles.

Show that as the number of rectangles N grows, the approximation
tends to the true integral.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP,
    Create, FadeIn, FadeOut, MathTex, Polygon, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, BRAND_TEAL, BRAND_TEAL_LIGHT, NumeraScene, brand_axes, numera_caption,
)


def f(x: float) -> float:
    return math.sin(x) + 0.3 * x + 1.0


class RiemannSums(NumeraScene):
    """Show left Riemann sum with increasing N until convergence."""

    def construct(self):
        self.numera_intro(
            "Riemann Sums",
            "Rectangles approximating the area",
        )

        axes = brand_axes(x_range=(-0.3, 4.5, 1), y_range=(-0.3, 3.2, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label("f(x)").set_color(BLACK).scale(0.7)
        curve = axes.plot(f, x_range=[0, 4], color=BRAND_TEAL, stroke_width=4)

        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.play(Create(curve), run_time=2.0)

        title = numera_caption(r"Compute  ∫₀⁴ f(x) dx  with rectangles").to_edge(UP, buff=0.4)
        self.play(FadeIn(title), run_time=0.6)
        self.wait(1.0)

        # ---------- Build rectangle group for given N ----------
        def build_rects(n: int) -> VGroup:
            a, b = 0.0, 4.0
            h = (b - a) / n
            rects = []
            for i in range(n):
                x_left = a + i * h
                p0 = axes.coords_to_point(x_left, 0)
                p1 = axes.coords_to_point(x_left + h, 0)
                p2 = axes.coords_to_point(x_left + h, f(x_left))
                p3 = axes.coords_to_point(x_left, f(x_left))
                rects.append(Polygon(p0, p1, p2, p3,
                                     color=ACCENT_AMBER, stroke_width=1.4,
                                     fill_color=BRAND_TEAL_LIGHT, fill_opacity=0.55))
            return VGroup(*rects)

        # N=4
        cap_n4 = numera_caption("N = 4 left rectangles").to_edge(UP, buff=0.4)
        self.play(Transform(title, cap_n4), run_time=0.6)
        rects = build_rects(4)
        self.play(FadeIn(rects), run_time=1.4)
        self.wait(1.6)

        # N=8
        cap_n8 = numera_caption("N = 8 — error halves").to_edge(UP, buff=0.4)
        self.play(Transform(title, cap_n8), run_time=0.6)
        self.play(Transform(rects, build_rects(8)), run_time=2.0)
        self.wait(1.4)

        # N=16
        cap_n16 = numera_caption("N = 16 — even closer").to_edge(UP, buff=0.4)
        self.play(Transform(title, cap_n16), run_time=0.6)
        self.play(Transform(rects, build_rects(16)), run_time=2.0)
        self.wait(1.4)

        # N=32
        cap_n32 = numera_caption("N = 32 — converging to the true area").to_edge(UP, buff=0.4)
        self.play(Transform(title, cap_n32), run_time=0.6)
        self.play(Transform(rects, build_rects(32)), run_time=2.0)
        self.wait(1.5)

        formula = MathTex(
            r"\int_a^b f(x)\,dx \;=\; \lim_{n \to \infty} \sum_{i=0}^{n-1} f(x_i)\,\Delta x",
            color=BLACK,
        ).scale(0.6)
        formula.to_edge(UP, buff=0.15)
        self.play(FadeOut(title), run_time=0.3)
        self.play(Write(formula), run_time=2.4)
        self.wait(3.0)

        self.play(FadeOut(VGroup(curve, rects, axes, x_lab, y_lab, formula)), run_time=0.6)
        self.numera_outro("Riemann Sums  ·  numera")
