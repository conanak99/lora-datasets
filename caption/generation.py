"""Caption model integration and resumable folder generation."""

from enum import Enum
from pathlib import Path
import re


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


class PromptMode(str, Enum):
    CHARACTER = "character"
    STYLE = "style"


def prompt_path(mode: PromptMode, repo_root: Path) -> Path:
    """Return the repository prompt file for a captioning mode."""
    return repo_root / f"prompt_{mode.value}.md"


def discover_images(folder: Path) -> list[Path]:
    """Find supported, visible images directly inside a folder."""
    return sorted(
        (
            path
            for path in folder.iterdir()
            if path.is_file()
            and not path.name.startswith(".")
            and path.suffix.lower() in IMAGE_EXTS
        ),
        key=lambda path: path.name.casefold(),
    )


def clean_caption(value: str) -> str:
    """Return plain caption text, removing one optional outer Markdown fence."""
    caption = value.strip()
    fenced = re.fullmatch(
        r"```(?:markdown|text)?[ \t]*\n?(.*?)\n?```",
        caption,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if fenced:
        return fenced.group(1).strip()
    return caption
