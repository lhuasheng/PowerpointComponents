from __future__ import annotations

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.oxml.ns import qn

from pptx_components.base import Component, _resolve
from pptx_components.theme import Theme
from pptx_components.components.chart_utils import chart_data_from, pie_data_from


# Distinct palette for pie slices / multi-series charts
_PIE_PALETTE = [
    (59, 130, 246),   # blue-500
    (16, 185, 129),   # emerald-500
    (249, 115, 22),   # orange-500
    (139, 92, 246),   # violet-500
    (236, 72, 153),   # pink-500
    (234, 179, 8),    # yellow-500
    (20, 184, 166),   # teal-500
    (244, 63, 94),    # rose-500
]


def _set_no_fill_xml(chart) -> None:
    """Make chart area and plot area transparent via direct XML manipulation."""
    from lxml import etree
    chart_space = chart._chartSpace

    # Chart area (c:chartSpace/c:spPr)
    spPr = chart_space.find(qn('c:spPr'))
    if spPr is None:
        spPr = etree.SubElement(chart_space, qn('c:spPr'))
    noFill = spPr.find(qn('a:noFill'))
    if noFill is None:
        # Remove any existing fill
        for child in list(spPr):
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag in ('solidFill', 'gradFill', 'pattFill', 'blipFill'):
                spPr.remove(child)
        etree.SubElement(spPr, qn('a:noFill'))

    # Plot area (c:chart/c:plotArea/c:spPr)
    c_chart = chart_space.find(qn('c:chart'))
    if c_chart is not None:
        plotArea = c_chart.find(qn('c:plotArea'))
        if plotArea is not None:
            pa_spPr = plotArea.find(qn('c:spPr'))
            if pa_spPr is None:
                pa_spPr = etree.SubElement(plotArea, qn('c:spPr'))
            noFill2 = pa_spPr.find(qn('a:noFill'))
            if noFill2 is None:
                for child in list(pa_spPr):
                    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    if tag in ('solidFill', 'gradFill', 'pattFill', 'blipFill'):
                        pa_spPr.remove(child)
                etree.SubElement(pa_spPr, qn('a:noFill'))


def _style_chart(chart, t: Theme, title: str | None,
                 is_line: bool = False, is_pie: bool = False) -> None:
    """Apply theme colors and optional title to a chart object."""
    # Title
    chart.has_title = title is not None
    if title:
        chart.chart_title.text_frame.text = title
        run = chart.chart_title.text_frame.paragraphs[0].runs[0]
        run.font.name = "Calibri"
        run.font.size = Pt(t.SUBHEADING)
        run.font.color.rgb = RGBColor(*t.TEXT_PRIMARY)

    # Plot area / chart area background — transparent via XML
    _set_no_fill_xml(chart)

    # Legend
    if chart.has_legend:
        chart.legend.font.color.rgb = RGBColor(*t.TEXT_SECONDARY)
        chart.legend.font.size = Pt(t.CAPTION)

    # ── Axis labels and tick marks ─────────────────────────────────────
    try:
        cat_axis = chart.category_axis
        cat_axis.tick_labels.font.color.rgb = RGBColor(*t.TEXT_SECONDARY)
        cat_axis.tick_labels.font.size = Pt(t.CAPTION)
        cat_axis.tick_labels.font.name = "Calibri"
        cat_axis.format.line.color.rgb = RGBColor(*t.SURFACE_ALT)
        cat_axis.has_major_gridlines = False
    except Exception:
        pass  # pie charts have no axes

    try:
        val_axis = chart.value_axis
        val_axis.tick_labels.font.color.rgb = RGBColor(*t.TEXT_SECONDARY)
        val_axis.tick_labels.font.size = Pt(t.CAPTION)
        val_axis.tick_labels.font.name = "Calibri"
        val_axis.format.line.color.rgb = RGBColor(*t.SURFACE_ALT)
        val_axis.major_gridlines.format.line.color.rgb = RGBColor(*t.SURFACE_ALT)
    except Exception:
        pass

    # ── Series colors ──────────────────────────────────────────────────
    if is_pie:
        # Color each data point with a distinct hue
        plot = chart.plots[0]
        for i, point in enumerate(plot.series[0].points):
            color = _PIE_PALETTE[i % len(_PIE_PALETTE)]
            point.format.fill.solid()
            point.format.fill.fore_color.rgb = RGBColor(*color)
    else:
        series_colors = [t.ACCENT, t.ACCENT_SOFT, t.TEXT_MUTED]
        for i, series in enumerate(chart.series):
            color = series_colors[i % len(series_colors)]
            if is_line:
                # Lines need visible strokes, not fills
                series.format.line.color.rgb = RGBColor(*color)
                series.format.line.width = Pt(2.5)
                series.smooth = True
            else:
                series.format.fill.solid()
                series.format.fill.fore_color.rgb = RGBColor(*color)
                series.format.line.fill.background()


