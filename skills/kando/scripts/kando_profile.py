#!/usr/bin/env python3
"""Draft a Kando profile: a short Markdown note about how this person uses Kando.

The skill should get more personal the more it is used. This script reads menus.json (and
optionally config.json) and writes down the facts it can find: which shortcut opens which
menu, where every top-level item sits, which items already share a direction across menus
(anchors to keep) and which ones drift, the apps the menus touch, and the look and feel
settings in use. The human parts (taste, voice, workflows, ideas they turned down) are left
as headings to fill in together. See references/profile.md for how the profile is used.

Usage:
    python kando_profile.py menus.json
    python kando_profile.py menus.json --config config.json
    python kando_profile.py menus.json --config config.json --out kando-profile.md

Privacy: the draft never contains full file paths, user folder names, email addresses or
long numbers. Commands are reduced to the program's name. Standard library only.
"""

import argparse
import datetime
import json
import math
import os
import re
import sys
from urllib.parse import urlsplit

from kando_check import PRIVACY_PATTERNS
from kando_layout import compass, levels, use_utf8_output

PLACEHOLDER = "- (add as you learn)"
MAX_DEPTH = 50  # deeper than any real menu; stops runaway recursion on odd files

# ------------------------------------------------------------------------- privacy --

USER_FOLDER = [
    re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[^\\/\"'\n]+", re.I),   # C:\Users\name
    re.compile(r"(?<![\w.])/(?:home|Users)/[^/\"'\n]+"),            # /home/name, /Users/name
]
# A path anchored at a drive, an env var, ~, a UNC share or a well-known Unix root.
ANCHORED_PATH = re.compile(
    r"(?:\b[A-Za-z]:|%\w+%|\$\{?\w+\}?|~|\\\\[^\\\s\"']+|(?<![\w.])(?=/(?:home|Users|root|mnt|"
    r"media|opt|usr|var|tmp|etc|Applications|Library|Volumes|run|snap|private)\b))"
    r"(?:[\\/][^\\/\s\"'<>|*?]+)+[\\/]?")
BACKSLASH_CHAIN = re.compile(r"(?:[^\s\\\"']*\\)+([^\s\\\"']*)")


def _redact_label(what):
    for word, label in (("email", "<email>"), ("number", "<number>"), ("handle", "<handle>"),
                        ("secret", "<secret>")):
        if word in what:
            return label
    return "~"  # user folders and home paths


REDACT = [(re.compile(p), _redact_label(w)) for p, w in PRIVACY_PATTERNS]


def basename(path):
    return re.split(r"[\\/]", path.rstrip("\\/"))[-1]


def scrub(text, color=False):
    """Make a string safe to keep in a profile: paths become their last part, and user
    names, emails, long numbers and secrets are replaced. color=True keeps #rgba values."""
    text = str(text)
    for pat in USER_FOLDER:
        text = pat.sub("~", text)
    text = ANCHORED_PATH.sub(lambda m: basename(m.group(0)), text)
    text = BACKSLASH_CHAIN.sub(lambda m: m.group(1), text)
    for pat, label in REDACT:
        if color and label == "<handle>":
            continue
        text = pat.sub(label, text)
    return text


def label(value, limit=60):
    """A readable, scrubbed one-line name, or '' if there isn't one."""
    if not isinstance(value, str):
        return ""
    text = scrub(" ".join(value.split()))
    return text if len(text) <= limit else text[:limit - 1] + "\u2026"


# ------------------------------------------------------------------------- reading --


def menu_list(data):
    """The readable menus of a menus.json or a single exported menu; skips the rest."""
    if isinstance(data, dict) and "menus" not in data and isinstance(data.get("menu"), dict):
        data = {"menus": [data["menu"]]}
    menus = data.get("menus") if isinstance(data, dict) else None
    if not isinstance(menus, list):
        return []
    return [m for m in menus if isinstance(m, dict) and isinstance(m.get("root"), dict)]


