from __future__ import annotations

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from pptx_components.base import Component, _resolve, add_rect, add_text_box
from pptx_components.components.chart_utils import default_theme_palette
from pptx_components.theme import Theme


class ScatterPlot(Component):
    """XY scatter plot visualization for correlation and distribution analysis.

    Renders data points as circles on a 2D grid. Useful for:
        - Correlation analysis (feature vs. performance)
        - Outlier detection
        - Risk/return quadrants
        - Portfolio positioning

    Axes:
        - X-axis: Horizontal numeric range
        - Y-axis: Vertical numeric range
        - Optional quadrant dividers and labels
        - Configurable axis labels and tick marks

    Data Points:
        - Each point: (x, y, size=0.15, color=theme.ACCENT)
        - Optional point labels (text annotation)
        - Optional grouping by color

    Args:
        points: List of (x, y, label=None, color_rgb=None, size=0.15) tuples.
            x, y: Numeric coordinates (will be scaled to grid).
            label: Optional text label for point.
            color_rgb: Optional (R, G, B) point color; theme.ACCENT used if None.
            size: Point radius in inches. Default: 0.15 (small dot).
        x_label: X-axis label string (e.g. "Features", "Cost").
        y_label: Y-axis label string (e.g. "Performance", "Value").
        title: Optional plot title.
        x_range: (min, max) numeric range for x-axis. Auto-calculated if None.
        y_range: (min, max) numeric range for y-axis. Auto-calculated if None.
        show_grid: Whether to draw gridlines. Default: True.
        quadrant_labels: (top_left, top_right, bottom_left, bottom_right) text labels for quadrants.

    Example:
        >>> scatter = ScatterPlot(
        ...     points=[
        ...         (2.5, 8.0, "Algorithm A", (100, 200, 255), 0.2),
        ...         (5.0, 6.5, "Algorithm B", (100, 200, 255), 0.2),
        ...         (3.0, 4.0, "Outlier", (255, 100, 100), 0.25),
        ...     ],
        ...     x_label="Complexity",
        ...     y_label="Accuracy (%)",
        ...     title="Model Performance Landscape",
        ...     quadrant_labels=("High Perf", "Ideal", "Low Complexity", "Avoid")
        ... )
    """

    # Layout constants
    TITLE_H = 0.4
    LABEL_H = 0.3
    TICK_H = 0.2
    MARGIN = 0.3

    def __init__(
        self,
        points: list[tuple[float, float, str | None, tuple[int, int, int] | None, float]],
        x_label: str | None = None,
        y_label: str | None = None,
        title: str | None = None,
        x_range: tuple[float, float] | None = None,
        y_range: tuple[float, float] | None = None,
        show_grid: bool = True,
        quadrant_labels: tuple[str, str, str, str] | None = None,
    ):
        if len(points) == 0:
            raise ValueError("points list must not be empty")

        # Parse points
        self.points = []
        for pt in points:
            if len(pt) == 2:
                self.points.append((pt[0], pt[1], None, None, 0.15))
            elif len(pt) == 3:
                self.points.append((pt[0], pt[1], pt[2], None, 0.15))
            elif len(pt) == 4:
                self.points.append((pt[0], pt[1], pt[2], pt[3], 0.15))
            elif len(pt) == 5:
                self.points.append(pt)
            else:
                raise ValueError(f"Each point must be 2-5 tuple, got {len(pt)}")

        self.x_label = x_label
        self.y_label = y_label
        self.title = title
        self.show_grid = show_grid
        self.quadrant_labels = quadrant_labels

        # Infer ranges from data
        xs = [pt[0] for pt in self.points]
        ys = [pt[1] for pt in self.points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        pad_x = (max_x - min_x) * 0.1 if max_x > min_x else 1.0
        pad_y = (max_y - min_y) * 0.1 if max_y > min_y else 1.0
        self.x_range = x_range or (min_x - pad_x, max_x + pad_x)
        self.y_range = y_range or (min_y - pad_y, max_y + pad_y)

    @property
    def min_height(self) -> float:
        h = (self.TITLE_H if self.title else 0.0) + 2.5
        if self.x_label:
            h += self.LABEL_H
        return h

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        cursor_y = y

        # Title
        if self.title:
            add_text_box(
                slide, x, cursor_y, width, self.TITLE_H,
                self.title, t.SUBHEADING, bold=True,
                color_rgb=t.TEXT_PRIMARY,
                alignment=PP_ALIGN.CENTER
            )
            cursor_y += self.TITLE_H

        # Plot area (reserve space for labels)
        plot_x = x + self.MARGIN + (0.4 if self.y_label else 0)
        plot_w = width - self.MARGIN * 2 - (0.4 if self.y_label else 0)
        plot_y = cursor_y
        plot_h = height - cursor_y + y - (self.LABEL_H if self.x_label else 0)

        # Draw axes (subtle lines)
        axis_color = t.SURFACE_ALT
        add_rect(slide, plot_x, plot_y + plot_h - 0.05, plot_w, 0.03, fill_rgb=axis_color)  # X-axis
        add_rect(slide, plot_x, plot_y, 0.03, plot_h, fill_rgb=axis_color)  # Y-axis

        # Draw gridlines if enabled
        if self.show_grid:
            grid_color = t.SURFACE
            for i in range(5):
                gx = plot_x + (plot_w * i / 4)
                gy = plot_y + (plot_h * i / 4)
                add_rect(slide, gx, plot_y, 0.02, plot_h, fill_rgb=grid_color)  # Vertical
                add_rect(slide, plot_x, gy, plot_w, 0.02, fill_rgb=grid_color)  # Horizontal

        # Draw quadrants if labels provided
        if self.quadrant_labels:
            tl, tr, bl, br = self.quadrant_labels
            q_x = plot_x + plot_w / 2
            q_y = plot_y + plot_h / 2
            for (qx, qy, label) in [
                (plot_x, plot_y, tl),
                (q_x, plot_y, tr),
                (plot_x, q_y, bl),
                (q_x, q_y, br),
            ]:
                add_text_box(
                    slide, qx, qy, q_x - plot_x, plot_h / 2,
                    label, t.CAPTION,
                    color_rgb=t.TEXT_MUTED,
                    alignment=PP_ALIGN.CENTER
                )

        # Plot points
        x_min, x_max = self.x_range
        y_min, y_max = self.y_range
        palette = default_theme_palette(t)

        for idx, (data_x, data_y, label, color_rgb, size) in enumerate(self.points):
            # Normalize to [0, 1]
            norm_x = (data_x - x_min) / (x_max - x_min) if x_max > x_min else 0.5
            norm_y = 1.0 - ((data_y - y_min) / (y_max - y_min) if y_max > y_min else 0.5)

            # Map to plot area
            pt_x = plot_x + norm_x * plot_w
            pt_y = plot_y + norm_y * plot_h

            # Draw point circle
            pt_color = color_rgb or palette[idx % len(palette)]
            add_rect(
                slide, pt_x - size / 2, pt_y - size / 2, size, size,
                fill_rgb=pt_color, radius=0.075
            )

            # Draw label if present
            if label:
                add_text_box(
                    slide, pt_x + size / 2 + 0.05, pt_y - 0.1, 0.6, 0.2,
                    label, t.CAPTION,
                    color_rgb=t.TEXT_PRIMARY
                )

        # Axis labels
        if self.x_label:
            add_text_box(
                slide, plot_x, plot_y + plot_h + 0.05, plot_w, self.LABEL_H,
                self.x_label, t.CAPTION,
                color_rgb=t.TEXT_MUTED,
                alignment=PP_ALIGN.CENTER
            )
        if self.y_label:
            add_text_box(
                slide, x, plot_y, 0.35, plot_h,
                self.y_label, t.CAPTION,
                color_rgb=t.TEXT_MUTED,
                alignment=PP_ALIGN.CENTER
            )
