#!/usr/bin/env python3
"""Learn from real use: log what you pick in Kando, then get layout advice from it.

    python kando_usage.py watch      # keep running; logs every menu open, pick and cancel
    python kando_usage.py report     # after a few days: what to move, remove or speed up

The report also finds items you use one after the other: two picks within 10 seconds, five
times or more. Those are one job done in two flicks, so it suggests one item for both.
(Idea from Simon Schneegans, who made Kando.)

`watch` listens on Kando's own IPC (start-observing), so it sees every menu. Kando's events
don't say which menu opened, so the app in front is logged with each open (Windows) and the
report matches it to your menus' conditions and to which item paths exist. The log is
claude-usage/usage.jsonl next to menus.json. It holds item positions, times and app names,
never commands, and it stays on this PC. Standard library only.
"""

import argparse
import json
import os
import re
import statistics
import sys
import time

from kando_layout import (KandoFileError, child_items, compass, compute_item_angles, item_name,
                          menu_list, raw_angle, read_json, resolve_menus_path)

LOG = os.path.join("claude-usage", "usage.jsonl")
KEEP = ("openMenu", "selectButton", "closeMenu")
GAP_MS = 10000  # two picks this close together count as one job done in two steps
MIN_PAIR = 5
RETRY = 10  # seconds between tries to reach Kando


def foreground_app():
    """The focused window's executable name (Windows only), else ''."""
    if os.name != "nt":
        return ""
    try:
        import ctypes
        from ctypes import wintypes
        user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
        user32.GetForegroundWindow.restype = wintypes.HWND  # 64-bit handles, not C ints
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                                        wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), ctypes.byref(pid))
        handle = kernel32.OpenProcess(0x1000, False, pid.value)  # QUERY_LIMITED_INFORMATION
        if not handle:
            return ""
        buf, size = ctypes.create_unicode_buffer(1024), wintypes.DWORD(1024)
        ok = kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size))
        kernel32.CloseHandle(handle)
        return os.path.basename(buf.value) if ok else ""
    except (AttributeError, OSError):
        return ""


def watch(log_path):
    from kando_ws import KandoIPCError, KandoSocket
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    print(f"Logging Kando picks to {log_path}. Ctrl+C to stop.")
    while True:
        try:
            ws = KandoSocket()
            ws.send({"type": "start-observing"})
            while True:
                msg = ws.receive()
                if msg is None:
                    break
                if not isinstance(msg, dict) or msg.get("type") != "menu-interaction" \
                        or msg.get("interaction") not in KEEP:
                    continue
                row = {"t": round(time.time() * 1000), "ev": msg["interaction"],
                       "path": msg.get("path", [])}
                if row["ev"] == "openMenu":
                    row["app"] = foreground_app()
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(row) + "\n")
            ws.close()
        except (KandoIPCError, OSError):
            pass  # Kando not running (yet), or restarting: wait and try again
        except KeyboardInterrupt:
            return 0
        try:
            time.sleep(RETRY)
        except KeyboardInterrupt:
            return 0


def matches(cond, value):
    """Kando's own testStringCondition."""
    if not cond:
        return True
    if cond.startswith("/"):
        m = re.fullmatch(r"/(.*?)/([gimy]*)", cond, re.S)
        if not m:
            return False
        try:
            return re.search(m.group(1), value, re.I if "i" in m.group(2) else 0) is not None
        except re.error:
            return False
    return cond.lower() in value.lower()


def locate(menu, path):
    """[(name, angle, depth)] along an index path, or None if the path doesn't exist."""
    node, parent, out = menu["root"], None, []
    for depth, i in enumerate(path, 1):
        kids = child_items(node)
        if not isinstance(i, int) or not 0 <= i < len(kids):
            return None
        angle = compute_item_angles([raw_angle(c) for c in kids], parent)[i]
        node, parent = kids[i], (angle + 180) % 360
        out.append((item_name(node), angle, depth))
    return out


def pick_menu(menus, app, path):
    """The menu this event most likely came from: matching conditions, then a valid path."""
    def score(m):
        c = m.get("conditions") if isinstance(m.get("conditions"), dict) else {}
        app_cond = c.get("appName") if isinstance(c.get("appName"), str) else ""
        if app_cond and not (app and matches(app_cond, app)):
            return -1
        return 1 if app_cond else 0
    best = sorted((m for m in menus if score(m) >= 0 and locate(m, path) is not None),
                  key=score, reverse=True)
    return best[0] if best else None


def sessions(rows):
    """[(app, path or None, ms)] per opened menu: the picked path, or None for a cancel."""
    out, cur = [], None
    for r in rows:
        if r.get("ev") == "openMenu":
            if cur:
                out.append(cur)
            cur = [r.get("app", ""), None, 0, r.get("t", 0)]
        elif cur and r.get("ev") == "selectButton" and cur[1] is None:
            cur[1], cur[2] = r.get("path") or [], r.get("t", 0) - cur[3]
        elif cur and r.get("ev") == "closeMenu":
            out.append(cur)
            cur = None
    if cur:
        out.append(cur)
    return [(a, p, ms) for a, p, ms, _ in out]


