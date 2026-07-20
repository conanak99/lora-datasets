# Caption

Desktop app (Tkinter) for generating, reviewing, and editing image/caption pairs
for LoRA datasets.

Caption generation runs locally with
[`huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated`](https://huggingface.co/huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated).

## Usage

Double-click `run.command` in Finder (opens a folder picker), or from a terminal:

```bash
./run.sh                    # folder picker
./run.sh ../data/hanaxame   # open a folder directly
```

- Images are paired with same-name `.txt` caption files in the chosen folder.
- Navigate with the arrow buttons or ←/→ keys (Esc leaves the caption editor first).
- Caption edits auto-save ~0.6s after you stop typing, and when navigating or closing.

## Generate captions for a folder

1. Select **Character** or **Style** in the Prompt menu. These modes read
   `prompt/prompt_character.md` and `prompt/prompt_style.md` from this app.
2. Click **Generate Folder Captions…** and select a dataset folder.
3. Leave the app running while the toolbar reports generation progress.

Images are processed in filename order. Each result is saved immediately as a
same-name `.txt` file. Any image that already has a `.txt` file is skipped,
including an empty file, so interrupted runs can safely resume by selecting the
same folder again.

Source images stay at their original resolution on disk. Before inference, the
app loads each image with Pillow and scales that in-memory copy to fit within
1024×1024 while preserving its aspect ratio. This keeps model memory use bounded
without changing the dataset files.

The first generation run downloads the model weights from Hugging Face and can
take a while. The 4B model also requires substantial memory. The model author
warns that this abliterated model has reduced safety filtering, so review its
captions before using or distributing them.
