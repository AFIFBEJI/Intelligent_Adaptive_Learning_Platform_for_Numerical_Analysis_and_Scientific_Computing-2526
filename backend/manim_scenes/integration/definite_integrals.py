"""Definite Integrals : visualizing the area under a curve as the integral.

We show a curve f(x) and slowly fill the area from a to b, ending with
the formal definition.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, UP,
    Create, FadeIn, FadeOut, MathTex, Transform, ValueTracker, VGroup, Write, always_redraw,
)

from manim_scenes._base import (  # noqa: E402
    BRAND_TEAL, NumeraScene, brand_axes, numera_caption,
)


def f(x: float) -> float:
    return 0.4 * (x - 1) ** 2 + 0.5 * math.sin(2 * x) + 1


class DefiniteIntegrals(NumeraScene):
    """Animate the area under f(x) growing from a to b."""

    def construct(self):
        self.numera_intro(
            "Definite Integrals",
            "The area under a curve, formalized",
        )

        axes = brand_axes(x_range=(-0.5, 5, 1), y_range=(-0.5, 4, 1), width=9, height=5)
        axes.to_edge(DOWN, buff=0.6)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label("f(x)").set_color(BLACK).scale(0.7)
        curve = axes.plot(f, x_range=[0, 4.5], color=BRAND_TEAL, stroke_width=4)

        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.play(Create(curve), run_time=2.0)

        cap = numera_caption("The integral is the signed area between f and the x-axis").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.6)
        self.wait(0.8)

        # Animate the right bound from a to b
        a = 0.3
        bound = ValueTracker(a)
        area = always_redraw(lambda: axes.get_area(curve, x_range=(a, bound.get_value()),
                                                   color=BRAND_TEAL, opacity=0.28))
        self.add(area)
        self.play(bound.animate.set_value(4.0), run_time=4.5)
        self.wait(1.5)

        cap2 = numera_caption("Integral from a = 0.3 to b = 4").to_edge(UP, buff=0.4)
        self.play(Transform(cap, cap2), run_time=0.6)
        self.wait(1.4)

        self.remove(area)
        # Static area for the formula screen
        static_area = axes.get_area(curve, x_range=(a, 4.0), color=BRAND_TEAL, opacity=0.28)
        self.add(static_area)

        formula = MathTex(
            r"\int_a^b f(x)\,dx \;=\; \lim_{\Delta x \to 0} \sum_i f(x_i)\,\Delta x",
            color=BLACK,
        ).scale(0.6)
        formula.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(Write(formula), run_time=2.4)
        self.wait(3.0)

        self.play(FadeOut(VGroup(curve, static_area, axes, x_lab, y_lab, formula)), run_time=0.6)
        self.numera_outro("Definite Integrals  ·  numera")
