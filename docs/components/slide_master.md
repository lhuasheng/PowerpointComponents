# Slide Master Demo

`MasterPresentation` lets you load an existing `.pptx` brand template as the slide
master and build every new slide on top of it — preserving logos, colour bars,
background imagery and footer chrome — while placing `pptx_components` data
components (charts, KPI grids, timelines, images) purely through the Python API.

!!! tip "New to `MasterPresentation`?"
    Read the [Slide Master Guide](guide_slide_master.md) for a step-by-step
    walkthrough before diving into the demo output below.

## How it works

```
Your brand .pptx template
        │
        ▼
MasterPresentation(template_path)   ← strips existing content slides
        │
        ├── add_slide("3_Title and Content", placeholders={0: "Slide Title"})
        │         └── MasterSlide  (fluent cursor editor)
        │                  ├── .add(component, h=…)
        │                  ├── .add_row(comp_a, comp_b, weights=[…], h=…)
        │                  ├── .set_cursor(y)
        │                  └── .skip(height)
        │
        └── .save("output.pptx")
```

All template assets (master, layouts, media, theme colours, footers) are preserved
exactly. Components are drawn on top as regular python-pptx shapes.

## Quickstart

```python
from pptx_components.master_builder import MasterPresentation, MasterSlide
import pptx_components as pc

prs = MasterPresentation("brand_template.pptx", clear_slides=True)

slide = prs.add_slide("3_Title and Content", placeholders={0: "My Title"})
slide.set_cursor(1.35).add(
    pc.BarChart(
        categories=["Q1", "Q2", "Q3", "Q4"],
        series={"Revenue ($M)": [4.2, 5.1, 6.8, 7.3]},
    ),
    h=3.2,
)

prs.save("output.pptx")
```

## MasterPresentation API

```python
MasterPresentation(
    template_path: str,          # path to .pptx brand template
    clear_slides: bool = True,   # strip existing content slides
    theme: Theme | None = None,  # optional component theme override
    margin: float = 0.4,         # default slide margin in inches
)
```

| Method | Returns | Description |
|---|---|---|
| `add_slide(layout, placeholders={})` | `MasterSlide` | Add a slide using a named or index-based layout |
| `save(path)` | `str` | Save the deck and return its resolved path |
| `layout_names` | `list[str]` | All available layout names in the template |

## MasterSlide API

| Method | Returns | Description |
|---|---|---|
| `set_placeholder(idx, text)` | `self` | Fill a layout text placeholder by index |
| `set_cursor(y)` | `self` | Move the vertical cursor to an absolute Y inch |
| `skip(height)` | `self` | Advance the cursor by `height` inches |
| `add(component, x?, y?, w?, h?)` | `self` | Place a component; advances cursor by `h` |
| `add_row(*components, h, weights?)` | `self` | Place components side-by-side; advances cursor by `h` |

## Full Demo — Pikachu Species Profile

The [slidemasterdemo script](https://github.com/lhuasheng/powerpointComponents/blob/main/examples/slidemasterdemo/slidemasterdemo.py)
builds a complete 9-slide deck using an A\*STAR brand template, with content
sourced from Wikipedia, pokemondb.net, and pokumon.com.

Run it:

```bash
python examples/slidemasterdemo/slidemasterdemo.py
# add --export to render slides to PNG
python examples/slidemasterdemo/slidemasterdemo.py --export
```

### Slide 1 — Cover

Brand template cover layout with Pikachu artwork placed via `ImageBlock`.

<div class="shot-grid">
  <figure>
    <img src="../../assets/examples/slidemasterdemo/slide_001.png"
         alt="Cover slide — Pikachu Species Profile" />
    <figcaption>Cover slide: template title placeholder + <code>ImageBlock</code> artwork overlay.</figcaption>
  </figure>
</div>

### Slide 2 — Intro with Image + List

`add_row()` places a Pikachu image and a bullet list side-by-side with weighted
column widths.

<div class="shot-grid">
  <figure>
    <img src="../../assets/examples/slidemasterdemo/slide_002.png"
         alt="Who is Pikachu — image and bullet list" />
    <figcaption><code>ImageBlock</code> + <code>ListBlock</code> in a weighted row.</figcaption>
  </figure>
</div>

### Slide 3 — Evolution Chain

Three images in one `add_row()`, then a second row of `TextCard` captions.

<div class="shot-grid">
  <figure>
    <img src="../../assets/examples/slidemasterdemo/slide_003.png"
         alt="Evolution chain — Pichu, Pikachu, Raichu" />
    <figcaption>Two stacked <code>add_row()</code> calls: images above, <code>TextCard</code> captions below.</figcaption>
  </figure>
</div>

### Slide 5 — KPI Grid

`KPIGrid` with four metric cards alongside an `ImageBlock` portrait.

<div class="shot-grid">
  <figure>
    <img src="../../assets/examples/slidemasterdemo/slide_005.png"
         alt="KPI grid with Pikachu image" />
    <figcaption><code>KPIGrid(cols=2)</code> + <code>ImageBlock</code> in a weighted row.</figcaption>
  </figure>
</div>

### Slide 6 — Line Chart

`LineChart` showing estimated Pokémon franchise revenue 1996 – 2023.

<div class="shot-grid">
  <figure>
    <img src="../../assets/examples/slidemasterdemo/slide_006.png"
         alt="Franchise revenue line chart" />
    <figcaption><code>LineChart</code> spanning the full content width.</figcaption>
  </figure>
</div>

### Slide 8 — Timeline

`Timeline` component with 10 milestones sourced from pokumon.com.

<div class="shot-grid">
  <figure>
    <img src="../../assets/examples/slidemasterdemo/slide_008.png"
         alt="Pikachu through the years — timeline" />
    <figcaption><code>Timeline</code> with done / current status markers.</figcaption>
  </figure>
</div>

## Full Source

The complete script is at
[`examples/slidemasterdemo/slidemasterdemo.py`](https://github.com/lhuasheng/powerpointComponents/blob/main/examples/slidemasterdemo/slidemasterdemo.py).
