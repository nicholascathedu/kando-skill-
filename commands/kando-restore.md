---
description: Put back an earlier snapshot of your Kando menus and settings
argument-hint: "[snapshot name, or empty for a list]"
---

Restore one of the user's Kando backups.

1. Run `python "${CLAUDE_PLUGIN_ROOT}/skills/kando/scripts/kando_backup.py" list`.
   On Windows, if `python` is the Microsoft Store stub, use `py -3` or `uv run --no-project python`.
2. If `$ARGUMENTS` names one of the listed backups, use it. Otherwise show the newest few in
   plain words (when each was made, and what's in it) and ask which one to restore.
3. Restore it with `... kando_backup.py restore <name>`. The script saves the current files
   first, so tell the user the restore can be undone and which snapshot undoes it.
4. Run `kando_check.py` on the restored `menus.json` and report the result in one line.
   Kando reloads `menus.json` and `config.json` by itself, so there's nothing to restart.
