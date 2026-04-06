from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pptx import Presentation
from pptx.util import Inches

import pptx_components as pc
from pptx_components.export import export_slides


SOURCE_URLS = [
    "https://www.channelnewsasia.com/singapore/parliament-order-paper-ministerial-statements-middle-east-war-impact-6038446",
    "https://www.channelnewsasia.com/world/iran-rejects-ceasefire-proposal-war-us-trump-deadline-6039316",
    "https://www.channelnewsasia.com/world/israel-strikes-south-pars-petrochemical-plant-iran-war-6039021",
]

SOURCE_IMAGE_PATHS = [
    os.path.join(os.path.dirname(__file__), "assets", "situation_briefing", "cna_singapore.jpg"),
    os.path.join(os.path.dirname(__file__), "assets", "situation_briefing", "cna_iran.jpg"),
    os.path.join(os.path.dirname(__file__), "assets", "situation_briefing", "cna_south_pars.jpg"),
]


def _cna_inspired_theme() -> pc.BrandTheme:
    # CNA-style editorial direction: neutral base + strong red alert accent.
    return pc.BrandTheme(
        bg=(246, 247, 249),
        surface=(255, 255, 255),
        surface_alt=(241, 243, 246),
        text_primary=(21, 22, 26),
        text_secondary=(54, 58, 66),
        text_muted=(99, 106, 118),
        accent=(200, 16, 46),
        accent_2=(42, 97, 164),
        accent_3=(120, 72, 37),
        accent_soft=(246, 205, 212),
        positive=(28, 126, 69),
        negative=(185, 42, 57),
        callout={
            "info": ((255, 239, 242), (128, 13, 31)),
            "warning": ((255, 243, 216), (126, 83, 29)),
            "success": ((227, 244, 232), (26, 105, 56)),
            "error": ((253, 228, 231), (132, 24, 40)),
        },
    )


def _add_newsroom_strap(slide, theme: pc.Theme) -> None:
    pc.NewsroomStrap("WORLD DESK | DEVELOPING", align="center").render(
        slide,
        x=9.42,
        y=0.19,
        width=3.4,
        height=0.34,
        theme=theme,
    )


def _add_headline(slide, theme: pc.Theme) -> None:
    pc.EditorialHeadline(
        "Situation Briefing: Middle East Conflict",
        byline="CNA synthesis for policy and enterprise leadership",
        dateline="06 Apr 2026",
        density="default",
    ).render(
        slide,
        x=0.5,
        y=0.57,
        width=8.8,
        height=0.54,
        theme=theme,
    )


def _add_image_strip(slide, theme: pc.Theme) -> None:
    strip_items = [
        (SOURCE_IMAGE_PATHS[0], "Singapore Parliament", "SINGAPORE"),
        (SOURCE_IMAGE_PATHS[1], "Iran Position", "IRAN"),
        (SOURCE_IMAGE_PATHS[2], "South Pars Strike", "ENERGY"),
    ]
    pc.ImageStrip(strip_items, gap=0.1, caption_position="below").render(
        slide,
        x=0.5,
        y=1.24,
        width=12.33,
        height=1.3,
        theme=theme,
    )


def _add_sources_footer(slide, theme: pc.Theme) -> None:
    pc.AttributionFooter(
        "Source: CNA reporting, 6 Apr 2026 | Three linked articles used for facts and imagery",
        align="left",
    ).render(
        slide,
        x=0.52,
        y=7.2,
        width=12.3,
        height=0.24,
        theme=theme,
    )


def _add_detail_photo_card(
    slide,
    theme: pc.Theme,
    image_path: str,
    caption: str | None = None,
    badge_text: str | None = None,
) -> None:
    # Keep the photo treatment fixed in the top-right to avoid manual per-slide choreography.
    pc.ImageCard(
        image_path=image_path,
        caption=caption,
        badge_text=badge_text,
        mode="stretch",
    ).render(
        slide,
        x=9.5,
        y=0.6,
        width=3.5,
        height=1.05,
        theme=theme,
    )


