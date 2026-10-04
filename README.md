# Kando skill for Claude

A [Claude](https://claude.ai) skill for [Kando](https://kando.menu), the open-source pie menu
by Simon Schneegans. Ask Claude to design, fix, theme or explain your Kando menus and it
knows the Kando 3.0 file format, how Kando places items, and what makes a pie menu fast.

![Radial cheat sheet generated from the example menus](docs/example-sheet.png)

## What it does

- **Designs menus for speed**: fixed directions, 8 items per ring, the same gesture for the
  same idea across apps, the way back to the parent kept clear.
- **Per-app work menus**: one shortcut that opens a different menu in Maya, Painter,
  Unreal, Blender or your browser, with a fallback everywhere else.
- **Checks your files before Kando does** (`kando_check.py`): invalid JSON, key *names* vs key
  *codes*, 2.x leftovers, angles Kando will drop, items sitting on the back link,
  hotkeys fired before the menu closes, clashing quick keys, and personal data before you share.
- **Shows you the layout** (`kando_preview.py`): a compass outline in chat and a radial HTML
  cheat sheet, using a port of Kando's own placement code, so what you see is where items land.
- **Themes**: turns a vibe ("dark purple glass") into a palette, then a color override,
  preset or a full menu theme (theme.json5 + CSS).
- **Teaches**: settings explained with tuning recipes, and Simon's learning path from
  point-and-click to marking and turbo mode.

## Install

Claude Code:

```
git clone https://github.com/nicholascathedu/kando-skill-
cp -r kando-skill-/skills/kando ~/.claude/skills/
```

Claude apps: zip the `skills/kando` folder and upload it under Settings → Capabilities → Skills.

The scripts need Python 3 (standard library only).

## Try it

- "Look at my Kando menus.json and tell me what would make it faster."
- "Make me a Kando menu for Blender on Ctrl+4 that only shows in Blender."
- "My Kando menu stopped updating after I edited the JSON."
- "I want a dark purple transparent look for my Kando menu."
- "Explain turbo mode and how to open Kando with my mouse's side button."

## Layout

```
skills/kando/
  SKILL.md               the workflow Claude follows
  references/            menus.json format, settings, navigation, design, themes, app hotkeys, sources
  scripts/               kando_check.py, kando_preview.py
  examples/              a desktop launcher and Maya / Painter / Unreal work menus
```

## Scope and sources

Written for **Kando 3.0** on Windows, macOS and Linux, from the official docs, the Kando
source code (settings schemas, placement math, actions) and Simon's videos. Where the 3.0
docs and code disagree, the skill follows the code; see `references/sources.md`.

Not affiliated with Kando. Kando is MIT-licensed by Simon Schneegans; this skill is MIT too.
If Kando helps you, consider [supporting Simon](https://kando.menu/donating/).
