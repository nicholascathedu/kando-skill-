#!/usr/bin/env python3
"""Start an app only if it isn't running yet. Pair it with Kando's focus-window for one item
that brings the app forward when it's open and starts it when it's not:

    focus-window    appName: maya.exe
    execute-command pythonw kando_launch.py maya.exe "C:\\Program Files\\Autodesk\\Maya2026\\bin\\maya.exe"

Kando's focus-window brings the window forward if there is one and does nothing otherwise;
this script then starts the app only when no process with that name exists, so pressing the
item twice, or while the app is still loading, never opens a second copy.

    python kando_launch.py NAME.exe PATH [ARGS...]
    python kando_launch.py --check NAME.exe    # just say whether it's running

Windows only (macOS already does this with `open -a "App"`). Standard library only.
"""

import argparse
import csv
import io
import os
import subprocess
import sys

CREATE_NO_WINDOW = 0x08000000  # so pythonw doesn't flash a console for tasklist


def running(name, tasklist=None):
    """True when a process called `name` (e.g. maya.exe) exists. Case-insensitive, like
    Windows itself."""
    name = name if name.lower().endswith(".exe") else name + ".exe"
    if tasklist is None:
        tasklist = subprocess.run(["tasklist", "/fo", "csv", "/nh", "/fi", f"imagename eq {name}"],
                                  capture_output=True, text=True, creationflags=CREATE_NO_WINDOW,
                                  check=False).stdout
    return any(row and row[0].lower() == name.lower() for row in csv.reader(io.StringIO(tasklist)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="only report whether it's running")
    ap.add_argument("name", help="the process name, e.g. maya.exe (Task Manager > Details)")
    ap.add_argument("path", nargs="?", help="what to start when it isn't running")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="arguments for the app")
    args = ap.parse_args(argv)
    if os.name != "nt":
        sys.exit("kando_launch.py is for Windows. On macOS, `open -a \"App\"` already starts or "
                 "focuses an app.")
    if running(args.name):
        if args.check:
            print(f"{args.name} is running.")
        return 0
    if args.check:
        print(f"{args.name} isn't running.")
        return 1
    if not args.path:
        sys.exit("Give the path to start, e.g. kando_launch.py maya.exe \"C:\\...\\maya.exe\"")
    if args.args:
        subprocess.Popen([args.path] + args.args, creationflags=CREATE_NO_WINDOW)
    else:
        os.startfile(args.path)  # works for .exe, .lnk and documents alike
    return 0


if __name__ == "__main__":
    sys.exit(main())
