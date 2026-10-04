#!/usr/bin/env python3
"""Check Kando 3.x menus.json / config.json files before Kando loads them.

Kando validates its files on load and silently refuses to reload an invalid one, so a
typo means "nothing happens". This script finds those typos first, plus a set of
design problems Kando itself accepts but that make menus slow or confusing.

Usage:
    python kando_check.py menus.json
    python kando_check.py menus.json --config config.json
    python kando_check.py menus.json --publish     # also scan for personal data
    python kando_check.py exported-menu.json        # single exported menu works too

Exit code: 0 = no errors (warnings allowed), 1 = errors found, 2 = file missing or unreadable.
Standard library only. Written against Kando 3.0 schemas
(src/common/settings-schemata/menu-settings-v2.ts and general-settings-v1.ts).
"""

import argparse
import json
import re
import sys

from kando_layout import (angle_problems, angular_distance, compass, item_name, levels,
                          raw_angle, use_utf8_output)

# The newest settings format this checker knows. Kando refuses files from a newer major.
KANDO_MAJOR = 3
# Deeper than this the checker stops descending (nobody flicks 100 rings deep, and it keeps
# Python's recursion limit out of reach).
MAX_DEPTH = 100

# --------------------------------------------------------------------------- schema --

ACTION_FIELDS = {
    # type: {field: (python types, required)}
    "close-menu": {},
    "close-submenu": {},
    "delay": {"duration": ((int, float), True)},
    "execute-command": {"command": (str, True), "detached": (bool, False), "isolated": (bool, False)},
    "execute-macro": {"macro": (list, True)},
    "focus-window": {"windowName": (str, False), "appName": (str, False)},
    "inhibit-shortcuts": {},
    "open-file": {"path": (str, True)},
    "open-menu": {"menu": (str, True)},
    "open-settings": {},
    "open-uri": {"uri": (str, True)},
    "set-clipboard": {"text": (str, True)},
    "send-websocket-message": {"url": (str, True), "message": (str, True)},
    "simulate-hotkey": {"hotkey": (str, True)},
}

MENU_KEYS = {"root", "shortcut", "shortcutID", "useFixedPosition", "fixedMenuPosition",
             "anchored", "hoverMode", "conditions", "tags"}
ITEM_KEYS = {
    "root": {"name", "icon", "iconTheme", "type", "children", "activateWorkflow"},
    "button": {"name", "icon", "iconTheme", "type", "angle", "hoverWorkflow", "selectWorkflow"},
    "submenu": {"name", "icon", "iconTheme", "type", "angle", "children", "hoverWorkflow",
                "openWorkflow", "activateWorkflow"},
}
OLD_KEYS = {
    "centered": "Kando 3.0 replaced 'centered' with 'useFixedPosition' + 'fixedMenuPosition'.",
    "data": "Kando 2.x item 'data' is gone in 3.0; items run workflows (selectWorkflow etc.).",
}
OLD_ITEM_TYPES = {"command", "hotkey", "macro", "uri", "file", "redirect", "text", "settings"}

# Key codes for simulate-hotkey / execute-macro (kando.menu/valid-keynames).
KEY_CODES = set(
    "AltLeft AltRight ControlLeft ControlRight MetaLeft MetaRight ShiftLeft ShiftRight "
    "Again ArrowDown ArrowLeft ArrowRight ArrowUp AudioVolumeDown AudioVolumeMute "
    "AudioVolumeUp Backquote Backslash Backspace BracketLeft BracketRight BrowserBack "
    "BrowserFavorites BrowserForward BrowserHome BrowserRefresh BrowserSearch BrowserStop "
    "CapsLock Comma ContextMenu Convert Copy Cut Delete Eject End Enter Equal Escape Find "
    "Help Home Insert IntlBackslash IntlRo IntlYen KanaMode LaunchApp1 LaunchApp2 "
    "LaunchMail MediaPlayPause MediaSelect MediaStop MediaTrackNext MediaTrackPrevious "
    "Minus NonConvert NumLock NumpadAdd NumpadComma NumpadDecimal NumpadDivide NumpadEnter "
    "NumpadEqual NumpadMultiply NumpadParenLeft NumpadParenRight NumpadSubtract Open "
    "PageDown PageUp Paste Pause Period Power PrintScreen Quote ScrollLock Select "
    "Semicolon Slash Sleep Space Tab Undo WakeUp".split()
)
KEY_CODES |= {f"Digit{i}" for i in range(10)} | {f"Numpad{i}" for i in range(10)}
KEY_CODES |= {f"F{i}" for i in range(1, 25)} | {f"Lang{i}" for i in range(1, 6)}
KEY_CODES |= {f"Key{chr(c)}" for c in range(ord("A"), ord("Z") + 1)}
KEY_CODES_LOWER = {k.lower() for k in KEY_CODES}  # Kando matches codes case-insensitively

