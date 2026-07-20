# Agent Instructions

Read `README.md` and, for Caption work, `caption/README.md`. Keep project and
usage details in those files rather than duplicating them here.

- Preserve unrelated working-tree changes and treat everything under `data/` as
  user-owned. Do not alter dataset files unless explicitly requested.
- For Caption changes, work from `caption/` and run every check listed under
  **Development checks** in `caption/README.md` before reporting completion.
- Do not commit unless the user asks.
- Before every commit, delete the entire `docs/plans/` directory if it exists.
  Never commit files under `docs/plans/`; include their deletions in the commit.
- Inspect the staged diff and run `git diff --cached --check` before committing.
