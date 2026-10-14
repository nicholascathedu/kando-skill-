#!/usr/bin/env python3
"""menus.json guard: a Claude Code hook that ships with the Kando plugin.

Kando watches menus.json and reloads it as soon as it changes, so every edit Claude makes is
live at once. This hook makes those edits safe:

    before  (PreToolUse on Edit / Write / MultiEdit)  copies menus.json into a
            claude-backups folder next to it (the newest 10 are kept).
    after   (PostToolUse)  runs kando_check.py on the new file. If the file is no longer
            valid JSON it puts the backup back and tells Claude why. If the checker finds
            errors it tells Claude, so Claude fixes them in the same turn.

Only files named menus.json inside a Kando config folder (a folder named "kando", or one
that also holds config.json) are touched. Everything else passes straight through.
Edits made from a shell command (a script writing the file) don't trigger it.
Standard library only, Python 3.9+.
"""

import json
import os
import shutil
import subprocess
import sys
import time

KEEP = 10
BACKUP_DIR = "claude-backups"
HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(HERE, "..", "skills", "kando", "scripts", "kando_check.py")


def target(event):
    """Return the menus.json path this tool call writes, or None."""
    path = (event.get("tool_input") or {}).get("file_path") or ""
    if os.path.basename(path).lower() != "menus.json":
        return None
    if not os.path.isabs(path):
        path = os.path.join(event.get("cwd") or os.getcwd(), path)
    folder = os.path.dirname(path)
    if os.path.basename(folder).lower() == "kando" or os.path.isfile(os.path.join(folder, "config.json")):
        return path
    return None


def backups(path):
    folder = os.path.join(os.path.dirname(path), BACKUP_DIR)
    if not os.path.isdir(folder):
        return folder, []
    names = sorted(n for n in os.listdir(folder) if n.startswith("menus-") and n.endswith(".json"))
    return folder, [os.path.join(folder, n) for n in names]


def before(path):
    if not os.path.isfile(path):
        return
    folder, old = backups(path)
    os.makedirs(folder, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time() * 1000) % 1000:03d}"
    copy, n = os.path.join(folder, f"menus-{stamp}.json"), 1
    while os.path.exists(copy):
        copy, n = os.path.join(folder, f"menus-{stamp}-{n}.json"), n + 1
    shutil.copy2(path, copy)
    for extra in old[:max(0, len(old) - KEEP + 1)]:
        try:
            os.remove(extra)
        except OSError:
            pass


def is_json(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            text = f.read()
        if not text.strip():
            return False, "the file is empty"
        json.loads(text)
        return True, ""
    except (OSError, UnicodeDecodeError, ValueError, RecursionError) as e:
        return False, str(e)


def after(path):
    """Return (exit code, message for Claude)."""
    ok, why = is_json(path)
    _, saved = backups(path)
    if not ok:
        if saved:
            shutil.copy2(saved[-1], path)
            return 2, (f"menus.json stopped being valid JSON ({why}), so the menu guard put back "
                       f"the copy from just before this edit ({saved[-1]}). Make the change again "
                       "with valid JSON.")
        return 2, f"menus.json is not valid JSON ({why}) and there was no backup to restore. Fix it now."
    run = subprocess.run([sys.executable, CHECKER, path], capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    report = (run.stdout or "").strip()
    where = f" Backup from before this edit: {saved[-1]}" if saved else ""
    if run.returncode == 1:
        return 2, ("kando_check.py found errors in menus.json. Kando keeps the old menus until "
                   f"the file is valid again, so fix these now.{where}\n\n{report}")
    if run.returncode != 0:
        return 0, ""
    last = report.splitlines()[-1] if report else "checked"
    return 0, f"Menu guard: kando_check.py on menus.json: {last}{where}"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    path = target(event)
    if not path:
        return 0
    if mode == "before":
        before(path)
        return 0
    if mode == "after":
        code, message = after(path)
        if code == 2:
            print(message, file=sys.stderr)
        elif message:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                     "additionalContext": message}}))
        return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
