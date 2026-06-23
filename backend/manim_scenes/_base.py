"""Shared utilities + base Scene for all Numera animations.

This module makes every animation in the platform look like it belongs
to the same product : same teal palette, same typography, same intro/
outro, same sub-second timings. Every scene file should import from here.
"""
from manim import *  # noqa: F401, F403

# ============================================================
# Brand palette (matches the frontend tokens.ts)
# ============================================================
BRAND_TEAL = "#0F766E"        # Primary action / curve highlight
BRAND_TEAL_LIGHT = "#5EEAD4"  # Soft accents
ACCENT_AMBER = "#F59E0B"      # "Look here" highlights, errors converging
ACCENT_RED = "#DC2626"        # Errors, divergence
ACCENT_GREEN = "#10B981"      # Convergence, success
TEXT_PRIMARY = "#0F172A"      # Headings
TEXT_MUTED = "#64748B"        # Captions, secondary
BG_LIGHT = "#FFFFFF"
GRID_LIGHT = "#E2E8F0"


def numera_title(text: str, scale: float = 0.85) -> "Text":
    """Standard title used at the top of each animation."""
    return Text(text, font="Inter", weight=BOLD, color=TEXT_PRIMARY).scale(scale)


def numera_caption(text: str, scale: float = 0.55) -> "Text":
    """Small explanation / status caption."""
    return Text(text, font="Inter", color=TEXT_MUTED).scale(scale)


def brand_axes(
    x_range: tuple = (-1, 5, 1),
    y_range: tuple = (-1, 5, 1),
    width: float = 8,
    height: float = 5,
) -> "Axes":
    """Create axes with the platform's brand palette."""
    return Axes(
        x_range=list(x_range),
        y_range=list(y_range),
        x_length=width,
        y_length=height,
        axis_config={
            "color": TEXT_MUTED,
            "stroke_width": 2,
            "include_tip": True,
            "tip_length": 0.18,
        },
        tips=True,
    )


class NumeraScene(Scene):
    """Base Scene class enforcing consistent branding.

    Every animation in the platform should subclass this rather than
    Scene directly. This guarantees :
      * white background
      * consistent default opacity / line-width
      * brand colors available without extra imports
      * a 0.4s intro/outro fade

    Override `intro_title()` to customize the intro card.
    """

    def setup(self):  # noqa: D401
        self.camera.background_color = BG_LIGHT

    def numera_intro(self, title: str, subtitle: str = ""):
        """Show a clean title card at the start. ~1.5s."""
        title_t = numera_title(title)
        if subtitle:
            sub_t = numera_caption(subtitle).next_to(title_t, DOWN, buff=0.3)
            group = VGroup(title_t, sub_t).move_to(ORIGIN)
        else:
            group = title_t
        self.play(FadeIn(group, shift=UP * 0.3), run_time=0.6)
        self.wait(0.8)
        self.play(FadeOut(group, shift=UP * 0.3), run_time=0.4)

    def numera_outro(self, message: str = "numera.ai"):
        """Optional outro at the end of an animation."""
        outro = numera_caption(message, scale=0.5).set_color(BRAND_TEAL)
        self.play(FadeIn(outro), run_time=0.4)
        self.wait(0.5)
        self.play(FadeOut(outro), run_time=0.3)
