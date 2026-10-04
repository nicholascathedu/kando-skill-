#!/usr/bin/env python3
"""Preview Kando menus as a radial cheat sheet (HTML) and a compass outline (text).

Kando places items without a fixed angle automatically, so it is hard to tell from the
JSON where an item will actually appear. This script reproduces Kando's own placement
(a port of computeItemAngles / fixFixedAngles from kando src/common/math/index.ts, MIT)
and draws every menu level as a pie, so you can design and check a layout before you
load it, and print it as a cheat sheet while you learn the gestures.

Usage:
    python kando_preview.py menus.json                       # outline of every menu
    python kando_preview.py menus.json --menu Maya           # one menu
    python kando_preview.py menus.json --html sheet.html     # radial cheat sheet
    python kando_preview.py menus.json --html sheet.html --palette purple
    python kando_preview.py menus.json --html sheet.html --accent "#b06cff"

Palettes: purple (dark translucent violet), midnight (neutral dark), light.
Standard library only.
"""

import argparse
import html
import json
import math
import sys

COMPASS = ["Up", "Up-right", "Right", "Down-right", "Down", "Down-left", "Left", "Up-left"]

PALETTES = {
    "purple": {"bg": "#0d0a14", "panel": "rgba(28,18,46,0.72)", "wedge": "rgba(74,40,120,0.55)",
               "wedge2": "rgba(58,30,98,0.55)", "line": "rgba(196,160,255,0.28)",
               "accent": "#b06cff", "text": "#efe6ff", "muted": "#a993c9", "center": "rgba(22,12,38,0.92)"},
    "midnight": {"bg": "#0f1115", "panel": "rgba(30,33,40,0.8)", "wedge": "rgba(60,67,80,0.6)",
                 "wedge2": "rgba(48,54,66,0.6)", "line": "rgba(255,255,255,0.15)",
                 "accent": "#5aa9ff", "text": "#f1f4f8", "muted": "#9aa4b2", "center": "rgba(20,22,27,0.95)"},
    "light": {"bg": "#f6f5f8", "panel": "#ffffff", "wedge": "#ece8f3", "wedge2": "#e2dcee",
              "line": "rgba(0,0,0,0.12)", "accent": "#7b3fe4", "text": "#1d1828",
              "muted": "#6b6478", "center": "#ffffff"},
}


