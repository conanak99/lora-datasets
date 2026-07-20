from pathlib import Path
import tomllib


PROJECT_DIR = Path(__file__).resolve().parents[1]


def test_uv_requires_managed_python():
    pyproject = tomllib.loads(
        (PROJECT_DIR / "pyproject.toml").read_text(encoding="utf-8")
    )

    assert pyproject["tool"]["uv"]["python-preference"] == "only-managed"


def test_finder_launcher_explicitly_requires_managed_python():
    launcher = (PROJECT_DIR / "run.sh").read_text(encoding="utf-8")

    assert 'exec uv run --managed-python main.py "$@"' in launcher
