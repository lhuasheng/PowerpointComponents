from __future__ import annotations

from pptx_components.base import Component, _resolve
from pptx_components.layout import Grid
from pptx_components.theme import Theme
from pptx_components.components.metric import MetricCard


class KPIGrid(Component):
    """Convenience wrapper for rendering many KPI cards in a grid.

    Args:
        metrics: Sequence of metric tuples as
            (label, value, delta, delta_positive).
        cols: Number of columns.
        col_gap: Optional horizontal gap override.
        row_gap: Optional vertical gap override.
    """

    def __init__(
        self,
        metrics: list[tuple[str, str, str | None, bool | None]],
        cols: int = 3,
        col_gap: float | None = None,
        row_gap: float | None = None,
    ):
        if cols <= 0:
            raise ValueError(f"cols must be positive; got {cols}")
        self.metrics = metrics
        self.cols = cols
        self.col_gap = col_gap
        self.row_gap = row_gap

    def _as_grid(self) -> Grid:
        cards = [MetricCard(label, value, delta=delta, delta_positive=delta_positive)
                 for label, value, delta, delta_positive in self.metrics]
        return Grid(cards, cols=self.cols, col_gap=self.col_gap, row_gap=self.row_gap)

    @property
    def min_height(self) -> float:
        return self._as_grid().min_height

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        self._as_grid().render(slide, x, y, width, height, theme=t)