# Common key *names* people type where a *code* is needed, and what they meant.
NAME_TO_CODE = {
    "ctrl": "ControlLeft", "control": "ControlLeft", "shift": "ShiftLeft", "alt": "AltLeft",
    "meta": "MetaLeft", "win": "MetaLeft", "super": "MetaLeft", "cmd": "MetaLeft",
    "esc": "Escape", "return": "Enter", "up": "ArrowUp", "down": "ArrowDown",
    "left": "ArrowLeft", "right": "ArrowRight", "del": "Delete", "`": "Backquote",
    "space": "Space", "tab": "Tab", "plus": "Equal", "-": "Minus", "=": "Equal",
}

# Key names for menu shortcuts (Electron accelerators).
SHORTCUT_MODIFIERS = {"command", "cmd", "control", "ctrl", "commandorcontrol", "cmdorctrl",
                      "alt", "option", "altgr", "shift", "super", "meta"}
SHORTCUT_KEYS = set("0123456789abcdefghijklmnopqrstuvwxyz") | {f"f{i}" for i in range(1, 25)}
SHORTCUT_KEYS |= set(")!@#$%^&*(:;'+=<,_->.?/~`{]}[|\\\"")
SHORTCUT_KEYS |= {k.lower() for k in (
    "Plus Space Tab Capslock Numlock Scrolllock Backspace Delete Insert Return Enter Up Down "
    "Left Right Home End PageUp PageDown Escape Esc VolumeUp VolumeDown VolumeMute "
    "MediaNextTrack MediaPreviousTrack MediaStop MediaPlayPause PrintScreen numdec numadd "
    "numsub nummult numdiv").split()}
SHORTCUT_KEYS |= {f"num{i}" for i in range(10)}

CONFIG_ENUMS = {
    "sameShortcutBehavior": {"cycle-from-first", "cycle-from-recent", "re-open", "close", "nothing"},
    "settingsWindowColorScheme": {"light", "dark", "system"},
    "settingsWindowFlavor": {"auto", "sakura-light", "sakura-dark", "sakura-system",
                             "transparent-light", "transparent-dark", "transparent-system"},
    "trayIconFlavor": {"light", "dark", "color", "black", "white", "none"},
    "settingsButtonPosition": {"top-left", "top-right", "bottom-left", "bottom-right"},
    "wlrootsPointerGetTimeoutDefaultBehavior": {"top-left", "top-right", "bottom-left",
                                                "bottom-right", "center",
                                                "previously-reported-position"},
}
CONFIG_TYPES = {
    bool: "showIntroductionDialog enableDarkModeForMenuThemes enableSelectionWedges "
          "underlineQuickSelectKey drawQuickSelectKey enableMenuAnimations "
          "enablePointerReactiveEffects enableVersionCheck ignoreWriteProtectedConfigFiles "
          "hardwareAcceleration lazyInitialization hideSettingsButton windowsInkWorkaround "
          "keepInputFocus hideOnFocusOut enableMarkingMode enableTurboMode warpMouse "
          "returnPointerToMenuOpeningPosition hoverModeNeedsConfirmation "
          "triggerCenterClickOnKeyRelease rmbSelectsParent enableGamepad "
          "useDefaultOsShowSettingsHotkey enableAchievements enableAchievementNotifications",
    (int, float): "soundVolume zoomFactor fadeInDuration fadeOutDuration maxSelectionRadius "
                  "centerDeadZone minParentDistance dragThreshold gestureMinStrokeLength "
                  "gestureMinStrokeAngle gestureJitterThreshold gesturePauseTimeout "
                  "fixedStrokeLength gamepadBackButton gamepadCloseButton "
                  "wlrootsPointerGetTimeoutMouse wlrootsPointerGetTimeoutTouch",
    str: "version locale menuTheme darkMenuTheme soundTheme",
    dict: "menuThemeColors darkMenuThemeColors",
}
CONFIG_KEYS = {k for v in CONFIG_TYPES.values() for k in v.split()} | set(CONFIG_ENUMS)
# Lower bounds from general-settings-v1.ts (z.number().min(...)). Every other number is >= 0.
CONFIG_MIN = {"zoomFactor": 0.5, "gamepadBackButton": -1, "gamepadCloseButton": -1}


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)

