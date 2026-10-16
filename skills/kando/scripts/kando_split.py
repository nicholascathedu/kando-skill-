#!/usr/bin/env python3
"""Split a menus.json into one importable file per menu.

    python kando_split.py ../examples/3d-work-menus.json --out importable/

Kando's editor imports single menus ({"version", "menu"}), so instead of merging JSON by
hand you click Import and pick a file. Each file is named after its menu.
Standard library only.
"""

import argparse
import json
import os
import re
import sys

from kando_layout import KandoFileError, item_name, menu_list, read_json, use_utf8_output


def split(data):
    """[(file name, exported menu)] for every menu in a menus.json."""
    out, used = [], set()
    for m in menu_list(data):
        base = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "-", item_name(m["root"], "menu")).strip(" .-") or "menu"
        name, n = base, 2
        while name.lower() in used:
            name, n = f"{base} {n}", n + 1
        used.add(name.lower())
        out.append((name + ".json", {"version": data.get("version", "3.0.0"), "menu": m}))
    return out


def main(argv=None):
    use_utf8_output()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("menus")
    ap.add_argument("--out", default="importable")
    args = ap.parse_args(argv)
    try:
        data = read_json(args.menus)
    except KandoFileError as e:
        print(f"{args.menus} {e.reason}", file=sys.stderr)
        return 2
    os.makedirs(args.out, exist_ok=True)
    for name, exported in split(data):
        with open(os.path.join(args.out, name), "w", encoding="utf-8") as f:
            json.dump(exported, f, indent=2, ensure_ascii=False)
        print(os.path.join(args.out, name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
