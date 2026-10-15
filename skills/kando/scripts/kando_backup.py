#!/usr/bin/env python3
"""Save, list and restore snapshots of Kando's settings.

    python kando_backup.py save [--label before-maya-menu]
    python kando_backup.py list
    python kando_backup.py restore [NAME]       # newest snapshot if NAME is left out

A snapshot is a folder in <kando config>/claude-backups/ holding menus.json, config.json and
kando-profile.md (whichever exist). Restoring first saves the current files as a new snapshot,
so a restore can always be undone. Kando reloads menus.json and config.json by itself.
The menu guard's automatic menus-*.json copies live in the same folder and are listed too.
Use --dir to point at a config folder other than Kando's own. Standard library only.
"""

import argparse
import os
import re
import shutil
import sys
import time

from kando_layout import KandoFileError, find_kando_file, read_json

FILES = ("menus.json", "config.json", "kando-profile.md")
BACKUP_DIR = "claude-backups"


def config_dir(given):
    if given:
        return given
    found = find_kando_file("menus.json") or find_kando_file("config.json")
    if not found:
        sys.exit("Kando's config folder was not found. Pass it with --dir.")
    return os.path.dirname(found)


def snapshots(folder):
    """(name, path, kind) for every backup, oldest first by time. kind is 'snapshot' or 'guard'."""
    root = os.path.join(folder, BACKUP_DIR)
    if not os.path.isdir(root):
        return []
    out = []
    for n in sorted(os.listdir(root)):
        p = os.path.join(root, n)
        if os.path.isdir(p) and n.startswith("snapshot-"):
            out.append((n, p, "snapshot"))
        elif n.startswith("menus-") and n.endswith(".json"):
            out.append((n, p, "guard"))
    return sorted(out, key=lambda s: (os.path.getmtime(s[1]), s[0]))


def save(folder, label=""):
    present = [f for f in FILES if os.path.isfile(os.path.join(folder, f))]
    if not present:
        sys.exit(f"Nothing to back up in {folder}.")
    label = re.sub(r"[^A-Za-z0-9_-]+", "-", label).strip("-")[:40]
    name = "snapshot-" + time.strftime("%Y%m%d-%H%M%S") + (f"-{label}" if label else "")
    dest, n = os.path.join(folder, BACKUP_DIR, name), 1
    while os.path.exists(dest):
        dest, n = os.path.join(folder, BACKUP_DIR, f"{name}-{n}"), n + 1
    os.makedirs(dest)
    for f in present:
        shutil.copy2(os.path.join(folder, f), dest)
    return dest, present


def restore(folder, name=None):
    snaps = snapshots(folder)
    if not snaps:
        sys.exit("There are no backups yet.")
    pick = snaps[-1] if not name else next((s for s in snaps if s[0] == name), None)
    if not pick:
        sys.exit(f"No backup called {name}. Run 'list' to see them.")
    _, path, kind = pick
    sources = ({"menus.json": path} if kind == "guard" else
               {f: os.path.join(path, f) for f in FILES if os.path.isfile(os.path.join(path, f))})
    for f, src in sources.items():
        if f.endswith(".json"):
            try:
                read_json(src)
            except KandoFileError as e:
                sys.exit(f"Not restoring: the backup's {f} {e.reason}")
    undo, _ = save(folder, "before-restore")
    for f, src in sources.items():
        shutil.copy2(src, os.path.join(folder, f))
    return sorted(sources), undo


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["save", "list", "restore"])
    ap.add_argument("name", nargs="?", help="backup to restore (default: the newest)")
    ap.add_argument("--label", default="", help="a few words to add to the snapshot's name")
    ap.add_argument("--dir", help="Kando config folder (default: Kando's own)")
    args = ap.parse_args(argv)
    folder = config_dir(args.dir)
    if args.action == "save":
        dest, files = save(folder, args.label)
        print(f"Saved {', '.join(files)} to {dest}")
    elif args.action == "list":
        snaps = snapshots(folder)
        if not snaps:
            print("There are no backups yet.")
        for name, path, kind in snaps:
            what = "menus.json (automatic, before an edit)" if kind == "guard" else \
                ", ".join(f for f in FILES if os.path.isfile(os.path.join(path, f)))
            print(f"{name}    {what}")
    else:
        files, undo = restore(folder, args.name)
        print(f"Restored {', '.join(files)}. Kando reloads them by itself. "
              f"To undo, restore {os.path.basename(undo)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