# ------------------------------------------------------------------------- reporting --


class Report:
    def __init__(self):
        self.items = []  # (level, where, message)
        self.load_errors = 0  # errors that make Kando reject the whole file

    def error(self, where, msg, blocks_load=True):
        """blocks_load=False: Kando loads the file, but the menu is broken."""
        self.items.append(("ERROR", where, msg))
        if blocks_load:
            self.load_errors += 1

    def warn(self, where, msg):
        self.items.append(("WARN", where, msg))

    def tip(self, where, msg):
        self.items.append(("TIP", where, msg))

    def count(self, level):
        return sum(1 for i in self.items if i[0] == level)

    def print(self):
        order = {"ERROR": 0, "WARN": 1, "TIP": 2}
        for level, where, msg in sorted(self.items, key=lambda i: order[i[0]]):
            print(f"{level:5}  {where}\n       {msg}")
        print(f"\n{self.count('ERROR')} error(s), {self.count('WARN')} warning(s), "
              f"{self.count('TIP')} tip(s).")
        if self.load_errors:
            print("Kando will refuse to load this file until the errors are fixed.")
        elif self.count("ERROR"):
            print("Kando loads this file, but the errors above break the menu. Fix them first.")


# ---------------------------------------------------------------------- key checks --


def check_hotkey(hotkey, where, rep):
    """simulate-hotkey uses key CODES joined by '+', e.g. ControlLeft+KeyS."""
    for part in hotkey.split("+"):
        if part.lower() in KEY_CODES_LOWER:
            continue
        hint = ""
        low = part.lower()
        if low in NAME_TO_CODE:
            hint = f" Did you mean '{NAME_TO_CODE[low]}'?"
        elif len(part) == 1 and part.isalpha():
            hint = f" Did you mean 'Key{part.upper()}'?"
        elif len(part) == 1 and part.isdigit():
            hint = f" Did you mean 'Digit{part}'?"
        rep.error(where, f"'{part}' in hotkey '{hotkey}' is not a key code.{hint} "
                         "Hotkeys and macros use physical key codes, not key names.")


def check_shortcut(shortcut, where, rep):
    """Menu shortcuts use key NAMES (Electron accelerator), e.g. Control+Space."""
    if not shortcut:
        return
    parts = shortcut.split("+")
    # "Ctrl++" style: a trailing empty part means the key is '+'
    if shortcut.endswith("++"):
        parts = parts[:-2] + ["+"]
    *mods, key = parts
    for m in mods:
        if m.lower() not in SHORTCUT_MODIFIERS:
            fix = " Shortcuts use key names like 'Control', not codes like 'ControlLeft'." \
                if m.lower() in KEY_CODES_LOWER else ""
            rep.error(where, f"'{m}' in shortcut '{shortcut}' is not a modifier name.{fix}")
    if key.lower() not in SHORTCUT_KEYS:
        fix = ""
        if key.startswith("Key") and len(key) == 4:
            fix = f" Use '{key[3]}' (a key name), not '{key}' (a key code)."
        elif key.startswith("Digit"):
            fix = f" Use '{key[5:]}' (a key name), not '{key}' (a key code)."
        rep.error(where, f"'{key}' in shortcut '{shortcut}' is not a valid key name.{fix}")
    if not mods and key.lower() not in {f"f{i}" for i in range(13, 25)}:
        rep.warn(where, f"Shortcut '{shortcut}' has no modifier. Kando registers it globally, "
                        "so that key stops typing in every other app.")


# --------------------------------------------------------------------- menu checks --


