# config.json: general settings (Kando 3.0)

Defaults come from `src/common/settings-schemata/general-settings-v1.ts`. Edit in the editor
(gear button / tray → Show Settings) or in `config.json`, which hot-reloads like menus.json.

## Contents
1. Tuning recipes (start here)
2. Look
3. Speed and feel
4. Selection geometry and gestures
5. Modes and focus
6. Other

## 1. Tuning recipes

**"Make it snappier"**
- `fadeOutDuration`: 60–80 (default 100). Actions after `close-menu` wait for the fade-out,
  so this is the biggest felt speed-up for hotkey menus.
- `fadeInDuration`: 50–75 (default 75). You can move before the fade finishes anyway.
- `windowsInkWorkaround`: false if the user never uses a pen/tablet (it adds ~100 ms on
  open). Keep it if they paint with a tablet. *(Speed-up inferred from the setting's description.)*
- `fixedStrokeLength`: 80–120 once directions are memorized. Items fire as soon as the
  pointer travels `centerDeadZone + fixedStrokeLength` px, without waiting for a pause.
- `sameShortcutBehavior`: `close`, so a second press dismisses the menu.

**"It selects things I didn't mean"**
- Raise `gesturePauseTimeout` to 150–200 (marking mode fires on a pause).
- Raise `gestureMinStrokeAngle` to 30 (wobbly lines count as turns).
- Raise `gestureJitterThreshold` for tablets.
- Turn off `hoverMode` on that menu, or set `hoverModeNeedsConfirmation`.

**"My cursor ends up somewhere else after picking"** (3D viewports)
- `returnPointerToMenuOpeningPosition`: true.

**"Deep menus are annoying to back out of"**
- `rmbSelectsParent`: true (right-click = back instead of close).

**"Gestures go wrong when I open the menu near a screen edge"**
- Kando always shifts a menu (or submenu) inside the screen near edges. Keep `warpMouse`
  true so the pointer is moved along with it and stays on the menu's center; with it off,
  the pointer is off-center and flicks land in the wrong wedge.
  (`src/menu-renderer/menu.ts`). It also centers the pointer on fixed-position menus.

## 2. Look

| Setting | Default | Notes |
|---|---|---|
| `menuTheme` / `darkMenuTheme` | `default` | Theme folder name. Dark one is used when `enableDarkModeForMenuThemes` and the OS is dark. |
| `menuThemeColors` / `darkMenuThemeColors` | `{}` | Per-theme color overrides: `{ "<theme-id>": { "<color-name>": "rgb(...)" } }`. See themes.md. |
| `enableDarkModeForMenuThemes` | false | |
| `enableSelectionWedges` | false | Highlights the wedge under the pointer, if the theme draws wedges. Great while learning. |
| `underlineQuickSelectKey` | true | Underlines the key letter in item names. |
| `drawQuickSelectKey` | false | Themes that support it draw a key badge on each item. |
| `zoomFactor` | 1 | Menu scale, minimum 0.5. |
| `hideSettingsButton` / `settingsButtonPosition` | false / bottom-right | |
| `trayIconFlavor` | color | color, white, light, dark, black, none |
| `settingsWindowColorScheme` | system | light, dark, system |
| `settingsWindowFlavor` | auto | auto, sakura-light/dark/system, transparent-light/dark/system |
| `soundTheme` / `soundVolume` | none / 0.5 | Built-in: `simple-clicks`. |
| `locale` | auto | |

## 3. Speed and feel

| Setting | Default | Notes |
|---|---|---|
| `fadeInDuration` | 75 ms | The docs still say 150; the 3.0 code says 75. |
| `fadeOutDuration` | 100 ms | Docs say 200. Later actions wait for it. |
| `enableMenuAnimations` | true | Submenus are clickable before their animation ends, so turning this off is rarely needed. |
| `enablePointerReactiveEffects` | true | Themes reacting to the pointer. |
| `hardwareAcceleration` | true | Turn off only if the menu renders wrongly. |
| `lazyInitialization` | false | true = slower first open, less memory. |
| `windowsInkWorkaround` | true | See recipes. |

## 4. Selection geometry and gestures

| Setting | Default | Meaning |
|---|---|---|
| `centerDeadZone` | 50 px | Center circle radius; clicking in it goes back / closes. |
| `minParentDistance` | 150 px | How far a submenu is pushed from its parent. |
| `dragThreshold` | 15 px | Movement with the button held before it counts as a drag (marking). |
| `maxSelectionRadius` | 0 | >0: clicks farther out close the menu. |
| `gestureMinStrokeLength` | 150 px | Minimum stroke before a turn counts as a selection. Lower (~100) for short fast flicks. |
| `gestureMinStrokeAngle` | 20° | How sharp a turn must be. |
| `gestureJitterThreshold` | 10 px | Movement ignored as hand shake. |
| `gesturePauseTimeout` | 100 ms | Holding still this long selects. |
| `fixedStrokeLength` | 0 | >0: instant selection after that distance, no pause/turn detection. |

## 5. Modes and focus

| Setting | Default | Notes |
|---|---|---|
| `enableMarkingMode` | true | Hold left button and draw. |
| `enableTurboMode` | true | Keep the shortcut's modifier held and move; release selects. |
| `hoverModeNeedsConfirmation` | false | Applies to menus with `hoverMode`. |
| `triggerCenterClickOnKeyRelease` | false | Releasing the turbo key over the center runs the center workflow. Undocumented. |
| `keepInputFocus` | false | true = Kando doesn't take keyboard focus: turbo and keyboard navigation stop working, but app hotkeys can be fired without closing the menu. Shows a warning in the editor. |
| `hideOnFocusOut` | true | Clicking another window closes the menu. Undocumented, new in 3.0. |
| `warpMouse` | true | Moves the pointer along when Kando shifts a menu away from a screen edge, and onto fixed-position menus. Keep on. |
| `returnPointerToMenuOpeningPosition` | false | |
| `rmbSelectsParent` | false | |
| `sameShortcutBehavior` | nothing | nothing, close, cycle-from-first, cycle-from-recent, re-open (new in 3.0; helps on multi-monitor). Cycling steps through menus that share the shortcut. |
| `useDefaultOsShowSettingsHotkey` | true | Ctrl+, (Cmd+, on macOS) opens settings while a menu is open. |

## 6. Other

| Setting | Default |
|---|---|
| `enableGamepad` / `gamepadBackButton` / `gamepadCloseButton` | true / 1 / 2 (W3C button numbers, −1 disables) |
| `enableVersionCheck` | true |
| `ignoreWriteProtectedConfigFiles` | false |
| `enableAchievements` / `enableAchievementNotifications` | true / true |
| `showIntroductionDialog` | true |
| `wlrootsPointerGetTimeout*` | Linux (wlroots) only |
