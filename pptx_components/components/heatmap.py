from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.theme import Theme


def _lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def _lerp_color(
    c1: tuple[int, int, int], c2: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    return (_lerp(c1[0], c2[0], t), _lerp(c1[1], c2[1], t), _lerp(c1[2], c2[2], t))


class Heatmap(Component):
    """Grid-based intensity heatmap.

    Args:
        matrix: 2-D list of floats (rows × cols).
        row_labels: Labels for each row.
        col_labels: Labels for each column.
        title: Optional heading above the heatmap.
        colormap: "sequential" (SURFACE_ALT → ACCENT) or
            "diverging" (NEGATIVE → SURFACE_ALT → POSITIVE).
        show_values: Render the numeric value inside each cell.
        fmt: Python format spec string applied to each value (default "g").
    """

    TITLE_H = 0.35
    COL_LABEL_H = 0.25
    ROW_LABEL_W = 1.1
    CELL_H = 0.32

    def __init__(
        self,
        matrix: list[list[float]],
        row_labels: list[str],
        col_labels: list[str],
        title: str | None = None,
        colormap: str = "sequential",
        show_values: bool = True,
        fmt: str = "g",
    ):
        if colormap not in ("sequential", "diverging"):
            raise ValueError(
                f"colormap must be 'sequential' or 'diverging'; got {colormap!r}"
            )
        if len(matrix) != len(row_labels):
            raise ValueError("matrix row count must match row_labels length")
        if matrix and len(matrix[0]) != len(col_labels):
            raise ValueError("matrix col count must match col_labels length")
        self.matrix = matrix
        self.row_labels = row_labels
        self.col_labels = col_labels
        self.title = title
        self.colormap = colormap
        self.show_values = show_values
        self.fmt = fmt

    @property
    def min_height(self) -> float:
        return (
            (self.TITLE_H if self.title else 0.0)
            + self.COL_LABEL_H
            + len(self.matrix) * self.CELL_H
        )

    def _cell_color(
        self, t: Theme, norm: float
    ) -> tuple[int, int, int]:
        if self.colormap == "diverging":
            if norm <= 0.5:
                return _lerp_color(t.NEGATIVE, t.SURFACE_ALT, norm * 2)
            return _lerp_color(t.SURFACE_ALT, t.POSITIVE, (norm - 0.5) * 2)
        # sequential
        return _lerp_color(t.SURFACE_ALT, t.ACCENT, norm)

    def _text_color(
        self, t: Theme, norm: float
    ) -> tuple[int, int, int]:
        # High-intensity cells: use BG for contrast; low-intensity: TEXT_PRIMARY.
        return t.BG if norm > 0.6 else t.TEXT_PRIMARY

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
        cursor_y = y

        if self.title:
            add_text_box(
                slide, x, cursor_y, width, self.TITLE_H,
                self.title, t.SUBHEADING, bold=True,
                color_rgb=t.TEXT_PRIMARY, font_name="Calibri Light",
            )
            cursor_y += self.TITLE_H

        flat = [v for row in self.matrix for v in row]
        lo, hi = min(flat), max(flat)
        val_range = hi - lo if hi != lo else 1.0

        cell_w = max(0.05, (width - self.ROW_LABEL_W) / max(1, len(self.col_labels)))

        # Column headers
        for ci, col in enumerate(self.col_labels):
            add_text_box(
                slide,
                x + self.ROW_LABEL_W + ci * cell_w,
                cursor_y,
                cell_w,
                self.COL_LABEL_H,
                col,
                t.CAPTION,
                bold=True,
                color_rgb=t.TEXT_SECONDARY,
                alignment=PP_ALIGN.CENTER,
                font_name="Calibri",
            )
        cursor_y += self.COL_LABEL_H

        # Cells
        for ri, row in enumerate(self.matrix):
            add_text_box(
                slide, x, cursor_y, self.ROW_LABEL_W, self.CELL_H,
                self.row_labels[ri], t.CAPTION,
                color_rgb=t.TEXT_SECONDARY, font_name="Calibri",
            )
            for ci, val in enumerate(row):
                norm = (val - lo) / val_range
                cell_color = self._cell_color(t, norm)
                text_color = self._text_color(t, norm)
                cx = x + self.ROW_LABEL_W + ci * cell_w
                add_rect(
                    slide,
                    cx + 0.02,
                    cursor_y + 0.02,
                    max(0.02, cell_w - 0.04),
                    max(0.02, self.CELL_H - 0.04),
                    fill_rgb=cell_color,
                    radius=0.02,
                )
                if self.show_values:
                    add_text_box(
                        slide, cx, cursor_y, cell_w, self.CELL_H,
                        format(val, self.fmt), t.CAPTION,
                        bold=True, color_rgb=text_color,
                        alignment=PP_ALIGN.CENTER, font_name="Calibri",
                    )
            cursor_y += self.CELL_H
