#!/usr/bin/env python3
from __future__ import annotations

import argparse
import mimetypes
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "Mozilla/5.0 (compatible; download-web-assets/1.0)"
HTML_MARKERS = (b"<!DOCTYPE html", b"<html", b"<HTML", b"<body", b"<BODY")
CONTENT_TYPE_EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and validate a direct asset URL.")
    parser.add_argument("--url", required=True, help="Direct asset URL to download")
    parser.add_argument("--out-dir", required=True, help="Destination directory")
    parser.add_argument("--filename", help="Override output filename")
    parser.add_argument("--manifest", help="Optional markdown manifest file to append to")
    parser.add_argument("--source-note", default="", help="Optional note for the manifest")
    parser.add_argument("--license-note", default="", help="Optional license/trademark note for the manifest")
    parser.add_argument("--render-png", action="store_true", help="Render SVG output to PNG with ImageMagick")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    return parser.parse_args()


def guess_filename(url: str, content_type: str, explicit_name: str | None) -> str:
    if explicit_name:
        return explicit_name

    parsed = urlparse(url)
    raw_name = Path(unquote(parsed.path)).name
    if raw_name:
        return raw_name

    extension = CONTENT_TYPE_EXTENSIONS.get(content_type.split(";")[0].strip().lower(), "")
    return f"downloaded_asset{extension or '.bin'}"


def validate_payload(payload: bytes, content_type: str, target_name: str) -> None:
    lowered_type = content_type.lower()
    prefix = payload[:512].lstrip()
    if "text/html" in lowered_type or any(prefix.startswith(marker) for marker in HTML_MARKERS):
        raise ValueError("downloaded content looks like HTML, not an asset")

    if lowered_type.startswith("text/") and not target_name.lower().endswith(".svg"):
        raise ValueError(f"unexpected text response: {content_type}")


def ensure_extension(name: str, content_type: str) -> str:
    path = Path(name)
    if path.suffix:
        return name

    extension = CONTENT_TYPE_EXTENSIONS.get(content_type.split(";")[0].strip().lower())
    if extension:
        return f"{name}{extension}"
    guessed = mimetypes.guess_extension(content_type.split(";")[0].strip().lower())
    return f"{name}{guessed}" if guessed else name


def download(url: str) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request) as response:
            content_type = response.headers.get("Content-Type", "application/octet-stream")
            payload = response.read()
        return payload, content_type
    except (HTTPError, URLError) as exc:
        return download_with_curl(url, exc)


def download_with_curl(url: str, original_error: Exception) -> tuple[bytes, str]:
    curl = shutil.which("curl")
    if not curl:
        raise RuntimeError(f"download failed and curl is unavailable: {original_error}") from original_error

    with tempfile.NamedTemporaryFile(delete=False) as handle:
        temp_path = Path(handle.name)

    try:
        result = subprocess.run(
            [curl, "-L", "--fail", "-A", USER_AGENT, "-sS", "-o", str(temp_path), "-w", "%{content_type}", url],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        payload = temp_path.read_bytes()
        content_type = result.stdout.strip() or "application/octet-stream"
        return payload, content_type
    finally:
        temp_path.unlink(missing_ok=True)


def render_png(svg_path: Path, overwrite: bool) -> Path:
    png_path = svg_path.with_suffix(".png")
    if png_path.exists() and not overwrite:
        raise FileExistsError(f"PNG already exists: {png_path}")

    magick = shutil.which("magick")
    if not magick:
        raise RuntimeError("ImageMagick 'magick' command is not available")

    subprocess.run(
        [magick, "-background", "none", str(svg_path), str(png_path)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return png_path


def append_manifest(manifest_path: Path, asset_name: str, url: str, source_note: str, license_note: str) -> None:
    if not manifest_path.exists():
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            "| Asset | Source | Notes | License |\n| --- | --- | --- | --- |\n",
            encoding="utf-8",
        )

    row = f"| {asset_name} | {url} | {source_note or '-'} | {license_note or '-'} |\n"
    with manifest_path.open("a", encoding="utf-8") as handle:
        handle.write(row)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        payload, content_type = download(args.url)
        file_name = guess_filename(args.url, content_type, args.filename)
        file_name = ensure_extension(file_name, content_type)
        validate_payload(payload, content_type, file_name)

        destination = out_dir / file_name
        if destination.exists() and not args.overwrite:
            raise FileExistsError(f"file already exists: {destination}")

        destination.write_bytes(payload)
        png_path = None
        if args.render_png and destination.suffix.lower() == ".svg":
            png_path = render_png(destination, overwrite=args.overwrite)

        if args.manifest:
            append_manifest(Path(args.manifest).expanduser().resolve(), destination.name, args.url, args.source_note, args.license_note)

        print(f"saved={destination}")
        print(f"content_type={content_type}")
        if png_path:
            print(f"rendered_png={png_path}")
        return 0
    except (HTTPError, URLError) as exc:
        print(f"download failed: {exc}", file=sys.stderr)
    except subprocess.CalledProcessError as exc:
        print(exc.stderr.strip() or str(exc), file=sys.stderr)
    except (FileExistsError, RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())