# uv-Managed Python Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make Caption consistently use a uv-managed Python 3.13 distribution with working Tkinter support.

**Architecture:** Configure uv at the project level to allow only managed Python distributions and reinforce that requirement in the Finder launcher. Document the one-time migration for an existing Homebrew-backed virtual environment and verify Tkinter with an import-only command.

**Tech Stack:** uv, Python 3.13, Tkinter, pytest, TOML, Bash

---

### Task 1: Lock the intended project configuration with tests

**Files:**
- Create: `caption/tests/test_project_config.py`

**Step 1: Write the failing tests**

Add one test that parses `caption/pyproject.toml` and expects
`tool.uv.python-preference` to equal `only-managed`. Add a second test that
expects `caption/run.sh` to invoke `uv run --managed-python main.py`.

**Step 2: Run the tests to verify RED**

Run:

```bash
cd caption
uv run python -m pytest tests/test_project_config.py -v
```

Expected: both tests fail because the preference and launcher flag are absent.

### Task 2: Configure uv and update user instructions

**Files:**
- Modify: `caption/pyproject.toml`
- Modify: `caption/run.sh`
- Modify: `caption/README.md`

**Step 1: Add the minimal configuration**

Add:

```toml
[tool.uv]
python-preference = "only-managed"
```

Change the launcher command to:

```bash
exec uv run --managed-python main.py "$@"
```

Document the managed-Python requirement and the one-time `.venv` migration:

```bash
uv python install 3.13
uv venv --clear --python 3.13 --managed-python
uv sync
```

**Step 2: Run the focused tests to verify GREEN**

Run:

```bash
cd caption
uv run python -m pytest tests/test_project_config.py -v
```

Expected: both tests pass.

### Task 3: Migrate and verify the local environment

**Files:**
- Recreate locally, not tracked: `caption/.venv`

**Step 1: Install managed Python and synchronize the environment**

Run:

```bash
cd caption
uv python install 3.13
uv sync
```

Expected: uv detects and replaces an incompatible system-Python `.venv`, then
`.venv/bin/python` resolves to a uv-managed Python distribution and dependencies
synchronize from `uv.lock`. If automatic migration is interrupted, recover with
`uv venv --clear --python 3.13 --managed-python` before `uv sync`.

**Step 2: Verify Tkinter without opening the app**

Run:

```bash
uv run --managed-python python -c "import tkinter; print(tkinter.TkVersion)"
```

Expected: prints the Tk version and exits successfully without opening a window.

**Step 3: Run full verification**

Run:

```bash
uv run --managed-python python -m pytest -v
git diff --check
```

Expected: all tests pass and the diff check is clean.

### Task 4: Commit the implementation

**Step 1: Review and commit**

Stage only the Caption configuration, launcher, documentation, tests, and plan
files. Leave unrelated dataset and Finder metadata changes untouched.

```bash
git commit -m "fix: use uv-managed Python for Caption"
```
