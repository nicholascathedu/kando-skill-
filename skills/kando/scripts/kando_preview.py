#!/usr/bin/env python3
"""Preview Kando menus as a radial cheat sheet (HTML) and a compass outline (text).

Kando places items without a fixed angle automatically, so it is hard to tell from the
JSON where an item will actually appear. This script uses a port of Kando's own placement
code (see kando_layout.py) and draws every ring of every menu where Kando will put it, so
you can check a layout before loading it, and print it as a cheat sheet while you learn
the gestures.

Usage:
    python kando_preview.py menus.json                       # outline of every menu
    python kando_preview.py menus.json --menu Maya           # one menu (root name)
    python kando_preview.py menus.json --html sheet.html     # radial cheat sheet
    python kando_preview.py menus.json --html sheet.html --palette midnight
    python kando_preview.py menus.json --html sheet.html --accent "#b06cff"

Palettes: purple (dark violet glass, default), midnight (neutral dark), light.
The sheet prints cleanly on white paper whatever the palette. Standard library only.
"""

import argparse
import html
import json
import math
import sys

from kando_layout import (COMPASS, angle_problems, angular_distance, child_items, compass,
                          item_name, levels, raw_angle, use_utf8_output)

ARROWS = ["↑", "↗", "→", "↘", "↓", "↙", "←", "↖"]

# Same major as the simple-icons-font Kando 3.0 bundles, so slugs match what Kando shows.
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@16/icons/"

PALETTES = {
    "purple": {
        "bg": "#0b0713", "aurora1": "rgba(124,58,237,0.35)", "aurora2": "rgba(192,38,211,0.22)",
        "glass": "rgba(30,18,52,0.55)", "rim": "rgba(206,176,255,0.22)",
        "wedge": "rgba(88,52,150,0.42)", "wedge-sub": "rgba(66,36,120,0.55)",
        "accent": "#b57bff", "glow": "rgba(160,96,255,0.55)",
        "text": "#f3ecff", "muted": "#b9a6d9", "center": "rgba(18,10,32,0.9)", "si-filter": "invert(1)",
    },
    "midnight": {
        "bg": "#0c0e12", "aurora1": "rgba(56,120,220,0.25)", "aurora2": "rgba(40,180,170,0.14)",
        "glass": "rgba(28,32,40,0.6)", "rim": "rgba(255,255,255,0.12)",
        "wedge": "rgba(70,80,98,0.45)", "wedge-sub": "rgba(52,60,76,0.6)",
        "accent": "#62a8ff", "glow": "rgba(98,168,255,0.45)",
        "text": "#eef2f7", "muted": "#9eabbb", "center": "rgba(14,16,20,0.92)", "si-filter": "invert(1)",
    },
    "light": {
        "bg": "#f4f1fa", "aurora1": "rgba(150,110,240,0.20)", "aurora2": "rgba(240,140,220,0.14)",
        "glass": "rgba(255,255,255,0.70)", "rim": "rgba(60,30,120,0.12)",
        "wedge": "rgba(120,90,200,0.12)", "wedge-sub": "rgba(120,90,200,0.22)",
        "accent": "#7339e0", "glow": "rgba(115,57,224,0.25)",
        "text": "#1c1530", "muted": "#5f5577", "center": "#ffffff", "si-filter": "none",
    },
}

KEY_LABELS = {
    "controlleft": "Ctrl", "controlright": "Ctrl", "shiftleft": "Shift", "shiftright": "Shift",
    "altleft": "Alt", "altright": "AltGr", "metaleft": "Win", "metaright": "Win",
    "backquote": "`", "arrowup": "↑", "arrowdown": "↓", "arrowleft": "←", "arrowright": "→",
    "escape": "Esc", "backspace": "Bksp", "numpaddecimal": "Num .", "numpaddivide": "Num /",
    "audiovolumeup": "Vol+", "audiovolumedown": "Vol−", "mediaplaypause": "Play/Pause",
}


# --------------------------------------------------------------------- summaries --

