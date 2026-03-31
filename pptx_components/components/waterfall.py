from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


class WaterfallChart(Component):
    """Cumulative delta (waterfall) chart built from themed rectangles.

    Each bar floats at the cumulative level, showing a positive (POSITIVE color)
    or negative (NEGATIVE color) contribution. An optional Total bar spans from
    zero to the final sum and is rendered in ACCENT color.

    No external chart library required — uses pptx rectangles directly.

    Args:
        categories: Label for each delta step.
        values: Positive or negative change at each step.
        title: Optional heading above the chart.
        show_total: Append a summary "Total" bar.
        total_label: Label for the total bar.
    """

    TITLE_H = 0.35
    LABEL_H = 0.28

    def __init__(
        self,
        categories: list[str],
        values: list[float],
        title: str | None = None,
        show_total: bool = True,
        total_label: str = "Total",
    ):
        if len(categories) != len(values):
            raise ValueError("categories and values must have the same length")
        if not categories:
            raise ValueError("categories must not be empty")
        self.categories = categories
        self.values = values
        self.title = title
        self.show_total = show_total
        self.total_label = total_label

    @property
    def min_height(self) -> float:
        return 2.5

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

        title_h = 0.0
        if self.title:
            add_text_box(
                slide, x, y, width, self.TITLE_H,
                self.title, t.SUBHEADING, bold=True,
                color_rgb=t.TEXT_PRIMARY, font_name="Calibri Light",
            )
            title_h = self.TITLE_H

        chart_y = y + title_h + t.SM * 0.5
        chart_h = max(0.5, height - title_h - t.SM * 0.5 - self.LABEL_H - t.SM)

        # Build cumulative running totals: runnings[i] = level before bar i
        runnings: list[float] = [0.0]
        for v in self.values:
            runnings.append(runnings[-1] + v)

        # All bars: (base, top, is_negative, is_total)
        all_cats = list(self.categories)
        bar_specs: list[tuple[float, float, bool, bool]] = []
        for i, v in enumerate(self.values):
            lo_v, hi_v = min(runnings[i], runnings[i + 1]), max(runnings[i], runnings[i + 1])
            bar_specs.append((lo_v, hi_v, v < 0, False))
        if self.show_total:
            total = runnings[-1]
            bar_specs.append((min(0.0, total), max(0.0, total), False, True))
            all_cats.append(self.total_label)

        n = len(all_cats)
        bar_gap = 0.06
        bar_w = max(0.08, (width - bar_gap * (n - 1)) / n)

        # Y-scale: include 0 and all running total levels
        all_levels = runnings + [0.0]
        lo_scale = min(all_levels)
        hi_scale = max(all_levels)
        v_range = max(1e-9, hi_scale - lo_scale)

        def to_y(v: float) -> float:
            """Map data value → slide y (high values → lower y coordinate)."""
            norm = (hi_scale - v) / v_range
            return chart_y + norm * chart_h

        # Zero line
        zero_y = to_y(0.0)
        if chart_y <= zero_y <= chart_y + chart_h:
            add_rect(slide, x, zero_y - 0.005, width, 0.01, fill_rgb=t.SURFACE_ALT)

        for i, (base, top_v, is_neg, is_total) in enumerate(bar_specs):
            bx = x + i * (bar_w + bar_gap)
            fill = t.ACCENT if is_total else (t.NEGATIVE if is_neg else t.POSITIVE)

            by_top = to_y(top_v)
            by_bot = to_y(base)
            bh = max(0.02, by_bot - by_top)

            add_rect(slide, bx, by_top, bar_w, bh, fill_rgb=fill, radius=0.02)

            # Connector: thin line at running total level between bar i-1 and bar i
            if i > 0 and not is_total:
                level = runnings[i]  # = end level of bar i-1
                conn_y = to_y(level)
                prev_right = x + (i - 1) * (bar_w + bar_gap) + bar_w
                add_rect(
                    slide, prev_right, conn_y - 0.005, bar_gap, 0.01,
                    fill_rgb=t.TEXT_MUTED,
                )

            # Value label (above bar if room; else below)
            raw_v = self.values[i] if not is_total else runnings[-1]
            sign = "+" if raw_v > 0 else ""
            lbl = f"{sign}{raw_v:,.0f}" if not is_total else f"{runnings[-1]:,.0f}"
            lbl_y = by_top - 0.24
            if lbl_y < chart_y:
                lbl_y = by_bot + 0.03
            add_text_box(
                slide, bx, lbl_y, bar_w, 0.22, lbl,
                t.CAPTION, bold=True, color_rgb=fill,
                alignment=PP_ALIGN.CENTER, font_name="Calibri",
            )

            # Category label below the chart area
            add_text_box(
                slide,
                bx,
                chart_y + chart_h + t.SM * 0.3,
                bar_w,
                self.LABEL_H,
                all_cats[i],
                t.CAPTION,
                color_rgb=t.TEXT_SECONDARY,
                alignment=PP_ALIGN.CENTER,
                font_name="Calibri",
                word_wrap=True,
            )
