---
name: reverse-slide-analysis
description: "Reverse-analyze existing PPTX outputs to recover reusable layout patterns, component opportunities, and UX rules that can be codified in this repository. Use when you want to infer how a slide was built and convert that into implementation guidance. Trigger phrases: reverse process, reverse engineer slide, analyze deck structure, infer component pattern."
argument-hint: "Provide the PPTX or exported images, target slides, and what you want extracted (layout grammar, component mapping, or token/style guidance)."
user-invocable: true
---

# Reverse Slide Analysis

## What This Skill Produces
- A decomposition of each target slide into semantic regions.
- Mapping from observed regions to existing components or new component candidates.
- Reusable design rules and implementation recommendations.

## When to Use
- You want to understand how a strong slide design should be rebuilt in code.
- You need to turn ad-hoc slide outcomes into reusable component patterns.
- You are diagnosing why a rendered slide feels visually inconsistent.
- You want to analyze arbitrary external PPTX files, not only repository-generated decks.

## Inputs to Gather First
- Target PPTX path and/or exported slide images (repository or external source).
- Slide numbers to analyze.
- Desired output type: design critique, component mapping, or implementation plan.

## Procedure
1. Inventory visual structure.
- Identify title zone, content blocks, charts/tables, annotations, and navigational cues.

2. Infer layout grammar.
- Estimate column rhythm, spacing scale, alignment anchors, and focal hierarchy.

3. Map to repository primitives.
- Connect observed structures to existing modules in `pptx_components/components/`.
- Flag gaps where no existing component cleanly matches.

4. Identify token and style behavior.
- Infer color/contrast intent, typography role changes, and density decisions.

5. Produce codification plan.
- Recommend whether to compose existing components or add a new reusable component.
- Define candidate API shape and usage pattern.

6. Validate against export QA.
- Propose one or two measurable checks to confirm rebuilt slides match intent.

## Output Structure
1. Slide decomposition summary.
2. Component mapping table (existing vs missing).
3. Reusable UX rules extracted.
4. Recommended implementation plan.
5. Validation checklist for regenerated output.

## Completion Checks
- Each analyzed slide has an explicit component mapping.
- At least one reusable rule is extracted per slide cluster.
- Recommendations are implementable in the current component architecture.
