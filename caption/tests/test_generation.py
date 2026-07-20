from pathlib import Path

from generation import PromptMode, clean_caption, discover_images, prompt_path


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