def clean_angle(value):
    """The angle as Kando's placement sees it (see kando_layout.raw_angle): a finite
    number, else None. Negative or out-of-order angles are left for the layout to ignore,
    the same way Kando does."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return float(value)


def clean_node(node, depth=0):
    """Copy just what the layout needs (type, name, angle, children), dropping anything
    unreadable, so the placement code only ever sees well-formed items."""
    out = {"type": node.get("type") if isinstance(node.get("type"), str) else "",
           "name": label(node.get("name")) or "(unnamed)"}
    angle = clean_angle(node.get("angle"))
    if angle is not None:
        out["angle"] = angle
    kids = node.get("children")
    out["children"] = ([clean_node(c, depth + 1) for c in kids if isinstance(c, dict)]
                       if isinstance(kids, list) and depth < MAX_DEPTH else [])
    return out


def placed_items(menu):
    """(depth, path, item, angle) for every item, where Kando really puts it.
    depth 1 = the top ring. path starts with the menu's name."""
    try:
        out = []
        for path, node, _parent, angles in levels({"root": clean_node(menu["root"])}):
            for child, angle in zip(node["children"], angles):
                out.append((len(path), path, child, angle % 360))
        return out
    except (TypeError, ValueError, KeyError, AttributeError, RecursionError):
        return []


def walk_items(node, depth=0):
    if not isinstance(node, dict) or depth > MAX_DEPTH:
        return
    yield node
    kids = node.get("children")
    if isinstance(kids, list):
        for c in kids:
            yield from walk_items(c, depth + 1)


def actions_of(item):
    for key in ("selectWorkflow", "openWorkflow", "activateWorkflow", "hoverWorkflow"):
        wf = item.get(key)
        acts = wf.get("actions") if isinstance(wf, dict) else None
        if isinstance(acts, list):
            yield from (a for a in acts if isinstance(a, dict))


def shortcut_of(menu):
    sc = menu.get("shortcut")
    if isinstance(sc, str) and sc.strip():
        return label(sc)
    sid = menu.get("shortcutID")
    if isinstance(sid, str) and sid.strip():
        return f"shortcut ID {label(sid)}"
    return ""


def conditions_of(menu):
    """Plain words for a menu's conditions, '' when it opens everywhere."""
    cond = menu.get("conditions")
    if not isinstance(cond, dict):
        return ""
    bits = []
    for key, what in (("appName", "app"), ("windowName", "window title")):
        v = cond.get(key)
        if isinstance(v, str) and v.strip():
            how = "matches" if v.startswith("/") else "contains"
            bits.append(f'{what} {how} "{label(v)}"')
    area = cond.get("screenArea")
    if isinstance(area, dict) and any(v not in (None, "") for v in area.values()):
        bits.append("pointer in a screen area")
    return ", ".join(bits)


# ------------------------------------------------------------------ app detection --

TOKEN = re.compile(r'"([^"]*)"|\'([^\']*)\'|(\S+)')
WRAPPERS = {"start", "cmd", "cmd.exe", "call", "open", "xdg-open", "gio", "gtk-launch",
            "kioclient", "kioclient5", "kde-open", "kde-open5", "env", "nohup", "setsid",
            "exec", "flatpak", "snap", "run", "powershell", "powershell.exe", "pwsh",
            "start-process", "sh", "bash", "zsh", "/bin/sh", "/bin/bash", "/usr/bin/env"}
SHELL_FLAGS = {"-c", "/c", "/k", "-command"}   # the next token is a whole command line
VALUE_FLAGS = {"/d"}                           # start /d <folder> app
NOT_APPS = {"echo", "cd", "set", "export", "rem", "true", "false", "exit", "sleep", "timeout"}
EXTENSIONS = re.compile(r"\.(exe|lnk|app|bat|cmd|com|sh|appimage|desktop|ps1|py|url)$", re.I)
URI = re.compile(r"^([A-Za-z][\w.+-]+):")


def program_name(token):
    name = EXTENSIONS.sub("", basename(token.strip()))
    if name.count(".") >= 2 and " " not in name:
        name = name.rsplit(".", 1)[-1]  # flatpak / bundle IDs: org.blender.Blender -> Blender
    name = label(name, 40)
    return "" if not name or name.startswith(("%", "$", "<", "~")) else name


def link_name(uri):
    try:
        parts = urlsplit(uri)
    except ValueError:
        return None
    scheme = parts.scheme.lower()
    if scheme in ("http", "https"):
        host = (parts.hostname or "").lower()
        host = host[4:] if host.startswith("www.") else host
        return ("site", label(host)) if host else None
    if not scheme or scheme == "file":
        return None
    return ("link", scheme + ("://" if uri[len(scheme) + 1:].startswith("//") else ":"))