def pretty_hotkey(hotkey):
    """ControlLeft+ShiftLeft+KeyS -> Ctrl+Shift+S"""
    out = []
    for k in hotkey.split("+"):
        low = k.lower()
        if low in KEY_LABELS:
            out.append(KEY_LABELS[low])
        elif low.startswith("key") and len(k) == 4:
            out.append(k[3].upper())
        elif low.startswith("digit"):
            out.append(k[5:])
        elif low.startswith("numpad") and k[6:].isdigit():
            out.append("Num " + k[6:])
        else:
            out.append(k)
    return "+".join(out)


def workflow_summary(item):
    wf = item.get("selectWorkflow") or item.get("openWorkflow") or {}
    acts = wf.get("actions", []) if isinstance(wf, dict) else []
    parts = []
    for a in acts if isinstance(acts, list) else []:
        if not isinstance(a, dict):
            continue
        t = a.get("type")
        if t == "close-menu":
            continue
        if t == "simulate-hotkey":
            parts.append(pretty_hotkey(str(a.get("hotkey", ""))))
        elif t == "execute-command":
            parts.append("launch")
        elif t == "open-uri":
            parts.append("open link")
        elif t == "open-file":
            parts.append("open file")
        elif t == "set-clipboard":
            parts.append(f"paste “{str(a.get('text', ''))[:18]}”")
        elif t == "focus-window":
            parts.append(f"go to {a.get('appName') or a.get('windowName')}")
        elif t == "open-menu":
            parts.append(f"open {a.get('menu')}")
        elif t == "execute-macro":
            parts.append("macro")
        elif t == "delay":
            continue
        elif t:
            parts.append(t)
    key = wf.get("quickSelectKey") if isinstance(wf, dict) else None
    key = key if isinstance(key, str) and key else None  # anything else is a checker error
    return " → ".join(parts[:3]) + (" …" if len(parts) > 3 else ""), key


def conditions_text(menu):
    cond = menu.get("conditions") if isinstance(menu.get("conditions"), dict) else {}
    bits = []
    if cond.get("appName"):
        bits.append(f"in {cond['appName']}")
    if cond.get("windowName"):
        bits.append(f"window “{cond['windowName']}”")
    if cond.get("screenArea"):
        bits.append("screen area")
    return ", ".join(bits) or "everywhere"


def fixed_flags(children, parent_angle):
    """True for each item whose fixed angle Kando actually uses (it ignores negative and
    out-of-order angles and auto-places those items)."""
    ignored = {i for i, *_ in angle_problems(children, parent_angle)[0]}
    return [raw_angle(c) is not None and i not in ignored for i, c in enumerate(children)]


def outline(menu):
    lines = []
    sc = menu.get("shortcut") or menu.get("shortcutID") or "no shortcut"
    lines.append(f"{item_name(menu['root'])}  [{sc}]  ({conditions_text(menu)})")
    for path, node, parent_angle, angles in levels(menu):
        indent = "  " * len(path)
        if len(path) > 1:
            lines.append(f"{'  ' * (len(path) - 1)}▸ {' ▸ '.join(path[1:])}"
                         f"  (back = {compass(parent_angle)})")
        children = child_items(node)
        flags = fixed_flags(children, parent_angle)
        for c, a, is_fixed in sorted(zip(children, angles, flags), key=lambda p: p[1]):
            what, key = workflow_summary(c)
            fixed = "" if is_fixed else " (auto)"
            sub = " ▸" if c.get("type") == "submenu" else ""
            if parent_angle is not None and angular_distance(a, parent_angle) < 25:
                sub += "  ⚠ on the back link"
            lines.append(f"{indent}{compass(a):10} {a % 360:5.0f}°{fixed:7} {item_name(c)}{sub}"
                         f"{'  [' + key + ']' if key else ''}{'  ' + what if what else ''}")
    return "\n".join(lines)


# ------------------------------------------------------------------------ geometry --

def wedge_bounds(angles, parent_angle):
    """Start/end of each wedge: halfway to the neighbouring items (and the parent link)."""
    pts = sorted([(a, i) for i, a in enumerate(angles)]
                 + ([(parent_angle, -1)] if parent_angle is not None else []))
    res, n = {}, len(pts)
    for k, (a, i) in enumerate(pts):
        if n == 1:
            res[i] = (a - 180, a + 180)
            continue
        prev_a = pts[k - 1][0] - (360 if k == 0 else 0)
        next_a = pts[(k + 1) % n][0] + (360 if k == n - 1 else 0)
        res[i] = ((prev_a + a) / 2, (a + next_a) / 2)
    return res


