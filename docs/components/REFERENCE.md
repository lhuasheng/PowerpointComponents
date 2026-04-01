# Component Reference

This reference documents constructor parameters and common usage snippets.

## Theme Cascade And Scope

### Precedence

Theme resolution follows this order:

1. Explicit component-level theme passed to `render(..., theme=...)`.
2. Local section override applied by `Container(local_theme=..., theme_patch=...)`.
3. `SlideBuilder(theme=...)` scope.
4. Global fallback from `set_theme(...)` / `get_theme()`.

### Container Section Override API

Import: `pc.Container`

Signature additions:

```python
Container(
    child: Component,
    padding: float | None = None,
    fill_rgb: tuple[int, int, int] | None = None,
    border_rgb: tuple[int, int, int] | None = None,
    radius: float = 0.05,
    local_theme: Theme | None = None,
    theme_patch: Mapping[str, object] | None = None,
)
```

`theme_patch` lets you patch only selected theme tokens for a section subtree.
Supported keys include spacing/typography constants and semantic color tokens:

- `DISPLAY`, `HEADING`, `SUBHEADING`, `BODY`, `CAPTION`
- `XS`, `SM`, `MD`, `LG`, `XL`
- `SLIDE_W`, `SLIDE_H`, `MARGIN`
- `BG`, `SURFACE`, `SURFACE_ALT`
- `TEXT_PRIMARY`, `TEXT_SECONDARY`, `TEXT_MUTED`
- `ACCENT`, `ACCENT_SOFT`, `CALLOUT`, `POSITIVE`, `NEGATIVE`

Example:

```python
section = pc.Container(
    pc.Column(
        pc.MetricCard("Pipeline", "$3.4M", "+6%", True),
        pc.TextCard("Section note", "This block uses a warmer local surface."),
    ),
    theme_patch={
        "SURFACE": (255, 248, 236),
        "SURFACE_ALT": (246, 230, 206),
        "TEXT_PRIMARY": (68, 44, 22),
        "MD": 0.18,
    },
)
```

### React Mental Model Mapping

- `SlideBuilder(theme=...)` is analogous to `ThemeProvider` scope.
- `Container(local_theme=..., theme_patch=...)` is analogous to nested provider overrides.
- `render(..., theme=...)` is analogous to per-component explicit prop override.
- `set_theme(...)` is analogous to process-level default context value.

## Title And Section Components

### TitleBlock

Import: `pc.TitleBlock`

Signature:

```python
TitleBlock(title: str, subtitle: str | None = None)
```

### SectionHeader

Import: `pc.SectionHeader`

Signature:

```python
SectionHeader(text: str, badge_text: str | None = None)
```

## Metrics

### MetricCard

Import: `pc.MetricCard`

Signature:

```python
MetricCard(
    label: str,
    value: str,
    delta: str | None = None,
    delta_positive: bool | None = None,
)
```

### BigStat

Import: `pc.BigStat`

Signature:

```python
BigStat(value: str, label: str, description: str | None = None)
```

## Tables

### DataTable

Import: `pc.DataTable`

Signature:

```python
DataTable(
    headers: list[str],
    rows: list[list[str]],
    weights: list[float] | None = None,
    zebra: bool = True,
    accent_header: bool = True,
)
```

Notes:

- `weights` must match header count.
- every row length must match header count.

## Charts

### BarChart

Import: `pc.BarChart`

Signature:

```python
BarChart(
    categories: list[str],
    series: dict[str, list[float]],
    title: str | None = None,
    stacked: bool = False,
    mode: str | None = None,
)
```

Supported `mode` values:

- `column_clustered`
- `column_stacked`
- `column_stacked_100`
- `bar_clustered`
- `bar_stacked`

### LineChart

Import: `pc.LineChart`

Signature:

```python
LineChart(
    categories: list[str],
    series: dict[str, list[float]],
    title: str | None = None,
)
```

### PieChart

Import: `pc.PieChart`

Signature:

```python
PieChart(
    categories: list[str],
    values: list[float],
    title: str | None = None,
)
```

## Lists And Text Blocks

### ListBlock

Import: `pc.ListBlock`

Signature:

```python
ListBlock(
    items: list[str],
    style: str = "bullet",  # bullet | number | check
    checked: list[int] | None = None,
    title: str | None = None,
)
```

### CalloutBox

Import: `pc.CalloutBox`

Signature:

```python
CalloutBox(text: str, style: str = "info")
```

Supported styles: `info`, `warning`, `success`, `error`

### QuoteBlock

Import: `pc.QuoteBlock`

Signature:

```python
QuoteBlock(text: str, author: str | None = None)
```

### Divider

Import: `pc.Divider`

Signature:

```python
Divider(label: str | None = None)
```

### Spacer

Import: `pc.Spacer`

Signature:

```python
Spacer(height: float)
```

## Progress And Status

### ProgressBar

Import: `pc.ProgressBar`

Signature:

```python
ProgressBar(
    label: str,
    value: float,
    max_value: float = 100,
    show_pct: bool = True,
)
```

### StatusBadge

Import: `pc.StatusBadge`

Signature:

```python
StatusBadge(text: str, status: str = "ok")
```

Supported statuses: `ok`, `warn`, `error`

## Navigation Components

### TabsPanel

Import: `pc.TabsPanel`

Signature:

```python
TabsPanel(
    tabs: list[str],
    active_index: int = 0,
    content: str | None = None,
    title: str | None = None,
    variant: str = "pill",  # pill | line
)
```

### StepFlow

Import: `pc.StepFlow`

Signature:

```python
StepFlow(
    steps: list[str],
    current: int = 0,
    statuses: list[str] | None = None,
    title: str | None = None,
    show_numbers: bool = True,
)
```

Supported statuses: `done`, `current`, `pending`, `error`

## Visual Primitives

### ImageBlock

Import: `pc.ImageBlock`

Signature:

```python
ImageBlock(
    image_path: str,
    mode: str = "contain",  # contain | stretch | fit_width | fit_height
    border_rgb: tuple[int, int, int] | None = None,
    border_width_pt: float = 1.0,
)
```

### Legend

Import: `pc.Legend`

Signature:

```python
Legend(
    items: list[tuple[str, tuple[int, int, int]]],
    title: str | None = None,
)
```

### KPIGrid

Import: `pc.KPIGrid`

Signature:

```python
KPIGrid(
    metrics: list[tuple[str, str, str | None, bool | None]],
    cols: int = 3,
    col_gap: float | None = None,
    row_gap: float | None = None,
)
```

## Additional Components In Codebase

### Timeline

Import:

```python
from pptx_components.components.timeline import Timeline
```

Signature:

```python
Timeline(
    events: list[tuple[str, str, str]],  # status in done|current|upcoming|risk
    title: str | None = None,
)
```

### ComparisonPanel

Import:

```python
from pptx_components.components.comparison import ComparisonPanel
```

Signature:

```python
ComparisonPanel(
    left_title: str,
    left_items: list[str],
    right_title: str,
    right_items: list[str],
    title: str | None = None,
)
```