def command_target(command, depth=0):
    """Best guess at what a command starts: ('app', name), ('site'|'link', name) or None.
    'start "" "%LOCALAPPDATA%\\Discord\\Update.exe" --processStart Discord.exe' -> Discord."""
    toks = [next((g for g in groups if g), "") for groups in TOKEN.findall(command)]
    lows = [t.lower() for t in toks]
    skip, prev = False, ""
    for tok, low in zip(toks, lows):
        tok = tok.strip()
        if skip:
            skip = False
            continue
        if prev in SHELL_FLAGS and depth < 3:
            return command_target(tok, depth + 1)
        prev = low
        if not tok or low in WRAPPERS or low in SHELL_FLAGS or re.match(r"^\w+=", tok):
            continue
        if low in VALUE_FLAGS:
            skip = True
            continue
        if tok.startswith("-") or re.fullmatch(r"/[A-Za-z?]{1,5}", tok):
            continue  # a switch, not the program
        if low in NOT_APPS:
            return None
        if URI.match(tok) and not re.match(r"^[A-Za-z]:[\\/]", tok):
            return link_name(tok)
        name = program_name(tok)
        if name.lower() == "update" and "--processstart" in lows:  # Squirrel apps (Discord...)
            i = lows.index("--processstart")
            name = program_name(toks[i + 1]) if i + 1 < len(toks) else name
        return ("app", name) if name else None
    return None


def apps_touched(menus):
    """{'conditions': [...], 'apps': [...], 'sites': [...], 'links': [...]}, deduplicated
    case-insensitively, in first-seen order."""
    found = {"conditions": {}, "apps": {}, "sites": {}, "links": {}}

    def add(kind, name):
        if name:
            found[kind].setdefault(name.casefold(), name)

    for menu in menus:
        cond = menu.get("conditions")
        if isinstance(cond, dict):
            add("conditions", label(cond.get("appName")))
        for item in walk_items(menu["root"]):
            for act in actions_of(item):
                t = act.get("type")
                target = None
                if t == "execute-command" and isinstance(act.get("command"), str):
                    target = command_target(act["command"])
                elif t == "open-uri" and isinstance(act.get("uri"), str):
                    target = link_name(act["uri"])
                elif t == "focus-window":
                    target = ("app", label(act.get("appName")))
                if target:
                    kind, name = target
                    add({"app": "apps", "site": "sites", "link": "links"}[kind], name)
    return {k: list(v.values()) for k, v in found.items()}


# ---------------------------------------------------------------------- analysis --


def anchors_and_drift(placed):
    """placed: [(menu_index, [(depth, path, item, angle), ...]), ...].
    Items with the same name (any case) at the same depth in two or more menus are anchors
    when they share a compass direction everywhere, and drift when they don't."""
    groups = {}
    for mi, items in placed:
        for depth, path, item, angle in items:
            key = (depth, item["name"].casefold())
            if item["name"] == "(unnamed)":
                continue
            where = " > ".join(path)
            groups.setdefault(key, []).append((mi, item["name"], where, compass(angle)))
    anchors, drift = [], []
    for (depth, _), hits in sorted(groups.items(), key=lambda kv: kv[0][0]):
        if len({h[0] for h in hits}) < 2:
            continue
        (anchors if len({h[3] for h in hits}) == 1 else drift).append((depth, hits))
    return anchors, drift


def ring_note(depth):
    return "" if depth == 1 else " (inside a submenu)" if depth == 2 else f" (ring {depth})"


# ------------------------------------------------------------------------- writing --

LOOK_KEYS = ["menuTheme", "darkMenuTheme", "enableDarkModeForMenuThemes", "soundTheme",
             "soundVolume", "zoomFactor", "enableSelectionWedges", "drawQuickSelectKey",
             "underlineQuickSelectKey", "enableMenuAnimations", "enablePointerReactiveEffects"]
FEEL_KEYS = ["enableMarkingMode", "enableTurboMode", "fixedStrokeLength", "fadeInDuration",
             "fadeOutDuration", "centerDeadZone", "minParentDistance", "maxSelectionRadius",
             "hoverModeNeedsConfirmation", "rmbSelectsParent", "keepInputFocus", "warpMouse",
             "sameShortcutBehavior", "enableGamepad"]


