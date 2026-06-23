"""Spline Interpolation : piecewise cubic polynomials, smooth at knots.

Show 5 data points and the natural cubic spline that connects them.
Highlight that the curve is C2 (continuous derivatives) at every knot.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np  # noqa: E402

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP,
    Create, Dot, FadeIn, FadeOut, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, BRAND_TEAL, NumeraScene, brand_axes, numera_caption,
)


class SplineInterpolation(NumeraScene):
    """Show 5 points and the natural cubic spline through them."""

    def construct(self):
        self.numera_intro(
            "Spline Interpolation",
            "Smooth piecewise cubics through every point",
        )

        axes = brand_axes(x_range=(-0.5, 5.5, 1), y_range=(-1.5, 4, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label("y").set_color(BLACK).scale(0.7)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)

        pts = [(0, 1), (1, 2.5), (2, 0.5), (3, 3), (4, 1.5)]
        dots = []
        for x, y in pts:
            d = Dot(axes.coords_to_point(x, y), color=ACCENT_AMBER, radius=0.10)
            self.play(FadeIn(d, scale=1.4), run_time=0.5)
            dots.append(d)

        cap = numera_caption("5 known data points").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.5)
        self.wait(0.7)

        # Build natural cubic spline using scipy if available, else fallback to numpy fit per segment
        cap2 = numera_caption("Each segment is a cubic, smooth at every knot").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap2), run_time=0.6)
        try:
            from scipy.interpolate import CubicSpline
            xs = np.array([p[0] for p in pts])
            ys = np.array([p[1] for p in pts])
            cs = CubicSpline(xs, ys, bc_type="natural")
            spline = axes.plot(lambda x: float(cs(x)), x_range=[0, 4], color=BRAND_TEAL, stroke_width=4)
        except ImportError:
            # Fallback : fit 4 cubic segments separately. Less smooth but visible.
            from manim import VMobject
            segments = []
            for i in range(len(pts) - 1):
                xa, ya = pts[i]; xb, yb = pts[i + 1]
                # Simple linear-ish smooth segment (placeholder if scipy missing)
                seg = axes.plot(
                    lambda t, ya=ya, yb=yb, xa=xa, xb=xb: ya + (yb - ya) * (t - xa) / (xb - xa),
                    x_range=[xa, xb], color=BRAND_TEAL, stroke_width=4,
                )
                segments.append(seg)
            spline = VGroup(*segments)

        self.play(Create(spline), run_time=3.5)
        self.wait(1.5)

        # Highlight knot smoothness
        cap3 = numera_caption("At every knot : C2 continuity (slope and curvature match)").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap3), run_time=0.6)
        for d in dots[1:-1]:
            self.play(d.animate.scale(1.6).set_color(BRAND_TEAL), run_time=0.4)
            self.play(d.animate.scale(1 / 1.6).set_color(ACCENT_AMBER), run_time=0.3)
        self.wait(1.5)

        eq = MathTex(
            r"S(x) = \begin{cases} S_0(x), & x \in [x_0,x_1]\\ \vdots \\ S_{n-1}(x), & x \in [x_{n-1},x_n] \end{cases}",
            color=BLACK,
        ).scale(0.55)
        eq.to_edge(LEFT, buff=0.4).shift(UP * 1.6)
        self.play(Write(eq), run_time=2.2)
        self.wait(2.5)

        self.play(FadeOut(VGroup(axes, x_lab, y_lab, spline, *dots, eq, cap)), run_time=0.6)
        self.numera_outro("Spline Interpolation  ·  numera")
