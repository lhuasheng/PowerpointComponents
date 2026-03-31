from __future__ import annotations

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


class Legend(Component):
    """A compact legend with color swatches and labels.

    Args:
        items: Sequence of (label, rgb_tuple) entries.
        title: Optional heading text.
    """

    TITLE_H = 0.35
    ITEM_H = 0.3
    SWATCH = 0.12

    def __init__(self, items: list[tuple[str, tuple[int, int, int]]],
                 title: str | None = None):
        self.items = items
        self.title = title

    @property
    def min_height(self) -> float:
        return (self.TITLE_H if self.title else 0.0) + (len(self.items) * self.ITEM_H)

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        cursor_y = y

        if self.title:
            add_text_box(
                slide, x, cursor_y, width, self.TITLE_H,
                self.title, t.SUBHEADING, bold=True,
                color_rgb=t.TEXT_PRIMARY, font_name="Calibri Light",
            )
            cursor_y += self.TITLE_H

        for label, rgb in self.items:
            swatch_y = cursor_y + (self.ITEM_H - self.SWATCH) / 2
            add_rect(slide, x, swatch_y, self.SWATCH, self.SWATCH, fill_rgb=rgb, radius=0.01)
            add_text_box(
                slide,
                x + self.SWATCH + t.XS,
                cursor_y,
                width - self.SWATCH - t.XS,
                self.ITEM_H,
                label,
                t.BODY,
                color_rgb=t.TEXT_PRIMARY,
                font_name="Calibri",
            )
            cursor_y += self.ITEM_H
