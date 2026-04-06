from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_text_box
from pptx_components.theme import Theme

_ALIGN = {
    "left": PP_ALIGN.LEFT,
    "center": PP_ALIGN.CENTER,
    "right": PP_ALIGN.RIGHT,
}


def _line_height(size_pt: int, leading: float = 1.15) -> float:
    return (size_pt / 72.0) * leading


class EditorialHeadline(Component):
    """Editorial title stack with optional subtitle and byline/dateline metadata."""

    def __init__(
        self,
        title: str,
        subtitle: str | None = None,
        byline: str | None = None,
        dateline: str | None = None,
        separator: str = " | ",
        align: str = "left",
        density: str = "default",
        font_name: str = "Arial",
        style_overrides: dict[str, int | float | str | bool | tuple[int, int, int]] | None = None,
    ):
        if align not in _ALIGN:
            raise ValueError("align must be one of 'left', 'center', 'right'")
        if density not in {"default", "dense"}:
            raise ValueError("density must be 'default' or 'dense'")

        self.title = title
        self.subtitle = subtitle
        self.byline = byline
        self.dateline = dateline
        self.separator = separator
        self.align = align
        self.density = density
        self.font_name = font_name
        self.style_overrides = style_overrides or {}

    @property
    def min_height(self) -> float:
        base_height = 0.34 if self.density == "dense" else 0.38
        subtitle_height = 0.18 if self.subtitle else 0.0
        meta_height = 0.16 if self._meta_text() else 0.0
        gap_count = int(bool(self.subtitle)) + int(bool(self._meta_text()))
        gap_height = gap_count * (0.035 if self.density == "dense" else 0.05)
        return base_height + subtitle_height + meta_height + gap_height

    def _meta_text(self) -> str:
        byline = (self.byline or "").strip()
        dateline = (self.dateline or "").strip()
        if byline and dateline:
            return f"{byline}{self.separator}{dateline}"
        return byline or dateline

    def render(
        self,
        slide,
        x: float,
        y: float,
        width: float,
        height: float,
        theme: Theme | None = None,
    ) -> None:
        if not self.title or not self.title.strip():
            return

        t = _resolve(theme)
        o = self.style_overrides
        is_dense = self.density == "dense"

        title_size = int(o.get("title_size", max(t.HEADING - (4 if is_dense else 3), 18)))
        subtitle_size = int(o.get("subtitle_size", max(t.BODY - (2 if is_dense else 1), 10)))
        byline_size = int(o.get("byline_size", max(t.CAPTION - (1 if is_dense else 0), 9)))
        gap = float(o.get("gap", 0.035 if is_dense else 0.05))
        title_bold = bool(o.get("title_bold", True))
        subtitle_bold = bool(o.get("subtitle_bold", False))
        byline_bold = bool(o.get("byline_bold", False))
        title_font = str(o.get("title_font_name", self.font_name))
        subtitle_font = str(o.get("subtitle_font_name", self.font_name))
        byline_font = str(o.get("byline_font_name", self.font_name))
        title_color = o.get("title_color_rgb", t.TEXT_PRIMARY)
        subtitle_color = o.get("subtitle_color_rgb", t.TEXT_SECONDARY)
        byline_color = o.get("byline_color_rgb", t.TEXT_SECONDARY)

        content = [("title", self.title.strip())]
        if self.subtitle and self.subtitle.strip():
            content.append(("subtitle", self.subtitle.strip()))
        meta_text = self._meta_text()
        if meta_text:
            content.append(("meta", meta_text))

        heights = {
            "title": _line_height(title_size, 1.08 if is_dense else 1.12),
            "subtitle": _line_height(subtitle_size, 1.08),
            "meta": _line_height(byline_size, 1.05),
        }
        total_content_height = sum(heights[kind] for kind, _ in content)
        total_gap_height = gap * max(len(content) - 1, 0)

        current_y = y
        if height > total_content_height + total_gap_height:
            current_y += (height - total_content_height - total_gap_height) / 2

        for index, (kind, text) in enumerate(content):
            if kind == "title":
                add_text_box(
                    slide,
                    x,
                    current_y,
                    width,
                    heights[kind],
                    text,
                    title_size,
                    bold=title_bold,
                    color_rgb=title_color,
                    alignment=_ALIGN[self.align],
                    font_name=title_font,
                    word_wrap=True,
                )
            elif kind == "subtitle":
                add_text_box(
                    slide,
                    x,
                    current_y,
                    width,
                    heights[kind],
                    text,
                    subtitle_size,
                    bold=subtitle_bold,
                    color_rgb=subtitle_color,
                    alignment=_ALIGN[self.align],
                    font_name=subtitle_font,
                    word_wrap=True,
                )
            else:
                add_text_box(
                    slide,
                    x,
                    current_y,
                    width,
                    heights[kind],
                    text,
                    byline_size,
                    bold=byline_bold,
                    color_rgb=byline_color,
                    alignment=_ALIGN[self.align],
                    font_name=byline_font,
                    word_wrap=False,
                )

            current_y += heights[kind]
            if index < len(content) - 1:
                current_y += gap