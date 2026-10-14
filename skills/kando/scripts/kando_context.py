#!/usr/bin/env python3
"""Context actions: act on the file open in the app you opened the menu over.

    pythonw kando_context.py folder "{{window_name}}"     # open the file's folder
    pythonw kando_context.py copy   "{{window_name}}"     # copy the file's full path

Kando fills {{window_name}} with the title of the window that was in front when the menu
opened. Apps that put the full file path in the title (Maya does: "Autodesk Maya 2026:
C:\\scenes\\hero.mb* - ...") give this script the path. Apps that show only the file name
(Painter, VS Code) don't, so this can't work for them. Standard library only.
"""

import os
import re
import subprocess
import sys

PATH = re.compile(r'(?:[A-Za-z]:[\\/]|/)[^*:"<>|\r\n]*?\.[A-Za-z0-9]{1,8}(?=[*\s\]\)-]|$)')


def path_in_title(title):
    """The longest file path in a window title, or None."""
    found = [m.group(0).strip() for m in PATH.finditer(title or "")]
    return max(found, key=len) if found else None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2 or argv[0] not in ("folder", "copy"):
        print(__doc__, file=sys.stderr)
        return 2
    path = path_in_title(argv[1])
    if not path:
        print(f"No file path in the window title: {argv[1]!r}", file=sys.stderr)
        return 1
    if argv[0] == "copy":
        if os.name == "nt":
            subprocess.run(["clip"], input=path.encode("utf-16-le"), check=False)
        else:
            subprocess.run(["pbcopy"] if sys.platform == "darwin" else ["xclip", "-selection", "clipboard"],
                           input=path.encode(), check=False)
    elif os.name == "nt":
        subprocess.run(["explorer", "/select," + os.path.normpath(path)], check=False)
    else:
        subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", os.path.dirname(path)], check=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