def value_text(v):
    return label(v, 40) if isinstance(v, str) else json.dumps(v)


def config_section(cfg):
    lines = []
    look = [k for k in LOOK_KEYS if k in cfg and isinstance(cfg[k], (bool, int, float, str))]
    for k in look:
        lines.append(f"- {k}: {value_text(cfg[k])}")
    for key in ("menuThemeColors", "darkMenuThemeColors"):
        if key not in cfg:
            continue
        themes = cfg[key]
        if not isinstance(themes, dict) or not any(isinstance(c, dict) and c for c in themes.values()):
            lines.append(f"- {key}: no overrides")
            continue
        for theme, colors in themes.items():
            if not isinstance(colors, dict) or not colors:
                continue
            shown = [f"{label(n, 30)} {scrub(str(v), color=True)[:40]}"
                     for n, v in list(colors.items())[:12] if isinstance(v, str)]
            more = f", +{len(colors) - 12} more" if len(colors) > 12 else ""
            lines.append(f"- {key} for {label(theme, 40)}: {'; '.join(shown)}{more}")
    feel = [k for k in FEEL_KEYS if k in cfg and isinstance(cfg[k], (bool, int, float, str))]
    if feel:
        lines.append("- Selection: " + ", ".join(f"{k} {value_text(cfg[k])}" for k in feel))
    return lines


def build_profile(data, cfg=None, sources="menus.json", today=None):
    menus = menu_list(data)
    today = today or datetime.date.today().isoformat()
    out = ["# Kando profile", "",
           f"Draft from {sources}, {today}. Facts first, then the parts only you can fill in.",
           "Edit it freely. Claude reads it at the start of every Kando task.", ""]
    if not menus:
        out += ["No readable menus found. Fix menus.json with kando_check.py, then run this again.", ""]

    # Shortcuts ---------------------------------------------------------------------
    by_key, no_key = {}, []
    for m in menus:
        sc = shortcut_of(m)
        name = label(m["root"].get("name")) or "(unnamed)"
        if sc:
            by_key.setdefault(sc.casefold(), (sc, []))[1].append((name, conditions_of(m)))
        else:
            no_key.append(name)
    if by_key or no_key:
        out += ["## Shortcuts", ""]
        for sc, entries in by_key.values():
            out.append(f"- {sc} opens:")
            fallback = " (the fallback)" if any(cond for _, cond in entries) else ""
            for name, cond in entries:
                out.append(f"  - {name}, {'when ' + cond if cond else 'everywhere' + fallback}")
            if all(cond for _, cond in entries):
                out.append("  - No fallback. In any other app the key is swallowed and nothing opens.")
        if no_key:
            out.append(f"- No shortcut (opened by open-menu, the CLI or IPC): {', '.join(no_key)}")
        out.append("")

    # Directions --------------------------------------------------------------------
    placed = [(mi, placed_items(m)) for mi, m in enumerate(menus)]
    if any(items for _, items in placed):
        out += ["## Directions", "", "Top ring of each menu, where Kando really puts each item.", ""]
        for (_, items), m in zip(placed, menus):
            top = sorted((it for it in items if it[0] == 1), key=lambda it: it[3])
            if not top:
                continue
            out.append(f"### {label(m['root'].get('name')) or '(unnamed)'}")
            out.append("")
            for _, _, item, angle in top:
                notes = []
                if item["type"] == "submenu":
                    n = len(item["children"])
                    notes.append(f"submenu, {n} item{'' if n == 1 else 's'}")
                if "angle" not in item:
                    notes.append("auto-placed")
                extra = f" ({', '.join(notes)})" if notes else ""
                out.append(f"- {compass(angle)} ({angle:.0f}\u00b0): {item['name']}{extra}")
            out.append("")

    # Anchors and drift -------------------------------------------------------------
    anchors, drift = anchors_and_drift(placed)
    if anchors:
        out += ["## Anchors", "",
                "Same item, same direction, in more than one menu. Keep these where they are.", ""]
        for depth, hits in anchors:
            places = ", ".join(dict.fromkeys(h[2] for h in hits))
            out.append(f"- {hits[0][1]}: {hits[0][3]} in {places}{ring_note(depth)}")
        out.append("")
    if drift:
        out += ["## Drift", "",
                "Same item, different directions. Aligning them means one gesture to learn.", ""]
        for depth, hits in drift:
            dirs = {}
            for h in hits:
                dirs.setdefault(h[3], []).append(h[2])
            parts = "; ".join(f"{d} in {', '.join(dict.fromkeys(w))}" for d, w in dirs.items())
            counts = sorted(((len(w), d) for d, w in dirs.items()), reverse=True)
            if counts[0][0] > counts[1][0]:
                tip = f"Most use {counts[0][1]}."
            else:
                tip = "Pick one direction for all of them."
            out.append(f"- {hits[0][1]}: {parts}{ring_note(depth)}. {tip}")
        out.append("")

    # Apps --------------------------------------------------------------------------
    apps = apps_touched(menus)
    if any(apps.values()):
        out += ["## Apps it touches", ""]
        for key, title in (("conditions", "Menus per app (appName)"),
                           ("apps", "Launched or focused"), ("sites", "Sites"),
                           ("links", "App links")):
            if apps[key]:
                out.append(f"- {title}: {', '.join(apps[key])}")
        out.append("")

    # Config ------------------------------------------------------------------------
    if cfg is not None:
        lines = config_section(cfg) if isinstance(cfg, dict) else \
            ["- config.json is not a settings object, so nothing was read from it."]
        out += ["## Look and feel", ""]
        out += lines or ["- config.json had none of the theme or selection settings this reads."]
        out.append("")

    # The human part ----------------------------------------------------------------
    icon_themes = {}
    for m in menus:
        for item in walk_items(m["root"]):
            t = label(item.get("iconTheme"), 40)
            if t:
                icon_themes[t] = icon_themes.get(t, 0) + 1
    out += ["## Taste and voice", "",
            "- Palette words: (add as you learn)",
            "- Naming style: (add as you learn)",
            "- Icon style: (add as you learn)"]
    if icon_themes:
        common = sorted(icon_themes.items(), key=lambda kv: -kv[1])
        out.append("- Icon themes in use: " + ", ".join(f"{t} ({n})" for t, n in common))
    out += ["", "## Workflows I care about", "", PLACEHOLDER, "",
            "## Things I said no to", "", PLACEHOLDER, ""]

    text = "\n".join(out)
    for pat, lab in REDACT:  # last safety net over everything written above
        if lab != "<handle>":
            text = pat.sub(lab, text)
    return text


