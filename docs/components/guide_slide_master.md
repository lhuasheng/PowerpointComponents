# Slide Master Guide

This guide walks through every step of building a branded deck from an existing
`.pptx` template using `MasterPresentation`.

## What "slide master" means here

PowerPoint's slide master is the design layer that holds backgrounds, logos,
colour bars, fonts, and footer text. When you open a brand template in
`MasterPresentation`, that master is kept intact. The existing *content* slides
are stripped out, and every new slide you add inherits the brand chrome
automatically — you only need to write the content.

```
Your brand .pptx
      │
      │  MasterPresentation opens the file
      │  strips content slides
      │  keeps: master, layouts, media, theme, fonts
      │
      ▼
  prs.add_slide("Layout Name", placeholders={...})
      │
      ▼
  MasterSlide  ← cursor-based fluent editor
      ├── .set_cursor(y)          move the cursor to a Y position
      ├── .add(component, h=…)   place a component, advance cursor
      ├── .add_row(a, b, h=…)    place components side-by-side
      └── .skip(height)          add blank space
      │
      ▼
  prs.save("output.pptx")
```

---

## Step 1 — Inspect your template's layouts

Every brand template has named layout slides (e.g. `"3_Title and Content"`,
`"4_Section Divider"`, `"6_Back Cover"`). You need to know which layouts are
available and which placeholder indices they expose.

```python
from pptx_components.master_builder import MasterPresentation

prs = MasterPresentation("your_template.pptx", clear_slides=False)
print(prs.layout_names)
# ['Cover Option - Generic (Default)', '2_Title Only', '3_Title and Content', ...]
```

To see placeholder indices for a layout, inspect the python-pptx layout object
directly:

```python
from pptx import Presentation
from pptx.enum.text import PP_PLACEHOLDER

pptx = Presentation("your_template.pptx")
for layout in pptx.slide_layouts:
    print(f"\n--- {layout.name} ---")
    for ph in layout.placeholders:
        print(f"  idx={ph.placeholder_format.idx}  type={ph.placeholder_format.type}  name={ph.name}")
```

Typical placeholder indices:

| idx | Meaning |
|-----|---------|
| 0   | Title (or centre title on a cover) |
| 1   | Main content / body |
| 11–14 | Template-specific (date, source, subtitle, etc.) |

---

## Step 2 — Open the template

```python
from pptx_components.master_builder import MasterPresentation
from pptx_components.theme import LightTheme
import pptx_components as pc

prs = MasterPresentation(
    "your_template.pptx",
    clear_slides=True,   # remove existing content slides
    theme=LightTheme(),  # optional: override component colour theme
    margin=0.4,          # default margin in inches for add() calls
)
```

`clear_slides=True` (default) strips the template's demo content so you start
with a blank deck that still has all brand assets.

---

## Step 3 — Add a cover slide

Pass `placeholders` as a dict of `idx → text` to fill the layout's text fields.

```python
cover = prs.add_slide(
    "Cover Option - Generic (Default)",
    placeholders={
        0:  "My Presentation Title",
        11: "April 2026",
        13: "Department · Team",
    },
)
```

You can also overlay components on top of layout placeholders. Use `.add()` with
explicit `x`, `y`, `w`, `h` to position freely:

```python
cover.add(
    pc.ImageBlock("images/hero.png", mode="contain"),
    x=6.5, y=0.3, w=3.0, h=3.5,
)
```

---

## Step 4 — Add content slides

The cursor starts just below the slide top (at `y = 0`). Use `.set_cursor()` to
move past the title placeholder before placing content.

```python
slide = prs.add_slide("3_Title and Content", placeholders={0: "Q2 Summary"})

slide.set_cursor(1.35)   # move below the ~1.2-inch title bar
slide.add(
    pc.BarChart(
        categories=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        series={"Revenue ($M)": [4.2, 4.8, 5.1, 5.6, 6.0, 6.8]},
    ),
    h=3.2,
)
```

`add()` advances the cursor by `h` automatically, so subsequent calls stack
vertically.

---

