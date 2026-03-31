from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


class Timeline(Component):
    """Static horizontal timeline for milestone storytelling.

    Args:
        events: Ordered list of (date_label, title, status) tuples.
            status: "done" | "current" | "upcoming" | "risk"
        title: Optional heading above the timeline.
    """

    TITLE_H = 0.35

    def __init__(
        self,
        events: list[tuple[str, str, str]],
        title: str | None = None,
    ):
        if len(events) < 2:
            raise ValueError("events must contain at least two items")
        allowed = {"done", "current", "upcoming", "risk"}
        invalid = [s for _, _, s in events if s not in allowed]
        if invalid:
            raise ValueError(f"invalid statuses found: {invalid!r}")
        self.events = events
        self.title = title

    @property
    def min_height(self) -> float:
        return (self.TITLE_H if self.title else 0.0) + 1.45

    def _status_color(self, t: Theme, status: str) -> tuple[int, int, int]:
        if status == "done":
            return t.POSITIVE
        if status == "current":
            return t.ACCENT
        if status == "risk":
            return t.NEGATIVE
        return t.TEXT_MUTED

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

        n = len(self.events)
        inner_h = max(0.0, (y + height) - cursor_y)
        line_y = cursor_y + inner_h * 0.53

        left_pad = 0.2
        right_pad = 0.2
        span = max(0.1, width - left_pad - right_pad)
        centers = [x + left_pad + (i * (span / (n - 1))) for i in range(n)]

        add_rect(
            slide,
            centers[0],
            line_y - 0.01,
            max(0.0, centers[-1] - centers[0]),
            0.02,
            fill_rgb=t.SURFACE_ALT,
            radius=0.01,
        )

        node_d = min(0.2, max(0.14, width / (n * 9)))
        for idx, (date_label, title, status) in enumerate(self.events):
            color = self._status_color(t, status)
            node_x = centers[idx] - node_d / 2
            node_y = line_y - node_d / 2
            add_rect(slide, node_x, node_y, node_d, node_d, fill_rgb=color, radius=node_d / 2)

            is_top = (idx % 2 == 0)
            card_h = 0.5
            if is_top:
                card_y = max(cursor_y, line_y - 0.62)
            else:
                card_y = min(y + height - card_h, line_y + 0.12)

            text_color = t.TEXT_PRIMARY if status in ("done", "current", "risk") else t.TEXT_SECONDARY
            add_text_box(
                slide,
                centers[idx] - 0.85,
                card_y,
                1.7,
                0.2,
                date_label,
                t.CAPTION,
                bold=True,
                color_rgb=t.TEXT_MUTED,
                alignment=PP_ALIGN.CENTER,
                font_name="Calibri",
            )
            add_text_box(
                slide,
                centers[idx] - 0.85,
                card_y + 0.2,
                1.7,
                0.3,
                title,
                t.CAPTION,
                bold=(status == "current"),
                color_rgb=text_color,
                alignment=PP_ALIGN.CENTER,
                font_name="Calibri",
                word_wrap=True,
            )
