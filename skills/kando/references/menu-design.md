# Designing Kando menus that get faster with use

## Contents
1. Principles
2. The design session (what to ask, what to produce)
3. Layout templates
4. Workflow patterns
5. Per-app "work mode" menus
6. Anti-patterns
7. Reviewing someone's existing menus

## 1. Principles

- **Direction is the memory.** People remember "down then right", not "the fourth item".
  Fixed angles on every item; never let a new item shift the others.
- **8 is the magic number.** The 8 compass directions are easy to hit blind. Up to 12 works
  with care; beyond that, split into submenus. Kando's docs: ~8 per ring, never above 12.
- **Depth beats width.** In marking mode, two short flicks are about as fast as one, and two
  rings of 8 hold 64 items you can hit blind.
- **Cardinals first.** Up / Down / Left / Right are the easiest and most accurate flicks;
  put the most frequent actions there.
- **Anchors across menus.** The same concept lives in the same direction in every menu
  (e.g. Save down-left, Switch app down). Gestures transfer between apps.
- **Clear way back.** In a submenu, the parent link sits opposite the submenu's direction.
  Leave about 45° around it empty.
- **Mirror related pairs.** Undo left / Redo right, Previous up / Next down, Zoom in / out
  opposite. Opposites feel natural as opposite directions.
- **Menus are for what's awkward.** Don't duplicate keys the user already hits without
  thinking. The menu wins for: hotkeys that need a stretch or a lookup, multi-step actions,
  snippets, switching apps, things buried in menus.
- **Same key, right menu.** One shortcut with per-app menus beats a different shortcut per
  app; the hand only learns one trigger.

## 2. The design session

Ask (or infer from files and conversation):
1. Which apps and what tasks? What do they do most often, and what do they keep looking up?
2. Mouse, tablet or touch? Which hand is on the mouse? Keyboard layout (QWERTY / AZERTY /
   QWERTZ matters for letter hotkeys)?
3. Which shortcut is free? Do they have spare mouse buttons?
4. Do they want one menu everywhere, or a different one per app?

Produce, in this order:
1. A **compass sketch** for each ring (a table: direction, item, what it does, quick key).
   Explain the reasoning in a sentence or two.
2. After they agree: the JSON, checked with `kando_check.py`, and the preview outline or
   HTML sheet from `kando_preview.py`.
3. A short "how to try it" list: which key opens it, what to flick first.

Quick-select keys: use the first letter when free, otherwise a strong consonant; keep keys
stable across menus (S = Save everywhere). Use `Backspace` on every center to go back.

## 3. Layout templates

**8-way launcher**

| Dir | Typical role |
|---|---|
| Up (0) | Most used app or group |
| Right (90) | Browser / web |
| Down (180) | Work apps group |
| Left (270) | Communication / media group |
| Diagonals | Files, settings, clipboard, screenshot |

**Work-mode menu (inside an app)**

| Dir | Typical role |
|---|---|
| Up | View: frame / focus selected |
| Up-right, Right | Display or view-mode submenu |
| Down-right | Cleanup (delete history, clear) |
| Down | **Switch app** submenu (same in every app) |
| Down-left | Save |
| Left | Organize (group, rename, prefixes) |
| Up-left | Duplicate / create |

**4-item submenus**: use the cardinals that aren't the back link, plus one diagonal; or
five evenly spaced slots (72° apart) with the back link in one of them.

## 4. Workflow patterns

| Pattern | Actions | Use for |
|---|---|---|
| App hotkey | close-menu → simulate-hotkey | Any app shortcut that's awkward to reach |
| Launch | close-menu → execute-command (app picker) | Starting apps |
| Switch app | close-menu → focus-window `appName` | Jumping between open apps in a pipeline |
| Snippet | close-menu → set-clipboard → Ctrl+V | Naming prefixes, email signature, code |
| Console command | close-menu → set-clipboard → open console key → delay 0.2 → Ctrl+V → Enter | Unreal / game consoles |
| Cross-app | close-menu → Ctrl+C → focus-window B → shortcut in B → paste | Search selected text, send to another app |
| Repeat-fire | (no close-menu) → global key or command | Volume, media, brightness; click many times |
| Menu hop | open-menu `Name` | A launcher that opens a bigger themed submenu as its own menu |
| Toggle pair | two items in opposite directions | `slomo 0.25` / `slomo 1`, show / hide |
| Smart center | root `activateWorkflow` with an action | Center click = the single most common action |

Notes:
- The clipboard patterns overwrite whatever was copied. Say so to the user.
- Add `delay` (0.1–0.3 s) where an app needs time to open a console or dialog.
- `inhibit-shortcuts` before simulating a key combo that is also a Kando shortcut.
- Use `{{app_name}}` / `{{window_name}}` in commands or URIs for context-aware actions.

## 5. Per-app "work mode" menus

1. One shortcut (e.g. Ctrl+4, or Ctrl+F13 on a mouse button) for all of them.
2. One menu per app with `conditions.appName` set to the exe name (window picker shows it).
3. One fallback menu without conditions on the same shortcut (the general launcher).
4. Tag them into a collection ("Work") so the editor stays tidy.
5. Shared anchors: Switch app always Down, Save always Down-left, etc.
6. Fill with that app's **default** hotkeys (see app-recipes.md) and leave gaps for the
   user's custom ones rather than inventing keys the app doesn't have.

## 6. Anti-patterns

| Anti-pattern | Why it hurts | Instead |
|---|---|---|
| No fixed angles | Items move when you add one; memory breaks | Angle on every item |
| 12+ items in a ring | Small wedges, slow, error-prone | Submenus |
| 5+ levels deep | Hard to remember the path | Max 3 levels; promote frequent items |
| Child on the back link | Flick is ambiguous | Keep 45° clear |
| Hotkey before close-menu | Keys go to Kando's window | close-menu first |
| Bare-letter or symbol shortcut | That key stops typing everywhere | Modifier combo or F13–F24 |
| Different shortcut per app | More to learn | One shortcut + conditions |
| Conditions on every menu of a shortcut | Key swallowed in other apps, nothing opens | Add an unconditioned fallback |
| Duplicating keys they already know | Slower than the keyboard | Only awkward / multi-step actions |
| Hard-coded user paths in shared menus | Breaks on other PCs, leaks the username | Env vars (`%APPDATA%`), app picker, `--publish` check |
| Long `fadeOutDuration` with hotkey menus | Every item waits | 60–80 ms |

## 7. Reviewing someone's existing menus

1. Run `kando_check.py` on menus.json (and config.json) and `kando_preview.py` for the outline.
2. Report in plain words, worst first: things that are broken, then things that slow them
   down, then nice-to-haves. Quote item names, not JSON paths.
3. Propose a revised compass sketch for any ring you'd change, with the reason.
4. Never silently drop items. If you'd remove something, say so and why.
5. Keep their names, icons and personal items exactly as they are unless asked.
