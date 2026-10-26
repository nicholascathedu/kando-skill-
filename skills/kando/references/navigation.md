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

Closing without picking: Esc, right-click (unless `rmbSelectsParent`), or click outside the menu. Clicking the center of the main ring runs the root's own action if it has one, and does nothing otherwise.

Single-key turbo was removed in 3.0; hover mode replaces it.

## Learning path (Simon's recommendation)

1. **Point and click** for a few days. Learn where things are; click anywhere in the wedge.
2. **Marking**: hold and flick. Start with top-level items, then two-level zig-zags.
3. **Turbo**: open with the shortcut, keep the modifier held, flick, release.
4. Optional: `fixedStrokeLength` ~100 for instant firing once the directions are automatic.

Turn on `enableSelectionWedges` while learning, so the active wedge is visible. Print the
cheat sheet from `kando_preview.py --html` and keep it next to the screen for the first week.

**A Learn item in every menu.** Give each menu one item, on a diagonal or in a submenu you
rarely use, that opens its own cheat sheet, always up to date with the menu:
`execute-command` `pythonw C:\path\to\kando_preview.py --menu Maya --html "%TEMP%\kando-maya.html" --open`.
When you forget where something is, flick to Learn instead of opening the editor. Drop the
item once the menu is in your hands.

Learning tips:
- Fixed angles are what make this work. Don't let items auto-shift.
- Learn one menu at a time.
- Say the direction out loud at first ("down, right = Unreal"). It sticks faster.

**Where am I on the path?** `scripts/kando_coach.py` reads Kando's own `achievements.json`
(totals of click / keyboard / flick / gamepad picks, speed tiers per depth, cancels) and prints
what to practise next. `--save` remembers today's numbers so the next run shows progress. It
coaches the hands only: Kando keeps no per-item stats. The numbers are personal, so keep them
out of anything shared.

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
  **Windows, no extra app:** `scripts/windows/kando-mouse-buttons.ps1` does option 1 with
  Windows PowerShell and a low-level mouse hook. The Forward (or Back) side button holds Ctrl
  and taps F13, and releasing it lets go of Ctrl, so turbo mode works. Set the menu's shortcut
  to `Control+F13`. `-InstallStartup` adds a Startup-folder shortcut so it runs at login (no
  admin). Tell the user its limits: the button loses Back / Forward while it runs; it can't
  reach apps running as admin unless it runs as admin too; some games' anti-cheat block
  simulated keys; antivirus may warn about the hook. Show them the script before they run it.
- **CLI**: `kando --menu "Name"`, `--trigger`, `--close-menu`, `--settings`,
  `--reload-menu-theme`, `--reload-sound-theme`, `--config-dir <dir>`, `--version`.
  `--menu` and `--trigger` behave like the shortcut (conditions apply).
- **IPC (WebSocket)**: `ipc-info.json` in the config folder has the port (changes each run).
  Messages `show-menu {name}` and `show-custom-menu {menu}` (a root menu item with its
  children, built on the fly; no shortcut or conditions). Kando answers with `menu-interaction` / `error`. The protocol changed in
  3.0. Use it for generated menus, e.g. a script that builds a "recent projects" menu.

## When the menu sometimes doesn't open (Windows)

From the Kando 3.0 source; the official docs don't cover this. First split the problem: with
the same app in front, open the menu from the tray icon or `kando --menu "Name"`. If that works,
the shortcut isn't reaching Kando (cause 2). If it doesn't, it's the window (causes 1, 3, 5).
To see Kando's log, start it from a terminal: `No menu was found for the current conditions`
means it heard the shortcut but no menu matched the app in front (cause 4).

1. **Exclusive fullscreen game.** Kando's menu is an always-on-top window, which covers normal
   and borderless fullscreen windows but not exclusive fullscreen. Fix: set the game to
   Borderless / Windowed fullscreen.
2. **Another app owns or eats the shortcut.** Kando binds it as a Windows global hotkey: one
   owner per combo, first come first served, and Kando doesn't report a failed bind. Overlays,
   Discord keybinds, AutoHotkey and some games also swallow keys with their own hooks. If it
   depends on start order, restarting Kando brings it back until the other app starts. Fix:
   free the combo there, or move the menu to `Control+F13`-style combos nothing uses.
3. **A menu is still open, out of sight.** With the default `sameShortcutBehavior: "nothing"`,
   Kando unbinds the menu's shortcut while it's open, so a menu stuck behind a window or on
   another monitor makes the shortcut seem dead. Test: Esc or `kando --close-menu`, then try
   again. Fix: `sameShortcutBehavior: "re-open"` keeps the shortcut bound, and a second press
   brings the menu to the cursor.
4. **The app in front runs as administrator, or is anti-cheat protected.** Windows (UIPI)
   blocks Kando from reading its app name, so menus with an `appName` condition don't match:
   Kando shows the unconditioned menu, or nothing if every menu on that shortcut has a
   condition. Keys Kando presses don't reach that window, and mouse-hook tools (like
   `kando-mouse-buttons.ps1`) don't see clicks over it. The global hotkey itself still works.
   Test: Task Manager → Details → add the Elevated column. Fix: stop running that app as
   admin. Running Kando as admin works, but everything it launches then runs as admin too.
5. **Something takes focus back.** With `hideOnFocusOut` on (the default), the menu closes as
   soon as it loses focus. A game that locks the cursor, or a popup or overlay, can close the
   menu before it's seen. Test: turn `hideOnFocusOut` off for a while. Fix: find the app
   stealing focus, or leave it off and close menus with Esc.

Edit config.json only with the settings window closed; it saves its own copy over your edits.

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
