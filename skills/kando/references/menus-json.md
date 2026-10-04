# menus.json format (Kando 3.0)

Source of truth: `src/common/settings-schemata/menu-settings-v2.ts` in
github.com/kando-menu/kando. The website docs (kando.menu/config-files) lag the code in places.

## Contents
1. Top level
2. Menu fields
3. Item types
4. Workflows
5. Actions (all 14)
6. Conditions
7. Keys: names vs codes
8. Angles
9. Minimal complete example

## 1. Top level

```json
{
  "version": "3.0.0",
  "menus": [ /* menu objects */ ],
  "collections": [ { "name": "3D Work", "icon": "view_in_ar",
                     "iconTheme": "material-symbols-rounded", "tags": ["3D Work"] } ]
}
```

- An empty `menus` list makes Kando generate its example menu.
- A collection lists every menu that has **all** of its tags. Collections are only for
  organizing the editor sidebar; they don't change behavior.
- Unknown keys are silently dropped on load (zod strips them), so a typo in a key name
  "does nothing" rather than failing. `kando_check.py` flags these.
- A single exported menu (editor → export) is `{ "menu": {...} }` plus metadata; the
  checker and preview scripts accept it too.

## 2. Menu fields

| Field | Default | Meaning |
|---|---|---|
| `root` | required | The root item (type `root`). |
| `shortcut` | `""` | Key **names**, e.g. `"Control+Space"`. See §7. |
| `shortcutID` | `""` | For Linux desktops where Kando can't bind keys; bind the ID in the OS. |
| `useFixedPosition` | false | Open at a fixed screen spot instead of the pointer. |
| `fixedMenuPosition` | `{x:0.5,y:0.5}` | 0–1 fractions of the screen. |
| `anchored` | false | Submenus open in place instead of at the pointer. Breaks marking mode; for touch/gamepad. |
| `hoverMode` | false | Select by hovering, no click. Fastest, but accidental picks happen. |
| `conditions` | none | Only show in certain apps / windows / screen areas (§6). |
| `tags` | `[]` | For collections. |

## 3. Item types

Every item has `name`, `icon`, `iconTheme`, `type`.

| `type` | Extra fields | Workflows |
|---|---|---|
| `root` | `children` | `activateWorkflow` = clicking the center |
| `submenu` | `children`, `angle?` | `openWorkflow` (runs when opened), `hoverWorkflow`, `activateWorkflow` (center click while open; default is go back) |
| `button` | `angle?` | `selectWorkflow` (the main one), `hoverWorkflow` |

Icon themes: `material-symbols-rounded` (icon = Material Symbols name like `save`),
`simple-icons` / `simple-icons-colored` (brand slug like `blender`, `unrealengine`),
`emoji`, `system` (installed-app icons on Windows/macOS; icon = app name), `base64`
(data or URL), and any folder the user adds in `icon-themes/`.

## 4. Workflows

```json
"selectWorkflow": {
  "quickSelectKey": "S",
  "actions": [ { "type": "close-menu" }, { "type": "simulate-hotkey", "hotkey": "ControlLeft+KeyS" } ]
}
```

- Actions run in order. Since 3.0 they run on key **release**.
- `close-menu` is just an action. Put it **first** when the next actions press keys or
  act on another window: while the menu is open, Kando's own window has keyboard focus,
  and `simulate-hotkey` just sends keys to whatever has focus (`src/main/actions/simulate-hotkey.ts`).
- Leave `close-menu` out to keep the menu open so the item can be clicked repeatedly. This
  works for actions that don't need your app focused: volume and media keys, commands,
  URIs, websocket messages. For app hotkeys (Ctrl+Z in Maya) it only works with
  `keepInputFocus: true`, which turns off turbo mode and keyboard navigation. *(Inferred
  from the source; test it on your setup.)*
- Actions after `close-menu` wait for the fade-out (`fadeOutDuration`), so a long fade
  delays every hotkey item.
- `quickSelectKey` is optional. Without one, items can be picked with 1–9 by position.

## 5. Actions (all 14)

