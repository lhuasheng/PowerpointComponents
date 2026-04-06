from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from pptx_components.slide_builder import LayoutIssue, SlideBuilder


@dataclass(frozen=True)
class LayoutValidationError(RuntimeError):
    """Raised when layout validation is configured to fail on collected issues."""

    report: str
    issues: tuple[LayoutIssue, ...]

    def __post_init__(self) -> None:
        RuntimeError.__init__(self, self.report)


def collect_layout_issues(builders: Iterable[SlideBuilder]) -> list[LayoutIssue]:
    """Collect layout issues from one or more SlideBuilder instances."""
    issues: list[LayoutIssue] = []
    for builder in builders:
        issues.extend(builder.layout_issues)
    return issues


def format_layout_validation_report(builders: Iterable[SlideBuilder]) -> str:
    """Return a plain-text, actionable overflow summary grouped by slide."""
    builder_list = list(builders)
    issues = collect_layout_issues(builder_list)
    total_slides = len(builder_list)

    if not issues:
        return (
            "Layout validation summary:\n"
            f"- Checked {total_slides} slide(s); no overflow issues found."
        )

    by_slide: dict[int, list[LayoutIssue]] = defaultdict(list)
    warning_count = 0
    error_count = 0

    for issue in issues:
        by_slide[issue.slide_number].append(issue)
        if issue.severity == "error":
            error_count += 1
        else:
            warning_count += 1

    lines = [
        "Layout validation summary:",
        (
            f"- Checked {total_slides} slide(s); found {len(issues)} issue(s) "
            f"({warning_count} warning(s), {error_count} error(s))."
        ),
    ]

    for slide_number in sorted(by_slide):
        slide_issues = by_slide[slide_number]
        lines.append(f"- Slide {slide_number}: {len(slide_issues)} issue(s)")
        for issue in slide_issues:
            lines.append(
                (
                    f"  [{issue.severity.upper()}] {issue.component_name}: overflow {issue.overflow:.2f}\" "
                    f"(y={issue.y:.2f}\", h={issue.h:.2f}\", safe_bottom={issue.safe_bottom:.2f}\")"
                )
            )
            lines.append(
                "  Action: reduce component height, move cursor up, split content, "
                "or pass allow_overflow=True for intentional overlays."
            )

    return "\n".join(lines)


def raise_for_layout_issues(
    builders: Iterable[SlideBuilder],
    *,
    report: str | None = None,
) -> str:
    """Raise LayoutValidationError when collected layout issues are present."""
    builder_list = list(builders)
    issues = collect_layout_issues(builder_list)
    final_report = report or format_layout_validation_report(builder_list)

    if issues:
        raise LayoutValidationError(final_report, tuple(issues))

    return final_report
