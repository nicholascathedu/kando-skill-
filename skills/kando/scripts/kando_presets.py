#!/usr/bin/env python3
"""Switch Kando between settings presets: learning, speed, pen, or your own.

    python kando_presets.py list
    python kando_presets.py show speed          # what it would change, nothing written
    python kando_presets.py apply speed         # back up config.json, check, then write
    python kando_presets.py apply kando         # Kando's defaults for every preset setting
    python kando_presets.py save my-painting    # keep your current values as a preset

A preset only touches the settings it names; everything else in config.json stays as it is.
Before writing, the new settings go through the checker, and the old config.json is copied to
claude-backups/config-<time>-before-<preset>.json. Kando reloads config.json by itself, so a
Kando item can switch presets: execute-command `pythonw kando_presets.py apply pen`.
Your own presets live in claude-presets.json next to config.json. Standard library only.
"""

import argparse
import json
import os
import shutil
import sys
import time

from kando_check import Report, check_config
from kando_layout import KandoFileError, find_kando_file, read_json, use_utf8_output

PRESETS = {
    # While the directions are still new: show more, forgive more.
    "learning": {"enableSelectionWedges": True, "drawQuickSelectKey": True,
                 "underlineQuickSelectKey": True, "fixedStrokeLength": 0,
                 "gesturePauseTimeout": 150, "rmbSelectsParent": True,
                 "fadeInDuration": 75, "fadeOutDuration": 100},
    # Directions are automatic: fire on distance, short fades, no extras.
    "speed": {"enableSelectionWedges": False, "drawQuickSelectKey": False,
              "fixedStrokeLength": 100, "gesturePauseTimeout": 100, "rmbSelectsParent": True,
              "fadeInDuration": 50, "fadeOutDuration": 70, "sameShortcutBehavior": "close",
              "windowsInkWorkaround": False},
    # Painting with a tablet: keep the ink fix, ignore pen jitter, no instant firing.
    "pen": {"windowsInkWorkaround": True, "fixedStrokeLength": 0, "gesturePauseTimeout": 200,
            "gestureMinStrokeAngle": 30, "gestureJitterThreshold": 20,
            "fadeInDuration": 75, "fadeOutDuration": 80},
}
# Kando 3.0's own defaults (general-settings-v1.ts) for every setting a preset touches.
KANDO_DEFAULTS = {
    "enableSelectionWedges": False, "drawQuickSelectKey": False, "underlineQuickSelectKey": True,
    "fixedStrokeLength": 0, "gesturePauseTimeout": 100, "rmbSelectsParent": False,
    "fadeInDuration": 75, "fadeOutDuration": 100, "sameShortcutBehavior": "nothing",
    "windowsInkWorkaround": True, "gestureMinStrokeAngle": 20, "gestureJitterThreshold": 10,
}
PRESETS["kando"] = KANDO_DEFAULTS
OWN = "claude-presets.json"


def own_presets(folder):
    path = os.path.join(folder, OWN)
    if not os.path.isfile(path):
        return {}
    data = read_json(path)
    return {k: v for k, v in data.items() if isinstance(v, dict)} if isinstance(data, dict) else {}


def all_presets(folder):
    return dict(PRESETS, **own_presets(folder))


def changes(cfg, preset):
    """[(setting, old, new)] for the settings the preset would change. A missing setting
    counts as Kando's default."""
    out = []
    for k, new in preset.items():
        old = cfg.get(k, KANDO_DEFAULTS.get(k))
        if old != new:
            out.append((k, old, new))
    return out


def apply(folder, name, cfg_path):
    presets = all_presets(folder)
    if name not in presets:
        sys.exit(f"No preset called {name}. Run 'list' to see them.")
    return apply_settings(folder, name, presets[name], cfg_path)


def apply_settings(folder, name, settings, cfg_path):
    """Write `settings` into config.json after checking them; `name` labels the backup."""
    cfg = read_json(cfg_path) if os.path.isfile(cfg_path) else {}
    diff = changes(cfg, settings)
    if not diff:
        return diff, None
    new = dict(cfg, **{k: v for k, _, v in diff})
    rep = Report()
    check_config(new, rep)
    if rep.count("ERROR"):
        rep.print()
        sys.exit(f"Not applying {name}: the result would have errors.")
    backup = None
    if os.path.isfile(cfg_path):
        os.makedirs(os.path.join(folder, "claude-backups"), exist_ok=True)
        backup = os.path.join(folder, "claude-backups",
                              f"config-{time.strftime('%Y%m%d-%H%M%S')}-before-{name}.json")
        shutil.copy2(cfg_path, backup)
    tmp = cfg_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, cfg_path)  # Kando never sees a half-written file
    return diff, backup


def save(folder, name, cfg_path):
    if name in PRESETS:
        sys.exit(f"{name} is a built-in preset; pick another name.")
    cfg = read_json(cfg_path) if os.path.isfile(cfg_path) else {}
    keys = sorted(set().union(*PRESETS.values()))
    mine = own_presets(folder)
    mine[name] = {k: cfg.get(k, KANDO_DEFAULTS[k]) for k in keys}
    with open(os.path.join(folder, OWN), "w", encoding="utf-8") as f:
        json.dump(mine, f, indent=2)
        f.write("\n")
    return mine[name]


def main(argv=None):
    use_utf8_output()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["list", "show", "apply", "save"])
    ap.add_argument("name", nargs="?")
    ap.add_argument("--dir", help="Kando config folder (default: Kando's own)")
    args = ap.parse_args(argv)
    folder = args.dir or os.path.dirname(find_kando_file("config.json") or
                                         find_kando_file("menus.json") or "")
    if not folder or not os.path.isdir(folder):
        sys.exit("Kando's config folder was not found. Pass it with --dir.")
    cfg_path = os.path.join(folder, "config.json")
    if args.action != "list" and not args.name:
        sys.exit(f"Name a preset: kando_presets.py {args.action} speed")
    try:
        if args.action == "list":
            for name, preset in all_presets(folder).items():
                print(f"{name:12} {', '.join(sorted(preset))}")
        elif args.action == "show":
            cfg = read_json(cfg_path) if os.path.isfile(cfg_path) else {}
            preset = all_presets(folder).get(args.name)
            if preset is None:
                sys.exit(f"No preset called {args.name}.")
            diff = changes(cfg, preset)
            for k, old, new in diff:
                print(f"{k}: {json.dumps(old)} -> {json.dumps(new)}")
            if not diff:
                print(f"Already on {args.name}.")
        elif args.action == "apply":
            diff, backup = apply(folder, args.name, cfg_path)
            if not diff:
                print(f"Already on {args.name}; nothing changed.")
            else:
                print(f"Applied {args.name}: " + ", ".join(f"{k} {json.dumps(n)}" for k, _, n in diff))
                if backup:
                    print(f"Old settings saved to {backup}")
        else:
            save(folder, args.name, cfg_path)
            print(f"Saved your current settings as '{args.name}'. Apply it with: apply {args.name}")
    except KandoFileError as e:
        sys.exit(f"config.json {e.reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
