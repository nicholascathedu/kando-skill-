---
name: kando
description: Design, build, fix, theme and learn menus for Kando, the open-source pie menu by Simon Schneegans (kando.menu). Use this whenever someone mentions Kando, a pie menu or radial/marking menu on their desktop, menus.json or config.json in a kando folder, Kando themes, workflows, quick-select keys, per-app menus, or wants a faster launcher or hotkey menu for apps like Maya, Blender, Substance Painter, Unreal, Photoshop or a browser, even if they never say "Kando" but describe a menu that pops up around the mouse. Keeps a short profile of their setup and taste so help gets more personal over time.
---

# Blessed: a Claude agent for Kando

Kando (https://kando.menu), by Simon Schneegans, is a cross-platform pie menu: press a
shortcut, a ring of items appears around the pointer, and you pick one by clicking, flicking or
keyboard. This skill helps you build menus that are fast to use and feel like the person's own:
it knows the Kando 3.x file format, how Kando places items, what makes a gesture memorable,
and how to theme it.

## Whose menu it is

The person brings the taste; you bring precision and memory. Work that way every time:

- Ask about the feeling they want (words, a game, an image) before proposing a look.
- Keep their names, icons and locked directions unless they ask for a change. Suggest, then let
  them choose; when you disagree, say why in one line and do it their way.
- Offer two or three directions for anything visual instead of one finished answer.
- Explain each placement in terms of their hands and habits, not rules.
- Credit what a design builds on (Kando's Default theme, a game, an artist) when it's shared.

Written against **Kando 3.0** (Sept 2026). The 3.0 code is ahead of the website docs in a few
places; where they disagree, trust the schema notes in `references/menus-json.md`.

## What you can do with it

| The user wants to... | Do this |
|---|---|
| Understand their setup | Read their files, run `scripts/kando_preview.py` and explain the outline |
| Make a new menu or redesign one | Follow **Designing a menu** below, then `references/menu-design.md` |
| Fix "my menu doesn't open / nothing happens" | Run `scripts/kando_check.py`, then the troubleshooting list below |
| Change speed, feel or behavior | `references/settings.md` |
| Learn to use Kando faster | `references/navigation.md` (learning path, turbo, marking, keyboard) |
| Build a menu for a specific app | `references/app-recipes.md` for hotkeys, then the design method |
| Change the look, colors or make a theme | `references/themes.md` |
| Share a menu publicly | `kando_check.py --publish` first, it flags personal data |
| Have Claude remember their setup and taste | `scripts/kando_profile.py`, then `references/profile.md` |

## Where the files are

| OS | Config folder |
|---|---|
| Windows | `%APPDATA%\kando\` |
| macOS | `~/Library/Application Support/kando/` |
| Linux | `~/.config/kando/` (Flatpak: `~/.var/app/menu.kando.Kando/config/kando/`) |

Inside: `menus.json` (menus), `config.json` (general settings), and the folders
`menu-themes/`, `sound-themes/`, `icon-themes/`. The install folder (`%LOCALAPPDATA%\Kando` on
Windows, with `kando.exe` and `app-<version>`) holds no settings, so don't edit there.

If you can't reach the user's disk, ask them to paste or upload `menus.json` and
`config.json`, or to export a single menu from the editor (it includes shortcut, tags and
conditions since 3.0).

## The safe-edit loop

Kando hot-reloads both JSON files the moment they're saved, and it **silently refuses an
invalid file** (it keeps the old menus, and refuses to start if the file is broken at launch).
So the failure mode of a bad edit is "nothing happens", which is confusing. Every edit goes:

1. **Back up** the file next to it with a date, e.g. `menus.backup-2026-10-04.json`.
   On Windows: `Copy-Item "$env:APPDATA\kando\menus.json" "$env:APPDATA\kando\menus.backup-$(Get-Date -f yyyy-MM-dd-HHmm).json"`
2. **Edit** a copy, keeping everything you didn't mean to change byte-for-byte.
3. **Check** it: `python scripts/kando_check.py menus.json --config config.json`.
   Fix every ERROR. Read the WARNs; most are real usability problems.
4. **Preview** it: `python scripts/kando_preview.py menus.json --menu "<name>"` and compare the
   compass outline with what the user asked for.
5. **Save** over the real file. Kando reloads it immediately. Ask the user to press the
   shortcut and try one item from each ring.
6. If something's wrong, restore the backup; it reloads just as fast.

Ask before writing into the user's real config folder; it's their live setup. Writing a
proposed file next to it, or in your own workspace, is fine without asking.

For bigger experiments, Kando can run on a throwaway config: `kando --config-dir <folder>`.

## It remembers you

The skill gets more personal the more it's used. It keeps a short `kando-profile.md` next
to `menus.json` with the person's anchors, apps, palette, naming voice, workflows and the
ideas they turned down.

- **Start of every Kando task:** read `kando-profile.md` if it exists. Keep its anchors
  fixed, name things in their voice, start themes from their palette, and don't
  re-suggest what they said no to.
- **No profile yet:** offer to draft one with `python scripts/kando_profile.py menus.json
  --config config.json`, fill the taste sections with them, and ask before saving.
- **After a change they accept:** propose the few lines to add and ask before writing.
  Never store secrets, IDs, emails or full paths. Details in `references/profile.md`.

## Designing a menu

A pie menu is fast because of **muscle memory**: the same item is always in the same
direction, so after a week the hand moves before the eyes look. Every design choice serves
that. The method (details and examples in `references/menu-design.md`):

1. **Inventory.** List what the user actually does, how often, and in which app. Ask if it
   isn't clear. Things they already press without thinking (Ctrl+C, the app's own hotbox)
   don't belong in the menu; things they look up, reach for awkwardly, or do in several steps do.
2. **Rank.** The 8 compass directions are the prime spots. Most-used actions get Up, Down,
   Left, Right (the easiest flicks), then the diagonals.
3. **Group the rest** into submenus of related things (Display modes, Switch app, Snippets).
   Aim for ~8 items per ring, never more than 12. Prefer depth over width: with marking mode
   two flicks are as fast as one.
4. **Fix the angles.** Give every item an explicit `angle` (0 = up, 90 = right, 180 = down,
   270 = left), listed clockwise so each angle is larger than the one before, all from 0 to
   359. Kando ignores an angle that is negative or smaller than the previous one. Auto-placement
   shifts items whenever you add one, which breaks muscle memory.
5. **Keep anchors consistent.** If several menus share an idea (Save, Undo, Switch app), put
   it in the same direction in all of them. One gesture learned, many menus served.
6. **Keep the way back clear.** Inside a submenu the parent sits opposite the submenu's own
   direction (a submenu at 90° has "back" at 270°). Never put a child there.
7. **Wire workflows.** Each item runs a list of actions. Usual shape for "press a key in my
   app": `close-menu` first, then `simulate-hotkey`. See the patterns in
   `references/menu-design.md` and every action in `references/menus-json.md`.
8. **Add quick-select keys** (`quickSelectKey`, one letter per item, mnemonic) so the menu also
   works from the keyboard, and `Backspace` on the center to go back.
9. **Check and preview** (safe-edit loop), then show the user the compass outline or the HTML
   sheet before they try it.

### Per-app menus on one key

Several menus can share one shortcut. Each gets `conditions.appName` (on Windows the process
file name, e.g. `maya`, `UnrealEditor`; case-insensitive "contains", or a regex if it starts
with `/`). Have the user confirm the name with the editor's window picker. Kando opens the
menu with the most matching conditions, so add one menu **without conditions** as the
fallback. Kando registers the key globally, so it's swallowed in every app even when no
menu matches, and it takes the key away from the apps themselves: check the combo isn't
an app hotkey they use (Blender: Ctrl+1–5 set subdivision level; Unreal: Ctrl+0–9 set
camera bookmarks). `Ctrl+F13`–`F24` never collide.

## Showing a design to the user

Don't paste raw JSON at people to explain a menu. Instead:
- Run `kando_preview.py` and show the compass outline (Up / Up-right / ... with names and keys).
- For a visual, run it with `--html sheet.html` (palettes: `purple`, `midnight`, `light`). It
  draws every ring where Kando will really put each item, with the back link dashed, plus a
  table per ring (direction, item, key, what it does). Red wedges mark items sitting on the way
  back out of a submenu. It doubles as a printable cheat sheet while learning the gestures.
- Explain *why* each item sits where it does (frequency, consistency with other menus).

## Key names vs key codes (the #1 mistake)

| Where | Format | Example |
|---|---|---|
| Menu `shortcut` | key **names** (layout-dependent) | `Control+Shift+K`, `Ctrl+F13` |
| `simulate-hotkey`, `execute-macro` | physical key **codes** | `ControlLeft+ShiftLeft+KeyK`, `Digit1`, `Backquote` |
| `quickSelectKey` | the key as typed | `A`, `Backspace` |

Codes are physical positions, so on AZERTY or QWERTZ keyboards `KeyZ` may type a different
letter. Ask about the keyboard layout when the menu presses letter keys.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Edits do nothing | JSON invalid → Kando kept the old file. Run `kando_check.py`. |
| Kando won't start | Invalid file at launch. Restore the backup or fix the error. |
| Hotkey item does nothing / types in the wrong place | `close-menu` missing or after the keys; or a key *name* used where a *code* is needed. |
| Hotkey is slow to fire | Actions after `close-menu` wait for the fade-out. Lower `fadeOutDuration` (60–80 ms). |
| Per-app menu doesn't appear | `appName` doesn't match the exe name. Use the editor's window picker to read it. |
| A key stopped typing in other apps | It's a Kando shortcut; Kando grabs it everywhere. Move the menu to a rarely used combo (`Ctrl+F13`, `Ctrl+Shift+<n>`). |
| Item ends up in an unexpected spot | No fixed angle, or an angle Kando ignores (negative, or smaller than the one listed before it). Two siblings on the same angle are drawn on top of each other. Run the check and the preview. |
| Turbo mode / keyboard stopped working | `keepInputFocus` is true. |

## Kando version notes

- 3.0 replaced 2.x item types (`command`, `hotkey`, `uri`...) with three types (`root`,
  `submenu`, `button`) that run **workflows** of actions. Configs upgrade automatically and
  can't go back to 2.x. If a user's JSON has `"type": "command"`, it's a 2.x file.
- `centered` is now `useFixedPosition` + `fixedMenuPosition`.
- If the user runs a newer Kando than 3.0, check the changelog
  (github.com/kando-menu/kando/blob/main/docs/changelog.md) before relying on details here.

## Reference files

Read the one you need; each is self-contained.

- `references/menus-json.md`: full menus.json format, every action type, conditions, keys
- `references/settings.md`: every config.json setting with defaults and tuning recipes
- `references/navigation.md`: selection modes, keyboard, learning path, opening via mouse
  buttons, CLI and IPC
- `references/menu-design.md`: the design method in depth, workflow patterns, anti-patterns
- `references/themes.md`: menu themes (theme.json5 + CSS), color overrides, icons, sounds
- `references/app-recipes.md`: ready hotkey sets for Maya, Substance Painter, Unreal, Blender,
  browsers, Discord, with what to verify
- `references/sources.md`: official sources and the docs-vs-code differences in 3.0
- `references/profile.md`: the personal profile, where it lives, what goes in it, and the
  read / draft / update loop

Scripts share `scripts/kando_layout.py`, a port of Kando's own placement code, so the checker,
the preview and the profile agree with what Kando draws. All run on Python 3.9+ with no installs.

- `scripts/kando_check.py`: validates menus.json / config.json, `--publish` flags personal data
- `scripts/kando_preview.py`: compass outline and radial HTML cheat sheet
- `scripts/kando_profile.py`: drafts `kando-profile.md` (shortcuts, directions, anchors,
  drift, apps, theme and selection settings), with no paths or personal data

Examples: `examples/desktop-launcher.json` (a general launcher with clipboard and media),
`examples/3d-work-menus.json` (Maya / Painter / Unreal menus on one key). Load them, run the
preview on them, and adapt. They're starting points, not finished configs: launch commands
differ per PC, so prefer the editor's app picker for those.
