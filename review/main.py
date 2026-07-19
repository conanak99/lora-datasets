"""Desktop image/caption review app (Tkinter).

Usage:
    uv run main.py [folder]

If no folder is given, a folder picker opens on launch. Every image in the
folder is paired with a same-name .txt caption file, shown side by side.
Caption edits auto-save shortly after you stop typing.
"""

import argparse
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, font

from PIL import Image, ImageTk

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}

BG = "#101014"
PANEL = "#18181f"
BORDER = "#2a2a35"
TEXT = "#e8e8ee"
MUTED = "#8a8a99"
GREEN = "#5fbf77"
AMBER = "#d9a441"

SAVE_DELAY_MS = 600
RESIZE_DELAY_MS = 80


class ReviewApp:
    def __init__(self, root: tk.Tk, folder: Path | None):
        self.root = root
        self.folder: Path | None = None
        self.images: list[Path] = []
        self.idx = 0
        self.save_job = None
        self.resize_job = None
        self.dirty = False
        self.loading = False  # suppress modified events while loading text
        self.pil_image: Image.Image | None = None
        self.tk_image = None

        root.title("Caption Review")
        root.geometry("1280x800")
        root.configure(bg=BG)
        self._build_ui()
        self._bind_keys()

        if folder:
            self.open_folder(folder)
        else:
            root.after(50, self.pick_folder)

    # ---------- UI ----------

    def _build_ui(self):
        # Toolbar
        bar = tk.Frame(self.root, bg=PANEL, padx=10, pady=6)
        bar.pack(fill="x")
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        def toolbar_btn(text, cmd):
            # macOS Aqua ignores bg/fg on tk.Button, so keep system styling
            # and only tint the surrounding highlight frame to match the bar.
            return tk.Button(
                bar, text=text, command=cmd,
                highlightbackground=PANEL, relief="flat", padx=10,
            )

        toolbar_btn("Open Folder…", self.pick_folder).pack(side="left")
        self.fname_var = tk.StringVar()
        tk.Label(bar, textvariable=self.fname_var, bg=PANEL, fg=MUTED).pack(
            side="left", padx=12
        )

        self.next_btn = toolbar_btn("→", lambda: self.goto(self.idx + 1))
        self.next_btn.pack(side="right")
        self.prev_btn = toolbar_btn("←", lambda: self.goto(self.idx - 1))
        self.prev_btn.pack(side="right")
        self.counter_var = tk.StringVar()
        tk.Label(bar, textvariable=self.counter_var, bg=PANEL, fg=MUTED).pack(
            side="right", padx=12
        )
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(bar, textvariable=self.status_var, bg=PANEL, fg=GREEN)
        self.status_label.pack(side="right", padx=8)

        # Main panes: image | caption
        main = tk.PanedWindow(
            self.root, orient="horizontal", bg=BORDER, sashwidth=3, bd=0
        )
        main.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(main, bg=BG, highlightthickness=0)
        main.add(self.canvas, minsize=300, stretch="always")
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        right = tk.Frame(main, bg=PANEL)
        main.add(right, minsize=300, width=480, stretch="always")

        mono = font.nametofont("TkFixedFont").copy()
        mono.configure(size=13)
        self.text = tk.Text(
            right, wrap="word", undo=True, bg=PANEL, fg=TEXT,
            insertbackground=TEXT, relief="flat", padx=16, pady=14,
            font=mono, spacing2=4, highlightthickness=0,
        )
        self.text.pack(fill="both", expand=True)
        self.text.bind("<<Modified>>", self._on_text_modified)

        hint = "Auto-saves as you type   \u2190/\u2192 navigate (Esc leaves the editor)"
        tk.Label(right, text=hint, bg=PANEL, fg=MUTED, anchor="w", padx=16, pady=4).pack(
            fill="x"
        )

    def _bind_keys(self):
        self.root.bind("<Left>", self._nav_key(-1))
        self.root.bind("<Right>", self._nav_key(+1))
        self.root.bind("<Escape>", lambda e: self.root.focus_set())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _nav_key(self, delta):
        def handler(event):
            # Let arrow keys move the cursor while typing in the caption box.
            if self.root.focus_get() is self.text:
                return
            self.goto(self.idx + delta)
        return handler

    # ---------- Folder / navigation ----------

    def pick_folder(self):
        if self.folder:
            initial = self.folder.parent
        else:
            # No folder open yet: start from the repo root (parent of the
            # folder this app lives in).
            initial = Path(__file__).resolve().parent.parent
        chosen = filedialog.askdirectory(
            title="Choose a dataset folder", initialdir=str(initial)
        )
        if chosen:
            self.open_folder(Path(chosen))

    def open_folder(self, folder: Path):
        self.flush_save()
        self.folder = folder.expanduser().resolve()
        self.images = sorted(
            p for p in self.folder.iterdir()
            if p.suffix.lower() in IMAGE_EXTS and not p.name.startswith(".")
        )
        self.root.title(f"Caption Review — {self.folder}")
        if not self.images:
            self.fname_var.set("No images found in this folder")
            self.counter_var.set("")
            self.canvas.delete("all")
            self._set_text("")
            return
        self.goto(0)

    def goto(self, i: int):
        if not self.images:
            return
        self.flush_save()
        self.idx = max(0, min(i, len(self.images) - 1))
        img_path = self.images[self.idx]

        self.fname_var.set(img_path.name)
        self.counter_var.set(f"{self.idx + 1} / {len(self.images)}")
        self.prev_btn.config(state="normal" if self.idx > 0 else "disabled")
        self.next_btn.config(
            state="normal" if self.idx < len(self.images) - 1 else "disabled"
        )

        self.pil_image = Image.open(img_path)
        self._render_image()

        cap = self.caption_path(img_path)
        self._set_text(cap.read_text(encoding="utf-8") if cap.is_file() else "")
        self._set_status("", GREEN)

    def caption_path(self, img_path: Path) -> Path:
        return img_path.with_suffix(".txt")

    # ---------- Image rendering ----------

    def _render_image(self):
        if self.pil_image is None:
            return
        cw = max(self.canvas.winfo_width(), 1)
        ch = max(self.canvas.winfo_height(), 1)
        iw, ih = self.pil_image.size
        scale = min((cw - 24) / iw, (ch - 24) / ih, 1.0)
        w, h = max(int(iw * scale), 1), max(int(ih * scale), 1)
        resized = self.pil_image.resize((w, h), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=self.tk_image)

    def _on_canvas_resize(self, _event):
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(RESIZE_DELAY_MS, self._render_image)

    # ---------- Caption editing / auto-save ----------

    def _set_text(self, value: str):
        self.loading = True
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)
        self.text.edit_reset()
        self.text.edit_modified(False)
        self.loading = False
        self.dirty = False

    def _on_text_modified(self, _event):
        # <<Modified>> fires for both set and clear; only react to real edits.
        if self.loading or not self.text.edit_modified():
            return
        self.text.edit_modified(False)
        self.dirty = True
        self._set_status("…", AMBER)
        if self.save_job:
            self.root.after_cancel(self.save_job)
        self.save_job = self.root.after(SAVE_DELAY_MS, self.save_caption)

    def save_caption(self):
        self.save_job = None
        if not self.dirty or not self.images:
            return
        cap = self.caption_path(self.images[self.idx])
        cap.write_text(self.text.get("1.0", "end-1c"), encoding="utf-8")
        self.dirty = False
        self._set_status("saved", GREEN)

    def flush_save(self):
        if self.save_job:
            self.root.after_cancel(self.save_job)
            self.save_job = None
        if self.dirty:
            self.save_caption()

    def _set_status(self, text: str, color: str):
        self.status_var.set(text)
        self.status_label.config(fg=color)

    def _on_close(self):
        self.flush_save()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description="Review image/caption pairs.")
    parser.add_argument(
        "folder", nargs="?", help="Folder containing images and .txt captions"
    )
    args = parser.parse_args()

    folder = None
    if args.folder:
        folder = Path(args.folder).expanduser().resolve()
        if not folder.is_dir():
            sys.exit(f"Not a folder: {folder}")

    root = tk.Tk()
    ReviewApp(root, folder)
    root.mainloop()


if __name__ == "__main__":
    main()
