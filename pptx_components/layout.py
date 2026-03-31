from __future__ import annotations

from pptx_components.base import Component, add_rect, apply_fill, apply_no_line, _resolve
from pptx_components.theme import Theme


# ── Row ────────────────────────────────────────────────────────────────────

class Row(Component):
    """Lays out children horizontally, sharing width proportionally."""

    def __init__(self, *components: Component,
                 gap: float | None = None,
                 weights: list[float] | None = None):
        if len(components) == 0:
            raise ValueError("Row requires at least one component")
        if weights is not None:
            if len(weights) != len(components):
                raise ValueError(
                    f"weights length ({len(weights)}) must match component count ({len(components)})"
                )
            if any(w <= 0 for w in weights):
                raise ValueError("weights must be positive numbers")
        self.components = components
        self._gap = gap          # None = use theme.SM at render time
        self.weights = weights

    def _gap_val(self, theme: Theme) -> float:
        return self._gap if self._gap is not None else theme.SM

    def _col_widths(self, total_width: float, gap: float) -> list[float]:
        n = len(self.components)
        available = total_width - gap * (n - 1)
        if available <= 0:
            raise ValueError(
                f"Row available width must be positive; got {available:.3f}. "
                f"Check total width ({total_width}) and gap ({gap})."
            )
        if self.weights:
            total_w = sum(self.weights)
            normalized = [w / total_w for w in self.weights]
        else:
            normalized = [1 / n] * n
        return [available * p for p in normalized]

    @property
    def min_height(self) -> float:
        return max(c.min_height for c in self.components)

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        gap = self._gap_val(t)
        col_widths = self._col_widths(width, gap)
        cursor_x = x
        for comp, col_w in zip(self.components, col_widths):
            comp.render(slide, cursor_x, y, col_w, height, theme=t)
            cursor_x += col_w + gap


# ── Column ─────────────────────────────────────────────────────────────────

class Column(Component):
    """Stacks children vertically, each receiving its min_height."""

    def __init__(self, *components: Component, gap: float | None = None):
        if len(components) == 0:
            raise ValueError("Column requires at least one component")
        self.components = components
        self._gap = gap

    def _gap_val(self, theme: Theme) -> float:
        return self._gap if self._gap is not None else theme.SM

    @property
    def min_height(self) -> float:
        return sum(c.min_height for c in self.components) + 0.2 * (len(self.components) - 1)

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        gap = self._gap_val(t)
        total_needed = sum(c.min_height for c in self.components) + gap * (len(self.components) - 1)
        if total_needed > height + 0.01:
            raise ValueError(
                f"Column min_height ({total_needed:.2f}\") exceeds available height ({height:.2f}\")"
            )
        cursor_y = y
        for comp in self.components:
            comp.render(slide, x, cursor_y, width, comp.min_height, theme=t)
            cursor_y += comp.min_height + gap


# ── Grid ───────────────────────────────────────────────────────────────────

class Grid(Component):
    """Wraps a list of components into rows of fixed column count."""

    def __init__(self, components: list[Component], cols: int = 3,
                 col_gap: float | None = None, row_gap: float | None = None):
        if len(components) == 0:
            raise ValueError("Grid requires at least one component")
        self.components = components
        self.cols = cols
        self._col_gap = col_gap
        self._row_gap = row_gap

    def _col_gap_val(self, t: Theme) -> float:
        return self._col_gap if self._col_gap is not None else t.SM

    def _row_gap_val(self, t: Theme) -> float:
        return self._row_gap if self._row_gap is not None else t.SM

    def _row_count(self) -> int:
        return (len(self.components) + self.cols - 1) // self.cols

    def _max_row_height(self, row_comps: list[Component]) -> float:
        return max(c.min_height for c in row_comps)

    @property
    def min_height(self) -> float:
        row_gap = self._row_gap if self._row_gap is not None else 0.2
        rows = self._row_count()
        # Compute max height per row
        total = 0.0
        for i in range(rows):
            chunk = self.components[i * self.cols: (i + 1) * self.cols]
            total += self._max_row_height(chunk)
        total += row_gap * (rows - 1)
        return total

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        col_gap = self._col_gap_val(t)
        row_gap = self._row_gap_val(t)
        n = len(self.components)
        cursor_y = y

        for row_idx in range(self._row_count()):
            chunk = self.components[row_idx * self.cols: (row_idx + 1) * self.cols]
            row_h = self._max_row_height(chunk)
            Row(*chunk, gap=col_gap).render(slide, x, cursor_y, width, row_h, theme=t)
            cursor_y += row_h + row_gap


# ── Container ──────────────────────────────────────────────────────────────

class Container(Component):
    """Draws a background rect then renders a child within padded bounds.

    This is the *only* place that implements background-drawing + padding.
    CalloutBox, QuoteBlock, etc. are built on top of this.
    """

    def __init__(self, child: Component,
                 padding: float | None = None,
                 fill_rgb: tuple[int, int, int] | None = None,
                 border_rgb: tuple[int, int, int] | None = None,
                 radius: float = 0.05):
        self.child = child
        self._padding = padding
        self.fill_rgb = fill_rgb
        self.border_rgb = border_rgb
        self.radius = radius

    def _pad(self, t: Theme) -> float:
        return self._padding if self._padding is not None else t.MD

    @property
    def min_height(self) -> float:
        from pptx_components.theme import get_theme
        t = get_theme()
        return self.child.min_height + 2 * self._pad(t)

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        pad = self._pad(t)
        fill = self.fill_rgb if self.fill_rgb is not None else t.SURFACE

        bg = add_rect(slide, x, y, width, height, fill_rgb=fill, radius=self.radius)

        if self.border_rgb is not None:
            bg.line.color.rgb = __import__('pptx.dml.color', fromlist=['RGBColor']).RGBColor(*self.border_rgb)
            bg.line.width = __import__('pptx.util', fromlist=['Pt']).Pt(1)

        inner_x = x + pad
        inner_y = y + pad
        inner_w = width - 2 * pad
        inner_h = height - 2 * pad
        self.child.render(slide, inner_x, inner_y, inner_w, inner_h, theme=t)
