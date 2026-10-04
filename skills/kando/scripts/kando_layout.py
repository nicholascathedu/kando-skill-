"""Kando's item placement, ported to Python so previews and checks match the real menu.

Port of fixFixedAngles / computeItemAngles / getEquivalentAngleLargerThan from
kando src/common/math/index.ts (MIT, Simon Schneegans). Angles are degrees clockwise
from up: 0 up, 90 right, 180 down, 270 left. Standard library only.
"""

COMPASS = ["Up", "Up-right", "Right", "Down-right", "Down", "Down-left", "Left", "Up-left"]


def larger_than(angle, than):
    while angle < than:
        angle += 360
    while angle - 360 >= than:
        angle -= 360
    return angle


def fix_fixed_angles(items):
    """Return per-item fixed angle or None, applying Kando's cleanup rules."""
    angles = [it.get("angle") if isinstance(it.get("angle"), (int, float)) else None for it in items]
    first = last = None
    for i, a in enumerate(angles):
        if a is None:
            continue
        a = larger_than(a, 0 if last is None else last)
        if last is None:
            first = a
        angles[i] = last = a
    if first is None:
        return angles
    last_i = -1
    for i, a in enumerate(angles):
        if a is None:
            continue
        if last_i >= 0 and a == angles[last_i]:
            angles[i] = None
        else:
            last_i = i
    return [None if (a is not None and a >= first + 360) else a for a in angles]


def compute_item_angles(fixed, parent_angle=None):
    n = len(fixed)
    out = [0.0] * n
    if n == 0:
        return out
    fx = [{"angle": a, "index": i} for i, a in enumerate(fixed) if a is not None and a >= 0]
    if parent_angle is not None:
        for f in fx:
            if abs(f["angle"] - parent_angle) < 1e-4:
                f["angle"] += 0.1
    i = 0
    while i < len(fx) - 1:
        if fx[i]["angle"] > fx[i + 1]["angle"]:
            fx.pop(i + 1)
        else:
            i += 1
    if not fx:
        first = 0.0
        if parent_angle is not None:
            wedge = 360 / (n + 1)
            first = min((parent_angle + (k + 1) * wedge) % 360 for k in range(n))
        fx.append({"angle": first, "index": 0})
        out[0] = first
    for i in range(len(fx)):
        b_idx, b_ang = fx[i]["index"], fx[i]["angle"]
        e_idx, e_ang = fx[(i + 1) % len(fx)]["index"], fx[(i + 1) % len(fx)]["angle"]
        out[b_idx] = b_ang
        if e_ang <= b_ang:
            e_ang += 360
        count_between = (e_idx - b_idx - 1 + n) % n
        p_in = False
        pa = parent_angle
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
            out[idx] = ang % 360
            idx, c = (idx + 1) % n, c + 1
    return out


def compass(angle):
    """Name of the nearest of the 8 compass directions."""
    return COMPASS[int(((angle % 360) + 22.5) // 45) % 8]


def angular_distance(a, b):
    """Smallest difference between two angles, 0..180."""
    return abs((a - b + 180) % 360 - 180)


def child_items(node):
    children = node.get("children", []) if isinstance(node, dict) else []
    return [c for c in children if isinstance(c, dict)] if isinstance(children, list) else []


def levels(menu):
    """Yield (path, node, parent_angle, child_angles) for root and every submenu."""
    def walk(node, path, parent_angle):
        children = child_items(node)
        angles = compute_item_angles(fix_fixed_angles(children), parent_angle)
        yield path, node, parent_angle, angles
        for c, a in zip(children, angles):
            if c.get("type") == "submenu":
                yield from walk(c, path + [c.get("name", "?")], (a + 180) % 360)
    yield from walk(menu["root"], [menu["root"].get("name", "?")], None)


def use_utf8_output():
    """Windows consoles often default to a legacy code page that can't print ° or ▸.
    Switch stdout to UTF-8 (falling back to replacement characters) so output never crashes."""
    import sys
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