## Step 5 — Place components side-by-side

`add_row()` splits the available width between components. Use `weights` to
control proportions (default is equal split).

```python
slide = prs.add_slide("3_Title and Content", placeholders={0: "At a Glance"})
slide.set_cursor(1.35)
slide.add_row(
    pc.ImageBlock("images/portrait.png", mode="contain"),
    pc.KPIGrid(
        [
            ("Revenue",  "$6.8M", "+18%", True),
            ("Users",    "24k",   "+7%",  True),
            ("NPS",      "72",    "+4",   True),
            ("Churn",    "3.2%",  "+0.4pp", False),
        ],
        cols=2,
    ),
    weights=[0.30, 0.70],   # 30 % image, 70 % KPIs
    h=3.0,
)
```

---

## Step 6 — Add a section divider and back cover

Layouts that have no content placeholders just use the brand chrome.

```python
prs.add_slide("4_Section Divider", placeholders={0: "Part 2 — Financials"})

# ... more slides ...

prs.add_slide("6_Back Cover")   # no placeholders needed
```

---

## Step 7 — Save and export

```python
prs.save("output.pptx")
```

Export to PNG (Windows, requires PowerPoint):

```python
from pptx_components.export import export_slides

paths = export_slides("output.pptx", "output_slides/", dpi=150)
print(f"Exported {len(paths)} slides")
```

Or from the command line:

```bash
python pptx_components/export.py output.pptx --dpi 150
```

---

## Step 8 — Sub-class the theme for your template dimensions

Most brand templates are not the python-pptx default size (10 × 7.5 in). Check
your template's slide dimensions and override the theme constants:

```python
from pptx_components.theme import LightTheme

class BrandTheme(LightTheme):
    SLIDE_W: float = 10.0    # inches — match your template
    SLIDE_H: float = 5.625
    MARGIN:  float = 0.4
```

Pass this to `MasterPresentation`:

```python
prs = MasterPresentation("template.pptx", theme=BrandTheme())
```

---

## Complete minimal example

```python
from pptx_components.master_builder import MasterPresentation
from pptx_components.theme import LightTheme
import pptx_components as pc


class BrandTheme(LightTheme):
    SLIDE_W, SLIDE_H, MARGIN = 10.0, 5.625, 0.4


prs = MasterPresentation("brand_template.pptx", theme=BrandTheme())

# Cover
cover = prs.add_slide("Cover Option - Generic (Default)", placeholders={
    0: "Quarterly Review", 11: "April 2026",
})
cover.add(pc.ImageBlock("logo.png", mode="contain"), x=7.0, y=0.5, w=2.5, h=2.5)

# Content slide
s = prs.add_slide("3_Title and Content", placeholders={0: "Revenue Trend"})
s.set_cursor(1.35).add(
    pc.LineChart(
        categories=["Q1", "Q2", "Q3", "Q4"],
        series={"Revenue ($M)": [4.2, 5.1, 6.8, 7.3]},
    ),
    h=3.2,
)

# Back cover
prs.add_slide("6_Back Cover")

prs.save("output.pptx")
```

---

## Tips and caveats

- **Layout name spelling** — names must match exactly (case-sensitive). Use
  `prs.layout_names` to list them.
- **Cursor position** — always call `.set_cursor(y)` before adding content on
  layouts that have a title placeholder, otherwise components will overlap the title.
- **Placeholder idx vs text** — `set_placeholder(idx, text)` and the
  `placeholders` dict both fill layout text boxes. Components are rendered as
  shapes *on top*, not inside a placeholder.
- **Image downloads** — if images need fetching at runtime, cache them locally
  first (see `_ensure_image()` in `slidemasterdemo.py`).
- **Locked output file** — if `output.pptx` is open in PowerPoint, `.save()` will
  fail. Close it first or save to a different filename.

---

## See also

- [Slide Master Demo](slide_master.md) — the full 9-slide Pikachu example with
  annotated screenshots
- [Component Reference](REFERENCE.md) — complete component API catalogue
- [Composition Patterns](PATTERNS.md) — layout and spacing patterns
