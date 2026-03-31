from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme

# Saturated amber visible on both dark and light backgrounds.
_AMBER = (217, 119, 6)


class RangeIndicator(Component):
    """Multi-band threshold bar with a current-value marker.

    Inspired by MUI's LinearProgress + Gauge composition pattern.

    Args:
        label: Description of the metric.
        value: Current value to mark on the bar.
        segments: Ordered list of (upper_bound, band_label, status) tuples.
            The first band starts at *min_value*. The last upper_bound becomes
            the scale maximum.
            status: "ok" | "warn" | "error"
        min_value: Minimum of the scale (default 0).
    """

    LABEL_H = 0.22
    TRACK_H = 0.22
    BAND_LABEL_H = 0.18
    MARKER_HALF_H = 0.10

    def __init__(
        self,
        label: str,
        value: float,
        segments: list[tuple[float, str, str]],
        min_value: float = 0.0,
    ):
        if not segments:
            raise ValueError("segments must contain at least one entry")
        bad = [s for _, _, s in segments if s not in ("ok", "warn", "error")]
        if bad:
            raise ValueError(f"segment status must be 'ok', 'warn', or 'error'; got {bad!r}")
        self.label = label
        self.value = value
        self.segments = segments
        self.min_value = min_value
        self.max_value: float = segments[-1][0]

    @property
    def min_height(self) -> float:
        return self.LABEL_H + self.TRACK_H + self.BAND_LABEL_H + self.MARKER_HALF_H * 2 + 0.08

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
        status_fill = {
            "ok":    t.POSITIVE,
            "warn":  _AMBER,
            "error": t.NEGATIVE,
        }
        val_range = max(1e-9, self.max_value - self.min_value)

        # Metric label (left) + current value (right)
        add_text_box(
            slide, x, y, width * 0.65, self.LABEL_H,
            self.label, t.CAPTION, color_rgb=t.TEXT_SECONDARY, font_name="Calibri",
        )
        add_text_box(
            slide, x + width * 0.65, y, width * 0.35, self.LABEL_H,
            format(self.value, "g"), t.CAPTION, bold=True,
            color_rgb=t.TEXT_PRIMARY, alignment=PP_ALIGN.RIGHT, font_name="Calibri",
        )

        track_y = y + self.LABEL_H + 0.04

        # Band segments
        prev = self.min_value
        for upper, band_lbl, status in self.segments:
            frac_start = (prev - self.min_value) / val_range
            frac_end = (upper - self.min_value) / val_range
            bx = x + frac_start * width
            bw = max(0.01, (frac_end - frac_start) * width)
            add_rect(slide, bx, track_y, bw, self.TRACK_H,
                     fill_rgb=status_fill[status], radius=0.02)
            add_text_box(
                slide, bx, track_y + self.TRACK_H + 0.01, bw, self.BAND_LABEL_H,
                band_lbl, t.CAPTION, color_rgb=t.TEXT_MUTED,
                alignment=PP_ALIGN.CENTER, font_name="Calibri",
            )
            prev = upper

        # Marker — narrow vertical bar spanning above and below the track
        marker_frac = max(0.0, min(1.0, (self.value - self.min_value) / val_range))
        marker_x = x + marker_frac * width - 0.02
        add_rect(
            slide,
            marker_x,
            track_y - self.MARKER_HALF_H,
            0.04,
            self.TRACK_H + self.MARKER_HALF_H * 2,
            fill_rgb=t.TEXT_PRIMARY,
            radius=0.01,
        )
