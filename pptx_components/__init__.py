from importlib.metadata import PackageNotFoundError, version as _package_version

from pptx_components.theme import (
    Theme,
    ThemePatch,
    DarkTheme,
    LightTheme,
    CorporateBlueTheme,
    EditorialWarmTheme,
    HighContrastTheme,
    BrandTheme,
    PatchedTheme,
    apply_theme_patch,
    set_theme,
    get_theme,
)
from pptx_components.base import Component
from pptx_components.layout import Row, Column, Grid, Container
from pptx_components.slide_builder import SlideBuilder

from pptx_components.components.title import TitleBlock, SectionHeader
from pptx_components.components.metric import MetricCard, BigStat
from pptx_components.components.sparkline_card import SparklineCard
from pptx_components.components.table import DataTable
from pptx_components.components.chart import BarChart, LineChart, PieChart, ScatterChart
from pptx_components.components.donut_chart import DonutChart
from pptx_components.components.list import ListBlock
from pptx_components.components.callout import CalloutBox, QuoteBlock
from pptx_components.components.divider import Divider, Spacer
from pptx_components.components.progress import ProgressBar, StatusBadge
from pptx_components.components.navigation import TabsPanel, StepFlow, AccordionBlock, FeatureGrid
from pptx_components.components.image import ImageBlock
from pptx_components.components.legend import Legend
from pptx_components.components.kpi_grid import KPIGrid
from pptx_components.components.timeline import Timeline
from pptx_components.components.comparison import ComparisonPanel
from pptx_components.components.heatmap import Heatmap
from pptx_components.components.range_indicator import RangeIndicator
from pptx_components.components.code_block import CodeBlock
from pptx_components.components.annotation import Annotation
from pptx_components.components.waterfall import WaterfallChart
from pptx_components.components.gantt_chart import GanttChart
from pptx_components.components.funnel_chart import FunnelChart
from pptx_components.components.radar_chart import RadarChart
from pptx_components.components.text_card import TextCard
from pptx_components.components.scatter import ScatterPlot
from pptx_components.components.grouped_table import GroupedTable
from pptx_components.components.narrative import (
    NarrativePage,
    NarrativeTwoColumnPage,
    LongNarrativeBlock,
    paginate_narrative,
    build_narrative_slides,
)
from pptx_components.export import export_slides
from pptx_components.reverse import (
    ReverseWarning,
    ReverseResult,
    PresentationReverser,
    reverse_pptx_to_script,
)
from pptx_components.master_builder import MasterPresentation, MasterSlide

try:
    __version__ = _package_version("pptx-components")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "Theme", "ThemePatch", "DarkTheme", "LightTheme", "CorporateBlueTheme", "EditorialWarmTheme", "HighContrastTheme", "BrandTheme", "PatchedTheme", "apply_theme_patch", "set_theme", "get_theme",
    "Component",
    "Row", "Column", "Grid", "Container",
    "SlideBuilder",
    "TitleBlock", "SectionHeader",
    "MetricCard", "BigStat", "SparklineCard",
    "DataTable",
    "BarChart", "LineChart", "PieChart", "ScatterChart", "DonutChart",
    "ListBlock",
    "CalloutBox", "QuoteBlock",
    "Divider", "Spacer",
    "ProgressBar", "StatusBadge",
    "TabsPanel", "StepFlow", "AccordionBlock", "FeatureGrid",
    "ImageBlock", "Legend", "KPIGrid",
    "Timeline", "ComparisonPanel",
    "Heatmap", "RangeIndicator", "CodeBlock", "Annotation", "WaterfallChart", "GanttChart", "FunnelChart", "RadarChart",
    "TextCard",    "ScatterPlot", "GroupedTable",
    "NarrativePage", "NarrativeTwoColumnPage", "LongNarrativeBlock", "paginate_narrative", "build_narrative_slides",
    "export_slides",
    "ReverseWarning", "ReverseResult", "PresentationReverser", "reverse_pptx_to_script",
]
