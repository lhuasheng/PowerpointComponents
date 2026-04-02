"""Pikachu — Slide Master Demo
===================================
Builds a complete deck about Pikachu using:
  • A real .pptx brand template as the slide master (logos, colour bars, fonts)
  • pptx_components for data-driven charts, KPIs and timelines
  • Downloaded artwork images (Pichu / Pikachu / Raichu) placed via ImageBlock
  • Content sourced from Wikipedia, pokemondb.net and pokumon.com

Images are fetched on first run from pokemondb.net and cached in images/.

Run from the repo root::

    python examples/slidemasterdemo/slidemasterdemo.py

Add --export to also render slides to PNG::

    python examples/slidemasterdemo/slidemasterdemo.py --export
"""
from __future__ import annotations

import os
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pptx_components as pc
from pptx_components.master_builder import MasterPresentation
from pptx_components.theme import LightTheme

# ── Paths ──────────────────────────────────────────────────────────────────
HERE     = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "6-hhp-iaf-pp-mtr-template_oct_2021.pptx")
OUTPUT   = os.path.join(HERE, "output.pptx")
OUTPUT_DIR = os.path.join(HERE, "output_slides")
IMAGES   = os.path.join(HERE, "images")

# ── Image download helper ──────────────────────────────────────────────────

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def _ensure_image(filename: str, url: str) -> str:
    """Download *url* to images/<filename> if not already cached. Returns path."""
    os.makedirs(IMAGES, exist_ok=True)
    path = os.path.join(IMAGES, filename)
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req) as r, open(path, "wb") as f:
            f.write(r.read())
        print(f"  ↓ downloaded {filename}")
    return path


def _fetch_images() -> dict[str, str]:
    base = "https://img.pokemondb.net/artwork/large"
    return {
        "pichu":   _ensure_image("pichu.jpg",   f"{base}/pichu.jpg"),
        "pikachu": _ensure_image("pikachu.jpg", f"{base}/pikachu.jpg"),
        "raichu":  _ensure_image("raichu.jpg",  f"{base}/raichu.jpg"),
    }


# ── Custom theme ────────────────────────────────────────────────────────────

class TemplateTheme(LightTheme):
    """LightTheme tuned for the 10 × 5.625-inch brand template canvas."""
    SLIDE_W: float  = 10.0
    SLIDE_H: float  = 5.625
    MARGIN:  float  = 0.4
    DISPLAY: int    = 24
    HEADING: int    = 18
    SUBHEADING: int = 14
    BODY:    int    = 11
    CAPTION: int    = 9


# ── Slide data — all from Wikipedia / pokemondb / pokumon.com ──────────────

# Base stats (pokemondb.net/pokedex/pikachu)
BASE_STATS = {
    "HP":      35,
    "Attack":  55,
    "Defense": 40,
    "Sp. Atk": 50,
    "Sp. Def": 50,
    "Speed":   90,
}

# KPI cards drawn from Wikipedia critical-reception section
KPI_DATA = [
    ("Pokédex No.",   "#025",    "Gen I",   True),
    ("Base Stats",    "320",     "total",   True),   # sum of base stats
    ("Speed Tier",    "90",      "base",    True),
    ("Catch Rate",    "190",     "/ 255",   True),
]

# Quarterly franchise revenue proxies ($B) — illustrative trend from Wikipedia
REVENUE_LABELS = ["1996", "1999", "2003", "2010", "2016", "2021", "2023"]
REVENUE_DATA = {
    "Est. Franchise Revenue ($B)": [0.1, 5.0, 6.5, 9.0, 15.0, 17.0, 21.0],
}

# Key facts list (Wikipedia)
FACTS = [
    'First introduced in Pokémon Red & Blue (1996); created by Atsuko Nishida.',
    'Name combines "pika" (sparkle) and "chū" (mouse squeak) in Japanese.',
    'Evolved from Pichu (high Friendship) → Pikachu → Raichu (Thunder Stone).',
    'Voiced by Ikue Ōtani in virtually every appearance since 1997.',
    'Ranked 2nd "Person of the Year" by TIME magazine in 1999.',
    'Appeared in all 5 Super Smash Bros. games as a playable fighter.',
    '"Surprised Pikachu" became one of the internet\'s most widely used memes.',
    'Gigantamax form (Sword & Shield) revisits the original "Fat Pikachu" design.',
]

# Timeline sourced from pokumon.com
PIKACHU_TIMELINE = [
    ("Feb 1996",  "Pokémon Red & Green launch in Japan",        "done"),
    ("Apr 1997",  "Anime series premieres; Pikachu stars",      "done"),
    ("Sep 1998",  "Pokémon Red & Blue launch in North America", "done"),
    ("Jul 1998",  "First Pokémon movie (Mewtwo Strikes Back)",  "done"),
    ("Nov 1998",  "Pokémon Yellow — Pikachu walks with you",    "done"),
    ("Nov 1999",  "Generation II (Gold & Silver) launches",     "done"),
    ("Jul 2016",  "Pokémon GO global launch",                   "done"),
    ("May 2019",  "Detective Pikachu live-action film",         "done"),
    ("Nov 2019",  "Pokémon Sword & Shield — Gigantamax form",   "done"),
    ("Apr 2026",  "Still the world's most recognised Pokémon",  "current"),
]


