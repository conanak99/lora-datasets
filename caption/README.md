# Caption

Desktop app (Tkinter) for generating, reviewing, and editing image/caption pairs
for LoRA datasets.

## Usage

Double-click `run.command` in Finder (opens a folder picker), or from a terminal:

```bash
./run.sh                    # folder picker
./run.sh ../data/hanaxame   # open a folder directly
```

- Images are paired with same-name `.txt` caption files in the chosen folder.
- Navigate with the arrow buttons or ←/→ keys (Esc leaves the caption editor first).
- Caption edits auto-save ~0.6s after you stop typing, and when navigating or closing.
