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

    CaptionApp(root, None)

    assert root.after_calls == []
