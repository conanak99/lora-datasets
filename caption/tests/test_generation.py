from pathlib import Path

import pytest

from generation import (
    PromptMode,
    clean_caption,
    discover_images,
    generate_folder,
    prompt_path,
)


class FakeCaptioner:
    def __init__(self, outputs: dict[str, str | Exception]):
        self.outputs = outputs
        self.load_calls = 0
        self.generate_calls: list[tuple[Path, str]] = []

    def load(self):
        self.load_calls += 1

    def generate(self, image_path: Path, prompt: str) -> str:
        self.generate_calls.append((image_path, prompt))
        output = self.outputs[image_path.name]
        if isinstance(output, Exception):
            raise output
        return output


def test_prompt_path_selects_character_and_style_files(tmp_path: Path):
    assert prompt_path(PromptMode.CHARACTER, tmp_path) == (
        tmp_path / "prompt_character.md"
    )
    assert prompt_path(PromptMode.STYLE, tmp_path) == tmp_path / "prompt_style.md"


def test_discover_images_returns_supported_non_hidden_files_in_name_order(
    tmp_path: Path,
):
    for name in ["b.JPG", "a.png", ".hidden.jpg", "notes.txt"]:
        (tmp_path / name).touch()
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "inside.webp").touch()

    assert discover_images(tmp_path) == [tmp_path / "a.png", tmp_path / "b.JPG"]


def test_clean_caption_removes_outer_markdown_fence():
    assert clean_caption("  ```markdown\nA plain training caption.\n```  ") == (
        "A plain training caption."
    )


def test_clean_caption_preserves_plain_caption():
    assert clean_caption("  A caption with `inline code`.  ") == (
        "A caption with `inline code`."
    )


def test_generate_folder_skips_existing_captions_and_writes_missing_ones(
    tmp_path: Path,
):
    for name in ["a.jpg", "b.png", "c.webp"]:
        (tmp_path / name).touch()
    (tmp_path / "a.txt").write_text("keep me", encoding="utf-8")
    (tmp_path / "b.txt").write_text("", encoding="utf-8")
    captioner = FakeCaptioner({"c.webp": "```markdown\nnew caption\n```"})

    result = generate_folder(tmp_path, "selected prompt", captioner)

    assert result.total == 3
    assert result.completed == 1
    assert result.skipped == 2
    assert (tmp_path / "a.txt").read_text(encoding="utf-8") == "keep me"
    assert (tmp_path / "b.txt").read_text(encoding="utf-8") == ""
    assert (tmp_path / "c.txt").read_text(encoding="utf-8") == "new caption"
    assert captioner.load_calls == 1
    assert captioner.generate_calls == [
        (tmp_path / "c.webp", "selected prompt")
    ]


def test_generate_folder_reports_progress_after_each_completed_image(tmp_path: Path):
    for name in ["a.jpg", "b.jpg"]:
        (tmp_path / name).touch()
    captioner = FakeCaptioner({"a.jpg": "first", "b.jpg": "second"})
    progress = []

    generate_folder(tmp_path, "prompt", captioner, progress.append)

    assert [(item.completed, item.current.name) for item in progress] == [
        (1, "a.jpg"),
        (2, "b.jpg"),
    ]
    assert all(item.total == 2 for item in progress)
    assert all(item.skipped == 0 for item in progress)


def test_generate_folder_stops_on_error_and_preserves_completed_captions(
    tmp_path: Path,
):
    for name in ["a.jpg", "b.jpg", "c.jpg"]:
        (tmp_path / name).touch()
    captioner = FakeCaptioner(
        {"a.jpg": "finished", "b.jpg": RuntimeError("inference failed")}
    )

    with pytest.raises(RuntimeError, match="inference failed"):
        generate_folder(tmp_path, "prompt", captioner)

    assert (tmp_path / "a.txt").read_text(encoding="utf-8") == "finished"
    assert not (tmp_path / "b.txt").exists()
    assert not (tmp_path / "c.txt").exists()


def test_generate_folder_does_not_load_captioner_when_every_caption_exists(
    tmp_path: Path,
):
    (tmp_path / "a.jpg").touch()
    (tmp_path / "a.txt").touch()
    captioner = FakeCaptioner({})

    result = generate_folder(tmp_path, "prompt", captioner)

    assert result.total == 1
    assert result.completed == 0
    assert result.skipped == 1
    assert captioner.load_calls == 0
