from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme

# Status → fixed fill color; None means resolve to t.ACCENT at render time.
_STATUS_FILL: dict[str, tuple[int, int, int] | None] = {
    "done":     (16, 185, 129),
    "current":  None,
    "upcoming": (100, 116, 139),
    "at_risk":  (239, 68, 68),
}


class GanttChart(Component):
    """Horizontal Gantt chart built from themed rectangles.

    Each lane has a label column and a proportional bar track.  Tasks are
    coloured by status and labelled either inside (wide bars) or above
    (narrow bars).  An optional title is rendered above the chart body.

    Args:
        lanes: Sequence of ``(lane_label, tasks)`` pairs where each task is
            ``(task_label, start_pct, end_pct, status)``.  ``start_pct`` and
            ``end_pct`` are 0.0–1.0 fractions of the total bar-track width.
            ``status`` is one of ``"done"``, ``"current"``, ``"upcoming"``,
            or ``"at_risk"``.
        title: Optional heading rendered above the chart in SUBHEADING style.
        tick_labels: Optional list of exactly 5 tick labels for 0%, 25%, 50%,
            75%, and 100% positions. Defaults to percentage labels.
    """

    LABEL_W: float = 1.5    # inches – left label column
    TITLE_H: float = 0.35   # inches – title row
    HEADER_H: float = 0.28  # inches – tick-mark header row
    ROW_H: float = 0.45     # inches – height of each lane row
    ROW_GAP: float = 0.05   # inches – vertical gap between consecutive lane rows
    _BAR_H_RATIO: float = 0.55   # bar height as fraction of ROW_H
    _TRACK_H: float = 0.06  # background track rectangle height
    _TICK_H: float = 0.05   # visible tick line height at bottom of header

    # Minimum bar width to attempt an inline label; below this, try above.
    _MIN_INLINE_W: float = 0.50
    # Minimum bar width to show any label at all (above-bar).
    _MIN_LABEL_W: float = 0.18

    def __init__(
        self,
        lanes: list[tuple[str, list[tuple[str, float, float, str]]]],
        title: str | None = None,
        tick_labels: list[str] | None = None,
    ) -> None:
        if not lanes:
            raise ValueError("lanes must not be empty")
        if tick_labels is not None and len(tick_labels) != 5:
            raise ValueError("tick_labels must contain exactly 5 labels")
        self.lanes = lanes
        self.title = title
        self.tick_labels = tick_labels

    @property
    def min_height(self) -> float:
        return 0.5 + len(self.lanes) * 0.5 + (0.4 if self.title else 0.0)

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
        cur_y = y

        # ── Title ─────────────────────────────────────────────────────────
        if self.title:
            add_text_box(
                slide, x, cur_y, width, self.TITLE_H,
                self.title, t.SUBHEADING, bold=True,
                color_rgb=t.TEXT_PRIMARY, font_name="Calibri Light",
            )
            cur_y += self.TITLE_H

        bar_area_x = x + self.LABEL_W
        bar_area_w = max(0.1, width - self.LABEL_W)

        # ── Header: tick labels + short tick lines ─────────────────────────
        ticks = [0.0, 0.25, 0.50, 0.75, 1.0]
        tick_labels = self.tick_labels or ["0%", "25%", "50%", "75%", "100%"]
        lbl_w = 0.4  # label box width

        for pct, lbl in zip(ticks, tick_labels):
            tick_x = bar_area_x + pct * bar_area_w

            if pct == 0.0:
                align = PP_ALIGN.LEFT
                lbl_x = tick_x
            elif pct == 1.0:
                align = PP_ALIGN.RIGHT
                lbl_x = tick_x - lbl_w
            else:
                align = PP_ALIGN.CENTER
                lbl_x = tick_x - lbl_w / 2

            add_text_box(
                slide, lbl_x, cur_y, lbl_w, self.HEADER_H - self._TICK_H,
                lbl, t.CAPTION,
                color_rgb=t.TEXT_MUTED,
                alignment=align,
                font_name="Calibri",
            )

            # Short vertical tick at bottom of header
            add_rect(
                slide,
                tick_x - 0.003,
                cur_y + self.HEADER_H - self._TICK_H,
                0.006,
                self._TICK_H,
                fill_rgb=t.TEXT_MUTED,
            )

        cur_y += self.HEADER_H

        # ── Lanes ──────────────────────────────────────────────────────────
        bar_h = self.ROW_H * self._BAR_H_RATIO
        label_h = 0.22  # text box height for lane labels and inline task labels

        for lane_label, tasks in self.lanes:
            lane_y = cur_y

            # Lane label (vertically centred in row)
            label_y = lane_y + (self.ROW_H - label_h) / 2
            add_text_box(
                slide,
                x,
                label_y,
                self.LABEL_W - 0.1,
                label_h,
                lane_label,
                t.BODY,
                color_rgb=t.TEXT_PRIMARY,
                alignment=PP_ALIGN.LEFT,
                font_name="Calibri",
            )

            # Background track (thin, full bar-area width, vertically centred)
            track_y = lane_y + (self.ROW_H - self._TRACK_H) / 2
            add_rect(
                slide,
                bar_area_x,
                track_y,
                bar_area_w,
                self._TRACK_H,
                fill_rgb=t.SURFACE_ALT,
            )

            # Task bars
            bar_y = lane_y + (self.ROW_H - bar_h) / 2

            for task_label, start_pct, end_pct, status in tasks:
                start_pct = max(0.0, min(1.0, float(start_pct)))
                end_pct = max(0.0, min(1.0, float(end_pct)))
                if end_pct <= start_pct:
                    continue

                fill = _STATUS_FILL.get(status)
                if fill is None:
                    fill = t.ACCENT

                bx = bar_area_x + start_pct * bar_area_w
                bw = (end_pct - start_pct) * bar_area_w

                add_rect(slide, bx, bar_y, bw, bar_h, fill_rgb=fill, radius=0.04)

                # Label placement: inline if wide enough, else above
                if bw >= self._MIN_INLINE_W:
                    # Inside the bar; use BG colour for contrast
                    add_text_box(
                        slide,
                        bx + 0.06,
                        bar_y,
                        max(0.05, bw - 0.12),
                        bar_h,
                        task_label,
                        t.CAPTION,
                        color_rgb=t.BG,
                        alignment=PP_ALIGN.LEFT,
                        font_name="Calibri",
                    )
                elif bw >= self._MIN_LABEL_W:
                    # Above the bar; use TEXT_SECONDARY colour
                    above_y = bar_y - label_h - 0.02
                    above_y = max(lane_y, above_y)
                    add_text_box(
                        slide,
                        bx,
                        above_y,
                        min(bw + 0.35, bar_area_w - (bx - bar_area_x)),
                        label_h,
                        task_label,
                        t.CAPTION,
                        color_rgb=t.TEXT_SECONDARY,
                        alignment=PP_ALIGN.LEFT,
                        font_name="Calibri",
                    )
                # else: bar too narrow — skip label entirely

            cur_y += self.ROW_H + self.ROW_GAP
