"""Demo deck — generates demo_dark.pptx and demo_light.pptx.

Run from the repo root:
    python examples/demo.py
"""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pptx import Presentation

import pptx_components as pc


# ── Shared sample data ─────────────────────────────────────────────────────

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
REVENUE = {"Revenue ($K)": [320, 380, 410, 470, 510, 580],
           "Target ($K)":  [350, 380, 400, 450, 490, 550]}
PIE_CATS = ["APAC", "EMEA", "Americas", "Other"]
PIE_VALS = [38, 27, 30, 5]
REGION_LEGEND = list(zip(PIE_CATS, [
    (59, 130, 246),
    (16, 185, 129),
    (249, 115, 22),
    (139, 92, 246),
]))

TABLE_HEADERS = ["Product", "Q1 Revenue", "Q2 Revenue", "Growth", "Status"]
TABLE_ROWS = [
    ["Alpha Suite",  "$420K", "$510K", "+21%", "On track"],
    ["Beta Platform","$280K", "$295K", "+5%",  "At risk"],
    ["Gamma API",    "$190K", "$240K", "+26%", "On track"],
    ["Delta Service","$95K",  "$88K",  "-7%",  "Behind"],
    ["Epsilon SDK",  "$60K",  "$75K",  "+25%", "On track"],
]

KPI_ITEMS = [
    ("New Leads", "1,284", "+9%", True),
    ("Conversion", "14.2%", "+1.1pp", True),
    ("Pipeline Value", "$3.4M", "+6%", True),
    ("Win Rate", "31%", "-2pp", False),
    ("Sales Cycle", "27 days", "-3 days", True),
    ("Upsell MRR", "$48K", "+12%", True),
]

TIMELINE_EVENTS = [
    ("Q1", "Discovery", "done"),
    ("Q2", "Pilot Launch", "done"),
    ("Q3", "Enterprise Rollout", "current"),
    ("Q4", "Automation Phase", "upcoming"),
    ("Q1 '27", "Scale + Expansion", "upcoming"),
]

BUILD_VS_BUY_LEFT = [
    "Full control over roadmap",
    "Can optimize for existing stack",
    "Higher upfront engineering cost",
    "Longer time-to-market",
]

BUILD_VS_BUY_RIGHT = [
    "Fastest path to launch",
    "Vendor support included",
    "Recurring license cost",
    "Less flexibility on edge cases",
]


# ── Slide factory functions (theme-agnostic) ───────────────────────────────

def slide_1_title(prs: Presentation) -> None:
    """Slide 1 — Title + Section Header."""
    b = pc.SlideBuilder(prs)
    b.add(pc.TitleBlock("Q2 Business Review",
                        "Performance metrics, trends, and outlook — June 2026"))
    b.skip(0.1)
    b.add(pc.SectionHeader("Key Highlights", badge_text="CONFIDENTIAL"))
    b.skip(0.2)
    b.add(pc.SectionHeader("Executive Summary"))


def slide_2_metrics(prs: Presentation) -> None:
    """Slide 2 — Metric cards + BigStat."""
    b = pc.SlideBuilder(prs)
    b.add(pc.SectionHeader("Performance KPIs", badge_text="Q2 2026"))
    b.skip(0.15)
    b.add_row(
        pc.MetricCard("Revenue", "$1.28M", delta="+18%", delta_positive=True),
        pc.MetricCard("Active Users", "24,370", delta="+7%", delta_positive=True),
        pc.MetricCard("Churn Rate", "3.2%", delta="+0.4pp", delta_positive=False),
        h=1.5,
    )
    b.skip(0.2)
    b.add_row(
        pc.BigStat("98.7%", "System Uptime", description="30-day rolling average"),
        pc.BigStat("4.2s", "Avg Response Time", description="p95 latency"),
        pc.BigStat("$42", "CAC", description="Customer acquisition cost"),
        h=1.8,
    )


def slide_3_table(prs: Presentation) -> None:
    """Slide 3 — Data table."""
    b = pc.SlideBuilder(prs)
    b.add(pc.SectionHeader("Product Revenue Breakdown"))
    b.skip(0.1)
    b.add(
        pc.DataTable(
            TABLE_HEADERS,
            TABLE_ROWS,
            weights=[3, 1.5, 1.5, 1, 1.2],
        ),
        h=pc.DataTable(TABLE_HEADERS, TABLE_ROWS).min_height,
    )


