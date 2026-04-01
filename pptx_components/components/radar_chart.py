from __future__ import annotations

from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE

from pptx_components.base import Component, _resolve
from pptx_components.theme import Theme
from pptx_components.components.chart import _add_chart_shape, _style_chart


class RadarChart(Component):
    """Radar (spider) chart for multi-axis comparisons.

    Args:
        categories: Axis spoke labels.
        series: Dict of series name → list of values, one per category.
        title: Optional chart title.
        filled: If True, use filled radar polygons (``XL_CHART_TYPE.RADAR_FILLED``);
            otherwise use outline-only radar (``XL_CHART_TYPE.RADAR``).
    """

    def __init__(
        self,
        categories: list[str],
        series: dict[str, list[float]],
        title: str | None = None,
        filled: bool = False,
    ):
        self.categories = categories
        self.series = series
        self.title = title
        self.filled = filled

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

        data = ChartData()
        data.categories = self.categories
        for name, values in self.series.items():
            data.add_series(name, values)

        chart_type = XL_CHART_TYPE.RADAR_FILLED if self.filled else XL_CHART_TYPE.RADAR
        graphic = _add_chart_shape(slide, data, chart_type, x, y, width, height)
        _style_chart(graphic.chart, t, self.title, is_line=True)
