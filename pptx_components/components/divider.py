from __future__ import annotations

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


class Divider(Component):
    """Horizontal rule with optional centered label."""

    LINE_H = 0.02   # actual line thickness in inches
    LABEL_W = 2.5   # reserved width for centered label

    def __init__(self, label: str | None = None):
        self.label = label

    @property
    def min_height(self) -> float:
        return 0.25

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        line_y = y + (height - self.LINE_H) / 2

        if self.label:
            label_x = x + (width - self.LABEL_W) / 2
            # Left segment
            add_rect(slide, x, line_y, (width - self.LABEL_W) / 2 - t.SM,
                     self.LINE_H, fill_rgb=t.ACCENT_SOFT)
            # Right segment
            right_x = label_x + self.LABEL_W + t.SM
            add_rect(slide, right_x, line_y,
                     width - right_x + x, self.LINE_H,
                     fill_rgb=t.ACCENT_SOFT)
            # Label text
            add_text_box(slide, label_x, y, self.LABEL_W, height,
                         self.label, t.CAPTION,
                         color_rgb=t.TEXT_MUTED, font_name="Calibri",
                         alignment=PP_ALIGN.CENTER)
        else:
            add_rect(slide, x, line_y, width, self.LINE_H, fill_rgb=t.ACCENT_SOFT)


class Spacer(Component):
    """No-op component that occupies vertical space in a Column."""

    def __init__(self, height: float):
        self._height = height

    @property
    def min_height(self) -> float:
        return self._height

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        pass  # intentionally empty