# ── Build deck ──────────────────────────────────────────────────────────────

def build_deck(export: bool = False) -> str:
    theme = TemplateTheme()

    print("Fetching images …")
    imgs = _fetch_images()

    prs = MasterPresentation(TEMPLATE, clear_slides=True, theme=theme, margin=0.4)

    # ── Slide 1 — Cover ───────────────────────────────────────────────────
    # Pikachu artwork placed in the right-hand white panel alongside the title
    cover = prs.add_slide("Cover Option - Generic (Default)", placeholders={
        0:  "Pikachu — Species Profile",
        11: "April 2026",
        13: "Source: Wikipedia · pokemondb.net · pokumon.com",
    })
    # Place the Pikachu artwork floating on top of the layout at top-right
    cover.add(
        pc.ImageBlock(imgs["pikachu"], mode="contain"),
        x=6.8, y=0.2, w=2.8, h=3.6,
    )

    # ── Slide 2 — Who is Pikachu? (image + facts) ─────────────────────────
    intro = prs.add_slide("3_Title and Content", placeholders={
        0: "Who is Pikachu?",
    })
    (
        intro
        .set_cursor(1.35)
        .add_row(
            pc.ImageBlock(imgs["pikachu"], mode="contain"),
            pc.ListBlock(FACTS[:4]),
            weights=[0.35, 0.65],
            h=3.2,
        )
    )

    # ── Slide 3 — Evolution chain (3 images in a row) ─────────────────────
    evo = prs.add_slide("3_Title and Content", placeholders={
        0: "Evolution Chain",
    })
    evo.set_cursor(1.3)
    # Three images side by side
    evo.add_row(
        pc.ImageBlock(imgs["pichu"],   mode="contain"),
        pc.ImageBlock(imgs["pikachu"], mode="contain"),
        pc.ImageBlock(imgs["raichu"],  mode="contain"),
        h=2.4,
    )
    evo.skip(0.1)
    # Captions row
    evo.add_row(
        pc.TextCard("Baby Electric-type · Evolves via high Friendship", title="Pichu"),
        pc.TextCard("Mouse Pokémon #025 · 0.4 m · 6.0 kg · Electric",  title="Pikachu"),
        pc.TextCard("Mouse Pokémon #026 · Evolves with Thunder Stone",  title="Raichu"),
        h=0.85,
    )

    # ── Slide 4 — Base stats bar chart ────────────────────────────────────
    stats_slide = prs.add_slide("3_Title and Content", placeholders={
        0: "Base Stats  (pokemondb.net)",
    })
    # Horizontal bar chart — one series per stat
    stats_slide.set_cursor(1.35).add(
        pc.BarChart(
            categories=list(BASE_STATS.keys()),
            series={"Base Value": list(BASE_STATS.values())},
            mode="bar_clustered",
        ),
        h=3.2,
    )

    # ── Slide 5 — KPI cards ────────────────────────────────────────────────
    kpi_slide = prs.add_slide("3_Title and Content", placeholders={
        0: "At a Glance",
    })
    (
        kpi_slide
        .set_cursor(1.35)
        .add_row(
            pc.ImageBlock(imgs["pikachu"], mode="contain"),
            pc.KPIGrid(KPI_DATA, cols=2),
            weights=[0.28, 0.72],
            h=2.8,
        )
    )

    # ── Slide 6 — Franchise revenue trend ─────────────────────────────────
    revenue_slide = prs.add_slide("3_Title and Content", placeholders={
        0: "Pokémon Franchise Revenue Growth",
    })
    revenue_slide.set_cursor(1.35).add(
        pc.LineChart(
            categories=REVENUE_LABELS,
            series=REVENUE_DATA,
        ),
        h=3.0,
    )

    # ── Slide 7 — Key facts ────────────────────────────────────────────────
    facts_slide = prs.add_slide("3_Title and Content", placeholders={
        0: "Notable Facts  (Wikipedia)",
    })
    (
        facts_slide
        .set_cursor(1.35)
        .add(pc.ListBlock(FACTS), h=3.2)
    )

    # ── Slide 8 — Timeline ─────────────────────────────────────────────────
    timeline_slide = prs.add_slide("3_Title and Content", placeholders={
        0: "Pikachu Through the Years  (pokumon.com)",
    })
    timeline_slide.set_cursor(1.35).add(
        pc.Timeline(PIKACHU_TIMELINE),
        h=3.2,
    )

    # ── Slide 9 — Back cover ───────────────────────────────────────────────
    prs.add_slide("6_Back Cover")

    # ── Save ───────────────────────────────────────────────────────────────
    saved = prs.save(OUTPUT)
    print(f"Saved:  {saved}  ({9} slides)")

    if export:
        from pptx_components.export import export_slides
        paths = export_slides(saved, OUTPUT_DIR)
        print(f"Exported {len(paths)} PNG(s) → {OUTPUT_DIR}")

    return saved


if __name__ == "__main__":
    build_deck(export="--export" in sys.argv)
