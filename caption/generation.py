"""Caption model integration and resumable folder generation."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
from typing import Protocol


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


class PromptMode(str, Enum):
    CHARACTER = "character"
    STYLE = "style"


class Captioner(Protocol):
    def load(self) -> None: ...

    def generate(self, image_path: Path, prompt: str) -> str: ...


@dataclass(frozen=True)
class GenerationProgress:
    completed: int
    total: int
    skipped: int
    current: Path


@dataclass(frozen=True)
class GenerationResult:
    completed: int
    total: int
    skipped: int


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


def generate_folder(
    folder: Path,
    prompt: str,
    captioner: Captioner,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> GenerationResult:
    """Generate every missing same-stem caption, preserving completed work."""
    images = discover_images(folder)
    pending = [image for image in images if not image.with_suffix(".txt").exists()]
    skipped = len(images) - len(pending)

    if not pending:
        return GenerationResult(completed=0, total=len(images), skipped=skipped)

    captioner.load()
    completed = 0
    for image_path in pending:
        caption = clean_caption(captioner.generate(image_path, prompt))
        image_path.with_suffix(".txt").write_text(caption, encoding="utf-8")
        completed += 1
        if on_progress:
            on_progress(
                GenerationProgress(
                    completed=completed,
                    total=len(images),
                    skipped=skipped,
                    current=image_path,
                )
            )

    return GenerationResult(completed=completed, total=len(images), skipped=skipped)