def check_workflow(wf, where, rep, kind):
    if not isinstance(wf, dict):
        rep.error(where, f"{kind} must be an object with 'actions'.")
        return []
    for k in wf:
        if k not in ("actions", "quickSelectKey"):
            rep.warn(where, f"Unknown key '{k}' in {kind}; Kando drops it.")
    if "quickSelectKey" in wf and not isinstance(wf["quickSelectKey"], str):
        rep.error(where, f"{kind}.quickSelectKey must be a string, e.g. \"a\" or \"3\" "
                         "(in quotes), not a number.")
    actions = wf.get("actions", [])
    if not isinstance(actions, list):
        rep.error(where, f"{kind}.actions must be a list.")
        return []
    types = []
    for i, a in enumerate(actions):
        aw = f"{where} > {kind}[{i}]"
        if not isinstance(a, dict) or "type" not in a:
            rep.error(aw, "Each action needs a 'type'.")
            continue
        t = a["type"]
        types.append(t)
        if t not in ACTION_FIELDS:
            rep.error(aw, f"Unknown action type '{t}'. Valid: {', '.join(sorted(ACTION_FIELDS))}.")
            continue
        for field, (typ, required) in ACTION_FIELDS[t].items():
            if field not in a:
                if required:
                    rep.error(aw, f"'{t}' needs a '{field}'.")
            elif not isinstance(a[field], typ) or (typ is not bool and isinstance(a[field], bool)
                                                   and typ != bool):
                rep.error(aw, f"'{field}' has the wrong type.")
        for field in a:
            if field != "type" and field not in ACTION_FIELDS[t]:
                rep.warn(aw, f"Unknown field '{field}' on '{t}'; Kando drops it.")
        if t == "simulate-hotkey" and isinstance(a.get("hotkey"), str):
            check_hotkey(a["hotkey"], aw, rep)
        if t == "execute-macro" and isinstance(a.get("macro"), list):
            for j, ev in enumerate(a["macro"]):
                if not isinstance(ev, dict) or ev.get("type") not in ("keyDown", "keyUp") \
                        or not isinstance(ev.get("key"), str):
                    rep.error(f"{aw} > macro[{j}]", "Macro events need type keyDown/keyUp and a key.")
                else:
                    check_hotkey(ev["key"], f"{aw} > macro[{j}]", rep)
            downs = [e.get("key") for e in a["macro"] if isinstance(e, dict) and e.get("type") == "keyDown"]
            ups = [e.get("key") for e in a["macro"] if isinstance(e, dict) and e.get("type") == "keyUp"]
            stuck = set(downs) - set(ups)
            if stuck:
                rep.warn(aw, f"Macro presses {sorted(stuck)} but never releases them; "
                             "the key can stay held down.")
        if t == "delay" and isinstance(a.get("duration"), (int, float)) and a["duration"] > 5:
            rep.warn(aw, f"delay is in SECONDS; {a['duration']} s is long. Did you mean ms?")
        if t == "execute-command" and re.search(r"[A-Za-z]:\\\\?Users\\\\?[^\\\\\"]+", a.get("command", "")):
            rep.tip(aw, "Command uses a user-specific path; it will break on other PCs if shared.")
    # Order problems
    if "open-menu" in types:
        idx = types.index("open-menu")
        if "close-menu" in types[idx + 1:]:
            rep.warn(where, f"{kind}: close-menu after open-menu closes the menu you just opened.")
    key_actions = {"simulate-hotkey", "execute-macro"}
    if kind == "selectWorkflow" and any(t in key_actions for t in types):
        first_key = min(types.index(t) for t in key_actions if t in types)
        if "close-menu" not in types:
            rep.tip(where, "Presses keys but never closes the menu. While the menu is open Kando "
                           "has keyboard focus, so app hotkeys land in Kando, not your app "
                           "(unless keepInputFocus is on). Fine for global keys like volume or "
                           "media; otherwise add close-menu FIRST.")
        elif types.index("close-menu") > first_key:
            rep.warn(where, "Keys are pressed before close-menu, so they may land in Kando's "
                            "own window instead of your app. Put close-menu first.")
    if kind == "selectWorkflow" and not types:
        rep.warn(where, "This button does nothing (empty selectWorkflow).")
    return types


