#!/bin/sh
# Starts menus_guard.py with the first working Python 3.9+. hooks.json runs this through sh
# on macOS, Linux and Windows with Git Bash; guard.ps1 does the same when Claude Code uses
# PowerShell. Without a working Python the guard stays out of the way.
input=$(cat)
case "$input" in
  *menus.json*) ;;
  *) exit 0 ;;
esac
here=$(dirname "$0")
for py in "py -3" python3 python "uv run --no-project python"; do
  if $py -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >/dev/null 2>&1; then
    printf '%s' "$input" | $py "$here/menus_guard.py" "$1"
    exit $?
  fi
done
exit 0
