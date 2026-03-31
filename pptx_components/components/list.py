from __future__ import annotations

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


class ListBlock(Component):
    """Unified list component supporting bullet, numbered, and checklist styles.

    Args:
        items: List of item strings.
        style: "bullet" | "number" | "check"
        checked: Indices of completed items (only used when style="check").
        title: Optional title rendered above the list.
    """

    ITEM_H = 0.35   # height per item row
    TITLE_H = 0.4   # height for title if present
    BULLET_SIZE = 0.07  # accent bullet square size

    def __init__(self, items: list[str],
                 style: str = "bullet",
                 checked: list[int] | None = None,
                 title: str | None = None):
        if style not in ("bullet", "number", "check"):
            raise ValueError(f"style must be 'bullet', 'number', or 'check'; got {style!r}")
        self.items = items
        self.style = style
        self.checked = set(checked or [])
        self.title = title

    @property
    def min_height(self) -> float:
        return (len(self.items) * self.ITEM_H) + (self.TITLE_H if self.title else 0)

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        cursor_y = y

        # Title
        if self.title:
            add_text_box(slide, x, cursor_y, width, self.TITLE_H,
                         self.title, t.SUBHEADING, bold=True,
                         color_rgb=t.TEXT_PRIMARY, font_name="Calibri Light")
            cursor_y += self.TITLE_H

        # Items
        bullet_col_w = 0.3   # width reserved for the glyph/number column
        text_x = x + bullet_col_w
        text_w = width - bullet_col_w

        for i, item in enumerate(self.items):
            item_mid_y = cursor_y + self.ITEM_H / 2

            if self.style == "bullet":
                # Small accent-colored square bullet
                sq = self.BULLET_SIZE
                sq_y = item_mid_y - sq / 2
                sq_x = x + (bullet_col_w - sq) / 2
                add_rect(slide, sq_x, sq_y, sq, sq, fill_rgb=t.ACCENT)
                add_text_box(slide, text_x, cursor_y, text_w, self.ITEM_H,
                             item, t.BODY, color_rgb=t.TEXT_PRIMARY)

            elif self.style == "number":
                # Accent-colored number
                add_text_box(slide, x, cursor_y, bullet_col_w, self.ITEM_H,
                             f"{i + 1}.", t.BODY, bold=True,
                             color_rgb=t.ACCENT, font_name="Calibri",
                             alignment=PP_ALIGN.RIGHT)
                add_text_box(slide, text_x, cursor_y, text_w, self.ITEM_H,
                             item, t.BODY, color_rgb=t.TEXT_PRIMARY)

            elif self.style == "check":
                is_checked = i in self.checked
                glyph = "✓" if is_checked else "○"
                glyph_color = t.POSITIVE if is_checked else t.TEXT_MUTED
                item_color = t.TEXT_MUTED if is_checked else t.TEXT_PRIMARY

                add_text_box(slide, x, cursor_y, bullet_col_w, self.ITEM_H,
                             glyph, t.BODY, bold=is_checked,
                             color_rgb=glyph_color, font_name="Calibri",
                             alignment=PP_ALIGN.CENTER)
                add_text_box(slide, text_x, cursor_y, text_w, self.ITEM_H,
                             item, t.BODY, color_rgb=item_color,
                             italic=is_checked)

            cursor_y += self.ITEM_H
