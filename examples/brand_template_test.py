from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pptx import Presentation
from pptx.util import Inches

import pptx_components as pc
from pptx_components.export import export_slides
import demo as demo_slides


VARIANT_SPEC = {
    "dark": {
        "config": "brand_template_dark.json",
        "pptx": "brand_template_dark.pptx",
        "slides_dir": "brand_template_dark_slides",
    },
    "light": {
        "config": "brand_template_light.json",
        "pptx": "brand_template_light.pptx",
        "slides_dir": "brand_template_light_slides",
    },
}


def build_deck(output_pptx: str, config_path: str) -> None:
    theme = pc.BrandTheme.from_file(config_path)
    pc.set_theme(theme)

    prs = Presentation()
    prs.slide_width = Inches(theme.SLIDE_W)
    prs.slide_height = Inches(theme.SLIDE_H)

    for slide_fn in demo_slides.SLIDES:
        slide_fn(prs)

    prs.save(output_pptx)
    print(f"Saved presentation: {output_pptx}")


def maybe_export_slides(output_pptx: str, output_dir: str, export_enabled: bool) -> None:
    if not export_enabled:
        return

    try:
        exported = export_slides(output_pptx, output_dir=output_dir, dpi=150)
        print(f"Exported {len(exported)} slide PNG(s) to: {output_dir}")
    except RuntimeError as exc:
        print(f"Warning: slide export failed ({exc}).")
    except Exception as exc:
        print(f"Warning: unexpected export error ({exc}).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate brand-matched demo decks from brand JSON configs.")
    parser.add_argument(
        "--variant",
        choices=["dark", "light", "both"],
        default="both",
        help="Theme variant(s) to build.",
    )
    parser.add_argument("--export", action="store_true", help="Export slides to PNG.")
    args = parser.parse_args()

    root = os.path.dirname(__file__)
    variants = ["dark", "light"] if args.variant == "both" else [args.variant]

    for variant in variants:
        spec = VARIANT_SPEC[variant]
        config_path = os.path.join(root, spec["config"])
        output_pptx = os.path.join(root, spec["pptx"])
        output_slides_dir = os.path.join(root, spec["slides_dir"])

        build_deck(output_pptx=output_pptx, config_path=config_path)
        maybe_export_slides(
            output_pptx=output_pptx,
            output_dir=output_slides_dir,
            export_enabled=args.export,
        )


if __name__ == "__main__":
    main()
