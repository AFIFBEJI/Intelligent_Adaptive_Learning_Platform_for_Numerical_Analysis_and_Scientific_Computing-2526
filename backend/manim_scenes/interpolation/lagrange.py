"""Lagrange Interpolation : a polynomial through n given points.

The animation shows :
  1. 4 data points appear one by one
  2. The Lagrange polynomial is built and drawn passing through all of them
  3. We highlight that the polynomial passes EXACTLY through each point

Render :
    cd backend
    manim -qm -o lagrange_en.mp4 manim_scenes/interpolation/lagrange.py LagrangeInterpolation
"""
import sys
from pathlib import Path

# Allow running this file directly via `manim` CLI from any cwd.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    UR,
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
    BRAND_TEAL,
    NumeraScene,
    brand_axes,
    numera_caption,
)


class LagrangeInterpolation(NumeraScene):
    """Show a Lagrange polynomial passing through 4 data points."""

    def construct(self):
        # ---------- Intro ----------
        self.numera_intro(
            "Lagrange Interpolation",
            "One polynomial through every point",
        )

        # ---------- Setup axes ----------
        axes = brand_axes(x_range=(-0.5, 4.5, 1), y_range=(-1.5, 4, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_label = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_label = axes.get_y_axis_label("y").set_color(BLACK).scale(0.7)
        self.play(Create(axes), Write(x_label), Write(y_label), run_time=1.4)
        self.wait(0.4)

        # ---------- Data points ----------
        # Hand-picked so the resulting polynomial has nice curves.
        points_xy = [(0, 1), (1, 3), (2, 0.5), (3.5, 2.5)]
        dots = []
        labels = []
        for i, (x, y) in enumerate(points_xy):
            d = Dot(axes.coords_to_point(x, y), color=ACCENT_AMBER, radius=0.09)
            lbl = MathTex(f"P_{i}", color=BLACK).scale(0.55)
            lbl.next_to(d, UR, buff=0.05)
            self.play(FadeIn(d, scale=1.4), Write(lbl), run_time=0.9)
            self.wait(0.3)
            dots.append(d)
            labels.append(lbl)

        caption = numera_caption("4 known data points").to_edge(UP, buff=0.4)
        self.play(FadeIn(caption), run_time=0.7)
        self.wait(1.2)

        # ---------- Build Lagrange polynomial via numpy ----------
        # We compute the unique polynomial of degree 3 through these 4 points.
        try:
            import numpy as np

            xs = np.array([p[0] for p in points_xy])
            ys = np.array([p[1] for p in points_xy])
            coeffs = np.polyfit(xs, ys, deg=3)  # high-power-first

            def L(x):
                return float(np.polyval(coeffs, x))
        except ImportError:
            # Fallback to the algebraic formula if numpy missing
            def basis(j: int, x: float) -> float:
                num = den = 1.0
                xj = points_xy[j][0]
                for k, (xk, _) in enumerate(points_xy):
                    if k != j:
                        num *= x - xk
                        den *= xj - xk
                return num / den

            def L(x):
                return sum(yj * basis(j, x) for j, (_, yj) in enumerate(points_xy))

        # ---------- Animate the polynomial sweeping in ----------
        new_caption = numera_caption("Building the unique cubic through them...").to_edge(UP, buff=0.4)
        self.play(Transform(caption, new_caption), run_time=0.8)

        poly_curve = axes.plot(L, x_range=[-0.4, 4.3], color=BRAND_TEAL, stroke_width=4.5)
        self.play(Create(poly_curve), run_time=4.0)
        self.wait(1.2)

        # ---------- Highlight that it passes through every point ----------
        confirm = numera_caption("The polynomial passes exactly through every data point").to_edge(UP, buff=0.4)
        self.play(Transform(caption, confirm), run_time=0.9)
        # Pulse the dots one by one — slower so each pulse is readable
        for d in dots:
            self.play(d.animate.scale(1.6).set_color(BRAND_TEAL), run_time=0.4)
            self.play(d.animate.scale(1 / 1.6).set_color(ACCENT_AMBER), run_time=0.35)
        self.wait(1.5)

        # ---------- Polynomial equation ----------
        equation = MathTex(
            r"P(x) = \sum_{j=0}^{n} y_j \, \ell_j(x), \quad",
            r"\ell_j(x) = \prod_{\substack{k=0 \\ k \neq j}}^{n} \frac{x - x_k}{x_j - x_k}",
            color=BLACK,
        ).scale(0.55)
        equation.to_edge(LEFT, buff=0.5).shift(UP * 1.7)
        self.play(Write(equation), run_time=2.2)
        self.wait(3.0)

        # ---------- Outro ----------
        self.play(
            FadeOut(VGroup(*dots, *labels, poly_curve, axes, x_label, y_label, equation, caption)),
            run_time=0.6,
        )
        self.numera_outro("Lagrange Interpolation  ·  numera")
