#!/usr/bin/env bash
# Generate PNG screenshots for every .pptx in examples/ and test_new_components.pptx.
# Output goes to docs/screenshots/<deck-name>/slide_NNN.png

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCREENSHOT_DIR="$REPO_ROOT/docs/screenshots"
SOFFICE="${SOFFICE:-libreoffice}"

snapshot_pptx() {
  local pptx="$1"
  local name
  name="$(basename "$pptx" .pptx)"
  local out_dir="$SCREENSHOT_DIR/$name"
  mkdir -p "$out_dir"

  echo "  Rendering $pptx → $out_dir/"
  # LibreOffice exports to PDF first, then we convert each page to PNG
  local tmp
  tmp="$(mktemp -d)"
  "$SOFFICE" --headless --convert-to pdf --outdir "$tmp" "$pptx" >/dev/null 2>&1
  local pdf="$tmp/$name.pdf"
  if [[ ! -f "$pdf" ]]; then
    echo "  WARNING: LibreOffice produced no PDF for $pptx, skipping."
    rm -rf "$tmp"
    return
  fi
  # Convert PDF pages to PNG (150 dpi — good balance of quality vs. size)
  pdftoppm -png -r 150 "$pdf" "$out_dir/slide"
  rm -rf "$tmp"
  echo "    → $(ls "$out_dir"/slide*.png 2>/dev/null | wc -l) slide(s) exported"
}

cd "$REPO_ROOT"

# Regenerate the quick test deck so screenshots reflect current code
if [[ "${SKIP_REGEN:-0}" != "1" ]]; then
  echo "Regenerating test_new_components.pptx..."
  python examples/demo.py 2>/dev/null || true
fi

targets=()
while IFS= read -r -d '' f; do
  targets+=("$f")
done < <(find examples -maxdepth 1 -name "*.pptx" -print0 | sort -z)
[[ -f test_new_components.pptx ]] && targets+=(test_new_components.pptx)

if [[ ${#targets[@]} -eq 0 ]]; then
  echo "No PPTX files found."
  exit 0
fi

echo "Updating screenshots for ${#targets[@]} deck(s)..."
for pptx in "${targets[@]}"; do
  snapshot_pptx "$pptx"
done

echo "Done. Screenshots in docs/screenshots/"