def pt(cx, cy, r, deg):
    rad = math.radians(deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def ring_path(cx, cy, r0, r1, a0, a1):
    if a1 - a0 >= 359.9:  # a single item fills the ring: draw a full annulus
        return (f"M{cx},{cy - r1} A{r1},{r1} 0 1 1 {cx - 0.01},{cy - r1} Z "
                f"M{cx},{cy - r0} A{r0},{r0} 0 1 0 {cx - 0.01},{cy - r0} Z")
    large = 1 if (a1 - a0) > 180 else 0
    x0, y0 = pt(cx, cy, r1, a0)
    x1, y1 = pt(cx, cy, r1, a1)
    x2, y2 = pt(cx, cy, r0, a1)
    x3, y3 = pt(cx, cy, r0, a0)
    return (f"M{x0:.1f},{y0:.1f} A{r1},{r1} 0 {large} 1 {x1:.1f},{y1:.1f} "
            f"L{x2:.1f},{y2:.1f} A{r0},{r0} 0 {large} 0 {x3:.1f},{y3:.1f} Z")


def arc(cx, cy, r, a0, a1):
    large = 1 if (a1 - a0) > 180 else 0
    x0, y0 = pt(cx, cy, r, a0)
    x1, y1 = pt(cx, cy, r, a1)
    return f"M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f}"


# ------------------------------------------------------------------------- render --

def esc(s):
    return html.escape(str(s), quote=True)


def icon_html(item, size):
    theme, icon = item.get("iconTheme", ""), str(item.get("icon", ""))
    initials = esc(item_name(item)[:1].upper() or "?")
    fallback = f'<span class="ini" style="--s:{size}px">{initials}</span>'
    if theme == "material-symbols-rounded":
        return f'<span class="ms" style="font-size:{size}px">{esc(icon)}</span>'
    if theme in ("simple-icons", "simple-icons-colored"):
        url = f"{SIMPLE_ICONS}{esc(icon)}.svg"
        return (f'<span class="si" style="--s:{size}px"><img src="{url}" alt="" loading="lazy" '
                f'onerror="this.parentNode.classList.add(\'broken\')">{fallback}</span>')
    if theme == "emoji":
        return f'<span style="font-size:{size}px;line-height:1">{esc(icon)}</span>'
    return fallback


def kbd(text):
    return "".join(f"<kbd>{esc(p)}</kbd>" for p in str(text).split("+") if p) if text else ""


def render_level(path, node, parent_angle, angles):
    S, cx, cy, r_in, r_out, r_lbl = 400, 200, 200, 52, 164, 116
    children = child_items(node)
    bounds = wedge_bounds(angles, parent_angle)
    gap = 0.9
    svg = [f'<svg viewBox="0 0 {S} {S}" class="pie" aria-hidden="true">',
           f'<circle cx="{cx}" cy="{cy}" r="{r_out + 14}" class="halo"/>']
    # direction ticks (the 8 compass points)
    for k in range(8):
        x0, y0 = pt(cx, cy, r_out + 6, k * 45)
        x1, y1 = pt(cx, cy, r_out + (14 if k % 2 == 0 else 10), k * 45)
        svg.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                   f'class="tick{" major" if k % 2 == 0 else ""}"/>')
    flags = fixed_flags(children, parent_angle)
    for i, (c, a) in enumerate(zip(children, angles)):
        a0, a1 = bounds[i]
        cls = "w sub" if c.get("type") == "submenu" else "w"
        svg.append(f'<path class="{cls}" d="{ring_path(cx, cy, r_in, r_out, a0 + gap, a1 - gap)}"/>')
        if c.get("type") == "submenu":
            svg.append(f'<path class="subarc" d="{arc(cx, cy, r_out - 4, a0 + 4, a1 - 4)}"/>')
        if parent_angle is not None and flags[i] \
                and angular_distance(a, parent_angle) < 25:
            svg.append(f'<path class="clash" d="{ring_path(cx, cy, r_in, r_out, a0 + gap, a1 - gap)}"/>')
    if parent_angle is not None:
        a0, a1 = bounds[-1]
        svg.append(f'<path class="w back" d="{ring_path(cx, cy, r_in, r_out, a0 + gap, a1 - gap)}"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_in - 6}" class="center"/>')
    svg.append("</svg>")

    labels = []
    for c, a in zip(children, angles):
        x, y = pt(cx, cy, r_lbl, a)
        _, key = workflow_summary(c)
        sub = '<i class="arrow">▸</i>' if c.get("type") == "submenu" else ""
        k = f'<b class="key">{esc(key)}</b>' if key else ""
        labels.append(f'<div class="lbl" style="left:{x / S * 100:.2f}%;top:{y / S * 100:.2f}%">'
                      f'{icon_html(c, 22)}<span class="nm">{esc(item_name(c, ""))}{sub}</span>{k}</div>')
    if parent_angle is not None:
        x, y = pt(cx, cy, r_lbl, parent_angle)
        labels.append(f'<div class="lbl backlbl" style="left:{x / S * 100:.2f}%;top:{y / S * 100:.2f}%">'
                      f'<span class="ms" style="font-size:18px">undo</span><span class="nm">back</span></div>')
    center = f'<div class="lbl ctr" style="left:50%;top:50%">{icon_html(node, 30)}</div>'

    rows = []
    for c, a in sorted(zip(children, angles), key=lambda p: p[1] % 360):
        what, key = workflow_summary(c)
        name = esc(item_name(c, "")) + (' <i class="arrow">▸</i>' if c.get("type") == "submenu" else "")
        rows.append(f'<tr><td class="dir"><span class="ar">{ARROWS[COMPASS.index(compass(a))]}</span>'
                    f'{compass(a)}</td><td>{name}</td><td>{kbd(key) if key else ""}</td>'
                    f'<td class="what">{esc(what)}</td></tr>')
    crumbs = '<span class="sep">▸</span>'.join(f"<span>{esc(p)}</span>" for p in path)
    level = "root ring" if len(path) == 1 else f"submenu · back is {compass(parent_angle).lower()}"
    return (f'<article class="card"><header><h3>{crumbs}</h3><span class="lvl">{level}</span></header>'
            f'<div class="stage">{"".join(svg)}{"".join(labels)}{center}</div>'
            f'<table><thead><tr><th>Flick</th><th>Item</th><th>Key</th><th>Does</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></article>')


