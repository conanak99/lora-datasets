# Open Generated Folder Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Open the selected caption-generation folder automatically after every successful completed batch.

**Architecture:** Reuse `CaptionApp.open_folder` from the successful completion handler so existing save, image discovery, thumbnail, and navigation behavior remains centralized. Keep the error path unchanged.

**Tech Stack:** Python 3.13, Tkinter, pytest

---

### Task 1: Add the completion regression test

**Files:**
- Modify: `caption/tests/test_main.py`

**Step 1: Write the failing test**

Create a `CaptionApp` instance without Tk widgets using `__new__`, assign a
temporary generation folder, and replace `_reset_generation_controls`,
`_set_batch_status`, and `open_folder` with recording functions. Call
`_finish_generation` with a successful `GenerationResult` and assert that
`open_folder` receives the generation folder exactly once.

**Step 2: Run the focused test to verify RED**

```bash
cd caption
uv run --managed-python python -m pytest tests/test_main.py -v
```

Expected: the new test fails because the current handler only refreshes a
folder that is already open.

### Task 2: Open the folder after successful completion

**Files:**
- Modify: `caption/main.py`

**Step 1: Implement the minimal behavior**

Replace the current same-folder conditional refresh in `_finish_generation`
with:

```python
if self.generation_folder:
    self.open_folder(self.generation_folder)
```

Do not change `_fail_generation`.

**Step 2: Run the focused test to verify GREEN**

```bash
cd caption
uv run --managed-python python -m pytest tests/test_main.py -v
```

Expected: all startup and completion tests pass without opening a window.

### Task 3: Verify and commit

**Step 1: Run full verification**

```bash
cd caption
uv run --managed-python python -m pytest -v
git diff --check
```

Expected: all tests pass and the diff check is clean.

**Step 2: Commit only this feature**

```bash
git commit -m "feat: open generated folder on completion"
```
