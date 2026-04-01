"""Quick test of AccordionBlock and FeatureGrid components."""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pptx import Presentation
from pptx.util import Inches

import pptx_components as pc


class DenseTheme(pc.BrandTheme):
    """Spacing-dense theme used to verify cascading min-height calculations."""
    MD = 0.1
    SM = 0.1


def test_theme_cascade_min_height_resolution():
    """min_height_for should respect the active scoped theme."""
    container = pc.Container(pc.TextCard("Title", "Body"))
    column = pc.Column(pc.TextCard("A", "B"), pc.TextCard("C", "D"))

    default_h = container.min_height_for(pc.DarkTheme())
    dense_h = container.min_height_for(DenseTheme())
    assert dense_h < default_h

    default_col_h = column.min_height_for(pc.DarkTheme())
    dense_col_h = column.min_height_for(DenseTheme())
    assert dense_col_h < default_col_h


def test_container_local_theme_patch_scope():
    """Container local theme patch should scope style + spacing to the section subtree."""
    base = pc.DarkTheme()
    patched = pc.apply_theme_patch(base, {"MD": 0.1, "SURFACE": (1, 2, 3)})

    regular = pc.Container(pc.TextCard("Title", "Body"))
    local = pc.Container(
        pc.TextCard("Title", "Body"),
        theme_patch={"MD": 0.1, "SURFACE": (1, 2, 3)},
    )

    assert patched.MD == 0.1
    assert patched.SURFACE == (1, 2, 3)
    assert local.min_height_for(base) < regular.min_height_for(base)


def test_new_components():
    """Validate new navigation components render without errors."""
    prs = Presentation()
    prs.slide_width = Inches(pc.DarkTheme().SLIDE_W)
    prs.slide_height = Inches(pc.DarkTheme().SLIDE_H)
    pc.set_theme(pc.DarkTheme())

    # Slide 1: TabsPanel & StepFlow
    print("Slide 1: TabsPanel & StepFlow...", flush=True)
    b = pc.SlideBuilder(prs)
    b.add(pc.SectionHeader("React Navigation Patterns"))
    b.skip(0.15)
    b.add(
        pc.TabsPanel(
            ["Overview", "Analytics", "Risks"],
            active_index=1,
            content="Analytics summary for Q2.",
            variant="line",
        ),
        h=1.9,
    )
    b.skip(0.2)
    b.add(
        pc.StepFlow(
            ["Step 1", "Step 2", "Step 3"],
            current=1,
            statuses=["done", "current", "pending"],
        ),
        h=1.3,
    )

    # Slide 2: AccordionBlock & FeatureGrid
    print("Slide 2: AccordionBlock & FeatureGrid...", flush=True)
    b = pc.SlideBuilder(prs)
    b.add(pc.SectionHeader("Content Organization"))
    b.skip(0.15)
    b.add(
        pc.AccordionBlock(
            [
                ("Question 1", "Answer 1 - detailed explanation here."),
                ("Question 2", "Answer 2 - more detailed explanation."),
                ("Question 3", "Answer 3 - final answer text."),
            ],
            expanded_index=0,
        ),
        h=2.0,
    )
    b.skip(0.2)
    b.add(
        pc.FeatureGrid(
            [
                ("⚡", "Feature 1", "First feature description"),
                ("🔒", "Feature 2", "Second feature description"),
                ("📊", "Feature 3", "Third feature description"),
            ],
            columns=3,
        ),
        h=1.8,
    )

    # Save
    output = os.path.join(os.path.dirname(__file__), "test_new_components.pptx")
    print(f"Saving: {output}", flush=True)
    prs.save(output)
    print("✓ All components rendered successfully!", flush=True)


if __name__ == "__main__":
    test_new_components()
