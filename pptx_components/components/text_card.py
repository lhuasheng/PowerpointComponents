from __future__ import annotations

import math

from pptx_components.base import (
    Component, _resolve, add_rect, add_accent_bar, add_text_box,
)
from pptx_components.theme import Theme

_VALID_STYLES = ("default", "muted", "accent")


def _line_height_in(font_size_pt: float, leading: float = 1.4) -> float:
    """Convert font size (pt) to line height (inches) with leading factor."""
    return font_size_pt / 72.0 * leading


def _approx_lines(text: str, font_size_pt: float, box_width_in: float) -> int:
    """Estimate how many lines a text block will occupy at given font size and width."""
    if not text:
        return 0
    # Average proportional character width ≈ 0.55 × em (font_size_pt / 72 inches)
    char_w_in = font_size_pt / 72.0 * 0.55
    chars_per_line = max(1, int(box_width_in / char_w_in))
    lines = sum(
        math.ceil(len(ln) / chars_per_line) if ln else 1
        for ln in text.split('\n')
    )
    return max(1, lines)


class TextCard(Component):
    """General-purpose surface card for narrative text and body copy.

    A flexible rectangular text panel with an optional title, left accent bar,
    and rounded corners. Three styles control the surface and text palette.

    Args:
        body: The main body copy to display.
        title: Optional heading rendered above the body in bold.
        style: ``"default"`` | ``"muted"`` | ``"accent"``
    """

    def __init__(
        self,
        body: str,
        title: str | None = None,
        style: str = "default",
        style_overrides: dict[str, int | str | bool] | None = None,
    ):
        if style not in _VALID_STYLES:
            raise ValueError(
                f"style must be one of {list(_VALID_STYLES)}; got {style!r}"
            )
        self.body = body
        self.title = title
        self.style = style
        self.style_overrides = style_overrides or {}

    @property
    def min_height(self) -> float:
        return 1.6 if self.title else 1.2

    def min_height_for(self, theme: Theme | None = None) -> float:
        """Content-proportional height estimate using conservative 4-inch card width."""
        t = _resolve(theme)
        o = self.style_overrides
        title_size = int(o.get("title_size", t.BODY))
        body_size = int(o.get("body_size", t.BODY))
        pad = t.SM
        bar_w = 0.05
        # Conservative width: assumes ~2-col layout at 13.333 in slide width
        est_content_w = max(1.0, 4.0 - bar_w - pad - t.XS)

        h = pad  # top padding
        if self.title:
            lines = _approx_lines(self.title, title_size, est_content_w)
            h += _line_height_in(title_size) * lines + t.XS + t.SM
        body_lines = _approx_lines(self.body, body_size, est_content_w)
        h += _line_height_in(body_size) * body_lines
        h += pad  # bottom padding
        return max(self.min_height, h)

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
        pad = t.SM
        bar_w = 0.05
        o = self.style_overrides
        title_size = int(o.get("title_size", t.BODY))
        body_size = int(o.get("body_size", t.BODY))
        title_bold = bool(o.get("title_bold", True))
        font_name = str(o.get("font_name", "Calibri"))

        # ── Resolve per-style colors ───────────────────────────────────────
        if self.style == "default":
            bg_rgb = t.SURFACE
            title_rgb = t.TEXT_PRIMARY
            body_rgb = t.TEXT_SECONDARY
        elif self.style == "muted":
            bg_rgb = t.SURFACE_ALT
            title_rgb = t.TEXT_SECONDARY
            body_rgb = t.TEXT_MUTED
        else:  # "accent"
            bg_rgb = t.ACCENT_SOFT
            title_rgb = t.TEXT_PRIMARY
            body_rgb = t.TEXT_PRIMARY

        # ── Card background ────────────────────────────────────────────────
        add_rect(slide, x, y, width, height, fill_rgb=bg_rgb, radius=0.05)

        # ── Left accent bar ────────────────────────────────────────────────
        add_accent_bar(slide, x, y, height, t, width=bar_w)

        # ── Content area ───────────────────────────────────────────────────
        content_x = x + bar_w + pad
        content_w = width - bar_w - pad - t.XS
        cursor_y = y + pad

        if self.title:
            # Compute title height from actual font size and measured wrap lines
            title_lines = _approx_lines(self.title, title_size, content_w)
            title_h = _line_height_in(title_size) * title_lines + t.XS
            add_text_box(
                slide, content_x, cursor_y, content_w, title_h,
                self.title, title_size, bold=title_bold,
                color_rgb=title_rgb, font_name=font_name,
            )
            cursor_y += title_h + t.SM

        body_h = height - (cursor_y - y) - pad
        add_text_box(
            slide, content_x, cursor_y, content_w, max(body_h, t.MD),
            self.body, body_size, bold=False,
            color_rgb=body_rgb, font_name=font_name,
            word_wrap=True,
        )
