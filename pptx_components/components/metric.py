from __future__ import annotations

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from pptx_components.base import (
    Component, _resolve, add_rect, add_accent_bar,
    add_text_box, set_font, set_text_frame_margins,
)
from pptx_components.theme import Theme


class MetricCard(Component):
    """KPI card with label, value, and optional delta indicator.

    Args:
        label: The metric name (e.g. "Revenue").
        value: The formatted value string (e.g. "$1.2M").
        delta: Pre-formatted change string (e.g. "+18%"). Caller owns formatting.
        delta_positive: Explicit direction — True=green, False=red, None=neutral.
    """

    def __init__(self, label: str, value: str,
                 delta: str | None = None,
                 delta_positive: bool | None = None):
        self.label = label
        self.value = value
        self.delta = delta
        self.delta_positive = delta_positive

    @property
    def min_height(self) -> float:
        return 1.5

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        bar_w = 0.05
        pad = t.SM  # tighter outer padding

        # Card background
        add_rect(slide, x, y, width, height, fill_rgb=t.SURFACE, radius=0.05)

        # Left accent bar
        add_accent_bar(slide, x, y, height, t, width=bar_w)

        content_x = x + bar_w + pad
        content_w = width - bar_w - pad - t.SM

        # Label
        label_h = 0.25
        add_text_box(slide, content_x, y + pad, content_w, label_h,
                     self.label.upper(), t.CAPTION,
                     color_rgb=t.TEXT_MUTED, font_name="Calibri")

        # Value
        value_y = y + pad + label_h
        value_h = 0.45
        add_text_box(slide, content_x, value_y, content_w, value_h,
                     self.value, t.HEADING, bold=True,
                     color_rgb=t.TEXT_PRIMARY, font_name="Calibri Light")

        # Delta
        if self.delta:
            if self.delta_positive is True:
                delta_color = t.POSITIVE
                arrow = "▲ "
            elif self.delta_positive is False:
                delta_color = t.NEGATIVE
                arrow = "▼ "
            else:
                delta_color = t.TEXT_MUTED
                arrow = ""
            delta_y = value_y + value_h
            delta_h = 0.25
            add_text_box(slide, content_x, delta_y, content_w, delta_h,
                         arrow + self.delta, t.CAPTION, bold=True,
                         color_rgb=delta_color, font_name="Calibri")


class BigStat(Component):
    """Hero statistic — large centered number for single-focus slides."""

    def __init__(self, value: str, label: str, description: str | None = None):
        self.value = value
        self.label = label
        self.description = description

    @property
    def min_height(self) -> float:
        return 1.8

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        pad = t.MD

        # Value
        value_h = 0.75
        value_y = y + pad
        add_text_box(slide, x, value_y, width, value_h,
                     self.value, t.DISPLAY, bold=True,
                     color_rgb=t.ACCENT, font_name="Calibri Light",
                     alignment=PP_ALIGN.CENTER)

        # Label
        label_y = value_y + value_h + t.XS
        label_h = 0.4
        add_text_box(slide, x, label_y, width, label_h,
                     self.label, t.SUBHEADING, bold=False,
                     color_rgb=t.TEXT_SECONDARY, font_name="Calibri",
                     alignment=PP_ALIGN.CENTER)

        # Description
        if self.description:
            desc_y = label_y + label_h + t.XS
            desc_h = 0.4
            add_text_box(slide, x, desc_y, width, desc_h,
                         self.description, t.CAPTION,
                         color_rgb=t.TEXT_MUTED, font_name="Calibri",
                         alignment=PP_ALIGN.CENTER)
