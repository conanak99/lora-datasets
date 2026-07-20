# Folder Caption Generation Design

## Goal

Extend the desktop caption editor so it can generate resumable, same-stem text captions for every image in a selected folder with `huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated`.

## User interface

Rename the `review` application directory to `caption` and update its titles and documentation to describe a general captioning tool. Keep the existing folder review and manual editing workflow.

Add two toolbar controls:

- A read-only Character/Style selector. Character reads `caption/prompt/prompt_character.md`; Style reads `caption/prompt/prompt_style.md`.
- A `Generate Folder Captions...` button. It opens a dataset folder picker independently of the folder currently shown in the editor.

The toolbar status reports model loading and `completed / total / skipped` progress. Generation runs off the Tk main thread so image navigation and caption editing remain responsive.

## Caption generation

The app uses the model author's Transformers approach: `Qwen3VLForConditionalGeneration.from_pretrained`, `AutoProcessor.from_pretrained`, a chat message containing the local image and selected prompt, `apply_chat_template`, `model.generate`, and `batch_decode`.

The model and processor load lazily on the first folder with missing captions and remain cached for later generation runs in the same application process. The implementation uses model id `huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated`, automatic device placement, bfloat16 weights, remote model code, and low-CPU-memory loading. Each source image is loaded with Pillow and resized only in memory to fit within 1024×1024 while retaining its aspect ratio; the dataset image on disk remains unchanged.

## Resume and output behavior

Supported, non-hidden images are sorted by filename. Before loading the model, the generator partitions them into skipped images whose same-stem `.txt` file already exists and pending images. Existing files are never modified, including empty files.

Each model response is normalized to a plain caption by trimming surrounding whitespace and an optional outer Markdown code fence. The completed caption is written after each image, before moving to the next one. If loading or inference fails, the current run stops, previously written captions stay in place, and the UI reports the error. Running the action again skips those completed files and resumes with the rest.

## Structure and testing

Keep model and batch behavior in `caption/generation.py`, separate from Tk widgets in `caption/main.py`. Store both user-editable prompts under `caption/prompt/`. Dependency injection allows the batch orchestration to be tested without downloading the model.

Tests cover deterministic image discovery, prompt selection, response cleanup, skipping existing captions, immediate same-stem writes, progress reporting, and stopping with completed outputs preserved. A compile check covers the Tk integration, and the project test suite verifies the generation core.
