"""Chart data helpers — pure data transformation, no python-pptx shapes here."""
from __future__ import annotations

from pptx.chart.data import ChartData, CategoryChartData, XyChartData

from pptx_components.theme import Theme


def chart_data_from(categories: list[str],
                    series: dict[str, list[float]]) -> CategoryChartData:
    """Build a CategoryChartData object from plain Python structures.

    Args:
        categories: X-axis category labels.
        series: Mapping of series name → list of values (same length as categories).
    """
    cd = CategoryChartData()
    cd.categories = categories
    for name, values in series.items():
        cd.add_series(name, values)
    return cd


def pie_data_from(categories: list[str],
                  values: list[float]) -> ChartData:
    """Build a ChartData object for pie charts."""
    cd = ChartData()
    cd.categories = categories
    cd.add_series("", values)
    return cd


def scatter_data_from(series: dict[str, list[tuple[float, float]]]) -> XyChartData:
    """Build an XyChartData object for scatter charts."""
    cd = XyChartData()
    for name, points in series.items():
        s = cd.add_series(name)
        for x, y in points:
            s.add_data_point(x, y)
    return cd


def default_theme_palette(theme: Theme) -> list[tuple[int, int, int]]:
    """Return an ordered palette for multi-series and multi-category charts."""
    return [
        theme.ACCENT,
        theme.ACCENT_2,
        theme.ACCENT_3,
        theme.ACCENT_SOFT,
        (99, 102, 241),
        (16, 185, 129),
        (249, 115, 22),
        (236, 72, 153),
    ]