| `type` | Fields | Notes |
|---|---|---|
| `close-menu` | — | See above. |
| `close-submenu` | — | Default center action for submenus (go back). |
| `delay` | `duration` (**seconds**, decimals ok) | e.g. `0.2` while a console or dialog opens. |
| `execute-command` | `command`, `detached` (true), `isolated` (false, Linux only) | Placeholders `{{app_name}}`, `{{window_name}}`, `{{pointer_x}}`, `{{pointer_y}}`. On Windows: `start "" "C:\\path\\app.exe"`, `start "" "shell:AppsFolder\\<AUMID>"` for Store apps. The editor's app picker writes the right command; prefer it. |
| `execute-macro` | `macro: [{type: keyDown|keyUp, key, delay(ms)}]` | Key codes. Record it in the editor. Release every key you press. |
| `focus-window` | `appName?`, `windowName?` | Regex/partial; both must match if both set. Brings an app forward: "switch app", or copy-here-paste-there workflows. |
| `inhibit-shortcuts` | — | Turns off Kando's shortcuts for the rest of the workflow, so a simulated key can't re-trigger a menu. |
| `open-file` | `path` | Opens with the default app; works for folders. |
| `open-menu` | `menu` (name, first match) | Jump to another menu. Never follow with `close-menu`. |
| `open-settings` | — | Opens the Kando editor. |
| `open-uri` | `uri` | http(s), file:///, mailto:, app protocols (`steam://`, `ms-settings:`). |
| `set-clipboard` | `text` | Text snippets. Pair with Ctrl+V to paste. Overwrites the clipboard. |
| `send-websocket-message` | `url`, `message` | New in 3.0, no docs page yet. For OBS, Home Assistant, custom tools. |
| `simulate-hotkey` | `hotkey` | Key codes joined by `+`, e.g. `AltLeft+ShiftLeft+KeyD`. |

Common combinations:

```json
// Paste a snippet
[{"type":"close-menu"},{"type":"set-clipboard","text":"MI_"},
 {"type":"simulate-hotkey","hotkey":"ControlLeft+KeyV"}]

// Run a console command (Unreal, games): open console, wait, paste, enter
[{"type":"close-menu"},{"type":"set-clipboard","text":"stat fps"},
 {"type":"simulate-hotkey","hotkey":"Backquote"},{"type":"delay","duration":0.2},
 {"type":"simulate-hotkey","hotkey":"ControlLeft+KeyV"},{"type":"simulate-hotkey","hotkey":"Enter"}]

// Search the web for the selected text (Simon's 3.0 demo)
[{"type":"close-menu"},{"type":"simulate-hotkey","hotkey":"ControlLeft+KeyC"},
 {"type":"focus-window","appName":"chrome"},{"type":"simulate-hotkey","hotkey":"ControlLeft+KeyT"},
 {"type":"delay","duration":0.1},{"type":"simulate-hotkey","hotkey":"ControlLeft+KeyV"},
 {"type":"simulate-hotkey","hotkey":"Enter"}]
```

## 6. Conditions

```json
"conditions": { "appName": "maya", "windowName": "", "screenArea": { "xMax": 200 } }
```

- All set conditions must match. Among menus on the same shortcut, the one with the **most**
  matching conditions wins; a menu with none is the fallback.
- `appName`, `windowName`: case-insensitive "contains"; a value starting with `/` is a regex.
- On Windows `appName` is the focused process's **executable file name** (from
  `QueryFullProcessImageName`), e.g. `maya.exe` → `maya`, `UnrealEditor.exe` → `UnrealEditor`.
  The editor's window picker shows it.
- `screenArea`: pixels from the primary display's top-left; omitted bounds are open. Useful
  for "a different menu when I open it at the screen edge".
- The shortcut is grabbed globally regardless of conditions; when nothing matches, the key
  is swallowed and nothing opens.

## 7. Keys: names vs codes

**Shortcut key names** (Electron accelerators, case-insensitive, `+`-separated):
modifiers `Control`/`Ctrl`, `Alt`, `Shift`, `Super`/`Meta`, `Command`/`Cmd`,
`CommandOrControl`, `AltGr`, `Option`; keys `A`–`Z`, `0`–`9`, `F1`–`F24`, `Space`, `Tab`,
`Backspace`, `Delete`, `Insert`, `Enter`/`Return`, `Up`/`Down`/`Left`/`Right`, `Home`, `End`,
`PageUp`, `PageDown`, `Escape`/`Esc`, `num0`–`num9`, `numadd`, `numsub`, `nummult`,
`numdiv`, `numdec`, media keys, and punctuation characters.

