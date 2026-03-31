# Composition Patterns

This page shows practical patterns for composing slides with `SlideBuilder`.

## 1) Executive Dashboard Pattern

```python
import pptx_components as pc

b.add(pc.TitleBlock("Executive Dashboard", "Weekly operating metrics"))
b.skip(0.1)
b.add_row(
    pc.MetricCard("MRR", "$128K", delta="+12%", delta_positive=True),
    pc.MetricCard("NPS", "72", delta="+4pts", delta_positive=True),
    pc.MetricCard("Churn", "3.2%", delta="+0.4pp", delta_positive=False),
    h=1.5,
)
b.skip(0.15)
b.add(pc.BarChart(["Jan", "Feb", "Mar"], {"Revenue": [90, 98, 105]}), h=2.4)
```

## 2) Status And Risk Pattern

```python
b.add(pc.SectionHeader("Operational Status", badge_text="WEEK 24"))
b.skip(0.1)
b.add(pc.CalloutBox("Payment retry latency above target in EU region.", style="warning"))
b.add(pc.CalloutBox("API error rate stabilized after hotfix.", style="success"))
b.skip(0.1)
b.add(pc.ProgressBar("API v3 rollout", 62))
b.add(pc.ProgressBar("Infrastructure migration", 40))
```

## 3) Product Story Pattern With Navigation

```python
b.add(
    pc.TabsPanel(
        ["Overview", "Analytics", "Risks", "Decisions"],
        active_index=1,
        title="Q2 Review",
        variant="line",
        content="Activation improved by 6% and CAC dropped 8%.",
    ),
    h=1.9,
)
b.skip(0.15)
b.add(
    pc.StepFlow(
        ["Discovery", "Prototype", "Validation", "Launch", "Scale"],
        current=2,
        statuses=["done", "done", "current", "pending", "pending"],
    ),
    h=1.4,
)
```

## 4) Data + Legend + KPI Grid Pattern

```python
legend_items = [
    ("APAC", (59, 130, 246)),
    ("EMEA", (16, 185, 129)),
    ("Americas", (249, 115, 22)),
]

b.add_row(
    pc.ImageBlock("examples/demo_dark_slides/slide_004.png", mode="contain"),
    pc.Legend(legend_items, title="Region Color Legend"),
    h=2.5,
    weights=[1.6, 1.0],
)
b.skip(0.1)
b.add(
    pc.KPIGrid(
        [
            ("New Leads", "1,284", "+9%", True),
            ("Conversion", "14.2%", "+1.1pp", True),
            ("Win Rate", "31%", "-2pp", False),
            ("Sales Cycle", "27 days", "-3 days", True),
        ],
        cols=2,
    ),
    h=2.2,
)
```

## 5) Internal Components Pattern

If you want to use components not yet re-exported at package root:

```python
from pptx_components.components.timeline import Timeline
from pptx_components.components.comparison import ComparisonPanel

b.add(
    Timeline(
        [
            ("Jan", "Discovery", "done"),
            ("Feb", "Prototype", "done"),
            ("Mar", "Validation", "current"),
            ("Apr", "Launch", "upcoming"),
        ],
        title="Roadmap",
    ),
    h=1.8,
)

b.add(
    ComparisonPanel(
        "Before",
        ["Manual reporting", "Siloed dashboards", "Late alerts"],
        "After",
        ["Automated pipeline", "Unified metrics", "Near real-time alerts"],
        title="Transformation",
    ),
    h=2.2,
)
```