def check_children(parent, where, rep, depth, stats):
    children = parent.get("children", [])
    if not isinstance(children, list):
        rep.error(where, "'children' must be a list.")
        return
    n = len(children)
    if n > 12:
        rep.warn(where, f"{n} items in one ring. Kando's docs say never more than 12; "
                        "go deeper with submenus instead.")
    elif n > 8:
        rep.tip(where, f"{n} items in one ring. About 8 is the sweet spot for fast marking "
                       "gestures (the 8 compass directions).")
    stats["max_depth"] = max(stats["max_depth"], depth)

    # Quick-select keys: duplicates among siblings (incl. this level's center key).
    keys = {}
    center = parent.get("activateWorkflow")
    if isinstance(center, dict) and isinstance(center.get("quickSelectKey"), str) and center["quickSelectKey"]:
        keys[center["quickSelectKey"].lower()] = "(center)"
    for c in children:
        if not isinstance(c, dict):
            continue
        wf = c.get("selectWorkflow") or c.get("openWorkflow") or {}
        k = wf.get("quickSelectKey") if isinstance(wf, dict) else None
        if isinstance(k, str) and k:
            if k.lower() in keys:
                rep.warn(where, f"Quick-select key '{k}' is used by both '{keys[k.lower()]}' "
                                f"and '{item_name(c)}'.")
            keys[k.lower()] = item_name(c)
            if k.isdigit():
                rep.tip(where, f"'{item_name(c)}' uses digit '{k}' as quick key; digits 1-9 already "
                               "select items without a key by position, which can clash.")

    names = {}
    for i, c in enumerate(children):
        cw = f"{where} > {item_name(c, f'#{i}')}"
        check_item(c, cw, rep, depth + 1, stats)
        nm = item_name(c, None)
        if nm is not None:
            if nm in names:
                rep.tip(where, f"Two items are both named '{nm}'.")
            names[nm] = True


def check_item(item, where, rep, depth, stats):
    if not isinstance(item, dict):
        rep.error(where, "Menu item must be an object.")
        return
    if depth > MAX_DEPTH:
        rep.warn(where, f"Nested more than {MAX_DEPTH} levels deep; the checker stops here. "
                        "Nobody can remember a path that long. Flatten it.")
        return
    t = item.get("type")
    if t in OLD_ITEM_TYPES:
        rep.error(where, f"Item type '{t}' is from Kando 2.x. In 3.0 use type 'button' with a "
                         "selectWorkflow (e.g. an execute-command / simulate-hotkey action).")
        return
    if depth == 0 and t != "root":
        rep.error(where, "The menu's top item must have type 'root'.")
    if depth > 0 and t not in ("button", "submenu"):
        rep.error(where, f"Child items must be 'button' or 'submenu', not '{t}'.")
        return
    for f in ("name", "icon", "iconTheme"):
        if not isinstance(item.get(f), str):
            rep.error(where, f"Item needs a string '{f}'.")
    if "angle" in item and not is_number(item["angle"]):
        rep.error(where, "'angle' must be a number (degrees, 0 = up, 90 = right), "
                         "not true/false, a string or null.")
    allowed = ITEM_KEYS.get(t, set())
    for k in item:
        if k in OLD_KEYS:
            rep.warn(where, OLD_KEYS[k] + " The old key is ignored.")
        elif k not in allowed:
            rep.warn(where, f"Unknown key '{k}' on a {t}; Kando drops it.")
    stats["items"] += 1
    for wfk in ("selectWorkflow", "openWorkflow", "activateWorkflow", "hoverWorkflow"):
        if wfk in item and wfk in allowed:
            check_workflow(item[wfk], where, rep, wfk)
    if t == "button" and "selectWorkflow" not in item:
        rep.warn(where, "Button has no selectWorkflow, so selecting it does nothing.")
    if t in ("root", "submenu"):
        if "children" not in item:
            rep.error(where, f"A {t} needs 'children' (can be empty).")
        else:
            check_children(item, where, rep, depth, stats)


