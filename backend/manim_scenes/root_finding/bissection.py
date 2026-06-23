"""Bisection Method : repeatedly halve an interval that brackets a root.

Show f(x) crossing zero, an initial interval [a, b], and 5 bisection
steps narrowing down on the root.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, RIGHT, UP,
    Brace, Create, FadeIn, FadeOut, Line, MathTex, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, ACCENT_GREEN, ACCENT_RED, BRAND_TEAL, NumeraScene,
    brand_axes, numera_caption,
)


def f(x: float) -> float:
    return x ** 3 - 2 * x - 5


class BisectionMethod(NumeraScene):
    """5 bisection iterations on f(x) = x^3 - 2x - 5 starting from [1, 3]."""

    def construct(self):
        self.numera_intro(
            "Bisection Method",
            "Halve the interval until you trap the root",
        )

        axes = brand_axes(x_range=(0, 4, 1), y_range=(-8, 12, 4), width=8.5, height=5)
        axes.to_edge(DOWN, buff=0.5)
        x_lab = axes.get_x_axis_label("x").set_color(BLACK).scale(0.7)
        y_lab = axes.get_y_axis_label(MathTex("f(x)")).set_color(BLACK).scale(0.7)
        curve = axes.plot(f, x_range=[0.1, 3.6], color=BRAND_TEAL, stroke_width=4)
        self.play(Create(axes), Write(x_lab), Write(y_lab), run_time=1.2)
        self.play(Create(curve), run_time=1.8)

        cap = numera_caption(r"Find x such that f(x) = x³ - 2x - 5 = 0").to_edge(UP, buff=0.35)
        self.play(FadeIn(cap), run_time=0.6)
        self.wait(0.6)

        cap2 = numera_caption("Start with [a, b] where f(a) and f(b) have opposite signs").to_edge(UP, buff=0.35)
        self.play(Transform(cap, cap2), run_time=0.5)

        a, b = 1.0, 3.0
        bracket_lines = []
        for _ in range(5):
            # Highlight current bracket as a horizontal segment on the x-axis
            seg = Line(
                axes.coords_to_point(a, 0),
                axes.coords_to_point(b, 0),
                color=ACCENT_AMBER, stroke_width=6,
            )
            self.play(Create(seg), run_time=0.5)

            # Compute midpoint
            m = (a + b) / 2
            mid_seg = Line(
                axes.coords_to_point(m, -0.3),
                axes.coords_to_point(m, 0.3),
                color=ACCENT_RED, stroke_width=4,
            )
            self.play(Create(mid_seg), run_time=0.4)
            self.wait(0.5)

            # Decide which half to keep based on sign of f(m)
            if f(a) * f(m) < 0:
                b = m
            else:
                a = m
            self.play(FadeOut(seg), FadeOut(mid_seg), run_time=0.3)
            bracket_lines.append((seg, mid_seg))

        # Final bracket : tiny segment near the root
        final = Line(
            axes.coords_to_point(a, 0),
            axes.coords_to_point(b, 0),
            color=ACCENT_GREEN, stroke_width=8,
        )
        self.play(Create(final), run_time=0.7)
        cap3 = numera_caption(f"After 5 iterations : x is in [{a:.3f}, {b:.3f}]").to_edge(UP, buff=0.35)
        self.play(Transform(cap, cap3), run_time=0.6)
        self.wait(2.0)

        rule = MathTex(
            r"\text{If } f(a)\,f(m) < 0 \;\Rightarrow\; b = m, \text{ else } a = m",
            color=BLACK,
        ).scale(0.6)
        rule.to_edge(UP, buff=0.15)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(Write(rule), run_time=2.4)
        self.wait(3.0)

        self.play(FadeOut(VGroup(curve, final, axes, x_lab, y_lab, rule)), run_time=0.6)
        self.numera_outro("Bisection Method  ·  numera")