def slide_4_charts(prs: Presentation) -> None:
    """Slide 4 — Bar + Line charts side by side."""
    b = pc.SlideBuilder(prs)
    b.add(pc.SectionHeader("Revenue Trend Analysis"))
    b.skip(0.1)
    b.add_row(
        pc.BarChart(MONTHS, REVENUE, title="Monthly Revenue vs Target"),
        pc.LineChart(MONTHS, REVENUE, title="Revenue Trend"),
        h=2.8,
    )
    b.skip(0.15)
    b.add(pc.PieChart(PIE_CATS, PIE_VALS, title="Revenue by Region"), h=2.6)


def slide_5_lists(prs: Presentation) -> None:
    """Slide 5 — Three list styles side by side."""
    b = pc.SlideBuilder(prs)
    b.add(pc.SectionHeader("Roadmap & Status"))
    b.skip(0.1)
    b.add_row(
        pc.ListBlock(
            ["Redesign onboarding flow", "Launch mobile app v2",
             "Integrate SSO providers", "Expand API docs"],
            style="bullet",
            title="Backlog",
        ),
        pc.ListBlock(
            ["Define OKRs for H2", "Security audit complete",
             "Migrate to GCP Cloud Run", "Enable A/B testing framework"],
            style="number",
            title="Priorities",
        ),
        pc.ListBlock(
            ["Deploy rate limiting", "Fix dashboard load time",
             "Update privacy policy", "Archive legacy endpoints",
             "Notify affected users"],
            style="check",
            checked=[0, 2],
            title="Checklist",
        ),
        h=2.2,
    )


def slide_6_callouts(prs: Presentation) -> None:
    """Slide 6 — Callout boxes + Quote block."""
    b = pc.SlideBuilder(prs)
    b.add(pc.SectionHeader("Notices & Insights"))
    b.skip(0.15)
    b.add(pc.CalloutBox("Database migration scheduled for July 4 — expect 2 min downtime.", "info"))
    b.add(pc.CalloutBox("Churn has increased 0.4pp — review retention playbook this sprint.", "warning"))
    b.add(pc.CalloutBox("Uptime target of 99.5% achieved for third consecutive month.", "success"))
    b.add(pc.CalloutBox("Payment gateway timeout rate exceeded SLA threshold on June 12.", "error"))
    b.skip(0.15)
    b.add(pc.QuoteBlock(
        "The goal is not to build more features — it's to make existing ones indispensable.",
        author="Product Review, May 2026"
    ), h=1.3)


def slide_7_progress(prs: Presentation) -> None:
    """Slide 7 — Progress bars + Status badges."""
    b = pc.SlideBuilder(prs)
    b.add(pc.SectionHeader("Sprint Progress", badge_text="Week 24"))
    b.skip(0.2)
    b.add(pc.ProgressBar("Authentication service migration", 85))
    b.add(pc.ProgressBar("API v3 rollout", 62))
    b.add(pc.ProgressBar("Data warehouse rebuild", 40))
    b.add(pc.ProgressBar("Mobile parity features", 91, show_pct=True))
    b.add(pc.ProgressBar("Legacy cleanup", 20, max_value=100))
    b.skip(0.25)
    b.add_row(
        pc.StatusBadge("Operational", "ok"),
        pc.StatusBadge("Degraded", "warn"),
        pc.StatusBadge("Outage", "error"),
        pc.StatusBadge("Healthy", "ok"),
        h=0.3,
    )


def slide_8_composite(prs: Presentation) -> None:
    """Slide 8 — Full composition: SectionHeader + Row(MetricCards) + Chart.

    This slide proves the composition model — all primitives, no special cases.
    """
    b = pc.SlideBuilder(prs)
    b.add(pc.TitleBlock("Executive Dashboard", "Composite layout — all components composed"))
    b.skip(0.1)
    b.add_row(
        pc.MetricCard("MRR", "$128K", delta="+12%", delta_positive=True),
        pc.MetricCard("NPS", "72", delta="+4pts", delta_positive=True),
        pc.MetricCard("CAC", "$42", delta="-8%", delta_positive=True),
        pc.MetricCard("LTV", "$890", delta="+6%", delta_positive=True),
        h=1.5,
    )
    b.skip(0.1)
    b.add(
        pc.BarChart(MONTHS,
                    {"MRR ($K)": [90, 98, 105, 112, 120, 128]},
                    title="Monthly Recurring Revenue"),
        h=2.6,
    )


