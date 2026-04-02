"""MkDocs hooks — runs during `mkdocs build` / `mkdocs serve`.

Copies generated slide PNGs from examples/ into docs/assets/ so they are
available as documentation images without committing large binaries twice.
"""
from __future__ import annotations

import pathlib
import shutil


def on_pre_build(config, **kwargs) -> None:
    """Copy demo slide exports into docs assets before the build starts."""
    repo = pathlib.Path(config["docs_dir"]).parent

    _copy_demo_slides(
        src=repo / "examples" / "slidemasterdemo" / "output_slides",
        dst=repo / "docs" / "assets" / "examples" / "slidemasterdemo",
    )


def _copy_demo_slides(src: pathlib.Path, dst: pathlib.Path) -> None:
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for png in src.glob("*.png"):
        dest_file = dst / png.name
        if not dest_file.exists() or png.stat().st_mtime > dest_file.stat().st_mtime:
            shutil.copy2(png, dest_file)
