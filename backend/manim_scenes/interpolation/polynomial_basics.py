"""Polynomial Basics : showing what polynomials look like and the
fundamental theorem of interpolation (n+1 points -> unique polynomial of degree n).

Render :
    cd backend
    python scripts/render_animations_docker.py polynomial_basics
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP,
    Create, Dot, FadeIn, FadeOut, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, BRAND_TEAL, NumeraScene, brand_axes, numera_caption,
)


class PolynomialBasics(NumeraScene):
    """Plot polynomials of degrees 1, 2, 3, 4, then show the unique-polynomial theorem."""

    def construct(self):
        self.numera_intro(
            "Polynomial Basics",
            "The building blocks of interpolation",
        )

        axes = brand_axes(x_range=(-2.5, 2.5, 1), y_range=(-3, 3, 1), width=8, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label("y").set_color(BLACK).scale(0.7)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.wait(0.4)

        # ---------- Plot polynomials of increasing degree ----------
        cap = numera_caption("Polynomials of increasing degree").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.6)

        polys = [
            ("Degree 1 : linear",     lambda x: x),
            ("Degree 2 : parabola",   lambda x: 0.5 * x ** 2 - 0.5),
            ("Degree 3 : cubic",      lambda x: 0.4 * x ** 3 - x),
            ("Degree 4 : quartic",    lambda x: 0.2 * x ** 4 - x ** 2 + 0.5),
        ]
        curve_obj = None
        for label, fn in polys:
            new_cap = numera_caption(label).to_edge(UP, buff=0.4)
            self.play(Transform(cap, new_cap), run_time=0.6)
            new_curve = axes.plot(fn, x_range=[-2.3, 2.3], color=BRAND_TEAL, stroke_width=4)
            if curve_obj is None:
                self.play(Create(new_curve), run_time=1.5)
            else:
                self.play(Transform(curve_obj, new_curve), run_time=1.4)
            curve_obj = new_curve
            self.wait(1.0)

        # ---------- Theorem ----------
        self.play(FadeOut(curve_obj), run_time=0.5)
        thm = numera_caption("n+1 points uniquely define a polynomial of degree n").to_edge(UP, buff=0.4)
        self.play(Transform(cap, thm), run_time=0.6)

        pts = [(-1.5, -1), (0, 1), (1.5, -0.5)]
        dots = [Dot(axes.coords_to_point(x, y), color=ACCENT_AMBER, radius=0.10) for x, y in pts]
        for d in dots:
            self.play(FadeIn(d, scale=1.4), run_time=0.5)
        self.wait(0.6)

        # The unique parabola through these 3 points
        import numpy as np
        xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
        c = np.polyfit(xs, ys, 2)
        unique_poly = axes.plot(lambda x: float(np.polyval(c, x)), x_range=[-2.3, 2.3],
                                color=BRAND_TEAL, stroke_width=4)
        self.play(Create(unique_poly), run_time=2.0)
        self.wait(2.0)

        eq = MathTex(r"P_n(x) = a_0 + a_1 x + a_2 x^2 + \dots + a_n x^n", color=BLACK).scale(0.65)
        eq.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(Write(eq), run_time=2.0)
        self.wait(2.5)

        self.play(FadeOut(VGroup(axes, x_lab, y_lab, unique_poly, *dots, eq)), run_time=0.6)
        self.numera_outro("Polynomial Basics  ·  numera")
