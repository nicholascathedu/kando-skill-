#!/usr/bin/env python3
"""Switch your whole desktop between modes, such as Work and Play, from one Kando item.

    pythonw kando_mode.py work
    python kando_mode.py list
    python kando_mode.py show work     # what it would do, nothing changed

A mode can set any of these, and leaves out what it doesn't name:

    wallpaper   a picture file for the desktop background
    windows     "dark" or "light" for Windows' own app colours
    kando       a preset name from kando_presets.py ("speed"), or settings to apply
                ({"menuTheme": "amethyst-arsenal"}); checked and backed up the same way
    apps        apps to start unless they're already running: [["maya.exe", "C:\\\\...\\\\maya.exe"]]
    layout      where windows go, as in kando_windows.py: ["maya=left", "PureRef=right"]

Modes live in claude-modes.json next to Kando's config.json:

    {
      "work": {"wallpaper": "C:\\\\Pictures\\\\hall.png", "windows": "dark", "kando": "speed",
               "apps": [["maya.exe", "C:\\\\Program Files\\\\Autodesk\\\\Maya2026\\\\bin\\\\maya.exe"]],
               "layout": ["maya=left-two-thirds", "PureRef=right-third"]},
      "play": {"wallpaper": "C:\\\\Pictures\\\\ratchet.png", "kando": "learning", "apps": [["Discord.exe",
               "C:\\\\Users\\\\you\\\\AppData\\\\Local\\\\Discord\\\\Update.exe", "--processStart", "Discord.exe"]]}
    }

The steps run in that order. When it had to start an app, it waits up to 30 seconds for the
windows to appear before placing them. Do Not Disturb is left alone: Windows has no supported
way for a script to switch it. Windows only for wallpaper, colours, apps and layout; the
kando part works everywhere. Standard library only.
"""

import argparse
import json
import os
import subprocess
import sys
import time

import kando_launch
import kando_presets
import kando_windows
from kando_layout import KandoFileError, find_kando_file, read_json

MODES = "claude-modes.json"
KEYS = ("wallpaper", "windows", "kando", "apps", "layout")
WAIT = 30  # seconds to wait for apps that were just started


def load(folder):
    path = os.path.join(folder, MODES)
    if not os.path.isfile(path):
        sys.exit(f"No {MODES} in {folder}. See the top of kando_mode.py for an example.")
    data = read_json(path)
    if not isinstance(data, dict):
        sys.exit(f"{MODES} should be an object of modes, like {{\"work\": {{...}}}}.")
    return data


def problems(mode, folder):
    """What's wrong with a mode, as sentences. An empty list means it can run."""
    out = []
    if not isinstance(mode, dict):
        return ["A mode should be an object, like {\"wallpaper\": \"...\"}."]
    for key in mode:
        if key not in KEYS:
            out.append(f"Unknown step '{key}'. Steps are: {', '.join(KEYS)}.")
    if "windows" in mode and mode["windows"] not in ("dark", "light"):
        out.append("'windows' should be \"dark\" or \"light\".")
    kando = mode.get("kando")
    if isinstance(kando, str) and kando not in kando_presets.all_presets(folder):
        out.append(f"No Kando preset called {kando}.")
    elif kando is not None and not isinstance(kando, (str, dict)):
        out.append("'kando' should be a preset name or an object of settings.")
    for app in mode.get("apps", []):
        if not (isinstance(app, list) and len(app) >= 2 and all(isinstance(a, str) for a in app)):
            out.append(f"Each app should be [\"name.exe\", \"path\", ...args], not {json.dumps(app)}.")
    for spot in mode.get("layout", []):
        try:
            kando_windows.parse(spot)
        except (ValueError, TypeError):
            out.append(f"Layout '{spot}' should look like 'maya=left'.")
    return out


def describe(name, mode):
    lines = []
    if "wallpaper" in mode:
        lines.append(f"wallpaper: {mode['wallpaper']}")
    if "windows" in mode:
        lines.append(f"Windows colours: {mode['windows']}")
    if "kando" in mode:
        k = mode["kando"]
        lines.append(f"Kando preset: {k}" if isinstance(k, str) else
                     "Kando settings: " + ", ".join(f"{a} {json.dumps(b)}" for a, b in k.items()))
    for app in mode.get("apps", []):
        lines.append(f"start {app[0]} unless it's running")
    if mode.get("layout"):
        lines.append("place " + ", ".join(mode["layout"]))
    return lines or [f"{name} does nothing yet."]