CSS = """
*{box-sizing:border-box}
html{background:var(--bg)}
body{margin:0;color:var(--text);font:14px/1.45 "Inter",system-ui,-apple-system,"Segoe UI",sans-serif;
  min-height:100vh;padding:40px 16px 56px;
  background:radial-gradient(1200px 700px at 12% -10%,var(--aurora1),transparent 60%),
             radial-gradient(900px 600px at 95% 10%,var(--aurora2),transparent 60%),var(--bg);
  background-attachment:fixed}
.wrap{max-width:1200px;margin:0 auto}
.top{display:flex;flex-wrap:wrap;gap:16px 32px;align-items:flex-end;justify-content:space-between;margin-bottom:8px}
h1{font-size:30px;line-height:1.1;margin:0;letter-spacing:-.02em;font-weight:700}
h1 span{color:var(--accent)}
.sub{color:var(--muted);margin:6px 0 0;max-width:60ch}
.legend{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:12px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:18px;height:12px;border-radius:3px;background:var(--wedge);border:1px solid var(--rim)}
.sw.sub{background:var(--wedge-sub);box-shadow:inset 0 -3px 0 var(--accent)}
.sw.back{background:transparent;border:1px dashed var(--muted)}
.sw.clash{background:repeating-linear-gradient(45deg,#ff5d7a55 0 3px,transparent 3px 6px);border-color:#ff5d7a}
.menu{margin-top:40px}
.menu>h2{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;margin:0 0 16px;font-size:22px;letter-spacing:-.01em}
.pill{font-size:12px;font-weight:500;padding:3px 10px;border-radius:999px;border:1px solid var(--rim);
  color:var(--muted);background:var(--glass)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px}
.card{background:var(--glass);border:1px solid var(--rim);border-radius:20px;padding:16px 16px 12px;
  backdrop-filter:blur(18px) saturate(140%);-webkit-backdrop-filter:blur(18px) saturate(140%);
  box-shadow:0 1px 0 rgba(255,255,255,.06) inset,0 20px 40px -24px rgba(0,0,0,.6)}
.card header{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:4px}
h3{margin:0;font-size:15px;font-weight:600}
h3 .sep{color:var(--accent);margin:0 6px;font-size:11px}
.lvl{font-size:11px;color:var(--muted);white-space:nowrap}
.stage{position:relative;width:100%;aspect-ratio:1}
.pie{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.halo{fill:none;stroke:var(--rim);stroke-width:1}
.tick{stroke:var(--muted);stroke-width:1;opacity:.5}.tick.major{stroke-width:2;opacity:.9}
.w{fill:var(--wedge);stroke:var(--rim);stroke-width:1}
.w.sub{fill:var(--wedge-sub)}
.subarc{fill:none;stroke:var(--accent);stroke-width:3;stroke-linecap:round;opacity:.9}
.w.back{fill:transparent;stroke:var(--muted);stroke-dasharray:4 5;opacity:.8}
.clash{fill:#ff5d7a33;stroke:#ff5d7a;stroke-width:1.5}
.center{fill:var(--center);stroke:var(--accent);stroke-width:2;filter:drop-shadow(0 0 12px var(--glow))}
.lbl{position:absolute;transform:translate(-50%,-50%);display:flex;flex-direction:column;
  align-items:center;gap:3px;width:92px;text-align:center;pointer-events:none}
.nm{font-size:12px;line-height:1.2;font-weight:500}
.backlbl{color:var(--muted)}.backlbl .ms{color:var(--muted)}
.arrow{color:var(--accent);font-style:normal;margin-left:3px;font-size:10px}
.key{font:600 10px/1 ui-monospace,"Cascadia Code",Consolas,monospace;padding:3px 5px;border-radius:5px;
  background:var(--accent);color:#fff;min-width:16px}
.ms{font-family:"Material Symbols Rounded";font-weight:normal;font-style:normal;line-height:1;
  color:var(--accent);display:inline-block;width:1em;height:1em;overflow:hidden;
  font-feature-settings:"liga";-webkit-font-smoothing:antialiased}
.si{position:relative;display:inline-grid;place-items:center;width:var(--s);height:var(--s)}
.si img{width:100%;height:100%;filter:var(--si-filter) drop-shadow(0 0 4px var(--glow))}
.si .ini{display:none}.si.broken img{display:none}.si.broken .ini{display:grid}
.ini{display:grid;place-items:center;width:var(--s);height:var(--s);border-radius:50%;
  font-weight:700;font-size:calc(var(--s) * .5);color:var(--accent);border:1.5px solid var(--accent)}
table{width:100%;border-collapse:collapse;margin-top:6px;font-size:12.5px}
th{text-align:left;font-size:10.5px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;
  color:var(--muted);padding:6px 6px;border-bottom:1px solid var(--rim)}
td{padding:6px 6px;border-top:1px solid var(--rim);vertical-align:top}
tbody tr:first-child td{border-top:0}
td.dir{white-space:nowrap;color:var(--muted)}.ar{display:inline-block;width:16px;color:var(--accent);font-weight:700}
td.what{color:var(--muted)}
kbd{font:600 11px/1 ui-monospace,"Cascadia Code",Consolas,monospace;padding:3px 6px;border-radius:6px;
  border:1px solid var(--rim);border-bottom-width:2px;background:rgba(255,255,255,.06);margin-right:3px;
  display:inline-block}
footer{margin-top:48px;color:var(--muted);font-size:12px;text-align:center}
footer a{color:var(--accent)}
@media (max-width:420px){.grid{grid-template-columns:1fr}h1{font-size:24px}}
@media print{
  html,body{background:#fff !important;color:#111}
  body{padding:0}
  :root{--text:#111;--muted:#555;--glass:#fff;--rim:#ccc;--wedge:#f1edf8;--wedge-sub:#e3dbf3;
        --center:#fff;--accent:#5b2bc4;--glow:transparent}
  .card{backdrop-filter:none;box-shadow:none;break-inside:avoid}
  :root{--si-filter:none}
  .key{color:#fff}
}
"""


