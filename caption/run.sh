#!/bin/bash
# Launch the caption app. A folder can be opened from the toolbar.
set -e
cd "$(dirname "$0")"

# uv may not be on PATH when launched from Finder.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"

exec uv run --managed-python main.py "$@"
