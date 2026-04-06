from __future__ import annotations

from pptx_components.base import (
    Component, _resolve, add_rect, add_accent_bar, add_text_box,
)
from pptx_components.theme import Theme

_VALID_STYLES = ("default", "muted", "accent")


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
            title_h = t.MD + t.XS
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