def render_html(menus, palette, accent):
    p = dict(PALETTES[palette])
    if accent:
        p["accent"] = accent
    vars_ = ";".join(f"--{k}:{v}" for k, v in p.items())
    body = []
    for m in menus:
        sc = m.get("shortcut") or m.get("shortcutID")
        cards = "".join(render_level(*lv) for lv in levels(m))
        body.append(f'<section class="menu"><h2>{esc(item_name(m["root"], ""))}'
                    f'<span>{kbd(sc) if sc else "<span class=pill>no shortcut</span>"}</span>'
                    f'<span class="pill">{esc(conditions_text(m))}</span></h2>'
                    f'<div class="grid">{cards}</div></section>')
    font = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
            '&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=block">')
    legend = ('<div class="legend"><span><i class="sw"></i>button</span>'
              '<span><i class="sw sub"></i>submenu</span><span><i class="sw back"></i>way back</span>'
              '<span><i class="sw clash"></i>blocks the way back</span>'
              '<span><b class="key">K</b>quick-select key</span></div>')
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Kando Menu Sheet</title>{font}<style>:root{{{vars_}}}{CSS}</style></head><body>'
            f'<div class="wrap"><div class="top"><div><h1>Kando <span>menu sheet</span></h1>'
            f'<p class="sub">Every ring, drawn where Kando will put each item. Learn the flicks: '
            f'click, then hold and draw, then turbo.</p></div>{legend}</div>{"".join(body)}'
            f'<footer>Made with the Kando skill for Claude · placement matches Kando 3.0 · '
            f'<a href="https://kando.menu">kando.menu</a></footer></div></body></html>')


