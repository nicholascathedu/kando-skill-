#!/usr/bin/env python3
"""Live menus: build a pie from what's on disk right now and show it through Kando.

    python kando_live.py maya                       # your 8 most recent Maya scenes
    python kando_live.py recent <folder> --ext .spp .uproject   # newest files in a folder

Run it from a Kando item (execute-command, after close-menu). It sends Kando a
show-custom-menu message, waits for the pick and opens that file with its default app,
then exits. A static menu can't do this: the list changes every day.
Standard library only; needs Kando running (it talks to Kando's local IPC).
"""

import argparse
import glob
import os
import re
import subprocess
import sys

from kando_layout import use_utf8_output

MAX_ITEMS = 8  # more than 8 and the pie stops being fast to read


def maya_recent(home=None):
    """Recent scenes from Maya's RecentFilesList (newest Maya prefs folder), newest first."""
    home = home or os.path.expanduser("~")
    prefs = glob.glob(os.path.join(home, "Documents", "maya", "*", "prefs", "userPrefs.mel"))
    prefs += glob.glob(os.path.join(home, "maya", "*", "prefs", "userPrefs.mel"))
    if not prefs:
        return []
    with open(max(prefs, key=os.path.getmtime), encoding="utf-8", errors="replace") as f:
        found = re.findall(r'-sva\s+"RecentFilesList"\s+"([^"]+)"', f.read())
    out = []
    for p in reversed(found):  # Maya appends the newest scene last
        if p not in out and os.path.isfile(p):
            out.append(p)
    return out[:MAX_ITEMS]


def newest_files(folder, exts, depth=3):
    found = []
    base = os.path.abspath(folder)
    for root, dirs, files in os.walk(base):
        if root[len(base):].count(os.sep) >= depth:
            dirs[:] = []
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        found += [os.path.join(root, f) for f in files if f.lower().endswith(tuple(exts))]
    return sorted(found, key=os.path.getmtime, reverse=True)[:MAX_ITEMS]


def build_menu(title, paths, icon="description"):
    """A Kando root item with one button per file, spread evenly around the ring."""
    def label(p):
        stem = os.path.splitext(os.path.basename(p))[0]
        return stem if len(stem) <= 24 else stem[:23] + "…"
    return {"type": "root", "name": title, "icon": "history", "iconTheme": "material-symbols-rounded",
            "activateWorkflow": {"actions": [{"type": "close-menu"}]},
            "children": [{"type": "button", "name": label(p), "icon": icon,
                          "iconTheme": "material-symbols-rounded",
                          "selectWorkflow": {"actions": [{"type": "close-menu"}]}} for p in paths]}


def open_file(path):
    if os.name == "nt":
        os.startfile(path)  # noqa: S606 - opening the user's own file is the point
    else:
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", path])


def show(title, paths, socket_factory=None):
    """Show the pie and open the picked file. Returns the picked path or None."""
    if not paths:
        print("Nothing to show: no matching files were found.", file=sys.stderr)
        return None
    if socket_factory is None:
        from kando_ws import KandoSocket as socket_factory
    ws = socket_factory()
    try:
        ws.send({"type": "show-custom-menu", "menu": build_menu(title, paths)})
        while True:
            msg = ws.receive()
            if msg is None:
                return None
            if msg.get("type") == "error":
                print(f"Kando said: {msg.get('description') or msg.get('reason')}", file=sys.stderr)
                return None
            if msg.get("type") != "menu-interaction":
                continue
            if msg.get("interaction") == "selectButton" and msg.get("path"):
                picked = paths[msg["path"][0]]
                open_file(picked)
                return picked
            if msg.get("interaction") == "closeMenu":
                return None
    finally:
        ws.close()


def main(argv=None):
    use_utf8_output()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", choices=["maya", "recent"])
    ap.add_argument("folder", nargs="?")
    ap.add_argument("--ext", nargs="+", default=[], help="file endings for 'recent', e.g. .spp")
    ap.add_argument("--title", default=None)
    args = ap.parse_args(argv)
    if args.source == "maya":
        paths, title = maya_recent(), args.title or "Recent Maya scenes"
    else:
        if not args.folder or not args.ext:
            ap.error("recent needs a folder and --ext")
        paths, title = newest_files(args.folder, [e.lower() for e in args.ext]), args.title or "Recent files"
    try:
        show(title, paths)
    except Exception as e:  # shown in Kando's log; never a traceback dialog
        print(e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
