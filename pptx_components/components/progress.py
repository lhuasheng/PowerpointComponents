from __future__ import annotations

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


class ProgressBar(Component):
    """Horizontal progress bar with label and optional percentage.

    Args:
        label: Description shown on the left.
        value: Current value.
        max_value: Maximum value (default 100).
        show_pct: Show percentage on the right side.
    """

    TRACK_H = 0.18   # track height in inches

    def __init__(self, label: str, value: float, max_value: float = 100,
                 show_pct: bool = True):
        self.label = label
        self.value = value
        self.max_value = max_value
        self.show_pct = show_pct

    @property
    def min_height(self) -> float:
        return 0.55

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        pct = max(0.0, min(1.0, self.value / self.max_value))
        pct_str = f"{int(pct * 100)}%"

        label_h = 0.25
        label_text_color = t.TEXT_SECONDARY

        pct_label_w = 0.5 if self.show_pct else 0.0
        label_w = width - pct_label_w

        # Label row
        add_text_box(slide, x, y, label_w, label_h,
                     self.label, t.CAPTION, color_rgb=label_text_color)
        if self.show_pct:
            add_text_box(slide, x + label_w, y, pct_label_w, label_h,
                         pct_str, t.CAPTION, bold=True,
                         color_rgb=t.ACCENT, alignment=PP_ALIGN.RIGHT)

        # Track + fill
        track_y = y + label_h + t.XS
        track_h = self.TRACK_H

        # Track background
        add_rect(slide, x, track_y, width, track_h,
                 fill_rgb=t.SURFACE_ALT, radius=0.09)

        # Fill
        fill_w = max(0.0, width * pct)
        if fill_w > 0:
            add_rect(slide, x, track_y, fill_w, track_h,
                     fill_rgb=t.ACCENT, radius=0.09)


# ── Status Badge ───────────────────────────────────────────────────────────

_BADGE_STATUS_MAP = {
    "ok":   "success",
    "warn": "warning",
    "error": "error",
}


class StatusBadge(Component):
    """Fixed-size pill badge. Anchors to top-left of bounding box.

    Designed to be composed inside other components rather than used
    standalone in add_row(). Fixed intrinsic size: 1.2" wide × 0.3" tall.

    Args:
        text: Badge label.
        status: "ok" | "warn" | "error"
    """

    WIDTH = 1.2
    HEIGHT = 0.3

    def __init__(self, text: str, status: str = "ok"):
        if status not in _BADGE_STATUS_MAP:
            raise ValueError(f"status must be one of {list(_BADGE_STATUS_MAP)}; got {status!r}")
        self.text = text
        self.status = status

    @property
    def min_height(self) -> float:
        return self.HEIGHT

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        callout_key = _BADGE_STATUS_MAP[self.status]
        fill_rgb, text_rgb = t.CALLOUT[callout_key]

        # Fixed intrinsic size, centered inside the allocated box.
        badge_w = min(self.WIDTH, width)
        badge_h = min(self.HEIGHT, height)
        badge_x = x + max(0.0, (width - badge_w) / 2)
        badge_y = y + max(0.0, (height - badge_h) / 2)

        badge = add_rect(slide, badge_x, badge_y, badge_w, badge_h,
                         fill_rgb=fill_rgb, radius=0.15)

        from pptx.util import Pt
        tf = badge.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = self.text
        run.font.name = "Calibri"
        run.font.size = Pt(t.CAPTION)
        run.font.bold = True
        run.font.color.rgb = RGBColor(*text_rgb)