def build_situation_briefing_slide(prs: Presentation, validate_layout: bool = False) -> pc.SlideBuilder:
    b = pc.SlideBuilder(prs, validate=validate_layout)
    theme = pc.get_theme()

    _add_newsroom_strap(b.slide, theme)
    _add_headline(b.slide, theme)
    _add_image_strip(b.slide, theme)

    b.set_cursor(2.4)

    b.add(
        pc.SectionHeader(
            "Operational Timeline",
            badge_text="AS OF 23:59 SGT",
            style_overrides={
                "title_size": 16,
                "caption_size": 8,
                "font_name": "Arial",
                "title_bold": True,
            },
        ),
        h=0.5,
    )

    b.add_row(
        pc.Timeline(
            [
                ("Mar", "Earlier strike on South Pars triggered wider energy attacks", "done"),
                ("Sat", "Mahshahr petrochemical zone hit; reported casualties", "risk"),
                ("Mon", "South Pars struck; disruptions in petrochemical operations", "current"),
                ("Mon", "Iran rejects ceasefire; seeks permanent war end", "current"),
                ("Tue", "US deadline linked to Hormuz transit discussions", "upcoming"),
            ],
            title="Conflict Escalation and Negotiation Signals",
        ),
        pc.TextCard(
            title="What Matters Now",
            style="muted",
            body=(
                "Primary risk channel is energy and maritime transit uncertainty. "
                "A 45-day ceasefire concept is under discussion but not approved. "
                "Attacks on petrochemical assets raise supply and confidence downside risk."
            ),
            style_overrides={
                "title_size": 12,
                "body_size": 10,
                "font_name": "Arial",
                "title_bold": True,
            },
        ),
        h=1.6,
        weights=[1.9, 1.1],
    )

    b.add(pc.SectionHeader("Singapore Impact Watchlist", badge_text="PARLIAMENT FOCUS"), h=0.5)

    b.add_row(
        pc.ListBlock(
            [
                "Government flagged severe consequences if Middle East supply routes stay constrained.",
                "Parliament agenda includes fuel and electricity pressure plus LNG resilience.",
                "More than 70 oral and written questions were filed on conflict fallout.",
            ],
            style="bullet",
            title="Policy and Domestic Exposure",
        ),
        pc.ListBlock(
            [
                "Track wholesale fuel and electricity trends weekly.",
                "Prepare continuity plans for prolonged higher shipping and energy costs.",
                "Pre-brief customer teams on inflation and lead-time scenarios.",
            ],
            style="number",
            title="Recommended Executive Actions (Next 72 Hours)",
            style_overrides={
                "title_size": 13,
                "body_size": 10,
                "font_name": "Arial",
            },
        ),
        h=1.4,
        weights=[1.05, 1.05],
    )

    _add_sources_footer(b.slide, theme)
    return b


def build_singapore_impact_slide(prs: Presentation, validate_layout: bool = False) -> pc.SlideBuilder:
    b = pc.SlideBuilder(prs, validate=validate_layout)
    theme = pc.get_theme()

    _add_newsroom_strap(b.slide, theme)
    _add_detail_photo_card(
        b.slide,
        theme,
        SOURCE_IMAGE_PATHS[0],
    )

    b.add(
        pc.SectionHeader(
            "Singapore Impact: Parliamentary Focus",
            badge_text="DOMESTIC EXPOSURE",
        ),
        h=0.55,
    )

    b.add(
        pc.TextCard(
            title="Energy & Supply Chain Risk",
            style="default",
            body=(
                "PM Lawrence Wong warned of severe consequences if Middle Eastern energy sources and supply routes "
                "remain constrained. Singapore depends on LNG imports and global shipping routes through the Persian Gulf. "
                "A sustained disruption would raise electricity, fuel, and logistics costs across all sectors."
            ),
        ),
        h=1.1,
    )

    b.add_row(
        pc.ListBlock(
            [
                "Fuel and electricity price escalation (6–12 month outlook)",
                "LNG supply resilience and alternative sourcing",
                "Shipping and logistics cost pass-through",
                "Broader supply shocks (telecom, semiconductors, food)",
            ],
            style="bullet",
            title="Parliament Agenda Items (70+ Questions Filed)",
        ),
        pc.ListBlock(
            [
                "Ministerial committee convened (Shanmugam chairs)",
                "Coordinating energy, supply, security, diplomacy",
                "Contingency plans for prolonged disruptions",
            ],
            style="check",
            checked=[0, 1, 2],
            title="Government Response",
        ),
        h=1.75,
        weights=[1.1, 0.95],
    )

    _add_sources_footer(b.slide, theme)
    return b


