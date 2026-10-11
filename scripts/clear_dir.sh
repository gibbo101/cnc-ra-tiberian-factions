#!/usr/bin/env bash
# Delete a folder without rm -rf: plain rm on every non-directory, then rmdir the emptied folders.
# A wrong path can only fail. A missing folder is not an error. Usage: clear_dir.sh <dir>...
set -euo pipefail

for dir in "$@"; do
    case "$dir" in
        "" | / | "$HOME" | "$HOME/") echo "clear_dir.sh: refusing '$dir'" >&2; exit 1 ;;
    esac
    [[ -e "$dir" ]] || continue
    find "$dir" ! -type d -exec rm -- {} +
    find "$dir" -depth -type d -exec rmdir -- {} +
done
