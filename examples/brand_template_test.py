from __future__ import annotations

import argparse
from contextlib import contextmanager
import os
import sys
from typing import Iterator

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


class _TrackedSlideBuilderFactory:
    def __init__(self, validate_layout: bool):
        self._validate_layout = validate_layout
        self._original = demo_slides.pc.SlideBuilder
        self.builders: list[pc.SlideBuilder] = []

    def __call__(self, prs: Presentation, *args, **kwargs) -> pc.SlideBuilder:
        if self._validate_layout:
            kwargs.setdefault("validate", True)
        builder = self._original(prs, *args, **kwargs)
        self.builders.append(builder)
        return builder


@contextmanager
def _track_demo_slide_builders(validate_layout: bool) -> Iterator[_TrackedSlideBuilderFactory]:
    tracker = _TrackedSlideBuilderFactory(validate_layout)
    original = demo_slides.pc.SlideBuilder
    demo_slides.pc.SlideBuilder = tracker
    try:
        yield tracker
    finally:
        demo_slides.pc.SlideBuilder = original


def build_deck(
    output_pptx: str,
    config_path: str,
    *,
    validate_layout: bool = False,
    strict_layout: bool = False,
) -> list[pc.SlideBuilder]:
    theme = pc.BrandTheme.from_file(config_path)
    pc.set_theme(theme)

    prs = Presentation()
    prs.slide_width = Inches(theme.SLIDE_W)
    prs.slide_height = Inches(theme.SLIDE_H)

    with _track_demo_slide_builders(validate_layout) as tracker:
        for slide_fn in demo_slides.SLIDES:
            slide_fn(prs)

    builders = tracker.builders

    if validate_layout:
        report = pc.format_layout_validation_report(builders)
        print(report)
        if strict_layout:
            pc.raise_for_layout_issues(builders, report=report)

    prs.save(output_pptx)
    print(f"Saved presentation: {output_pptx}")
    return builders


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
    parser.add_argument(
        "--validate-layout",
        action="store_true",
        help="Enable overflow validation and print per-slide summaries before save/export.",
    )
    parser.add_argument(
        "--strict-layout",
        action="store_true",
        help="Enable layout validation and exit non-zero when any layout issues are found.",
    )
    parser.add_argument("--export", action="store_true", help="Export slides to PNG.")
    args = parser.parse_args()

    root = os.path.dirname(__file__)
    variants = ["dark", "light"] if args.variant == "both" else [args.variant]
    validate_layout = args.validate_layout or args.strict_layout

    try:
        for variant in variants:
            spec = VARIANT_SPEC[variant]
            config_path = os.path.join(root, spec["config"])
            output_pptx = os.path.join(root, spec["pptx"])
            output_slides_dir = os.path.join(root, spec["slides_dir"])

            build_deck(
                output_pptx=output_pptx,
                config_path=config_path,
                validate_layout=validate_layout,
                strict_layout=args.strict_layout,
            )
            maybe_export_slides(
                output_pptx=output_pptx,
                output_dir=output_slides_dir,
                export_enabled=args.export,
            )
    except pc.LayoutValidationError:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
