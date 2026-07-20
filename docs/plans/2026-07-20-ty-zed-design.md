# ty and Zed Type Checking Design

## Goal

Use Astral ty as Caption's reproducible command-line type checker and Zed's
primary Python language server, while retaining Ruff for linting and formatting.

## Project tooling

Add ty to Caption's uv development dependency group so every developer and Zed
can use the locked version from `.venv`. Add `uv run ty check` to the documented
development gate. Run ty over all project Python files and fix its diagnostics
with real narrowing or stronger types rather than broad ignores.

## Zed integration

Add a repository-level `.zed/settings.json`. Configure Python language servers
as `ty` and `ruff`; omitting BasedPyright disables it. Keep Ruff's organize-
imports action and formatter, with format-on-save enabled. Zed will prefer the
ty binary installed in the active project virtual environment.

## Verification

Run locked uv synchronization, `ty check`, Ruff lint and format checks, and the
full pytest suite. Review the diff and commit only project tooling, Zed settings,
documentation, and necessary typing fixes.
