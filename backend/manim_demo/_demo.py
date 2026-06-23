"""Demonstration style — 3Blue1Brown look, with a STRICT non-overlapping layout.

Layout contract (so text never crosses the curve):
  * Title: top-left.
  * Graph: LEFT half only  (use self.demo_axes()).
  * Maths panel (formula, table, labels): RIGHT half only  (use self.panel()).
  * Worked computations: a clear horizontal strip just under the graph
    (use self.work()).
  * Caption: a BOLD WHITE line on a dark band pinned to the very bottom
    (use self.subtitle()); the band hides whatever is behind it.
Everything is slow and readable. Real maths only in MathTex.
"""
from manim import *  # noqa: F401, F403

# ---- 3Blue1Brown dark palette ----------------------------------------------
BG = "#0E1117"
INK = "#ECEDEE"
WHITE = "#FFFFFF"
MUTED = "#9AA4B2"
PRIMARY = "#5C9DFF"
STEPC = "#F5C542"
ROOT = "#5BD17E"
ACCENT2 = "#FF6B6B"

PAUSE = 1.6

# Reserved zones (Manim units; frame is ~14.2 x 8).
_PANEL_X = 3.7          # centre x of the right maths panel
_PANEL_MAXW = 5.2       # max width of anything in the panel
_WORK_Y = -1.95         # y of the worked-computation strip (under the graph)


def mono(text, scale=0.45, color=INK, weight=NORMAL):
    return Text(text, font="DejaVu Sans Mono", color=color, weight=weight).scale(scale)


class DemoScene(Scene):
    lang = "en"
    strings: dict = {}

    def setup(self):
        self.camera.background_color = BG

    def t(self, key, **fmt):
        table = self.strings or {}
        lt = table.get(self.lang) or table.get("en") or {}
        s = lt.get(key) if key in lt else (table.get("en") or {}).get(key, key)
        return s.format(**fmt) if fmt else s

    # ---------- title ----------
    def title(self, key):
        t = Text(self.t(key), font="Arial", weight=BOLD, color=INK).scale(0.58)
        t.to_corner(UL, buff=0.5)
        if t.width > config.frame_width - 1.2:
            t.scale_to_fit_width(config.frame_width - 1.2)
        self.play(Write(t), run_time=1.0)
        return t

    # ---------- bottom caption: bold white on a dark band ----------
    def subtitle(self, prev, key, **fmt):
        cap = Text(self.t(key, **fmt), font="Arial", weight=BOLD, color=WHITE).scale(0.5)
        if cap.width > config.frame_width - 1.4:
            cap.scale_to_fit_width(config.frame_width - 1.4)
        band = Rectangle(width=config.frame_width, height=cap.height + 0.5,
                         stroke_width=0, fill_color="#05070B", fill_opacity=0.82)
        band.to_edge(DOWN, buff=0.55)
        cap.move_to(band.get_center())
        group = VGroup(band, cap)
        if prev is not None:
            self.play(FadeOut(prev), FadeIn(group), run_time=0.5)
        else:
            self.play(FadeIn(group), run_time=0.6)
        self.wait(1.9)  # time to read
        return group

    # ---------- graph: LEFT half ----------
    def demo_axes(self, x_range, y_range, width=6.2, height=3.6):
        def dec(s):
            return 0 if float(s).is_integer() else 1
        ax = Axes(
            x_range=list(x_range), y_range=list(y_range),
            x_length=width, y_length=height,
            axis_config={"color": MUTED, "stroke_width": 2.5,
                         "include_tip": True, "tip_length": 0.16},
            x_axis_config={"include_numbers": True, "font_size": 18,
                           "decimal_number_config": {
                               "num_decimal_places": dec(x_range[2]), "color": MUTED}},
            y_axis_config={"include_numbers": True, "font_size": 18,
                           "decimal_number_config": {
                               "num_decimal_places": dec(y_range[2]), "color": MUTED}},
            tips=True,
        )
        # left half, lifted so the bottom strip + caption band stay clear
        ax.to_edge(LEFT, buff=0.6).shift(UP * 0.55)
        return ax

    # ---------- maths panel: RIGHT half ----------
    def panel(self, mobj, y=0.0):
        if mobj.width > _PANEL_MAXW:
            mobj.scale_to_fit_width(_PANEL_MAXW)
        mobj.move_to([_PANEL_X, y, 0])
        return mobj

    # ---------- worked computation strip (under the graph) ----------
    def work(self, mobj):
        maxw = config.frame_width - 1.4
        if mobj.width > maxw:
            mobj.scale_to_fit_width(maxw)
        mobj.move_to([-0.6, _WORK_Y, 0])
        return mobj
