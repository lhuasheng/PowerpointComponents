from __future__ import annotations

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


class SparklineCard(Component):
    """Metric card with a mini bar-chart sparkline in the lower section."""

    def __init__(
        self,
        label: str,
        value: str,
        series: list[float],
        delta: str | None = None,
        delta_positive: bool | None = None,
    ):
        self.label = label
        self.value = value
        self.series = series
        self.delta = delta
        self.delta_positive = delta_positive

    @property
    def min_height(self) -> float:
        return 1.6

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
        accent_w = 0.04
        pad_x = t.SM
        top_pad = t.SM
        right_pad = t.SM
        bottom_pad = t.SM

        add_rect(slide, x, y, width, height, fill_rgb=t.SURFACE, radius=0.05)
        add_rect(slide, x, y, accent_w, height, fill_rgb=t.ACCENT)

        content_x = x + accent_w + pad_x
        content_w = max(0.0, width - accent_w - pad_x - right_pad)

        label_y = y + top_pad
        label_h = height * 0.25
        add_text_box(
            slide,
            content_x,
            label_y,
            content_w,
            label_h,
            self.label.upper(),
            t.CAPTION,
            color_rgb=t.TEXT_SECONDARY,
            font_name="Calibri",
        )

        value_y = label_y + label_h
        value_h = height * 0.35
        add_text_box(
            slide,
            content_x,
            value_y,
            content_w,
            value_h,
            self.value,
            t.HEADING,
            bold=True,
            color_rgb=t.TEXT_PRIMARY,
            font_name="Calibri Light",
        )

        spark_zone_h = height * 0.35
        spark_zone_y = y + height - bottom_pad - spark_zone_h
        delta_bottom = spark_zone_y - t.XS
        if self.delta:
            if self.delta_positive is True:
                delta_color = (34, 197, 94)
            elif self.delta_positive is False:
                delta_color = (239, 68, 68)
            else:
                delta_color = t.TEXT_MUTED

            delta_y = value_y + value_h
            delta_h = max(t.XS + 0.1, delta_bottom - delta_y)
            if delta_h > 0:
                add_text_box(
                    slide,
                    content_x,
                    delta_y,
                    content_w,
                    delta_h,
                    self.delta,
                    t.CAPTION,
                    color_rgb=delta_color,
                    font_name="Calibri",
                )

        if not self.series:
            return

        spark_inner_w = max(0.0, content_w - 0.15)
        bar_w = spark_inner_w / len(self.series) if self.series else 0.0
        series_min = min(self.series)
        series_max = max(self.series)
        series_span = (series_max - series_min) + 1e-9
        max_bar_h = spark_zone_h
        bar_gap = min(t.XS * 0.2, bar_w * 0.2) if bar_w > 0 else 0.0
        draw_w = max(0.0, bar_w - bar_gap)

        for index, value in enumerate(self.series):
            normalized = (value - series_min) / series_span
            bar_h = max(normalized * max_bar_h, 0.03)
            bar_x = content_x + (index * bar_w)
            bar_y = spark_zone_y + max_bar_h - bar_h
            bar_color = t.ACCENT if index == len(self.series) - 1 else t.ACCENT_SOFT
            add_rect(slide, bar_x, bar_y, draw_w, bar_h, fill_rgb=bar_color)