def check_layout(menu, where, rep):
    """Checks that need Kando's real placement (kando_layout.py, a port of
    computeItemAngles): fixed angles Kando ignores, stacks or keeps a full lap too far, and
    items on a submenu's way back. Runs per ring, so it also catches submenus whose own
    angle is automatic."""
    for path, node, parent_angle, angles in levels(menu):
        ring = f"{where} > {' > '.join(path[1:])}" if len(path) > 1 else where
        kids = [c for c in node.get("children", []) if isinstance(c, dict)] \
            if isinstance(node.get("children"), list) else []
        ignored, stacked, lapped = angle_problems(kids, parent_angle)
        for i, raw, reason, prev in ignored:
            a = angles[i]
            placed = f"({compass(a)}, {a % 360:.0f}\u00b0)"
            if reason == "negative":
                rep.warn(ring, f"'{item_name(kids[i])}' has angle {raw:g}\u00b0. Angles count clockwise "
                               f"from 0 = up and cannot be negative, so Kando ignores this angle "
                               f"and places the item automatically {placed}. Did you mean "
                               f"{raw % 360:g}?")
            else:
                rep.warn(ring, f"'{item_name(kids[i])}' ({raw:g}\u00b0) comes after an item fixed at "
                               f"{prev:g}\u00b0. Fixed angles must grow in list order, so Kando "
                               f"ignores this angle and places the item automatically {placed}. "
                               "List the items clockwise from the smallest angle.")
        for group in stacked:
            names = ", ".join(f"'{item_name(kids[i])}'" for i in group)
            rep.error(ring, f"{names} all point at {angles[group[0]] % 360:.0f}\u00b0, so Kando draws "
                            "them on top of each other and only one can be selected. Give each "
                            "its own angle.", blocks_load=False)
        stacked_idx = {i for g in stacked for i in g}
        for i, first in lapped:
            if i in stacked_idx:
                continue  # already reported as stacked
            raw = raw_angle(kids[i])
            rep.warn(ring, f"'{item_name(kids[i])}' ({raw:g}\u00b0) is a full turn or more past the "
                           f"first fixed angle in this ring ({first:g}\u00b0). Kando keeps it as is, "
                           "so it lands among the items listed before it and their selection "
                           f"wedges overlap. Write {raw % 360:g} and move the item to its "
                           "clockwise place in the list.")
        if parent_angle is None:
            continue
        auto = {i for i, *_ in ignored}
        for i, (c, a) in enumerate(zip(kids, angles)):
            if raw_angle(c) is None or i in auto:
                continue  # Kando keeps auto-placed items clear of the back link itself
            dist = angular_distance(a, parent_angle)
            if 25 <= dist < 40:
                rep.tip(ring, f"'{item_name(c)}' is only {dist:.0f}\u00b0 from the way back. "
                              "45\u00b0 or more makes both flicks easy to tell apart.")
            if dist < 25:
                rep.warn(ring, f"'{item_name(c)}' ({a % 360:.0f}\u00b0, {compass(a)}) sits on the way back "
                               f"to the parent ({parent_angle % 360:.0f}\u00b0). Flicking that way is "
                               "ambiguous; move it at least 45\u00b0 away.")


def check_version(data, where, rep):
    """Kando backs up and refuses a file written by a newer major version (settings.ts)."""
    if not isinstance(data, dict) or "version" not in data:
        return
    v = data["version"]
    if not isinstance(v, str):
        rep.error(where, "'version' must be a string such as \"3.0.1\".")
        return
    m = re.search(r"(\d+)", v)
    if m and int(m.group(1)) > KANDO_MAJOR:
        rep.warn(where, f"version '{v}' is from a newer major version of Kando. Kando "
                        f"{KANDO_MAJOR}.x will not load it: it shows an error, copies the file to "
                        "its backups folder and starts with default settings instead.")


def condition_key(menu):
    """Conditions that actually filter: empty strings / empty objects don't count."""
    c = menu.get("conditions")
    if not isinstance(c, dict):
        return "{}"
    c = {k: v for k, v in c.items() if v not in ("", None, {}, [])}
    return json.dumps(c, sort_keys=True)