def timed_picks(rows):
    """[(app, path, t)] for every pick, in order; app is the one logged when its menu opened."""
    out, app = [], ""
    for r in rows:
        if r.get("ev") == "openMenu":
            app = r.get("app", "")
        elif r.get("ev") == "selectButton":
            out.append((app, r.get("path") or [], r.get("t", 0)))
    return out


def follow_ups(rows, menus, gap_ms=GAP_MS):
    """{(first, second): count} for two different items picked within gap_ms of each other.
    Each item is (menu name, item path text)."""
    named, counts = [], {}
    for app, path, t in timed_picks(rows):
        menu = pick_menu(menus, app, path)
        if menu is not None:
            named.append(((item_name(menu["root"]),
                           " > ".join(n for n, _, _ in locate(menu, path))), t))
    for (a, ta), (b, tb) in zip(named, named[1:]):
        if a != b and 0 <= tb - ta <= gap_ms:
            counts[(a, b)] = counts.get((a, b), 0) + 1
    return counts


def report(rows, data, min_opens=20):
    menus = menu_list(data)
    picks, opens, cancels = {}, {}, {}
    for app, path, ms in sessions(rows):
        menu = pick_menu(menus, app, path or [])
        if menu is None:
            continue
        name = item_name(menu["root"])
        opens[name] = opens.get(name, 0) + 1
        if path is None:
            cancels[name] = cancels.get(name, 0) + 1
            continue
        where = locate(menu, path)
        key = (name, " > ".join(n for n, _, _ in where))
        p = picks.setdefault(key, {"times": [], "angle": where[-1][1], "depth": where[-1][2]})
        p["times"].append(ms)
    lines = []
    total = sum(opens.values())
    if total < min_opens:
        return [f"Only {total} menu opens logged so far. Leave `watch` running for a few days."]
    ranked = sorted(picks.items(), key=lambda kv: -len(kv[1]["times"]))
    lines.append("Most used: " + ", ".join(f"{k[1]} ({len(v['times'])})" for k, v in ranked[:8]))
    for (menu, item), p in ranked[:8]:
        if p["angle"] % 90 or p["depth"] > 1:
            spot = f"{compass(p['angle'])}" + (f", {p['depth']} levels deep" if p["depth"] > 1 else "")
            lines.append(f"Move: '{item}' in {menu} is one of your most used items but sits "
                         f"{spot}. A straight direction in the first ring is faster.")
        slow = statistics.median(p["times"])
        if slow > (1500 if p["depth"] == 1 else 2500):
            lines.append(f"Slow: '{item}' in {menu} takes {slow / 1000:.1f} s on average. "
                         "You're probably searching for it; give it a fixed spot you can learn.")
    pairs = sorted(follow_ups(rows, menus).items(), key=lambda kv: -kv[1])
    for ((m1, a), (m2, b)), n in pairs[:5]:
        if n < MIN_PAIR:
            break
        where = (f"them next to each other in {m1}" if m1 == m2 else f"'{b}' in {m1} too")
        lines.append(f"Used together: you picked '{a}' then '{b}' within {GAP_MS // 1000} s "
                     f"{n} times. Make one item that does both, or put {where}.")
    for m in menus:
        name = item_name(m["root"])
        if opens.get(name, 0) < min_opens:
            continue
        used = {k[1] for k in picks if k[0] == name}
        unused = []
        stack = [(m["root"], [])]
        while stack:
            node, trail = stack.pop()
            for c in child_items(node):
                t = trail + [item_name(c)]
                if c.get("type") == "submenu":
                    stack.append((c, t))
                elif " > ".join(t) not in used:
                    unused.append(" > ".join(t))
        if unused:
            lines.append(f"Never used in {name} ({opens[name]} opens): {', '.join(sorted(unused)[:10])}"
                         ". Removing them makes the ring easier to scan.")
        rate = cancels.get(name, 0) / opens[name]
        if rate >= 0.15:
            lines.append(f"Hard to find: {name} is closed without a pick {round(rate * 100)}% of "
                         "the time. Something you look for isn't where you expect it.")
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["watch", "report"])
    ap.add_argument("menus", nargs="?", help="menus.json (default: Kando's own)")
    args = ap.parse_args(argv)
    path = resolve_menus_path(args.menus)
    log_path = os.path.join(os.path.dirname(os.path.abspath(path)), LOG)
    if args.action == "watch":
        return watch(log_path)
    try:
        data = read_json(path)
    except KandoFileError as e:
        print(f"{path} {e.reason}", file=sys.stderr)
        return 2
    rows = []
    if os.path.isfile(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    pass
    for line in report(rows, data):
        print("- " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