# ------------------------------------------------------------------------------ main --


UNREADABLE = object()


def load(path, what):
    """Parsed JSON, or UNREADABLE with a message on stderr. Never prints the full path."""
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Cannot find {what} ({name}).", file=sys.stderr)
    except UnicodeDecodeError:
        print(f"{name} is not UTF-8 text. Kando reads its files as UTF-8; re-save it as UTF-8.",
              file=sys.stderr)
    except OSError as e:
        print(f"Cannot read {name}: {e.__class__.__name__}.", file=sys.stderr)
    except json.JSONDecodeError as e:
        print(f"{name} is not valid JSON (line {e.lineno}, column {e.colno}). "
              "Run kando_check.py on it first.", file=sys.stderr)
    except RecursionError:
        print(f"{name} is nested too deeply to read.", file=sys.stderr)
    return UNREADABLE


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("menus", help="menus.json, or a single exported menu .json")
    ap.add_argument("--config", help="config.json, for theme and selection settings")
    ap.add_argument("--out", help="write the draft to this file instead of printing it")
    ap.add_argument("--force", action="store_true", help="let --out replace an existing file")
    args = ap.parse_args()
    use_utf8_output()
    data = load(args.menus, "the menus file")
    if data is UNREADABLE:
        sys.exit(2)
    cfg, sources = None, os.path.basename(args.menus)
    if args.config:
        cfg = load(args.config, "the config file")
        if cfg is UNREADABLE:
            cfg = None
        else:
            sources += " and " + os.path.basename(args.config)
    text = build_profile(data, cfg, sources)
    if not args.out:
        print(text)
        return
    if os.path.exists(args.out) and not args.force:
        print(f"{os.path.basename(args.out)} already exists and may hold notes written by hand. "
              "Print to the screen and merge, or pass --force to replace it.", file=sys.stderr)
        sys.exit(1)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Wrote {os.path.basename(args.out)}")


if __name__ == "__main__":
    main()
