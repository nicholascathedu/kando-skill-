#!/usr/bin/env python3
"""Keep your own menu tweaks when the menus underneath them change.

    python kando_overlay.py extract base.json current.json -o my-tweaks.json
    python kando_overlay.py apply new-base.json my-tweaks.json -o menus.json

The idea comes from Omarchy, which keeps its defaults and your overrides in separate files so
an update never wipes your changes. Here the base is a menus file Claude or an example built,
and the overlay holds only what you changed by hand in Kando's editor:

- `extract` compares your current menus with the base they started from and writes the
  differences: items you added or changed, items you removed, and changed menu settings
  (shortcut, conditions...).
- `apply` puts those differences on top of a new base, checks the result with the checker and
  writes it (backing up the target first if it exists).

Menus are matched by their root name and items by their name path (Maya > Save > Incremental),
so renaming an item counts as removing one and adding another. An overlay is an ordinary
menus file whose items may carry "remove": true. Standard library only.
"""

import argparse
import copy
import json
import os
import shutil
import sys
import time

from kando_check import Report, check_menus
from kando_layout import (KandoFileError, child_items, item_name, menu_list, read_json,
                          use_utf8_output)


def by_name(items):
    return {item_name(i): i for i in items}


def diff_items(base, mine):
    """Overlay children turning `base` children into `mine` children."""
    old, out = by_name(base), []
    for item in mine:
        name = item_name(item)
        if name not in old:
            out.append(copy.deepcopy(item))
        elif item != old[name]:
            if item.get("type") == old[name].get("type") == "submenu":
                patch = {k: v for k, v in item.items() if k != "children" and old[name].get(k) != v}
                patch.update(name=name, type="submenu",
                             children=diff_items(child_items(old[name]), child_items(item)))
                out.append(patch)
            else:
                out.append(copy.deepcopy(item))
    out += [{"name": n, "remove": True} for n in old if n not in by_name(mine)]
    return out


def apply_items(base, overlay):
    items = [copy.deepcopy(i) for i in base]
    for patch in overlay:
        names = [item_name(i) for i in items]
        name = item_name(patch)
        at = names.index(name) if name in names else None
        if patch.get("remove"):
            if at is not None:
                items.pop(at)
        elif at is None:
            items.append(copy.deepcopy(patch))
        elif patch.get("type") == items[at].get("type") == "submenu":  # merge, don't replace
            merged = dict(items[at], **{k: v for k, v in patch.items() if k != "children"})
            merged["children"] = apply_items(child_items(items[at]), patch.get("children", []))
            items[at] = merged
        else:
            items[at] = copy.deepcopy(patch)
    if all(isinstance(i.get("angle"), (int, float)) for i in items):
        items.sort(key=lambda i: i["angle"])  # Kando wants fixed angles in increasing order
    return items


def extract(base, current):
    base_menus = {item_name(m["root"]): m for m in menu_list(base)}
    out = []
    for m in menu_list(current):
        name = item_name(m["root"])
        if name not in base_menus:
            out.append(copy.deepcopy(m))
            continue
        b = base_menus[name]
        patch = {k: v for k, v in m.items() if k != "root" and b.get(k) != v}
        kids = diff_items(child_items(b["root"]), child_items(m["root"]))
        root_changes = {k: v for k, v in m["root"].items() if k != "children" and b["root"].get(k) != v}
        if patch or kids or root_changes:
            patch["root"] = dict(root_changes, name=name, type="root", children=kids)
            out.append(patch)
    gone = set(base_menus) - {item_name(m["root"]) for m in menu_list(current)}
    out += [{"root": {"name": n, "type": "root"}, "remove": True} for n in sorted(gone)]
    return {"version": current.get("version", "3.0.0"), "menus": out}


def apply(base, overlay):
    result = copy.deepcopy(base)
    menus = result.setdefault("menus", [])
    for patch in menu_list(overlay):
        name = item_name(patch["root"])
        at = next((i for i, m in enumerate(menus) if item_name(m["root"]) == name), None)
        if patch.get("remove"):
            if at is not None:
                menus.pop(at)
        elif at is None:
            menus.append(copy.deepcopy(patch))
        else:
            m = menus[at]
            m.update({k: v for k, v in patch.items() if k != "root"})
            root = dict(m["root"], **{k: v for k, v in patch["root"].items() if k != "children"})
            root["children"] = apply_items(child_items(m["root"]), patch["root"].get("children", []))
            m["root"] = root
    return result


def write(data, path):
    if os.path.isfile(path):
        shutil.copy2(path, f"{path}.{time.strftime('%Y%m%d-%H%M%S')}.bak")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def main(argv=None):
    use_utf8_output()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["extract", "apply"])
    ap.add_argument("first", help="extract: the base you started from; apply: the new base")
    ap.add_argument("second", help="extract: your current menus; apply: your overlay")
    ap.add_argument("-o", "--out", required=True, help="file to write")
    args = ap.parse_args(argv)
    try:
        first, second = read_json(args.first), read_json(args.second)
    except KandoFileError as e:
        sys.exit(f"Can't read the input: {e.reason}")
    if args.action == "extract":
        data = extract(first, second)
        print(f"{len(data['menus'])} menu(s) with your changes.")
    else:
        data = apply(first, second)
        rep = Report()
        check_menus(data, rep)
        if rep.count("ERROR"):
            rep.print()
            sys.exit("Not writing: the merged menus would have errors (see above).")
    write(data, args.out)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
