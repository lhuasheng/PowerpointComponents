"""Export PPTX slides to PNG images.

Windows – PowerPoint COM (pywin32).
macOS   – AppleScript driving Microsoft PowerPoint for Mac; falls back to
          LibreOffice + ImageMagick when PowerPoint is not installed.
Linux   – LibreOffice + ImageMagick.

Usage:
    from pptx_components.export import export_slides

    paths = export_slides("deck.pptx")           # → ["out/slide_001.png", ...]
    paths = export_slides("deck.pptx", dpi=200)  # higher res (Windows/LibreOffice only)
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import time
import tempfile
import warnings


MAX_IMAGE_DIMENSION = 1800


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
        dpi: Export resolution (default 150). Honoured on Windows and the
            PDF-based conversion paths before the final images are constrained
            to a maximum longest dimension of 1800 pixels.
        prefix: Filename prefix for each PNG.

    Returns:
        List of absolute paths to the exported PNG files, sorted by slide order.

    Raises:
        FileNotFoundError: If *pptx_path* does not exist.
        RuntimeError: If export fails or no supported backend is available.
    """
    pptx_path = os.path.abspath(pptx_path)
    if not os.path.isfile(pptx_path):
        raise FileNotFoundError(pptx_path)

    if output_dir is None:
        stem = os.path.splitext(os.path.basename(pptx_path))[0]
        output_dir = os.path.join(os.path.dirname(pptx_path), f"{stem}_slides")
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    if sys.platform == "win32":
        return _export_windows(pptx_path, output_dir, dpi, prefix)
    elif sys.platform == "darwin":
        return _export_macos(pptx_path, output_dir, dpi, prefix)
    else:
        return _export_libreoffice(pptx_path, output_dir, dpi, prefix)


def _pdf_output_path(pptx_path: str) -> str:
    """Return the persisted PDF path beside the source deck with an _pdf suffix."""
    folder = os.path.dirname(pptx_path)
    stem = os.path.splitext(os.path.basename(pptx_path))[0]
    return os.path.join(folder, f"{stem}_pdf.pdf")


# ── Windows ────────────────────────────────────────────────────────────────

def _export_windows(pptx_path: str, output_dir: str, dpi: int, prefix: str) -> list[str]:
    """Windows: PowerPoint COM via pywin32."""
    try:
        import win32com.client  # noqa: F401
    except ImportError:
        raise RuntimeError("pywin32 is required: pip install pywin32")

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
            warnings.warn(
                f"Requested dpi={dpi} ignored: registry key not found ({key_path}).",
                RuntimeWarning,
                stacklevel=2,
            )
            return
        winreg.SetValueEx(key, "ExportBitmapResolution", 0, winreg.REG_DWORD, dpi)
        winreg.CloseKey(key)
    except (ImportError, OSError, PermissionError) as exc:
        warnings.warn(
            f"Requested dpi={dpi} ignored: could not set ExportBitmapResolution ({exc}).",
            RuntimeWarning,
            stacklevel=2,
        )


# ── macOS ──────────────────────────────────────────────────────────────────

def _export_macos(pptx_path: str, output_dir: str, dpi: int, prefix: str) -> list[str]:
    """macOS: LibreOffice + ImageMagick."""
    return _export_libreoffice(pptx_path, output_dir, dpi, prefix)


