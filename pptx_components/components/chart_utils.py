"""Chart data helpers — pure data transformation, no python-pptx shapes here."""
from __future__ import annotations

from pptx.chart.data import ChartData, CategoryChartData


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