def build_escalation_slide(prs: Presentation, validate_layout: bool = False) -> pc.SlideBuilder:
    b = pc.SlideBuilder(prs, validate=validate_layout)
    theme = pc.get_theme()

    _add_newsroom_strap(b.slide, theme)
    _add_detail_photo_card(
        b.slide,
        theme,
        SOURCE_IMAGE_PATHS[2],
    )

    b.add(
        pc.SectionHeader(
            "Iran-Israel Escalation: Strategic Infrastructure Targeted",
            badge_text="CEASEFIRE STALLED",
        ),
        h=0.55,
    )

    b.add(
        pc.Timeline(
            [
                ("Mar", "Initial South Pars and Mahshahr strikes", "done"),
                ("Sat", "Mahshahr secondary strike (5 reported killed)", "risk"),
                ("Mon", "South Pars hit again; 85% of petrochemical exports offline", "current"),
                ("Mon", "Iran's 10-clause response: permanent war end, not ceasefire", "current"),
                ("Tue", "Trump 8pm EDT deadline: Hormuz transit deal or escalation", "upcoming"),
            ],
        ),
        h=1.5,
    )

    b.add_row(
        pc.TextCard(
            title="Iran's Negotiating Position",
            style="muted",
            body=(
                "Iran rejected temporary ceasefire under Trump pressure. "
                "Diplomatic response emphasizes permanent war end, regional conflict resolution, sanctions relief, "
                "and reconstruction guarantees—not short-term transit deals."
            ),
        ),
        pc.TextCard(
            title="Israel's Strategic Targeting",
            style="accent",
            body=(
                "~70% of Iran's steel capacity destroyed; petrochemical complex offline. "
                "Goal: severely constrain Iran's military-industrial capacity and revenue. "
                "Messaging: war is ongoing as negotiations continue."
            ),
        ),
        h=1.3,
        weights=[1.0, 1.0],
    )

    b.add(
        pc.CalloutBox(
            "South Pars holds 51 trillion cubic metres of gas (world's largest field). "
            "Damage to supply infrastructure affects global LNG pricing.",
            style="warning",
        ),
        h=0.65,
    )

    _add_sources_footer(b.slide, theme)
    return b