def _convert_pdf_to_png(pdf_path: str, output_dir: str, dpi: int, prefix: str) -> list[str]:
    """Convert a PDF into per-slide PNGs capped at MAX_IMAGE_DIMENSION."""
    png_pattern = os.path.join(output_dir, f"{prefix}_%03d.png")
    result = subprocess.run(
        [
            "convert",
            "-density",
            str(dpi),
            pdf_path,
            "-resize",
            f"{MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}>",
            png_pattern,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ImageMagick conversion failed:\n{result.stderr.strip()}")

    exported = sorted(glob.glob(os.path.join(output_dir, f"{prefix}_*.png")))
    if not exported:
        raise RuntimeError("ImageMagick ran but no PNG files were produced.")
    return exported


def _export_applescript(pptx_path: str, output_dir: str, dpi: int, prefix: str) -> list[str]:
    """Export via AppleScript (PPTX → PDF) then ImageMagick (PDF → PNG).

    PowerPoint's per-slide PNG export via AppleScript is broken on current macOS builds.
    The reliable approach is to save the whole presentation as PDF first (which works
    once the user has approved folder access in the macOS permission dialog), then use
    ImageMagick's ``convert`` to split the PDF into individual slide PNGs.

    Note: On first run for a new output folder, macOS will show a permission dialog
    for PowerPoint — click Allow. Subsequent runs are silent.
    """
    if shutil.which("convert") is None:
        raise RuntimeError(
            "ImageMagick 'convert' not found. Install it:\n"
            "  brew install imagemagick"
        )

    temp_dir = tempfile.mkdtemp(prefix="pptx_export_")
    staged_pptx = os.path.join(temp_dir, os.path.basename(pptx_path))
    shutil.copy2(pptx_path, staged_pptx)

    safe_pptx = staged_pptx.replace("\\", "\\\\").replace('"', '\\"')
    pdf_path = _pdf_output_path(pptx_path)
    safe_pdf = pdf_path.replace("\\", "\\\\").replace('"', '\\"')

    script = (
        'tell application "Microsoft PowerPoint"\n'
        f'    open POSIX file "{safe_pptx}"\n'
        '    set theDoc to active presentation\n'
        f'    save theDoc in (POSIX file "{safe_pdf}") as save as PDF\n'
        '    close theDoc saving no\n'
        'end tell\n'
    )

    try:
        try:
            os.remove(pdf_path)
        except OSError:
            pass

        result = subprocess.run(["osascript"], input=script, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"AppleScript PDF export failed:\n{result.stderr.strip()}")

        if not os.path.isfile(pdf_path):
            raise RuntimeError(f"PDF not produced by PowerPoint: {pdf_path}")

        return _convert_pdf_to_png(pdf_path, output_dir, dpi, prefix)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# ── Linux / LibreOffice fallback ───────────────────────────────────────────

def _soffice_bin() -> str:
    """Return the soffice binary path, checking both PATH and the macOS cask location."""
    import shutil
    which = shutil.which("soffice")
    if which:
        return which
    mac_cask = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if os.path.isfile(mac_cask):
        return mac_cask
    return "soffice"  # will fail with a clear error below


def _export_libreoffice(pptx_path: str, output_dir: str, dpi: int, prefix: str) -> list[str]:
    """Export via LibreOffice (PPTX → PDF) then ImageMagick (PDF → PNG).

    Requires ``soffice`` and ``convert`` (ImageMagick).
      macOS install:  brew install --cask libreoffice && brew install imagemagick
      Linux install:  sudo apt-get install libreoffice imagemagick
    """
    soffice = _soffice_bin()

    for cmd, label in ((soffice, "soffice"), ("convert", "convert")):
        if subprocess.run(["which", cmd], capture_output=True).returncode != 0:
            if label == "soffice" and os.path.isfile(cmd):
                pass  # found at explicit path, fine
            else:
                raise RuntimeError(
                    f"'{label}' not found. Install the required tools:\n"
                    "  macOS:  brew install --cask libreoffice && brew install imagemagick\n"
                    "  Linux:  sudo apt-get install libreoffice imagemagick"
                )

    # Step 1: PPTX → PDF
    pdf_dir = os.path.dirname(pptx_path)
    result = subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", pdf_dir, pptx_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice conversion failed:\n{result.stderr.strip()}")

    stem = os.path.splitext(os.path.basename(pptx_path))[0]
    generated_pdf = os.path.join(pdf_dir, f"{stem}.pdf")
    pdf_path = _pdf_output_path(pptx_path)
    try:
        os.remove(pdf_path)
    except OSError:
        pass
    if not os.path.isfile(generated_pdf):
        raise RuntimeError(f"Expected PDF not produced: {generated_pdf}")
    os.replace(generated_pdf, pdf_path)

    return _convert_pdf_to_png(pdf_path, output_dir, dpi, prefix)


# ── CLI entry point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export PPTX slides to PNG")
    parser.add_argument("pptx", help="Path to .pptx file")
    parser.add_argument("-o", "--output", default=None, help="Output directory")
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="Export DPI (default: 150; ignored on macOS AppleScript path)",
    )
    args = parser.parse_args()

    paths = export_slides(args.pptx, output_dir=args.output, dpi=args.dpi)
    for p in paths:
        print(p)
    print(f"\nExported {len(paths)} slides.")