def load(path):
    """Parsed JSON, or exit with a one-line reason (never a traceback)."""
    try:
        with open(path, encoding="utf-8-sig") as f:
            text = f.read()
    except FileNotFoundError:
        sys.exit(f"Cannot find {path}.")
    except UnicodeDecodeError:
        sys.exit(f"{path} is not UTF-8 text. Kando reads its files as UTF-8; re-save it as UTF-8.")
    except OSError as e:
        sys.exit(f"Cannot read {path}: {e.strerror or e.__class__.__name__}.")
    if not text.strip():
        sys.exit(f"{path} is empty.")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        sys.exit(f"{path} is not valid JSON (line {e.lineno}, column {e.colno}). "
                 "Run kando_check.py on it first.")
    except RecursionError:
        sys.exit(f"{path} is nested too deeply to read.")


def menu_list(data):
    """The drawable menus of a menus.json or a single exported menu; skips the rest."""
    if isinstance(data, dict) and "menus" not in data and isinstance(data.get("menu"), dict):
        data = {"menus": [data["menu"]]}
    menus = data.get("menus") if isinstance(data, dict) else None
    if not isinstance(menus, list):
        return []
    return [m for m in menus if isinstance(m, dict) and isinstance(m.get("root"), dict)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("menus", help="menus.json or a single exported menu")
    ap.add_argument("--menu", action="append", help="only this menu (root name, repeatable)")
    ap.add_argument("--html", help="write a radial cheat sheet to this .html file")
    ap.add_argument("--palette", choices=sorted(PALETTES), default="purple")
    ap.add_argument("--accent", help="override the accent color, e.g. #b06cff")
    args = ap.parse_args()
    use_utf8_output()
    menus = menu_list(load(args.menus))
    if not menus:
        sys.exit(f"No menus found in {args.menus}. Expected a menus.json with a 'menus' list, "
                 "or a single exported menu. Run kando_check.py on it for details.")
    if args.menu:
        wanted = {m.lower() for m in args.menu}
        menus = [m for m in menus if item_name(m["root"], "").lower() in wanted]
        if not menus:
            sys.exit(f"No menu named {', '.join(args.menu)}.")
    for m in menus:
        print(outline(m))
        print()
    if args.html:
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(render_html(menus, args.palette, args.accent))
        print(f"Wrote {args.html}")


if __name__ == "__main__":
    main()
