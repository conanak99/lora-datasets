# uv-Managed Python Design

## Goal

Make the Caption project use a uv-managed Python distribution that includes
Tkinter, instead of silently reusing a compatible Homebrew Python installation
that may omit `_tkinter`.

## Project configuration

Keep `.python-version` pinned to Python 3.13 and add
`python-preference = "only-managed"` under `[tool.uv]` in
`caption/pyproject.toml`. This makes ordinary project commands such as
`uv sync` and `uv run` reject system Python installations and select a Python
distribution managed by uv.

The Finder launcher also passes `--managed-python` explicitly. This keeps its
runtime requirement visible at the execution boundary and protects the launcher
if it is used with configuration discovery disabled or changed later.

## Existing environments

uv detects when an existing project environment uses a disallowed system
Python and recreates `caption/.venv` with managed Python. Document a manual
`uv venv --clear` recovery command in case that automatic migration is
interrupted. Hugging Face model caches and dataset files are outside the
virtual environment and remain untouched.

## Verification

Add project-configuration tests for the uv preference and launcher flag. Run
those tests red before implementation and green afterward, then run the full
test suite. Recreate the local virtual environment with uv-managed Python and
verify `import tkinter` in a non-GUI command. Do not instantiate `tk.Tk()` or
launch the desktop app.
