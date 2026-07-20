import json
from pathlib import Path

import tomllib

PROJECT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_DIR.parent


def test_uv_requires_managed_python():
    pyproject = tomllib.loads(
        (PROJECT_DIR / "pyproject.toml").read_text(encoding="utf-8")
    )

    assert pyproject["tool"]["uv"]["python-preference"] == "only-managed"


def test_ty_targets_the_managed_python_version():
    pyproject = tomllib.loads(
        (PROJECT_DIR / "pyproject.toml").read_text(encoding="utf-8")
    )

    assert pyproject["tool"]["ty"]["environment"]["python-version"] == "3.13"


def test_zed_uses_ty_and_ruff_language_servers():
    settings = json.loads(
        (REPO_ROOT / ".zed" / "settings.json").read_text(encoding="utf-8")
    )

    assert settings["languages"]["Python"]["language_servers"] == ["ty", "ruff"]


def test_finder_launcher_explicitly_requires_managed_python():
    launcher = (PROJECT_DIR / "run.sh").read_text(encoding="utf-8")

    assert 'exec uv run --managed-python main.py "$@"' in launcher
