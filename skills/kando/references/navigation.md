# Using Kando fast: navigation, opening, learning path

Sources: kando.menu/usage, the 3.0 changelog, and Simon's video "How to be FAST with Kando"
(youtube.com/watch?v=elHUCarOiXQ).

## Selection modes (switch freely, any time)

| Mode | How | Best for |
|---|---|---|
| Point and click | Click anywhere in the item's wedge (Fitts's law: no aiming at the icon). Submenu wedges are clickable before the animation ends. | Learning the layout |
| Marking | Hold left button, draw. A pause or sharp turn selects / opens the next ring. Draw straight zig-zags, not curves. | Daily use; two-level picks become one stroke |
| Turbo | Open with a key combo, keep the modifier (Ctrl/Alt/Shift/Meta) held, move, release to select. No clicking. | Keyboard + mouse users, mouse buttons mapped to shortcuts |
| Hover | Per-menu `hoverMode`: move and pause, no click or key. | Fastest, but accidental picks; small menus |
| Keyboard | Quick-select keys, 1–9 by position, arrows + Enter, Backspace back, Esc close | Hands on keyboard; chains like `G` `D` |
| Gamepad | Stick to point, buttons to select/back/close | Couch / Steam Deck |

Closing without picking: Esc, right-click (unless `rmbSelectsParent`), or click the center.

Single-key turbo was removed in 3.0; hover mode replaces it.

## Learning path (Simon's recommendation)

1. **Point and click** for a few days. Learn where things are; click anywhere in the wedge.
2. **Marking**: hold and flick. Start with top-level items, then two-level zig-zags.
3. **Turbo**: open with the shortcut, keep the modifier held, flick, release.
4. Optional: `fixedStrokeLength` ~100 for instant firing once the directions are automatic.

Turn on `enableSelectionWedges` while learning, so the active wedge is visible. Print the
cheat sheet from `kando_preview.py --html` and keep it next to the screen for the first week.

Learning tips:
- Fixed angles are what make this work. Don't let items auto-shift.
- Learn one menu at a time.
- Say the direction out loud at first ("down, right = Unreal"). It sticks faster.

## Opening menus

- **Shortcut per menu** (key names, see menus-json.md §7). Pick combos that nothing else uses;
  Kando grabs them globally.
- **Same shortcut, different menu per app** with conditions (menus-json.md §6).
- **Mouse buttons / pens / touch** need a helper tool. Two ways:
  1. Make the tool send the menu's shortcut. Use an otherwise unused combo like `Ctrl+F13`
     (keyboards don't have F13, so nothing clashes). Fastest.
  2. Make the tool run `kando --menu "Name"` or `kando --trigger <shortcut|shortcutID>`.
  Windows tools named in the docs: AutoHotkey (mouse buttons, hold-to-mark, gamepad),
  GestureSign (touch), Kanata (key chords). Many mouse/keyboard vendor apps can also map a
  button to `Ctrl+F13` directly. Turbo mode works with a mouse button mapped to a combo:
  hold the button (it holds Ctrl), move, release.
- **CLI**: `kando --menu "Name"`, `--trigger`, `--close-menu`, `--settings`,
  `--reload-menu-theme`, `--reload-sound-theme`, `--config-dir <dir>`, `--version`.
  `--menu` and `--trigger` behave like the shortcut (conditions apply).
- **IPC (WebSocket)**: `ipc-info.json` in the config folder has the port (changes each run).
  Messages `show-menu {name}` and `show-custom-menu {menu}` (a full menu in menus.json format,
  built on the fly). Kando answers with `menu-interaction` / `error`. The protocol changed in
  3.0. Use it for generated menus, e.g. a script that builds a "recent projects" menu.

## Placement options per menu

- Default: opens at the pointer, submenus open where you select them. Best for marking.
- `useFixedPosition` + `fixedMenuPosition`: always at one spot (0.5/0.5 = screen center).
  Touchscreens; smaller targets.
- `anchored`: submenus open in place. Simon: "basically breaks marking mode". Touch or
  gamepad only.

## Editor tips

- Open: gear button on an open menu, Ctrl+, while a menu is open, tray → Show Settings,
  or `kando --settings`.
- Drag items from the bottom toolbar into the preview; drag back to delete. Double-click a
  submenu to edit inside it.
- App picker (Execute Command), window picker (Focus Window and conditions), file picker,
  macro recorder. Drag Start-menu apps, files or links straight into the editor.
- Backups: General Settings has backup/restore buttons; Kando also backs up automatically
  when the version changes.
