"""Caption model integration and resumable folder generation."""

import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

from PIL import Image, ImageOps

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
MODEL_ID = "huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated"
DEFAULT_PROMPT_DIR = Path(__file__).resolve().parent / "prompt"
MAX_IMAGE_SIZE = (1024, 1024)
MAX_IMAGE_PIXELS = 1024 * 1024


class PromptMode(str, Enum):
    PERSON = "person"
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


class HuggingFaceCaptioner:
    """Lazy local adapter for the Huihui Qwen3-VL caption model."""

    def __init__(self, model: Any = None, processor: Any = None):
        self.model = model
        self.processor = processor

    def load(self) -> None:
        if self.model is not None and self.processor is not None:
            return

        import torch
        from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

        cpu_threads = max((os.cpu_count() or 1) // 2, 1)
        os.environ["MKL_NUM_THREADS"] = str(cpu_threads)
        os.environ["OMP_NUM_THREADS"] = str(cpu_threads)
        torch.set_num_threads(cpu_threads)

        self.model = Qwen3VLForConditionalGeneration.from_pretrained(
            MODEL_ID,
            device_map="auto",
            trust_remote_code=True,
            dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
        )
        self.processor = AutoProcessor.from_pretrained(MODEL_ID)

    def generate(self, image_path: Path, prompt: str) -> str:
        self.load()
        image = resize_image_for_model(image_path)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        try:
            inputs = self.processor.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_dict=True,
                return_tensors="pt",
                processor_kwargs={"images_kwargs": {"max_pixels": MAX_IMAGE_PIXELS}},
            ).to(self.model.device)
        finally:
            image.close()
        # transformers' Qwen3-VL type currently conflicts with its own writable
        # generation cache protocol, although the runtime model implements generate.
        generated_ids = self.model.generate(  # ty: ignore[invalid-argument-type]
            **inputs, max_new_tokens=512
        )
        generated_ids_trimmed = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(
                inputs.input_ids, generated_ids, strict=True
            )
        ]
        return self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )[0]


def prompt_path(mode: PromptMode, prompt_dir: Path) -> Path:
    """Return the prompt file for a captioning mode."""
    return prompt_dir / f"prompt_{mode.value}.md"


def read_prompt(mode: PromptMode, prompt_dir: Path = DEFAULT_PROMPT_DIR) -> str:
    """Read the full instructions for a captioning mode."""
    return prompt_path(mode, prompt_dir).read_text(encoding="utf-8")


def format_progress(progress: GenerationProgress | GenerationResult) -> str:
    """Format generated and skipped counts for the desktop toolbar."""
    pending_total = progress.total - progress.skipped
    return (
        f"generated {progress.completed} / {pending_total} · skipped {progress.skipped}"
    )


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


def resize_image_for_model(
    image_path: Path, max_size: tuple[int, int] = MAX_IMAGE_SIZE
) -> Image.Image:
    """Load and resize an image in memory without modifying its source file."""
    with Image.open(image_path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image


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
