from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pptx import Presentation
from pptx.util import Inches

import pptx_components as pc


ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "situation_briefing")
OUTPUT_PPTX = os.path.join(os.path.dirname(__file__), "image_strip_overlay.pptx")

IMAGE_ITEMS = [
    (os.path.join(ASSET_DIR, "cna_singapore.jpg"), "Singapore Parliament", "SINGAPORE"),
    (os.path.join(ASSET_DIR, "cna_iran.jpg"), "Iran Position", "IRAN"),
    (os.path.join(ASSET_DIR, "cna_south_pars.jpg"), "South Pars Strike", "ENERGY"),
]


def build_example(output_path: str = OUTPUT_PPTX) -> str:
    theme = pc.LightTheme()

    prs = Presentation()
    prs.slide_width = Inches(theme.SLIDE_W)
    prs.slide_height = Inches(theme.SLIDE_H)

    builder = pc.SlideBuilder(prs, theme=theme)
    builder.add(
        pc.SectionHeader(
            "ImageStrip Overlay Caption",
            badge_text="IMAGE-NATIVE",
        ),
        h=0.55,
    )
    builder.skip(0.08)
    builder.add(
        pc.ImageStrip(
            IMAGE_ITEMS,
            gap=0.12,
            caption_position="overlay",
        ),
        h=2.1,
    )

    prs.save(output_path)
    return output_path


if __name__ == "__main__":
    saved = build_example()
    print(f"Saved: {saved}")