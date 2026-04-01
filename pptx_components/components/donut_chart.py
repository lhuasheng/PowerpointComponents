from __future__ import annotations

from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_text_box
from pptx_components.theme import Theme
from pptx_components.components.chart_utils import pie_data_from
from pptx_components.components.chart import _add_chart_shape, _style_chart


class DonutChart(Component):
    """Doughnut chart with an optional centered label overlaid on the hole.

    Args:
        categories: Slice labels.
        values: Slice values.
        center_label: Text to render in the center of the donut hole. Styled
            with ``t.HEADING`` point size, ``t.ACCENT`` color, bold.
        title: Optional chart title.
    """

    def __init__(
        self,
        categories: list[str],
        values: list[float],
        center_label: str | None = None,
        title: str | None = None,
    ):
        self.categories = categories
        self.values = values
        self.center_label = center_label
        self.title = title

    @property
    def min_height(self) -> float:
        return 2.0

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

        # Build chart
        cd = pie_data_from(self.categories, self.values)
        graphic = _add_chart_shape(
            slide, cd, XL_CHART_TYPE.DOUGHNUT, x, y, width, height
        )
        _style_chart(graphic.chart, t, self.title, is_pie=True)

        # Center label overlay
        if self.center_label is not None:
            # The default PowerPoint doughnut hole is ~75 % of the outer radius,
            # so the usable inner-hole diameter ≈ 0.75 × min(width, height).
            # Use ~40 % of the narrower chart dimension for the text box so it
            # fits comfortably inside the hole.
            hole_span = min(width, height) * 0.40
            box_w = hole_span
            box_h = hole_span * 0.5

            cx = x + width / 2
            cy = y + height / 2
            if self.title is not None:
                cy += 0.07 * height
            box_x = cx - box_w / 2
            box_y = cy - box_h / 2

            add_text_box(
                slide,
                x=box_x,
                y=box_y,
                w=box_w,
                h=box_h,
                text=self.center_label,
                size=t.HEADING,
                bold=True,
                color_rgb=t.ACCENT,
                alignment=PP_ALIGN.CENTER,
            )
