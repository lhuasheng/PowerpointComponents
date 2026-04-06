---
name: download-web-assets
description: 'Download direct asset URLs for logos, icons, screenshots, and slide imagery into the workspace. Use when you already have a trusted image URL and want the agent to save it locally, reject HTML/error downloads, optionally rasterize SVG to PNG, and record the source in a manifest.'
argument-hint: 'Provide the URL, destination folder, preferred filename, and whether you want an SVG rendered to PNG or added to a source manifest.'
user-invocable: true
---

# Download Web Assets

## What This Skill Produces
- Local image files saved into the workspace from direct URLs.
- Validation that the download is an actual asset, not an HTML error page.
- Optional SVG-to-PNG raster output when ImageMagick is available.
- Optional source manifest rows for asset provenance.

## When to Use
- You already have a direct file URL and want it downloaded reliably.
- You are collecting brand logos, icons, or slide images from official or clearly licensed sources.
- A previous download may have saved an error page instead of an image.
- You want to keep a lightweight `SOURCES.md` trail beside downloaded assets.

## Inputs to Gather First
- Direct asset URL.
- Destination folder in the workspace.
- Preferred filename if the URL name is weak or unstable.
- Whether to keep the original format only, or also render SVG to PNG.
- Whether the download should append a provenance row to a markdown manifest.

## Procedure
1. Validate the source choice before downloading.
- Prefer official vendor/project URLs or clearly licensed sources.
- If the source is a mirror, check whether an official source exists first.

2. Download with the helper script.
- Run [download_asset.py](./scripts/download_asset.py) with the URL and output folder.
- Pass `--filename` when the remote filename is unclear.
- Pass `--manifest` when you want the source logged automatically.

3. Verify the result.
- Confirm the file is present.
- Check the file type with `file` if needed.
- If the script rejects the response as HTML or text, switch to the original asset URL instead of a thumbnail or preview page.

4. Rasterize SVGs only when needed.
- If the deck or workflow needs PNG output, rerun the script with `--render-png`.
- Prefer keeping the SVG original even when a PNG is rendered.

5. Record provenance.
- Add or update a local `SOURCES.md` manifest when the assets matter beyond one-off experimentation.
- Include source URL and short license or trademark notes when known.

## Decision Logic
- If the URL points to a page instead of a file, stop and fetch the actual file URL first.
- If the response is HTML, treat it as a failed download even if the extension looks correct.
- If the asset is SVG and will be scaled in slides, keep the SVG original.
- If ImageMagick fails to render an SVG to PNG, keep the SVG and use an existing upstream PNG if available.
- If licensing is unclear, save the file only if the user explicitly accepts that risk or a stronger source cannot be found.

## Completion Checks
- Asset saved in the requested folder.
- File is an image or SVG, not an HTML/text error response.
- PNG render exists when requested and supported.
- Manifest entry exists when requested.

## Commands
- Run these from the repository root.
- Single download:
  `python ./PowerpointComponents/.github/skills/download-web-assets/scripts/download_asset.py --url <direct-url> --out-dir <folder>`
- Download with explicit filename and manifest:
  `python ./PowerpointComponents/.github/skills/download-web-assets/scripts/download_asset.py --url <direct-url> --out-dir <folder> --filename <name.ext> --manifest <folder>/SOURCES.md --source-note "official site asset"`
- Download SVG and render PNG:
  `python ./PowerpointComponents/.github/skills/download-web-assets/scripts/download_asset.py --url <direct-url> --out-dir <folder> --filename <name>.svg --render-png`

## References
- [usage notes](./references/usage.md)