def check_menus(data, rep):
    if isinstance(data, dict) and "menu" in data and "menus" not in data:
        data = {"menus": [data["menu"]]}  # a single exported menu
    if not isinstance(data, dict) or not isinstance(data.get("menus"), list):
        rep.error("menus.json", "Top level must be an object with a 'menus' list.")
        return
    for k in data:
        if k not in ("version", "menus", "collections"):
            rep.warn("menus.json", f"Unknown top-level key '{k}'; Kando drops it.")
    check_version(data, "menus.json", rep)
    by_shortcut = {}
    seen_names = {}
    for mi, menu in enumerate(data["menus"]):
        root = menu.get("root", {}) if isinstance(menu, dict) else {}
        name = item_name(root, f"menu #{mi}")
        where = f"[{name}]"
        if not isinstance(menu, dict) or "root" not in menu:
            rep.error(where, "Each menu needs a 'root' item.")
            continue
        for k in menu:
            if k in OLD_KEYS:
                rep.warn(where, OLD_KEYS[k] + " The old key is ignored.")
            elif k not in MENU_KEYS:
                rep.warn(where, f"Unknown menu key '{k}'; Kando drops it.")
        if name in seen_names:
            rep.warn(where, "Another menu has the same name. open-menu and --menu pick the first one.")
        seen_names[name] = True
        sc = menu.get("shortcut", "")
        if not isinstance(sc, str):
            rep.error(where, "'shortcut' must be a string.")
            sc = ""
        check_shortcut(sc, where, rep)
        if not sc and not menu.get("shortcutID"):
            rep.tip(where, "No shortcut. Reachable only via open-menu, CLI (--menu) or IPC.")
        cond = menu.get("conditions")
        if cond is not None:
            if not isinstance(cond, dict):
                rep.error(where, "'conditions' must be an object.")
            else:
                for k in cond:
                    if k not in ("appName", "windowName", "screenArea"):
                        rep.warn(where, f"Unknown condition '{k}'; Kando drops it.")
                app = cond.get("appName", "")
                if isinstance(app, str) and app.startswith("/"):
                    try:
                        re.compile(app.strip("/"))
                    except re.error as e:
                        rep.error(where, f"appName regex does not compile: {e}")
        if menu.get("anchored"):
            rep.tip(where, "anchored is on. Simon's advice: anchored mode basically breaks "
                           "marking mode; use it mainly for touch or gamepad.")
        fp = menu.get("fixedMenuPosition")
        if fp is not None and not isinstance(fp, dict):
            rep.error(where, "fixedMenuPosition must be an object like {\"x\": 0.5, \"y\": 0.5}.")
        elif isinstance(fp, dict):
            for ax in ("x", "y"):
                v = fp.get(ax)
                if not is_number(v):
                    rep.error(where, f"fixedMenuPosition.{ax} must be a number.")
                elif not 0 <= v <= 1:
                    rep.warn(where, f"fixedMenuPosition.{ax} is {v:g}. It is a fraction of the "
                                    "screen (0 to 1); Kando multiplies it by the screen size, so "
                                    "this opens the menu partly or fully off screen.")
        if sc:
            by_shortcut.setdefault(sc.lower(), []).append((name, condition_key(menu)))
        stats = {"items": 0, "max_depth": 0}
        check_item(root, where, rep, 0, stats)
        if isinstance(root, dict):
            check_layout(menu, where, rep)
        if stats["max_depth"] > 3:
            rep.tip(where, f"Menu is {stats['max_depth'] + 1} levels deep; past 3 the gestures get "
                           "hard to remember.")
    for sc, menus in by_shortcut.items():
        conds = [c for _, c in menus]
        if "{}" not in conds:
            rep.tip(f"shortcut {sc}", "Every menu on this shortcut has conditions. In any other "
                                      "app the key is still swallowed but no menu opens. Add a "
                                      "fallback menu with no conditions.")
        if len(menus) < 2:
            continue
        dupes = {c for c in conds if conds.count(c) > 1}
        for c in dupes:
            names = [n for n, cc in menus if cc == c]
            rep.warn(f"shortcut {sc}", f"Menus {names} share this shortcut with identical "
                                        "conditions, so only one of them can ever open.")
    cols = data.get("collections", [])
    if not isinstance(cols, list):
        rep.error("collections", "'collections' must be a list.")
        cols = []
    for ci, c in enumerate(cols):
        cw = f"collections[{ci}]"
        if not isinstance(c, dict):
            rep.error(cw, "Each collection must be an object with name, icon and iconTheme.")
            continue
        missing = [f for f in ("name", "icon", "iconTheme") if not isinstance(c.get(f), str)]
        if missing:
            rep.error(cw, f"Collection needs a string {', '.join(repr(f) for f in missing)}.")
        tags = c.get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            rep.error(cw, "'tags' must be a list of strings.")


