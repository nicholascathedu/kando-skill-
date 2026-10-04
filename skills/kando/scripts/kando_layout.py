"""Kando's item placement, ported to Python so previews and checks match the real menu.

Port of computeItemAngles from kando src/common/math/index.ts (MIT, Simon Schneegans),
which the live menu (src/menu-renderer/menu.ts) runs on the raw `angle` values of each
ring. Angles are degrees clockwise from up: 0 up, 90 right, 180 down, 270 left.
Standard library only.

How Kando reads fixed angles, in list order:
  - only numbers >= 0 count; a negative angle is ignored and the item placed automatically;
  - inside a submenu, a fixed angle exactly on the way back is nudged by 0.1 degrees;
  - a fixed angle smaller than the previous kept one is ignored (auto-placed);
  - equal fixed angles are all kept, so those items are drawn on top of each other;
  - everything else is spread evenly in the gaps, leaving room for the way back.
"""

import math

COMPASS = ["Up", "Up-right", "Right", "Down-right", "Down", "Down-left", "Left", "Up-left"]


def _finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def raw_angle(item):
    """The item's `angle` as Kando sees it: a finite number, or None when absent or not a
    number (Kando's schema rejects those, so the file would not load anyway)."""
    value = item.get("angle") if isinstance(item, dict) else None
    return float(value) if _finite_number(value) else None


def kept_fixed_angles(fixed, parent_angle=None):
    """The (index, angle) pairs Kando keeps as fixed, after the parent nudge and after
    dropping angles that are negative or smaller than the previous kept one."""
    fx = [[i, a] for i, a in enumerate(fixed) if a is not None and a >= 0]
    if parent_angle is not None:
        for f in fx:
            if abs(f[1] - parent_angle) < 0.0001:
                f[1] += 0.1
    i = 0
    while i < len(fx) - 1:
        if fx[i][1] > fx[i + 1][1]:
            fx.pop(i + 1)
        else:
            i += 1
    return [(i, a) for i, a in fx]


def compute_item_angles(fixed, parent_angle=None):
    """Kando's computeItemAngles. `fixed` holds each item's raw angle or None.
    Returns one angle per item, in degrees (fixed angles are returned as given)."""
    n = len(fixed)
    out = [0.0] * n
    if n == 0:
        return out
    fx = [{"index": i, "angle": a} for i, a in kept_fixed_angles(fixed, parent_angle)]
    if not fx:
        first = 0.0
        if parent_angle is not None:
            wedge = 360 / (n + 1)
            first = min(math.fmod(parent_angle + (k + 1) * wedge, 360) for k in range(n))
        fx.append({"angle": first, "index": 0})
        out[0] = first
    # Like Kando, the parent angle is shifted by a full turn once it falls behind a wedge,
    # and that shift carries over to the following wedges.
    pa = parent_angle
    for i in range(len(fx)):
        b_idx, b_ang = fx[i]["index"], fx[i]["angle"]
        e_idx, e_ang = fx[(i + 1) % len(fx)]["index"], fx[(i + 1) % len(fx)]["angle"]
        out[b_idx] = b_ang
        if e_ang <= b_ang:
            e_ang += 360
        count_between = (e_idx - b_idx - 1 + n) % n
        p_in = False
        if pa is not None:
            if pa < b_ang:
                pa += 360
            p_in = b_ang < pa < e_ang
            if p_in:
                count_between += 1
        gap = (e_ang - b_ang) / (count_between + 1)
        idx, c, need_gap = (b_idx + 1) % n, 1, p_in
        while idx != e_idx:
            ang = b_ang + gap * c
            if need_gap and ang + gap / 2 - pa > 0:
                c += 1
                ang = b_ang + gap * c
                need_gap = False
            out[idx] = math.fmod(ang, 360)
            idx, c = (idx + 1) % n, c + 1
    return out


def angle_problems(items, parent_angle=None):
    """How Kando treats the fixed angles of one ring, for explaining surprises.

    Returns (ignored, stacked, lapped):
      ignored: (index, raw angle, reason, previous kept angle) for each angle Kando skips,
               reason "negative" or "smaller" (than the previous kept angle);
      stacked: groups of indices whose kept angles point the same way (equal modulo 360),
               so Kando draws those items on top of each other;
      lapped:  (index, first kept angle) for kept angles a full turn or more past the first
               one. Kando keeps them as is, so they land among earlier items and the
               selection wedges overlap (computeItemWedges).
    """
    fixed = [raw_angle(c) for c in items]
    kept = kept_fixed_angles(fixed, parent_angle)
    kept_at = dict(kept)
    ignored, prev = [], None
    for i, a in enumerate(fixed):
        if a is None:
            continue
        if i in kept_at:
            prev = kept_at[i]
        else:
            ignored.append((i, a, "negative" if a < 0 else "smaller", prev))
    groups = {}
    for i, a in kept:
        groups.setdefault(round(math.fmod(a, 360), 6) % 360, []).append(i)
    stacked = [g for g in groups.values() if len(g) > 1]
    lapped = [(i, kept[0][1]) for i, a in kept[1:] if a >= kept[0][1] + 360]
    return ignored, stacked, lapped


def compass(angle):
    """Name of the nearest of the 8 compass directions."""
    return COMPASS[int(((angle % 360) + 22.5) // 45) % 8]


def angular_distance(a, b):
    """Smallest difference between two angles, 0..180."""
    return abs((a - b + 180) % 360 - 180)


def item_name(node, default="?"):
    """The item's name for display; anything that is not a string becomes `default`."""
    name = node.get("name") if isinstance(node, dict) else None
    return name if isinstance(name, str) else default


def child_items(node):
    children = node.get("children", []) if isinstance(node, dict) else []
    return [c for c in children if isinstance(c, dict)] if isinstance(children, list) else []


def levels(menu):
    """Yield (path, node, parent_angle, child_angles) for root and every submenu, depth
    first. Iterative, so a very deeply nested file cannot hit Python's recursion limit."""
    root = menu["root"]
    stack = [(root, [item_name(root)], None)]
    while stack:
        node, path, parent_angle = stack.pop()
        children = child_items(node)
        angles = compute_item_angles([raw_angle(c) for c in children], parent_angle)
        yield path, node, parent_angle, angles
        subs = [(c, path + [item_name(c)], math.fmod(a + 180, 360))
                for c, a in zip(children, angles) if c.get("type") == "submenu"]
        stack.extend(reversed(subs))


def use_utf8_output():
    """Windows consoles often default to a legacy code page that can't print ° or ▸.
    Switch stdout to UTF-8 (falling back to replacement characters) so output never crashes."""
    import sys
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
