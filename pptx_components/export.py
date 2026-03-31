"""Export PPTX slides to PNG images via PowerPoint COM (Windows only).

Usage:
    from pptx_components.export import export_slides

    paths = export_slides("deck.pptx")           # → ["out/slide_001.png", ...]
    paths = export_slides("deck.pptx", dpi=200)  # higher res
"""
from __future__ import annotations

import os
import sys
import time


def export_slides(
    pptx_path: str,
    output_dir: str | None = None,
    dpi: int = 150,
    prefix: str = "slide",
) -> list[str]:
    """Convert every slide in *pptx_path* to a PNG file.

    Args:
        pptx_path: Path to the .pptx file.
        output_dir: Folder for PNGs. Defaults to ``<pptx_stem>_slides/`` next to the file.
        dpi: Export resolution (default 150 — good for screen review).
        prefix: Filename prefix for each PNG.

    Returns:
        List of absolute paths to the exported PNG files.

    Raises:
        RuntimeError: If PowerPoint COM is unavailable or export fails.
    """
    if sys.platform != "win32":
        raise RuntimeError(
            "PowerPoint COM export is Windows-only. "
            "On other platforms, use LibreOffice: "
            "soffice --headless --convert-to png <file.pptx>"
        )

    try:
        import win32com.client  # noqa: F401
    except ImportError:
        raise RuntimeError("pywin32 is required: pip install pywin32")

    pptx_path = os.path.abspath(pptx_path)
    if not os.path.isfile(pptx_path):
        raise FileNotFoundError(pptx_path)

    if output_dir is None:
        stem = os.path.splitext(os.path.basename(pptx_path))[0]
        output_dir = os.path.join(os.path.dirname(pptx_path), f"{stem}_slides")
    os.makedirs(output_dir, exist_ok=True)

    # Set export DPI via registry (PowerPoint reads this at export time)
    _set_export_dpi(dpi)

    app = None
    prs = None
    exported: list[str] = []

    try:
        app = win32com.client.Dispatch("PowerPoint.Application")
        prs = app.Presentations.Open(
            pptx_path,
            ReadOnly=True,
            Untitled=False,
            WithWindow=False,
        )

        count = prs.Slides.Count
        for i in range(1, count + 1):
            out_file = os.path.join(output_dir, f"{prefix}_{i:03d}.png")
            prs.Slides(i).Export(out_file, "PNG")
            exported.append(out_file)

        return exported

    except Exception as exc:
        raise RuntimeError(f"PowerPoint export failed: {exc}") from exc

    finally:
        if prs is not None:
            try:
                prs.Close()
            except Exception:
                pass
        if app is not None:
            try:
                app.Quit()
            except Exception:
                pass
            # Give COM time to release
            time.sleep(0.3)
        # Drop references so COM ref-count hits zero
        prs = None  # noqa: F841
        app = None  # noqa: F841


def _set_export_dpi(dpi: int) -> None:
    """Write the ExportBitmapResolution registry key so PowerPoint uses *dpi*."""
    try:
        import winreg
        key_path = r"Software\Microsoft\Office\16.0\PowerPoint\Options"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        except FileNotFoundError:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, "ExportBitmapResolution", 0, winreg.REG_DWORD, dpi)
        winreg.CloseKey(key)
    except Exception:
        # Non-fatal — PowerPoint will fall back to its default DPI
        pass


# ── CLI entry point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export PPTX slides to PNG")
    parser.add_argument("pptx", help="Path to .pptx file")
    parser.add_argument("-o", "--output", default=None, help="Output directory")
    parser.add_argument("--dpi", type=int, default=150, help="Export DPI (default: 150)")
    args = parser.parse_args()

    paths = export_slides(args.pptx, output_dir=args.output, dpi=args.dpi)
    for p in paths:
        print(p)
    print(f"\nExported {len(paths)} slides.")
