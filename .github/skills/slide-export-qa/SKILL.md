---
name: slide-export-qa
description: "Export generated slides to images and run structured visual QA checks across themes and slide states. Use when you need evidence-based review of layout, contrast, spacing, clipping, hierarchy, and consistency before accepting PPTX output. Trigger phrases: export qa, visual regression, review slide output, inspect png exports."
argument-hint: "Provide the source PPTX or demo command, slides to inspect, theme expectations (dark/light), and pass criteria."
user-invocable: true
---

# Slide Export QA

## What This Skill Produces
- Exported slide images for review.
- A structured pass/fail QA checklist result.
- Concrete issue notes tied to slide numbers and component patterns.

## When to Use
- You generated or modified slides and need visual verification.
- A component change may affect readability or spacing.
- You need dark/light parity checks before finalizing output.

## Inputs to Gather First
- Source PPTX path or command that generates the PPTX.
- Which slides to export (all vs subset).
- Theme expectations (dark, light, or both).
- Acceptance criteria (for example, no clipping, no overlap, contrast preserved).

## Procedure
1. Prepare output folders.
- Create deterministic output folders for the current run.

2. Generate or locate PPTX.
- Run the relevant demo/build command or use the existing PPTX.

3. Export slides to images.
- Use `pptx_components/export.py` workflow to produce PNG outputs.

4. Run visual checks.
- Validate text clipping, safe margins, visual hierarchy, contrast, and alignment.
- Compare dark/light variants only when both variants are explicitly requested.

5. Report findings.
- Mark each reviewed slide as pass/fail.
- Map each issue to probable component, theme token, or layout source.

6. Feed back improvements.
- Propose minimal edits to components/layout/theme and rerun export if needed.

## QA Checklist
- No text clipping at intended sizes.
- No component overlap or off-slide placement.
- Contrast supports readability for headings, body text, and annotations.
- Spacing rhythm is consistent across adjacent modules.
- Visual emphasis follows intended information hierarchy.
- Dark/light variants keep equivalent readability and hierarchy when both variants are explicitly requested.

## Completion Checks
- Exported artifacts exist for the requested slides.
- Pass/fail result is explicit for each reviewed slide.
- Any failures include actionable fix suggestions.
