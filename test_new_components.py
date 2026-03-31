"""Quick test of AccordionBlock and FeatureGrid components."""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pptx import Presentation
from pptx.util import Inches

import pptx_components as pc


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
