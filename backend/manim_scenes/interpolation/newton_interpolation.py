"""Newton Interpolation : the nested form, useful when adding points incrementally.

Show that adding a 4th point only requires ONE new divided difference,
no need to redo the whole polynomial like with Lagrange.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np  # noqa: E402

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP, UR,
    Create, Dot, FadeIn, FadeOut, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, BRAND_TEAL, NumeraScene, brand_axes, numera_caption,
)


class NewtonInterpolation(NumeraScene):
    """Show the polynomial growing degree by degree as new points are added."""

    def construct(self):
        self.numera_intro(
            "Newton Interpolation",
            "Add points incrementally without rebuilding",
        )

        axes = brand_axes(x_range=(-0.5, 4.5, 1), y_range=(-1, 4, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label("y").set_color(BLACK).scale(0.7)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)

        pts = [(0, 1), (1, 3), (2, 0.5), (3.5, 2.5)]
        cap = numera_caption("Add points one at a time").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.5)

        dots = []
        prev_curve = None
        for i, (x, y) in enumerate(pts):
            d = Dot(axes.coords_to_point(x, y), color=ACCENT_AMBER, radius=0.10)
            lbl = MathTex(f"P_{i}", color=BLACK).scale(0.5).next_to(d, UR, buff=0.05)
            self.play(FadeIn(d, scale=1.4), Write(lbl), run_time=0.7)
            dots.append((d, lbl))

            if i >= 1:
                # Polynomial of degree i through current points
                xs = np.array([p[0] for p in pts[:i + 1]])
                ys = np.array([p[1] for p in pts[:i + 1]])
                coeffs = np.polyfit(xs, ys, i)

                degree_label = ["", "Linear (1 added)", "Quadratic (1 added)", "Cubic (1 added)"][i]
                deg_cap = numera_caption(degree_label).to_edge(UP, buff=0.4)
                self.play(Transform(cap, deg_cap), run_time=0.5)

                new_curve = axes.plot(
                    lambda x, c=coeffs: float(np.polyval(c, x)),
                    x_range=[-0.4, 4.3], color=BRAND_TEAL, stroke_width=4,
                )
                if prev_curve is None:
                    self.play(Create(new_curve), run_time=2.0)
                else:
                    self.play(Transform(prev_curve, new_curve), run_time=1.6)
                prev_curve = new_curve
                self.wait(1.2)

        # Newton's form
        eq = MathTex(
            r"P(x) = c_0 + c_1(x{-}x_0) + c_2(x{-}x_0)(x{-}x_1) + \dots",
            color=BLACK,
        ).scale(0.55)
        eq.to_edge(LEFT, buff=0.4).shift(UP * 1.6)
        self.play(Write(eq), run_time=2.2)
        self.wait(2.5)

        # Cleanup
        all_dots = VGroup(*[d for pair in dots for d in pair])
        self.play(FadeOut(VGroup(axes, x_lab, y_lab, prev_curve, all_dots, eq, cap)), run_time=0.6)
        self.numera_outro("Newton Interpolation  ·  numera")
