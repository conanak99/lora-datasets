import tkinter as tk
from typing import cast

from generation import GenerationResult
from main import CaptionApp


class FakeRoot:
    def __init__(self):
        self.after_calls = []

    def title(self, _value):
        pass

    def geometry(self, _value):
        pass

    def configure(self, **_kwargs):
        pass

    def after(self, *args):
        self.after_calls.append(args)


def test_app_does_not_open_folder_picker_on_empty_startup(monkeypatch):
    monkeypatch.setattr(CaptionApp, "_build_ui", lambda self: None)
    monkeypatch.setattr(CaptionApp, "_bind_keys", lambda self: None)
    root = FakeRoot()

    CaptionApp(cast(tk.Tk, root), None)

    assert root.after_calls == []


def test_completed_generation_opens_selected_folder(tmp_path):
    app = CaptionApp.__new__(CaptionApp)
    app.folder = None
    app.images = []
    app.generation_folder = tmp_path
    reset_calls = []
    statuses = []
    opened_folders = []
    app._reset_generation_controls = lambda: reset_calls.append(True)
    app._set_batch_status = lambda text, color: statuses.append((text, color))
    app.open_folder = opened_folders.append

    app._finish_generation(GenerationResult(completed=0, total=3, skipped=3))

    assert reset_calls == [True]
    assert statuses
    assert opened_folders == [tmp_path]
