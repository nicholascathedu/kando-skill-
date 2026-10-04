# App recipes: hotkeys and ideas for per-app menus

These are the apps' **default** shortcuts on Windows. Users rebind keys, so confirm against
their app (each app has a hotkey editor) before building on them. Items marked *(verify)*
are from memory rather than the vendor's docs. Remember: in Kando, hotkeys use key codes
(`ControlLeft+KeyS`), and letter keys are physical positions (matters on AZERTY / QWERTZ).

`appName` is the process file name, such as `maya.exe`, matched as "contains"
(case-insensitive), so the shorter values below work. Confirm with the editor's window picker.

Icons: `simple-icons` has slugs for `autodeskmaya`, `blender`, `unrealengine`,
`googlechrome`, `firefoxbrowser`, `discord`, `steam` (check simpleicons.org; brands get
removed sometimes). Adobe apps aren't reliably there, so use Material Symbols
(`texture`, `brush`) or the `system` icon theme with the installed app's name.

## Contents
- Autodesk Maya
- Adobe Substance 3D Painter
- Unreal Engine 5
- Blender
- Browsers (Chrome / Edge / Firefox)
- Discord
- Cross-app pipeline ideas

## Autodesk Maya — `appName: "maya"`

| Action | Default key | Kando hotkey |
|---|---|---|
| Frame selected | F | `KeyF` |
| Frame all | A | `KeyA` |
| Isolate selected (current panel) | Ctrl+1 | `ControlLeft+Digit1` |
| Rough / medium / smooth preview | 1 / 2 / 3 | `Digit1` / `Digit2` / `Digit3` |
| Wireframe / shaded / textured / all lights | 4 / 5 / 6 / 7 | `Digit4`..`Digit7` |
| Delete history (selected) | Alt+Shift+D | `AltLeft+ShiftLeft+KeyD` |
| Group / duplicate | Ctrl+G / Ctrl+D | `ControlLeft+KeyG` / `ControlLeft+KeyD` |
| Save scene | Ctrl+S | `ControlLeft+KeyS` |
| Center pivot | — (menu only) | bind one in Hotkey Editor first |

Maya has its own radial marking menus (Space hotbox, Shift/Ctrl + right-click). Don't
duplicate those; use Kando for cross-app things and for commands without a default key
once the user binds them in Windows → Settings/Preferences → Hotkey Editor.

## Adobe Substance 3D Painter — `appName: "Painter"`

| Action | Default key | Kando hotkey |
|---|---|---|
| 3D + 2D view / 3D only / 2D only | F1 / F2 / F3 | `F1` / `F2` / `F3` |
| Material view / cycle channels | M / C | `KeyM` / `KeyC` |
| Export textures | Ctrl+Shift+E | `ControlLeft+ShiftLeft+KeyE` |
| Save | Ctrl+S | `ControlLeft+KeyS` |
| Paint / eraser / projection / polygon fill | 1 / 2 / 3 / 4 *(verify)* | `Digit1`..`Digit4` |

Adding generators, filters and smart masks goes through the layer stack's right-click menu
with no default key; the shelf (drag and drop) is faster there than Kando.

## Unreal Engine 5 — `appName: "UnrealEditor"`

| Action | Default key | Kando hotkey |
|---|---|---|
| Play in editor | Alt+P | `AltLeft+KeyP` |
| Simulate | Alt+S | `AltLeft+KeyS` |
| Lit / unlit / wireframe view | Alt+4 / Alt+3 / Alt+2 | `AltLeft+Digit4` / `Digit3` / `Digit2` |
| Content drawer | Ctrl+Space | `ControlLeft+Space` |
| Save all | Ctrl+Shift+S | `ControlLeft+ShiftLeft+KeyS` |
| Open console | ` | `Backquote` |
| Game view toggle | G | `KeyG` |

Note: Ctrl+0..9 set camera bookmarks in Unreal; a Kando shortcut on Ctrl+<digit> takes that
key over while Unreal is focused.

Console-command items (pattern in menus-json.md §5): `stat fps`, `stat unit`,
`show collision`, `slomo 0.25` / `slomo 1`, `pause`, `p.Chaos.DebugDraw.Enabled 1`.

Asset-name snippet items (set-clipboard + Ctrl+V while renaming with F2): `M_`, `MI_`, `MF_`,
`T_`, `SM_`, `SK_`, `BP_`, `WBP_`, `NS_`, suffixes `_BC`, `_N`, `_ORM`.

## Blender — `appName: "blender"`

| Action | Default key *(verify against the user's keymap)* | Kando hotkey |
|---|---|---|
| Frame selected | Numpad . | `NumpadDecimal` |
| Local view (isolate) | Numpad / | `NumpadDivide` |
| Shading pie (solid / material / rendered have no direct default keys) | Z | `KeyZ` |
| Toggle wireframe | Shift+Z | `ShiftLeft+KeyZ` |
| Toggle X-ray | Alt+Z | `AltLeft+KeyZ` |
| Edit / object mode | Tab | `Tab` |
| Duplicate | Shift+D | `ShiftLeft+KeyD` |
| Apply transform menu | Ctrl+A | `ControlLeft+KeyA` |
| Move to collection | M | `KeyM` |
| Save | Ctrl+S | `ControlLeft+KeyS` |
| Render image | F12 | `F12` |

Blender has built-in pie menus too (Z, Tab with the Pie Menus add-on, ~ for view). Kando
earns its place for cross-app actions and for operators the user searches for with F3.
Numpad keys: Frame selected and Local view need a numpad. Without one, the user can turn on
Preferences → Input → Emulate Numpad, then the top-row digits act as the numpad, or bind
other keys. Shortcut clash: in Object mode Ctrl+1–5 set the subdivision level, so a Kando
menu on Ctrl+<digit> takes that away while Blender is focused. Prefer Ctrl+F13 or similar.

## Browsers — `appName: "chrome"` / `"msedge"` / `"firefox"`

| Action | Key |
|---|---|
| New tab / reopen closed tab / close tab | Ctrl+T / Ctrl+Shift+T / Ctrl+W |
| Address bar | Ctrl+L |
| Private window | Ctrl+Shift+N (Chrome/Edge), Ctrl+Shift+P (Firefox) |
| History / downloads | Ctrl+H / Ctrl+J (Firefox downloads: Ctrl+Shift+Y) |
| Back / forward | Alt+Left / Alt+Right, or key codes `BrowserBack` / `BrowserForward` |
| Find | Ctrl+F |

Good items: open-uri for bookmarks (docs, forums, asset stores), "search selected text"
cross-app workflow.

## Discord — `appName: "Discord"`

| Action | Key *(verify)* |
|---|---|
| Toggle mute / deafen | Ctrl+Shift+M / Ctrl+Shift+D |
| Quick switcher | Ctrl+K |
| Mark server read | Shift+Esc |

Mute and deafen only work while Discord is focused unless the user sets global keybinds in
Discord's settings; a `focus-window` first, or global binds, make them work from anywhere.

## Cross-app pipeline ideas

- **Switch app submenu** in the same direction in every work menu: `focus-window` with
  `appName` of each other app in the pipeline (Maya → Painter → Unreal).
- **Search selected text** in the browser from any app (Ctrl+C → focus browser → Ctrl+T →
  paste → Enter).
- **Open the project folder**: `open-file` with the folder path (keep personal paths out of
  anything shared).
- **Export then switch**: an item that exports (Painter Ctrl+Shift+E) and a neighbour that
  jumps to the engine, so a handoff is two flicks.