**Hotkey / macro key codes** (physical keys): `ControlLeft`, `ShiftLeft`, `AltLeft`,
`MetaLeft` (and `Right` variants), `KeyA`–`KeyZ`, `Digit0`–`Digit9`, `F1`–`F24`,
`Numpad0`–`Numpad9`, `NumpadAdd`..., `ArrowUp/Down/Left/Right`, `Enter`, `Escape`, `Space`,
`Tab`, `Backspace`, `Delete`, `Backquote` (the ` key), `Minus`, `Equal`, `BracketLeft`,
`BracketRight`, `Semicolon`, `Quote`, `Comma`, `Period`, `Slash`, `Backslash`, `Home`, `End`,
`PageUp`, `PageDown`, `MediaPlayPause`, `AudioVolumeUp`... Full list: kando.menu/valid-keynames.

Codes are physical: on QWERTZ `KeyZ` types Y, on AZERTY `KeyQ` types A. Digits and F-keys
are the same on every layout.

Good spare shortcuts: `Ctrl+F13`…`Ctrl+F24` (no physical key, perfect for mouse buttons or
macro pads), `Ctrl+Shift+<digit>`, `Ctrl+Alt+<letter>`. Avoid bare letters or symbols:
they stop typing everywhere.

## 8. Angles

- Degrees clockwise from up: 0 up, 45 up-right, 90 right, 135 down-right, 180 down,
  225 down-left, 270 left, 315 up-left.
- Kando reads fixed angles in list order and wraps each one to the first equivalent angle
  **after** the previous one (`[90, 270, 0]` becomes 90, 270, 360). An angle equal to the
  previous one, or a full turn past the first, is dropped and that item placed
  automatically. Simplest rule: list items clockwise and give each an angle.
- Items without an angle are spread evenly in the gaps between fixed ones.
- In a submenu, the back link to the parent sits at (submenu angle + 180). Keep children at
  least 45° away from it.

## 9. Minimal complete example

```json
{
  "version": "3.0.0",
  "menus": [{
    "shortcut": "Control+Space",
    "tags": [],
    "root": {
      "type": "root", "name": "Quick", "icon": "bolt", "iconTheme": "material-symbols-rounded",
      "activateWorkflow": { "quickSelectKey": "Backspace", "actions": [{ "type": "close-menu" }] },
      "children": [
        { "type": "button", "name": "Browser", "icon": "public", "iconTheme": "material-symbols-rounded",
          "angle": 0,
          "selectWorkflow": { "quickSelectKey": "B", "actions": [
            { "type": "close-menu" }, { "type": "open-uri", "uri": "https://kando.menu" } ] } },
        { "type": "submenu", "name": "Edit", "icon": "edit", "iconTheme": "material-symbols-rounded",
          "angle": 90,
          "openWorkflow": { "quickSelectKey": "E", "actions": [] },
          "activateWorkflow": { "quickSelectKey": "Backspace", "actions": [{ "type": "close-submenu" }] },
          "children": [
            { "type": "button", "name": "Undo", "icon": "undo", "iconTheme": "material-symbols-rounded",
              "angle": 0,
              "selectWorkflow": { "quickSelectKey": "U", "actions": [
                { "type": "close-menu" }, { "type": "simulate-hotkey", "hotkey": "ControlLeft+KeyZ" } ] } },
            { "type": "button", "name": "Louder", "icon": "volume_up", "iconTheme": "material-symbols-rounded",
              "angle": 180,
              "selectWorkflow": { "quickSelectKey": "L", "actions": [
                { "type": "simulate-hotkey", "hotkey": "AudioVolumeUp" } ] } }
          ] }
      ]
    }
  }],
  "collections": []
}
```

"Louder" has no `close-menu`: it's a repeat-fire item you can click several times, which
works because volume keys are global. "Undo" closes first so Ctrl+Z reaches your app.
