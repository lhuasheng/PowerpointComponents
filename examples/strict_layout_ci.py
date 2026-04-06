from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import demo
import pptx_components as pc
import situation_briefing


@dataclass
class ValidationResult:
    name: str
    ok: bool
    detail: str


def _validate_situation_briefing(output_dir: Path) -> None:
    situation_briefing.build_deck(
        str(output_dir / "situation_briefing_strict_ci.pptx"),
        validate_layout=True,
        strict_layout=True,
    )


def _validate_demo_quick(output_dir: Path) -> None:
    demo.build_quick_test_deck(
        str(output_dir / "demo_quick_strict_ci.pptx"),
        validate_layout=True,
        strict_layout=True,
    )


def _validate_brand_variant(output_dir: Path, variant_name: str, config_name: str) -> None:
    config_path = Path(__file__).with_name(config_name)
    theme = pc.BrandTheme.from_file(str(config_path))
    demo.build_quick_test_deck(
        str(output_dir / f"brand_template_{variant_name}_strict_ci.pptx"),
        theme=theme,
        validate_layout=True,
        strict_layout=True,
    )


def _run_case(name: str, callback) -> ValidationResult:
    try:
        callback()
    except Exception as exc:
        print(f"[FAIL] {name}")
        print(f"  {exc}")
        return ValidationResult(name=name, ok=False, detail=str(exc))

    print(f"[PASS] {name}")
    return ValidationResult(name=name, ok=True, detail="ok")


def main() -> None:
    cases: list[tuple[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="pptx_strict_layout_") as temp_dir:
        output_dir = Path(temp_dir)
        cases = [
            (
                "situation_briefing",
                lambda: _validate_situation_briefing(output_dir),
            ),
            (
                "demo_quick",
                lambda: _validate_demo_quick(output_dir),
            ),
            (
                "brand_template_dark",
                lambda: _validate_brand_variant(output_dir, "dark", "brand_template_dark.json"),
            ),
            (
                "brand_template_light",
                lambda: _validate_brand_variant(output_dir, "light", "brand_template_light.json"),
            ),
        ]

        results = [_run_case(name, callback) for name, callback in cases]

    passed = sum(1 for result in results if result.ok)
    failed = [result for result in results if not result.ok]

    print("Strict layout validation summary:")
    print(f"- Passed {passed}/{len(results)} validation target(s).")

    if failed:
        for result in failed:
            print(f"- FAIL {result.name}: {result.detail}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()