def _add_chart_shape(slide, chart_data, chart_type, x, y, w, h):
    from pptx.util import Inches
    return slide.shapes.add_chart(chart_type, Inches(x), Inches(y), Inches(w), Inches(h), chart_data)


class BarChart(Component):
    """Vertical bar chart.

    Args:
        categories: X-axis labels.
        series: Dict of series name → list of values.
        title: Optional chart title.
        stacked: Use stacked bar chart.
        mode: Optional explicit chart mode. Supported values:
            "column_clustered", "column_stacked", "column_stacked_100",
            "bar_clustered", "bar_stacked".
    """

    def __init__(self, categories: list[str], series: dict[str, list[float]],
                 title: str | None = None, stacked: bool = False,
                 mode: str | None = None):
        if mode is not None and mode not in (
            "column_clustered", "column_stacked", "column_stacked_100",
            "bar_clustered", "bar_stacked",
        ):
            raise ValueError(
                "mode must be one of: 'column_clustered', 'column_stacked', "
                "'column_stacked_100', 'bar_clustered', 'bar_stacked'"
            )
        self.categories = categories
        self.series = series
        self.title = title
        self.stacked = stacked
        self.mode = mode

    @property
    def min_height(self) -> float:
        return 2.5

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        cd = chart_data_from(self.categories, self.series)
        if self.mode == "column_stacked":
            chart_type = XL_CHART_TYPE.COLUMN_STACKED
        elif self.mode == "column_stacked_100":
            chart_type = XL_CHART_TYPE.COLUMN_STACKED_100
        elif self.mode == "bar_clustered":
            chart_type = XL_CHART_TYPE.BAR_CLUSTERED
        elif self.mode == "bar_stacked":
            chart_type = XL_CHART_TYPE.BAR_STACKED
        elif self.mode == "column_clustered":
            chart_type = XL_CHART_TYPE.COLUMN_CLUSTERED
        else:
            # Backward-compatible behavior.
            chart_type = (XL_CHART_TYPE.BAR_STACKED if self.stacked
                          else XL_CHART_TYPE.COLUMN_CLUSTERED)
        graphic = _add_chart_shape(slide, cd, chart_type, x, y, width, height)
        _style_chart(graphic.chart, t, self.title, is_line=False, is_pie=False)


class LineChart(Component):
    """Line chart.

    Args:
        categories: X-axis labels.
        series: Dict of series name → list of values.
        title: Optional chart title.
    """

    def __init__(self, categories: list[str], series: dict[str, list[float]],
                 title: str | None = None):
        self.categories = categories
        self.series = series
        self.title = title

    @property
    def min_height(self) -> float:
        return 2.5

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        cd = chart_data_from(self.categories, self.series)
        graphic = _add_chart_shape(slide, cd, XL_CHART_TYPE.LINE, x, y, width, height)
        _style_chart(graphic.chart, t, self.title, is_line=True)


class PieChart(Component):
    """Pie chart.

    Args:
        categories: Slice labels.
        values: Slice values.
        title: Optional chart title.
    """

    def __init__(self, categories: list[str], values: list[float],
                 title: str | None = None):
        self.categories = categories
        self.values = values
        self.title = title

    @property
    def min_height(self) -> float:
        return 2.5

    def render(self, slide, x: float, y: float, width: float, height: float,
               theme: Theme | None = None) -> None:
        t = _resolve(theme)
        cd = pie_data_from(self.categories, self.values)
        graphic = _add_chart_shape(slide, cd, XL_CHART_TYPE.PIE, x, y, width, height)
        _style_chart(graphic.chart, t, self.title, is_pie=True)