# --------------------------------------------------------- Kando placement (ported) --

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
    return COMPASS[int(((angle % 360) + 22.5) // 45) % 8]


# --------------------------------------------------------------------- tree walking --

def workflow_summary(item):
    wf = item.get("selectWorkflow") or item.get("openWorkflow") or {}
    acts = wf.get("actions", []) if isinstance(wf, dict) else []
    parts = []
    for a in acts:
        t = a.get("type")
        if t == "close-menu":
            continue
        if t == "simulate-hotkey":
            parts.append(a.get("hotkey", "").replace("Left", "").replace("Key", "").replace("Digit", ""))
        elif t == "execute-command":
            parts.append("run app")
        elif t == "open-uri":
            parts.append("open link")
        elif t == "set-clipboard":
            parts.append(f"paste “{a.get('text', '')[:18]}”")
        elif t == "focus-window":
            parts.append(f"focus {a.get('appName') or a.get('windowName')}")
        elif t == "open-menu":
            parts.append(f"open {a.get('menu')}")
        elif t == "execute-macro":
            parts.append("macro")
        elif t:
            parts.append(t)
    key = wf.get("quickSelectKey") if isinstance(wf, dict) else None
    return " → ".join(parts[:3]) + (" …" if len(parts) > 3 else ""), key


def levels(menu):
    """Yield (path, node, parent_angle, child_angles) for root and every submenu."""
    def walk(node, path, parent_angle):
        children = [c for c in node.get("children", []) if isinstance(c, dict)]
        angles = compute_item_angles(fix_fixed_angles(children), parent_angle)
        yield path, node, parent_angle, angles
        for c, a in zip(children, angles):
            if c.get("type") == "submenu":
                yield from walk(c, path + [c.get("name", "?")], (a + 180) % 360)
    yield from walk(menu["root"], [menu["root"].get("name", "?")], None)


def outline(menu):
    lines = []
    sc = menu.get("shortcut") or menu.get("shortcutID") or "no shortcut"
    cond = menu.get("conditions") or {}
    cond_s = ", ".join(f"{k}={v}" for k, v in cond.items() if v) or "everywhere"
    lines.append(f"{menu['root'].get('name')}  [{sc}]  ({cond_s})")
    for path, node, parent_angle, angles in levels(menu):
        indent = "  " * len(path)
        if len(path) > 1:
            lines.append(f"{'  ' * (len(path) - 1)}▸ {' ▸ '.join(path[1:])}"
                         f"  (back = {compass(parent_angle)})")
        children = [c for c in node.get("children", []) if isinstance(c, dict)]
        for c, a in sorted(zip(children, angles), key=lambda p: p[1]):
            what, key = workflow_summary(c)
            fixed = "" if isinstance(c.get("angle"), (int, float)) else " (auto)"
            sub = " ▸" if c.get("type") == "submenu" else ""
            if parent_angle is not None and abs((a - parent_angle + 180) % 360 - 180) < 25:
                sub += "  ⚠ on the back link"
            lines.append(f"{indent}{compass(a):10} {a % 360:5.0f}°{fixed:7} {c.get('name')}{sub}"
                         f"{'  [' + key + ']' if key else ''}{'  ' + what if what else ''}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- render --

def wedge_bounds(angles, parent_angle):
    """Start/end of each wedge: halfway to the neighbouring items (and the parent link)."""
    pts = [(a, i) for i, a in enumerate(angles)]
    if parent_angle is not None:
        pts.append((parent_angle, -1))
    pts.sort()
    res = {}
    n = len(pts)
    for k, (a, i) in enumerate(pts):
        prev_a = pts[k - 1][0] - (360 if k == 0 else 0)
        next_a = pts[(k + 1) % n][0] + (360 if k == n - 1 else 0)
        if n == 1:
            prev_a, next_a = a - 180, a + 180
        res[i] = ((prev_a + a) / 2, (a + next_a) / 2)
    return res


def pt(cx, cy, r, deg):
    rad = math.radians(deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def arc_path(cx, cy, r0, r1, a0, a1):
    large = 1 if (a1 - a0) > 180 else 0
    x0, y0 = pt(cx, cy, r1, a0)
    x1, y1 = pt(cx, cy, r1, a1)
    x2, y2 = pt(cx, cy, r0, a1)
    x3, y3 = pt(cx, cy, r0, a0)
    return (f"M{x0:.1f},{y0:.1f} A{r1},{r1} 0 {large} 1 {x1:.1f},{y1:.1f} "
            f"L{x2:.1f},{y2:.1f} A{r0},{r0} 0 {large} 0 {x3:.1f},{y3:.1f} Z")


def icon_html(item, size):
    theme, icon = item.get("iconTheme", ""), item.get("icon", "")
    e = html.escape
    if theme == "material-symbols-rounded":
        return f'<span class="ms" style="font-size:{size}px">{e(icon)}</span>'
    if theme in ("simple-icons", "simple-icons-colored"):
        url = f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{e(icon)}.svg"
        return (f'<img class="si" src="{url}" width="{size}" height="{size}" alt="" '
                f'onerror="this.replaceWith(document.createTextNode(\'{e(item.get("name", "?")[:2])}\'))">')
    if theme == "emoji":
        return f'<span style="font-size:{size}px">{e(icon)}</span>'
    return f'<span class="ini">{e(item.get("name", "?")[:2])}</span>'


def render_level(path, node, parent_angle, angles):
    S, cx, cy, r_in, r_out, r_icon = 360, 180, 180, 46, 150, 108
    children = [c for c in node.get("children", []) if isinstance(c, dict)]
    bounds = wedge_bounds(angles, parent_angle)
    svg = [f'<svg viewBox="0 0 {S} {S}" class="pie">']
    for i, (c, a) in enumerate(zip(children, angles)):
        a0, a1 = bounds[i]
        cls = "w sub" if c.get("type") == "submenu" else "w"
        svg.append(f'<path class="{cls}" d="{arc_path(cx, cy, r_in, r_out, a0 + 0.6, a1 - 0.6)}"/>')
    if parent_angle is not None:
        a0, a1 = bounds[-1]
        svg.append(f'<path class="w back" d="{arc_path(cx, cy, r_in, r_out, a0 + 0.6, a1 - 0.6)}"/>')
        bx, by = pt(cx, cy, r_icon, parent_angle)
        svg.append(f'<text x="{bx:.1f}" y="{by + 5:.1f}" class="backtxt">↩ back</text>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_in - 4}" class="center"/>')
    svg.append("</svg>")
    labels = []
    for c, a in zip(children, angles):
        x, y = pt(cx, cy, r_icon, a)
        _, key = workflow_summary(c)
        sub = '<i class="arrow">▸</i>' if c.get("type") == "submenu" else ""
        k = f'<b class="key">{html.escape(key)}</b>' if key else ""
        labels.append(f'<div class="lbl" style="left:{x / S * 100:.2f}%;top:{y / S * 100:.2f}%">'
                      f'{icon_html(c, 22)}<span class="nm">{html.escape(c.get("name", ""))}{sub}</span>{k}</div>')
    center = (f'<div class="lbl ctr" style="left:50%;top:50%">{icon_html(node, 26)}'
              f'<span class="nm">{html.escape(path[-1])}</span></div>')
    title = " ▸ ".join(html.escape(p) for p in path)
    rows = []
    for c, a in sorted(zip(children, angles), key=lambda p: p[1]):
        what, key = workflow_summary(c)
        rows.append(f"<tr><td>{compass(a)}</td><td>{html.escape(c.get('name', ''))}</td>"
                    f"<td>{html.escape(what)}</td></tr>")
    return (f'<section class="card"><h3>{title}</h3><div class="stage">{"".join(svg)}'
            f'{"".join(labels)}{center}</div><table>{"".join(rows)}</table></section>')


def render_html(menus, palette, accent):
    p = dict(PALETTES[palette])
    if accent:
        p["accent"] = accent
    body = []
    for m in menus:
        sc = m.get("shortcut") or m.get("shortcutID") or "no shortcut"
        cond = m.get("conditions") or {}
        cond_s = ", ".join(f"{k}: {v}" for k, v in cond.items() if v) or "everywhere"
        cards = "".join(render_level(*lv) for lv in levels(m))
        body.append(f'<div class="menu"><h2>{html.escape(m["root"].get("name", ""))}'
                    f'<span class="meta">{html.escape(sc)} · {html.escape(cond_s)}</span></h2>'
                    f'<div class="grid">{cards}</div></div>')
    css = f"""
:root{{--bg:{p['bg']};--panel:{p['panel']};--wedge:{p['wedge']};--wedge2:{p['wedge2']};
--line:{p['line']};--accent:{p['accent']};--text:{p['text']};--muted:{p['muted']};--center:{p['center']}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);
font:14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif;padding:24px 16px}}
h1{{font-weight:600;margin:0 0 4px}}.sub{{color:var(--muted);margin:0 0 24px}}
h2{{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap;margin:32px 0 12px}}
.meta{{font-size:13px;font-weight:400;color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:12px;
backdrop-filter:blur(12px)}}
h3{{margin:0 0 8px;font-size:14px;font-weight:600;color:var(--muted)}}
.stage{{position:relative;width:100%;aspect-ratio:1}}.pie{{position:absolute;inset:0;width:100%;height:100%}}
.w{{fill:var(--wedge);stroke:var(--line);stroke-width:1}}.w.sub{{fill:var(--wedge2)}}
.w.back{{fill:transparent;stroke-dasharray:3 4}}
.backtxt{{fill:var(--muted);font-size:11px;text-anchor:middle}}
.center{{fill:var(--center);stroke:var(--accent);stroke-width:2}}
.lbl{{position:absolute;transform:translate(-50%,-50%);display:flex;flex-direction:column;
align-items:center;gap:2px;width:84px;text-align:center}}
.nm{{font-size:11px;line-height:1.15}}.ctr .nm{{font-size:11px;color:var(--muted)}}
.arrow{{color:var(--accent);font-style:normal;margin-left:2px}}
.key{{font-size:10px;padding:0 5px;border-radius:4px;background:var(--accent);color:#fff}}
.ms{{font-family:"Material Symbols Rounded";color:var(--accent);line-height:1;display:inline-block;width:1em;height:1em;overflow:hidden;font-feature-settings:"liga"}}
.si{{filter:drop-shadow(0 0 4px rgba(0,0,0,.4))}}.ini{{font-weight:700;color:var(--accent)}}
table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:12px}}
td{{padding:3px 4px;border-top:1px solid var(--line);vertical-align:top}}
td:first-child{{color:var(--muted);white-space:nowrap}}
@media print{{body{{background:#fff;color:#000}}.card{{break-inside:avoid}}}}
"""
    font = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family='
            'Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=block">')
    return (f'<!doctype html><html><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Kando Menu Sheet</title>{font}<style>{css}</style></head><body>'
            f'<h1>Kando menu sheet</h1><p class="sub">Every ring of every menu, drawn where Kando '
            f'will put it. Dashed wedge = the way back to the parent.</p>{"".join(body)}</body></html>')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("menus", help="menus.json or a single exported menu")
    ap.add_argument("--menu", action="append", help="only this menu (repeatable, name match)")
    ap.add_argument("--html", help="write a radial cheat sheet to this .html file")
    ap.add_argument("--palette", choices=sorted(PALETTES), default="purple")
    ap.add_argument("--accent", help="override accent color, e.g. #b06cff")
    args = ap.parse_args()
    with open(args.menus, encoding="utf-8-sig") as f:
        data = json.load(f)
    menus = data.get("menus") or ([data["menu"]] if "menu" in data else [])
    if args.menu:
        wanted = {m.lower() for m in args.menu}
        menus = [m for m in menus if m["root"].get("name", "").lower() in wanted]
        if not menus:
            sys.exit(f"No menu named {args.menu}.")
    for m in menus:
        print(outline(m))
        print()
    if args.html:
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(render_html(menus, args.palette, args.accent))
        print(f"Wrote {args.html}")


if __name__ == "__main__":
    main()
