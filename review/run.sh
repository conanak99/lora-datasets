#!/bin/bash
# Launch the caption review app. Opens a folder picker if no folder is given.
set -e
cd "$(dirname "$0")"

# uv may not be on PATH when launched from Finder.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"

exec uv run main.py "$@"
