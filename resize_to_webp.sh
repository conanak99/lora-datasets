#!/usr/bin/env bash
# Convert all images in a folder to WebP (quality 95), resizing so the
# shortest edge is 1536px (never upscaling smaller images).
# Output goes to <folder>_webp next to the input.
#
# Usage: ./resize_to_webp.sh <folder>

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <folder>" >&2
    exit 1
fi

INPUT_DIR="${1%/}"

if [[ ! -d "$INPUT_DIR" ]]; then
    echo "Error: '$INPUT_DIR' is not a directory" >&2
    exit 1
fi

if ! command -v magick >/dev/null 2>&1; then
    echo "Error: ImageMagick ('magick') is required. Install with: brew install imagemagick" >&2
    exit 1
fi

OUTPUT_DIR="${INPUT_DIR}_webp"
mkdir -p "$OUTPUT_DIR"

TARGET=1536
count=0
skipped=0

shopt -s nullglob nocaseglob
for img in "$INPUT_DIR"/*.{jpg,jpeg,png,webp,tif,tiff,bmp,heic,gif}; do
    name="$(basename "$img")"
    out="$OUTPUT_DIR/${name%.*}.webp"

    # "1536x1536^>" resizes so the *shortest* edge becomes 1536 (^ = fill),
    # and ">" only shrinks — images already smaller are never upscaled.
    if magick "$img" -auto-orient -resize "${TARGET}x${TARGET}^>" -quality 95 "$out"; then
        count=$((count + 1))
        echo "OK  $name -> $(basename "$out")"
    else
        skipped=$((skipped + 1))
        echo "FAIL $name" >&2
    fi
done
shopt -u nullglob nocaseglob

echo
echo "Done: $count converted, $skipped failed. Output in: $OUTPUT_DIR"
