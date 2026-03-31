from __future__ import annotations

from pptx.dml.color import RGBColor
from pptx.util import Inches

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme

# Isosceles triangle MSO_AUTO_SHAPE_TYPE value
_TRIANGLE = 7


class Annotation(Component):
    """Floating note box with an optional directional pointer.

    Inspired by Tooltip / Popover patterns in shadcn/ui and MUI.

    Args:
        text: Annotation message.
        style: "note" | "highlight" | "warning" | "info"
        pointer: Direction the pointer triangle sticks out:
            "top" | "bottom" | "left" | "right" | None.
        title: Optional bold heading above the body text.
    """

    POINTER_SIZE = 0.14

    def __init__(
        self,
        text: str,
        style: str = "note",
        pointer: str | None = "bottom",
        title: str | None = None,
    ):
        if style not in ("note", "highlight", "warning", "info"):
            raise ValueError(
                f"style must be 'note', 'highlight', 'warning', or 'info'; got {style!r}"
            )
        if pointer is not None and pointer not in ("top", "bottom", "left", "right"):
            raise ValueError(
                "pointer must be 'top', 'bottom', 'left', 'right', or None"
            )
        self.text = text
        self.style = style
        self.pointer = pointer
        self.title = title

    @property
    def min_height(self) -> float:
        title_h = 0.28 if self.title else 0.0
        ptr_h = self.POINTER_SIZE if self.pointer in ("top", "bottom") else 0.0
        return 0.72 + title_h + ptr_h

    def _colors(self, t: Theme) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        if self.style == "highlight":
            return t.ACCENT, (255, 255, 255)
        if self.style in ("warning", "info"):
            fill, text = t.CALLOUT[self.style]
            return fill, text
        # note
        return t.SURFACE, t.TEXT_PRIMARY

    def _draw_pointer(
        self, slide, fill: tuple[int, int, int], px: float, py: float, rotation: int
    ) -> None:
        ps = self.POINTER_SIZE
        try:
            shape = slide.shapes.add_shape(
                _TRIANGLE, Inches(px), Inches(py), Inches(ps), Inches(ps)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = RGBColor(*fill)
            shape.line.fill.background()
            shape.rotation = rotation
        except Exception:
            pass  # pointer is cosmetic — continue without it on failure

    def render(
        self,
        slide,
        x: float,
        y: float,
        width: float,
        height: float,
        theme: Theme | None = None,
    ) -> None:
        t = _resolve(theme)
        fill, text_color = self._colors(t)
        pad = t.SM
        ps = self.POINTER_SIZE

        # Compute box bounds, shrunk to leave room for pointer
        box_x, box_y, box_h = x, y, height
        if self.pointer == "top":
            box_y = y + ps
            box_h = height - ps
        elif self.pointer == "bottom":
            box_h = height - ps

        add_rect(slide, box_x, box_y, width, box_h, fill_rgb=fill, radius=0.05)

        # Pointer triangle — apex direction = pointer direction.
        # MSO isosceles triangle default: apex UP (rotation 0).
        _ROTATIONS = {"top": 0, "bottom": 180, "left": 270, "right": 90}
        if self.pointer in ("top", "bottom"):
            tri_x = box_x + width / 2 - ps / 2
            tri_y = y if self.pointer == "top" else box_y + box_h
            self._draw_pointer(slide, fill, tri_x, tri_y, _ROTATIONS[self.pointer])
        elif self.pointer in ("left", "right"):
            tri_y = box_y + box_h / 2 - ps / 2
            tri_x = x if self.pointer == "left" else box_x + width
            self._draw_pointer(slide, fill, tri_x, tri_y, _ROTATIONS[self.pointer])

        # Text content
        content_x = box_x + pad
        content_y = box_y + pad
        content_w = width - 2 * pad
        content_h = box_h - 2 * pad

        if self.title:
            title_h = 0.28
            add_text_box(
                slide, content_x, content_y, content_w, title_h,
                self.title, t.BODY, bold=True, color_rgb=text_color,
                font_name="Calibri",
            )
            content_y += title_h
            content_h -= title_h

        add_text_box(
            slide, content_x, content_y, content_w, max(0.1, content_h),
            self.text, t.CAPTION, color_rgb=text_color,
            font_name="Calibri", word_wrap=True,
        )
