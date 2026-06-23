"""Divided Differences : building the table that produces Newton's coefficients.

We show 4 data points, then build the divided differences table column by
column, highlighting the diagonal (which gives the Newton form coefficients).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import (  # noqa: E402
    BLACK, DOWN, LEFT, ORIGIN, RIGHT, UP,
    Create, FadeIn, FadeOut, MathTex, SurroundingRectangle, Transform, VGroup, Write,
)

from manim_scenes._base import (  # noqa: E402
    ACCENT_AMBER, BRAND_TEAL, NumeraScene, numera_caption,
)


class DividedDifferences(NumeraScene):
    """Build the divided differences table for 4 points step by step."""

    def construct(self):
        self.numera_intro(
            "Divided Differences",
            "The recursive table behind Newton interpolation",
        )

        # Sample data : 4 points
        pts = [(0, 1), (1, 3), (2, 2), (3, 4)]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]

        # ---------- Column 0 : the y values themselves ----------
        col0 = VGroup(*[
            MathTex(f"f[x_{i}] = {ys[i]}", color=BLACK).scale(0.7) for i in range(4)
        ]).arrange(DOWN, buff=0.6).move_to(LEFT * 4)
        for m in col0:
            self.play(Write(m), run_time=0.5)
        self.wait(0.6)

        cap = numera_caption("Start with f(x_i) values").to_edge(UP, buff=0.4)
        self.play(FadeIn(cap), run_time=0.5)
        self.wait(1.0)

        # ---------- Column 1 : first divided differences ----------
        new_cap = numera_caption("First divided differences").to_edge(UP, buff=0.4)
        self.play(Transform(cap, new_cap), run_time=0.5)
        col1_vals = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(3)]
        col1 = VGroup(*[
            MathTex(f"f[x_{i},x_{i+1}] = {col1_vals[i]:+.2f}", color=BLACK).scale(0.6)
            for i in range(3)
        ]).arrange(DOWN, buff=0.6).move_to(ORIGIN + RIGHT * 0.2)
        # Stagger between elements of col0
        for i, m in enumerate(col1):
            m.move_to((col0[i].get_center() + col0[i + 1].get_center()) / 2 + RIGHT * 3.4)
            self.play(FadeIn(m, shift=RIGHT * 0.3), run_time=0.7)
        self.wait(0.8)

        # ---------- Column 2 : second divided differences ----------
        new_cap2 = numera_caption("Second divided differences").to_edge(UP, buff=0.4)
        self.play(Transform(cap, new_cap2), run_time=0.5)
        col2_vals = [(col1_vals[i + 1] - col1_vals[i]) / (xs[i + 2] - xs[i]) for i in range(2)]
        col2 = VGroup()
        for i, val in enumerate(col2_vals):
            m = MathTex(f"f[\\dots] = {val:+.2f}", color=BLACK).scale(0.55)
            m.move_to((col1[i].get_center() + col1[i + 1].get_center()) / 2 + RIGHT * 3.0)
            col2.add(m)
            self.play(FadeIn(m, shift=RIGHT * 0.3), run_time=0.7)
        self.wait(0.8)

        # ---------- Column 3 : third divided difference ----------
        col3_val = (col2_vals[1] - col2_vals[0]) / (xs[3] - xs[0])
        m3 = MathTex(f"f[\\dots] = {col3_val:+.3f}", color=BLACK).scale(0.55)
        m3.move_to((col2[0].get_center() + col2[1].get_center()) / 2 + RIGHT * 2.8)
        self.play(FadeIn(m3, shift=RIGHT * 0.3), run_time=0.7)
        self.wait(0.8)

        # ---------- Highlight the diagonal (Newton coefficients) ----------
        diag_cap = numera_caption("The diagonal gives Newton's coefficients").to_edge(UP, buff=0.4)
        self.play(Transform(cap, diag_cap), run_time=0.6)
        diagonal = VGroup(col0[0], col1[0], col2[0], m3)
        rect = SurroundingRectangle(diagonal, color=BRAND_TEAL, buff=0.15, stroke_width=3)
        self.play(Create(rect), run_time=1.2)
        self.wait(2.5)

        # ---------- The Newton form ----------
        self.play(
            FadeOut(VGroup(col0, col1, col2, m3, rect, cap)),
            run_time=0.6,
        )
        formula = MathTex(
            r"P(x) = a_0 + a_1(x - x_0) + a_2(x - x_0)(x - x_1) + \dots",
            color=BLACK,
        ).scale(0.65)
        self.play(Write(formula), run_time=2.2)
        self.wait(2.5)

        self.play(FadeOut(formula), run_time=0.5)
        self.numera_outro("Divided Differences  ·  numera")