def build_executive_brief_slide(prs: Presentation, validate_layout: bool = False) -> pc.SlideBuilder:
    b = pc.SlideBuilder(prs, validate=validate_layout)
    theme = pc.get_theme()

    _add_newsroom_strap(b.slide, theme)
    pc.EditorialHeadline(
        "Executive Brief: 72-Hour Outlook & Decisions",
        density="dense",
    ).render(
        b.slide,
        x=0.5,
        y=0.57,
        width=8.8,
        height=0.34,
        theme=theme,
    )

    b.set_cursor(1.15)

    b.add(
        pc.SectionHeader("Status & Risk Assessment", badge_text="MODERATE CONFIDENCE"),
        h=0.5,
    )

    b.add_row(
        pc.ListBlock(
            [
                "Ceasefire talks stalled; Iran rejects temporary measures.",
                "Trump's 8pm EDT Tuesday deadline likely to be extended (historical pattern).",
                "Petrochemical and steel targeting signals Israel prioritizes asymmetric economic damage.",
                "Global LNG markets show modest volatility; Hormuz transit remains open.",
            ],
            style="bullet",
            title="Current Facts",
        ),
        pc.ListBlock(
            [
                "HIGH: Prolonged supply-route uncertainty pushes energy costs up 5–15% Q2–Q3.",
                "MEDIUM: Regional escalation (Yemen, Iraq, Gulf partners) could widen conflict.",
                "MEDIUM: Ceasefire breakthrough allows gradual cost normalization.",
            ],
            style="bullet",
            title="Key Scenarios",
        ),
        h=1.28,
        weights=[1.05, 0.95],
    )

    b.add(
        pc.SectionHeader("Decision Points & Next Steps", badge_text="ENTERPRISE ACTION"),
        h=0.5,
    )

    b.add(
        pc.ListBlock(
            [
                "Activate energy/logistics cost pass-through conversations with finance and procurement teams.",
                "Prepare 2–3 contingency supply chain scenarios (extended disruption, regional spread, normalization).",
                "Schedule a briefing with board or C-suite advisors by end of week.",
                "Monitor Singapore government policy updates on price controls or subsidy announcements.",
            ],
            style="number",
            title="Immediate Actions (Next 72 Hours)",
        ),
        h=1.58,
    )

    b.add(
        pc.CalloutBox(
            "Next briefing recommended: Tuesday evening (post-Trump announcement) and Friday (weekly risk review).",
            style="info",
        ),
        h=0.5,
    )

    _add_sources_footer(b.slide, theme)
    return b


def build_deck(
    output_pptx: str,
    validate_layout: bool = False,
    strict_layout: bool = False,
) -> list[pc.SlideBuilder]:
    theme = _cna_inspired_theme()
    pc.set_theme(theme)

    prs = Presentation()
    prs.slide_width = Inches(theme.SLIDE_W)
    prs.slide_height = Inches(theme.SLIDE_H)

    builders = [
        build_situation_briefing_slide(prs, validate_layout=validate_layout),
        build_singapore_impact_slide(prs, validate_layout=validate_layout),
        build_escalation_slide(prs, validate_layout=validate_layout),
        build_executive_brief_slide(prs, validate_layout=validate_layout),
    ]

    if validate_layout:
        report = pc.format_layout_validation_report(builders)
        print(report)
        if strict_layout:
            pc.raise_for_layout_issues(builders, report=report)

    prs.save(output_pptx)
    print(f"Saved presentation: {output_pptx}")
    return builders


def maybe_export(output_pptx: str, output_dir: str, export_enabled: bool) -> None:
    if not export_enabled:
        return

    try:
        exported = export_slides(output_pptx, output_dir=output_dir, dpi=170)
        print(f"Exported {len(exported)} slide PNG(s) to: {output_dir}")
    except RuntimeError as exc:
        print(f"Warning: slide export failed ({exc}).")
    except Exception as exc:
        print(f"Warning: unexpected export error ({exc}).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a CNA-style situation briefing slide.")
    parser.add_argument(
        "--output",
        default=os.path.join(os.path.dirname(__file__), "situation_briefing.pptx"),
        help="Output PPTX path.",
    )
    parser.add_argument(
        "--slides-dir",
        default=os.path.join(os.path.dirname(__file__), "situation_briefing_slides"),
        help="Output directory for exported slide PNGs.",
    )
    parser.add_argument(
        "--validate-layout",
        action="store_true",
        help="Enable overflow validation and print per-slide summary before save/export.",
    )
    parser.add_argument(
        "--strict-layout",
        action="store_true",
        help="Enable layout validation and exit non-zero when any layout issues are found.",
    )
    parser.add_argument("--export", action="store_true", help="Export slides to PNG.")
    args = parser.parse_args()

    validate_layout = args.validate_layout or args.strict_layout

    try:
        build_deck(
            args.output,
            validate_layout=validate_layout,
            strict_layout=args.strict_layout,
        )
    except pc.LayoutValidationError:
        raise SystemExit(1)

    maybe_export(args.output, args.slides_dir, args.export)

    print("Source links used:")
    for url in SOURCE_URLS:
        print(f"- {url}")


if __name__ == "__main__":
    main()
