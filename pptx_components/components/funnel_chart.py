from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


_DEFAULT_PALETTE: list[tuple[int, int, int]] = [
    None,                    # slot 0 → replaced with t.ACCENT at render time
    (249, 115, 22),
    (16, 185, 129),
    (139, 92, 246),
    (239, 68, 68),
]


class FunnelChart(Component):
    """Top-to-bottom funnel chart rendered with themed rectangles.

    Each stage is drawn as a horizontally centered bar whose width is
    proportional to its value relative to the maximum stage value.
    Labels are embedded inside each bar.

    No OOXML chart type is used — all drawing uses ``add_rect`` primitives.

    Args:
        stages: Sequence of ``(label, value, color_rgb)`` tuples. Pass
            ``None`` for ``color_rgb`` to use the cycling default palette.
        title: Optional heading rendered above the funnel in SUBHEADING size.
    """

    TITLE_H = 0.35

    def __init__(
        self,
        stages: list[tuple[str, float, tuple[int, int, int] | None]],
        title: str | None = None,
    ):
        if not stages:
            raise ValueError("stages must not be empty")
        self.stages = stages
        self.title = title

    @property
    def min_height(self) -> float:
        return 1.5 + len(self.stages) * 0.55

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

        # ── Title ──────────────────────────────────────────────────────────
        cur_y = y
        if self.title:
            add_text_box(
                slide, x, cur_y, width, self.TITLE_H,
                self.title, t.SUBHEADING, bold=True,
                color_rgb=t.TEXT_PRIMARY, font_name="Calibri Light",
            )
            cur_y += self.TITLE_H + t.SM * 0.5

        # ── Layout math ────────────────────────────────────────────────────
        n = len(self.stages)
        gap = t.SM
        available_h = height - (cur_y - y)
        bar_h = max(0.25, (available_h - gap * (n - 1)) / n)

        max_val = max(v for _, v, _ in self.stages) or 1.0

        # Palette: slot 0 is t.ACCENT (resolved at render time)
        palette: list[tuple[int, int, int]] = [t.ACCENT] + list(_DEFAULT_PALETTE[1:])

        # ── Bars ───────────────────────────────────────────────────────────
        for i, (label, value, color_rgb) in enumerate(self.stages):
            fill = color_rgb if color_rgb is not None else palette[i % len(palette)]

            bar_w = (value / max_val) * width
            bar_x = x + (width - bar_w) / 2.0
            bar_y = cur_y + i * (bar_h + gap)

            add_rect(slide, bar_x, bar_y, bar_w, bar_h, fill_rgb=fill, radius=0.02)

            # Label centered inside bar: "Label  value"
            label_text = f"{label}  {value:,}"
            add_text_box(
                slide, bar_x, bar_y, bar_w, bar_h,
                label_text, t.BODY, bold=True,
                color_rgb=t.BG, alignment=PP_ALIGN.CENTER,
            )
