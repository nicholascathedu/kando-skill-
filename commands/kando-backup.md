---
description: Save a snapshot of your Kando menus, settings and profile before trying something new
argument-hint: "[a few words to name it]"
---

Save a snapshot of the user's Kando setup.

1. Run `python "${CLAUDE_PLUGIN_ROOT}/skills/kando/scripts/kando_backup.py" save --label "$ARGUMENTS"`.
   On Windows, if `python` is the Microsoft Store stub, use `py -3` or `uv run --no-project python`.
2. Tell the user in one or two sentences where the snapshot is and that `/kando-restore` brings it back.

If the script can't find Kando's config folder, ask the user where Kando keeps `menus.json` and
pass that folder with `--dir`.