def check_config(cfg, rep):
    if not isinstance(cfg, dict):
        rep.error("config.json", "Top level must be an object.")
        return
    check_version(cfg, "config.version", rep)
    for k, v in cfg.items():
        w = f"config.{k}"
        if k == "centered":
            rep.warn(w, OLD_KEYS["centered"])
        elif k not in CONFIG_KEYS:
            rep.warn(w, "Unknown setting; Kando 3.0 drops it (typo, or from another version?).")
        elif k in CONFIG_ENUMS:
            if not isinstance(v, str) or v not in CONFIG_ENUMS[k]:
                rep.error(w, f"{json.dumps(v)} is not one of {sorted(CONFIG_ENUMS[k])}.")
        elif k == "version":
            continue  # checked above
        else:
            for typ, keys in CONFIG_TYPES.items():
                if k in keys.split():
                    bad = not isinstance(v, typ) or (typ != bool and isinstance(v, bool))
                    if bad:
                        rep.error(w, f"Wrong type: expected {getattr(typ, '__name__', 'number')}.")
                    elif typ == dict and not all(
                            isinstance(t, dict) and all(isinstance(c, str) for c in t.values())
                            for t in v.values()):
                        rep.error(w, "Must map theme names to {\"color-name\": \"color\"} objects.")
                    elif typ == (int, float) and v < CONFIG_MIN.get(k, 0):
                        rep.error(w, f"Must be at least {CONFIG_MIN.get(k, 0)}.")
    if cfg.get("keepInputFocus") is True:
        rep.warn("config.keepInputFocus", "true disables Turbo mode and all keyboard navigation.")
    fade_out, fade_in = cfg.get("fadeOutDuration"), cfg.get("fadeInDuration")
    if is_number(fade_out) and fade_out > 120:
        rep.tip("config.fadeOutDuration", f"{fade_out} ms. Actions after close-menu "
                "wait for the fade-out; 60-80 ms feels much snappier.")
    if is_number(fade_in) and fade_in > 100:
        rep.tip("config.fadeInDuration", f"{fade_in} ms; default is 75.")


# ----------------------------------------------------------------- privacy scanning --

PRIVACY_PATTERNS = [
    (r"[A-Za-z]:(?:\\\\?|/)Users(?:\\\\?|/)(?!Public)[^\\\\\"/]+", "Windows user folder (reveals your account name)"),
    (r"/(?:home|Users)/[^/\"]+", "home folder path (reveals your account name)"),
    (r"[\w.+-]+@[\w-]+\.[\w.]+", "email address"),
    (r"(?<!\d)\d{9,}(?!\d)", "long number (account / friend / phone ID?)"),
    (r"#[0-9a-fA-F]{4}\b", "name#tag style handle"),
    (r"(?i)\b(?:api[_-]?key|token|password|secret)\s*[=:]\s*\S+", "possible secret"),
]


def scan_privacy(text, rep):
    for pat, what in PRIVACY_PATTERNS:
        for m in sorted(set(re.findall(pat, text))):
            rep.warn("publish", f"{what}: '{m}'. Remove or replace before sharing.")


# ------------------------------------------------------------------------------ main --


def _reject_constant(name):
    raise ValueError(name)


def load(path, rep):
    try:
        with open(path, encoding="utf-8-sig") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Cannot find {path}")
        sys.exit(2)
    except UnicodeDecodeError as e:
        rep.error(path, f"Not UTF-8 text (byte 0x{e.object[e.start]:02x} at position {e.start}). "
                        "Kando reads its files as UTF-8, so the file fails to load or names turn "
                        "into replacement marks. Re-save it as UTF-8.")
        return None, ""
    except OSError as e:
        print(f"Cannot read {path}: {e.strerror or e.__class__.__name__}")
        sys.exit(2)
    if not text.strip():
        rep.error(path, "The file is empty. Kando needs at least {\"version\": ..., \"menus\": []}.")
        return None, ""
    try:
        return json.loads(text, parse_constant=_reject_constant), text
    except json.JSONDecodeError as e:
        rep.error(path, f"Not valid JSON (line {e.lineno}, column {e.colno}): {e.msg}. "
                        "Common causes: trailing comma, missing comma, unescaped backslash "
                        "in a Windows path (write \\\\).")
    except ValueError as e:
        rep.error(path, f"Not valid JSON: {e} is not allowed. Write a plain number.")
    except RecursionError:
        rep.error(path, "Nested too deeply for this checker to read. No menu needs that many "
                        "levels; look for a submenu that accidentally contains itself.")
    return None, ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("menus", help="menus.json, or a single exported menu .json")
    ap.add_argument("--config", help="config.json to check as well")
    ap.add_argument("--publish", action="store_true", help="scan for personal data before sharing")
    args = ap.parse_args()
    use_utf8_output()
    rep = Report()
    data, text = load(args.menus, rep)
    if data is not None:
        check_menus(data, rep)
        if args.publish:
            scan_privacy(text, rep)
    if args.config:
        cfg, ctext = load(args.config, rep)
        if cfg is not None:
            check_config(cfg, rep)
            if args.publish:
                scan_privacy(ctext, rep)
    rep.print()
    sys.exit(1 if rep.count("ERROR") else 0)


if __name__ == "__main__":
    main()
