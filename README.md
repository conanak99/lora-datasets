# LoRA Datasets

Image datasets and helper tooling for LoRA training.

## Cloning

Since this repo stores images, the full git history gets heavy. Just clone the latest snapshot instead:

```bash
git clone --depth 1 https://github.com/conanak99/lora-datasets.git
```

## Contents

- `data/*` — dataset images and captions.
- `prompt_character.md` — character LoRA image-captioning prompt.
- `prompt_style.md` — style LoRA image-captioning prompt.
- `caption/` — desktop app for generating, reviewing, and editing captions.
- `resize_to_jpeg.sh` — batch-converts a folder of images to JPEG.

## Resizing images

Requires ImageMagick (`brew install imagemagick`).

```bash
./resize_to_jpeg.sh <folder>
```

Converts every image in `<folder>` to JPEG at quality 95, resizing so the shortest edge is 1536px (images already smaller are never upscaled). Output goes to a sibling folder named `<folder>_jpeg`; originals are untouched.