def slide_9_navigation(prs: Presentation) -> None:
    """Slide 9 - React-inspired navigation patterns for storytelling."""
    b = pc.SlideBuilder(prs)
    b.add(pc.SectionHeader("React Pattern Adaptations", badge_text="Tabs + Steps"))
    b.skip(0.15)
    b.add(
        pc.TabsPanel(
            ["Overview", "Analytics", "Risks", "Decisions"],
            active_index=1,
            title="TabsPanel (inspired by Radix/shadcn Tabs)",
            variant="line",
            content=(
                "Q2 analytics summary: Revenue is up 18% YoY, activation improved by 6%, "
                "and churn remains above target in two enterprise segments."
            ),
        ),
        h=1.9,
    )
    b.skip(0.25)
    b.add(
        pc.StepFlow(
            ["Discovery", "Prototype", "Validation", "Launch", "Scale"],
            current=2,
            title="StepFlow (inspired by Ant Design Steps)",
            statuses=["done", "done", "current", "pending", "pending"],
        ),
        h=1.4,
    )


def slide_10_new_primitives(prs: Presentation) -> None:
    """Slide 10 - New composable primitives inspired by React ecosystems."""
    b = pc.SlideBuilder(prs)
    b.add(pc.SectionHeader("Phase 1 Additions", badge_text="Image + Legend + KPIGrid"))
    b.skip(0.1)

    image_path = os.path.join(os.path.dirname(__file__), "demo_dark_slides", "slide_004.png")

    b.add_row(
        pc.ImageBlock(image_path, mode="contain", border_rgb=(148, 163, 184), border_width_pt=1.0),
        pc.Legend(REGION_LEGEND, title="Region Color Legend"),
        h=2.6,
        weights=[1.6, 1.0],
    )
    b.skip(0.15)
    b.add(pc.KPIGrid(KPI_ITEMS, cols=3), h=3.0)


def slide_11_timeline_comparison(prs: Presentation) -> None:
    """Slide 11 - Timeline and comparison patterns with expanded chart mode."""
    b = pc.SlideBuilder(prs)
    b.add(pc.SectionHeader("Phase 2 Additions", badge_text="Timeline + Comparison"))
    b.skip(0.1)
    b.add(
        pc.Timeline(
            TIMELINE_EVENTS,
            title="Program Roadmap (MUI Timeline inspired)",
        ),
        h=1.85,
    )
    b.skip(0.15)
    b.add_row(
        pc.ComparisonPanel(
            "Build In-House",
            BUILD_VS_BUY_LEFT,
            "Buy Platform",
            BUILD_VS_BUY_RIGHT,
            title="Decision Matrix (shadcn composable style)",
        ),
        pc.BarChart(
            ["Build", "Buy", "Hybrid"],
            {
                "Delivery Speed": [55, 85, 75],
                "Flexibility": [92, 60, 80],
            },
            title="Evaluation Snapshot",
            mode="bar_clustered",
        ),
        h=2.8,
        weights=[1.45, 1.0],
    )


# ── Main ───────────────────────────────────────────────────────────────────

SLIDES = [
    slide_1_title,
    slide_2_metrics,
    slide_3_table,
    slide_4_charts,
    slide_5_lists,
    slide_6_callouts,
    slide_7_progress,
    slide_8_composite,
    slide_9_navigation,
    slide_10_new_primitives,
    slide_11_timeline_comparison,
]


def build_deck(theme: pc.Theme, output_path: str) -> None:
    prs = Presentation()
    prs.slide_width = __import__('pptx.util', fromlist=['Inches']).Inches(theme.SLIDE_W)
    prs.slide_height = __import__('pptx.util', fromlist=['Inches']).Inches(theme.SLIDE_H)
    pc.set_theme(theme)

    print(f"Building: {output_path}", flush=True)
    for idx, slide_fn in enumerate(SLIDES, start=1):
        print(f"  Rendering slide {idx}/{len(SLIDES)}: {slide_fn.__name__}", flush=True)
        slide_fn(prs)

    print("  Saving file...", flush=True)
    prs.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    out_dir = os.path.dirname(__file__)
    build_deck(pc.DarkTheme(),  os.path.join(out_dir, "demo_dark.pptx"))
    build_deck(pc.LightTheme(), os.path.join(out_dir, "demo_light.pptx"))
    print("Done.")
