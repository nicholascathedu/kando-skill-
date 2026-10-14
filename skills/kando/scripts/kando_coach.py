#!/usr/bin/env python3
"""Speed coach: reads Kando's own stats (achievements.json) and says what to practise next.

    python kando_coach.py                 # Kando's own achievements.json
    python kando_coach.py --save          # also remember today's numbers to compare next time
    python kando_coach.py path/to/achievements.json

Kando counts every selection by how it was made (click, keyboard, marking/turbo, gamepad) and
how fast it was at each depth, as long as achievements are on (the default). It keeps totals
only, nothing per item, so this coaches your hands, not your layout. The numbers never leave
your PC: --save writes kando-coach-history.json next to achievements.json. Standard library only.
"""

import argparse
import json
import os
import sys
import time

from kando_layout import KandoFileError, find_kando_file, read_json

# Kando's SELECTION_TIME_LIMITS (src/main/achievements/achievement-tracker.ts), in ms.
LIMITS = {1: [1000, 750, 500, 250, 150], 2: [2000, 1000, 750, 500, 250], 3: [3000, 2000, 1000, 750, 500]}
HISTORY = "kando-coach-history.json"


def num(stats, key):
    v = stats.get(key, 0)
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else 0


def summary(stats):
    """The numbers the advice is based on."""
    total = num(stats, "selections")
    ways = {w: num(stats, w + "Selections") for w in ("click", "keyboard", "gesture", "gamepad")}
    speed = {}
    for depth, limits in LIMITS.items():
        counts = [num(stats, f"selectionsSpeed{t + 1}Depth{depth}") for t in range(5)]
        if counts[0]:  # share of the picks under the slowest limit that also beat each faster one
            speed[depth] = [(limits[t], round(100 * counts[t] / counts[0])) for t in range(5)]
    return {"selections": total, "cancels": num(stats, "cancels"), "ways": ways, "speed": speed}


def pct(part, whole):
    return round(100 * part / whole) if whole else 0


def advice(s):
    tips = []
    total, ways = s["selections"], s["ways"]
    if total < 50:
        return ["Kando has counted fewer than 50 picks so far. Use it for a few days and run this "
                "again; there isn't enough to coach on yet."]
    click, gesture, keys = pct(ways["click"], total), pct(ways["gesture"], total), pct(ways["keyboard"], total)
    if click >= 60:
        tips.append(f"{click}% of your picks are clicks. Next step on Simon's learning path: hold the "
                    "left button and flick toward the item (marking mode), or open with your shortcut "
                    "and keep its modifier held while you move (turbo mode). Both skip the click.")
    elif gesture >= 50:
        tips.append(f"{gesture}% of your picks are flicks (marking or turbo). That's the fast way; "
                    "keep the layout still so your hand can memorise it.")
    if keys >= 30:
        tips.append(f"{keys}% of your picks use the keyboard. Quick-select keys are great for menus "
                    "you're still learning; flicks get faster once a layout is in your hand.")
    d1 = dict(s["speed"].get(1, []))
    if d1 and d1.get(250, 0) < 25:
        tips.append(f"Only {d1.get(250, 0)}% of your first-ring picks are under 250 ms. Practise the "
                    "four straight flicks (Up, Down, Left, Right) without looking at the menu, and put "
                    "your most used items there.")
    d2 = dict(s["speed"].get(2, []))
    if d2 and d2.get(750, 0) < 30:
        tips.append(f"Only {d2.get(750, 0)}% of your submenu picks are under 750 ms. Draw both flicks "
                    "as one zig-zag without stopping in between, and keep the same item in the same "
                    "direction in every submenu.")
    cancelled = pct(s["cancels"], total + s["cancels"])
    if cancelled >= 15:
        tips.append(f"You close {cancelled}% of the menus you open without picking anything. That "
                    "usually means something is hard to find. Ask Claude to review the menus you "
                    "open most.")
    return tips or ["Nothing stands out: your mix of picks and speeds is already in good shape."]


def compare(now, before):
    lines = []
    for depth, rows in now["speed"].items():
        old = dict(before.get("speed", {}).get(str(depth), []))
        for limit, share in rows:
            if limit in old and share != old[limit]:
                lines.append(f"Depth {depth} under {limit} ms: {old[limit]}% -> {share}%")
    gained = now["selections"] - before.get("selections", 0)
    return [f"{gained} picks since last time."] + lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", help="achievements.json (default: Kando's own)")
    ap.add_argument("--save", action="store_true", help="remember these numbers for next time")
    args = ap.parse_args(argv)
    path = args.path or find_kando_file("achievements.json")
    if not path:
        print("Kando's achievements.json was not found. It appears after your first picks, if "
              "achievements are on in Kando's settings.", file=sys.stderr)
        return 2
    try:
        stats = read_json(path)
    except KandoFileError as e:
        print(f"{path} {e.reason}", file=sys.stderr)
        return 2
    if not isinstance(stats, dict):
        print(f"{path} is not a Kando stats file.", file=sys.stderr)
        return 2
    s = summary(stats)
    w = s["ways"]
    print(f"{s['selections']} picks: {pct(w['click'], s['selections'])}% click, "
          f"{pct(w['gesture'], s['selections'])}% flick, {pct(w['keyboard'], s['selections'])}% keyboard, "
          f"{pct(w['gamepad'], s['selections'])}% gamepad. {s['cancels']} menus closed without a pick.")
    for depth, rows in s["speed"].items():
        print(f"Depth {depth}, of the picks under {rows[0][0]} ms: "
              + ", ".join(f"{share}% under {limit}" for limit, share in rows[1:]))
    history = os.path.join(os.path.dirname(os.path.abspath(path)), HISTORY)
    if os.path.isfile(history):
        try:
            before = read_json(history)
            print("\nSince " + before.get("date", "last time") + ":")
            for line in compare(s, before):
                print("  " + line)
        except (KandoFileError, AttributeError):
            pass
    print("\nWhat to practise:")
    for tip in advice(s):
        print("- " + tip)
    if args.save:
        with open(history, "w", encoding="utf-8") as f:
            json.dump(dict(s, date=time.strftime("%Y-%m-%d")), f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