def set_wallpaper(path):
    import ctypes
    if not os.path.isfile(path):
        raise OSError(f"no picture at {path}")
    # SPI_SETDESKWALLPAPER, saved to the profile and announced to other apps.
    if not ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(path), 3):
        raise OSError("Windows refused the picture")


def set_windows_colours(theme):
    import ctypes
    import winreg
    light = 1 if theme == "light" else 0
    key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, "AppsUseLightTheme", 0, winreg.REG_DWORD, light)
        winreg.SetValueEx(k, "SystemUsesLightTheme", 0, winreg.REG_DWORD, light)
    # Tell open windows the colours changed (WM_SETTINGCHANGE "ImmersiveColorSet").
    ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "ImmersiveColorSet", 2, 1000, None)


def start_apps(apps):
    """Start the apps that aren't running. Returns the names it started."""
    started = []
    for name, path, *args in apps:
        if kando_launch.running(name):
            continue
        if args:
            subprocess.Popen([path] + args, creationflags=kando_launch.CREATE_NO_WINDOW)
        else:
            os.startfile(path)
        started.append(name)
    return started


def place_windows(layout, wait):
    """Place what's open; when apps were just started, keep looking for up to `wait` seconds.
    Returns the matches that never showed up."""
    wanted = [kando_windows.parse(s) for s in layout]
    deadline = time.monotonic() + wait
    while True:
        windows = kando_windows.open_windows()
        found = [(kando_windows.pick(windows, app, title), box, app) for app, title, box in wanted]
        missing = [app for w, _, app in found if w is None]
        if not missing or time.monotonic() >= deadline:
            break
        time.sleep(1)
    found = [(w, box) for w, box, _ in found if w is not None]
    if found:
        area = kando_windows.work_area(found[0][0][0])
        for (hwnd, _, _), box in found:
            kando_windows.move(hwnd, kando_windows.place(box, area))
    return missing


def run(name, mode, folder):
    """Do each step; one failing step doesn't stop the rest. Returns (done, failed)."""
    done, failed = [], []

    def step(label, fn, *a):
        try:
            result = fn(*a)
            done.append(label)
            return result
        except (OSError, KandoFileError) as e:
            failed.append(f"{label}: {e}")
        except SystemExit as e:  # kando_presets refuses settings the checker rejects
            failed.append(f"{label}: {e}")
        return None

    if "kando" in mode:
        k = mode["kando"]
        cfg = os.path.join(folder, "config.json")
        if isinstance(k, str):
            step("Kando preset", kando_presets.apply, folder, k, cfg)
        else:
            step("Kando settings", kando_presets.apply_settings, folder, f"mode-{name}", k, cfg)
    if os.name != "nt":
        if any(key in mode for key in ("wallpaper", "windows", "apps", "layout")):
            failed.append("wallpaper, colours, apps and layout only work on Windows")
        return done, failed
    if "wallpaper" in mode:
        step("wallpaper", set_wallpaper, mode["wallpaper"])
    if "windows" in mode:
        step("Windows colours", set_windows_colours, mode["windows"])
    started = (step("apps", start_apps, mode["apps"]) or []) if mode.get("apps") else []
    if mode.get("layout"):
        missing = step("layout", place_windows, mode["layout"], WAIT if started else 0)
        if missing:
            failed.append("not open, so not placed: " + ", ".join(missing))
    return done, failed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("name", help="a mode from claude-modes.json, or 'list'")
    ap.add_argument("what", nargs="?", help="with 'show': the mode to describe")
    ap.add_argument("--dir", help="Kando config folder (default: Kando's own)")
    args = ap.parse_args(argv)
    folder = args.dir or os.path.dirname(find_kando_file("config.json") or
                                         find_kando_file("menus.json") or "")
    if not folder or not os.path.isdir(folder):
        sys.exit("Kando's config folder was not found. Pass it with --dir.")
    try:
        modes = load(folder)
    except KandoFileError as e:
        sys.exit(f"{MODES} {e.reason}")
    if args.name == "list":
        for name, mode in modes.items():
            print(f"{name:12} " + "; ".join(describe(name, mode)))
        return 0
    show = args.name == "show"
    name = args.what if show else args.name
    if name not in modes:
        sys.exit(f"No mode called {name}. Modes: {', '.join(modes) or 'none yet'}.")
    issues = problems(modes[name], folder)
    if issues:
        sys.exit(f"Not switching to {name}:\n  " + "\n  ".join(issues))
    if show:
        print("\n".join(describe(name, modes[name])))
        return 0
    done, failed = run(name, modes[name], folder)
    print(f"{name}: " + (", ".join(done) or "nothing changed"))
    for f in failed:
        print(f"  {f}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
