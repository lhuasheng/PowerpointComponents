from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


class ComparisonPanel(Component):
    """Two-column comparison component.

    Args:
        left_title: Left column heading.
        left_items: Left column bullet items.
        right_title: Right column heading.
        right_items: Right column bullet items.
        title: Optional heading above both columns.
    """

    TITLE_H = 0.35
    HEADER_H = 0.35
    ITEM_H = 0.28

    def __init__(
        self,
        left_title: str,
        left_items: list[str],
        right_title: str,
        right_items: list[str],
        title: str | None = None,
    ):
        self.left_title = left_title
        self.left_items = left_items
        self.right_title = right_title
        self.right_items = right_items
        self.title = title

    @property
    def min_height(self) -> float:
        rows = max(len(self.left_items), len(self.right_items))
        return (self.TITLE_H if self.title else 0.0) + self.HEADER_H + (rows * self.ITEM_H) + 0.12

    def _render_col(self, slide, x: float, y: float, w: float, h: float,
                    heading: str, items: list[str], t: Theme) -> None:
        add_rect(slide, x, y, w, h, fill_rgb=t.SURFACE, radius=0.04)
        add_rect(slide, x, y, w, 0.03, fill_rgb=t.ACCENT_SOFT, radius=0.01)
        add_text_box(
            slide, x + t.SM, y + 0.05, w - 2 * t.SM, self.HEADER_H,
            heading, t.BODY, bold=True, color_rgb=t.TEXT_PRIMARY,
            font_name="Calibri",
        )

        cursor_y = y + self.HEADER_H + 0.05
        bullet_w = 0.22
        for item in items:
            add_text_box(
                slide,
                x + t.SM,
                cursor_y,
                bullet_w,
                self.ITEM_H,
                "•",
                t.BODY,
                color_rgb=t.ACCENT,
                alignment=PP_ALIGN.CENTER,
                font_name="Calibri",
            )
            add_text_box(
                slide,
                x + t.SM + bullet_w,
                cursor_y,
                w - (2 * t.SM) - bullet_w,
                self.ITEM_H,
                item,
                t.CAPTION,
                color_rgb=t.TEXT_SECONDARY,
                font_name="Calibri",
                word_wrap=True,
            )
            cursor_y += self.ITEM_H

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

        body_h = max(0.0, (y + height) - cursor_y)
        gap = t.SM
        col_w = (width - gap) / 2

        self._render_col(slide, x, cursor_y, col_w, body_h, self.left_title, self.left_items, t)
        self._render_col(slide, x + col_w + gap, cursor_y, col_w, body_h,
                         self.right_title, self.right_items, t)
