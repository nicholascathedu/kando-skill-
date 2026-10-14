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
- Adobe Substance 3D Designer
- Unreal Engine 5
- Blender
- ZBrush
- Adobe Photoshop
- Adobe Illustrator
- Marvelous Designer
- Marmoset Toolbag 5
- Browsers (Chrome / Edge / Firefox)
- Discord
- Cross-app pipeline ideas
- Cross-app macros: save everything, colour picker

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

Checked against Adobe's Painter "Shortcuts" page (Experience League), 2026-10.

| Action | Default key | Kando hotkey |
|---|---|---|
| 3D + 2D view / 3D only / 2D only / swap 2D and 3D | F1 / F2 / F3 / F4 | `F1` / `F2` / `F3` / `F4` |
| Material view / next channel / next mesh map | M / C / B | `KeyM` / `KeyC` / `KeyB` |
| Bake mesh maps (opens the baking window) | Ctrl+Shift+B | `ControlLeft+ShiftLeft+KeyB` |
| Baking / painting mode | F8 / F9 | `F8` / `F9` |
| Export textures | Ctrl+Shift+E | `ControlLeft+ShiftLeft+KeyE` |
| Save | Ctrl+S | `ControlLeft+KeyS` |
| Paint / eraser / projection / polygon fill / smudge / clone | 1 / 2 / 3 / 4 / 5 / 6 | `Digit1`..`Digit6` |
| Symmetry / show manipulator | L / Q | `KeyL` / `KeyQ` |
| Texture set isolate / hide UI | Alt+Q / Tab | `AltLeft+KeyQ` / `Tab` |
| Camera perspective / orthographic | F5 / F6 | `F5` / `F6` |

There's no default "Save as" key and no colour-picker key; for colours, see the PowerToys
macro at the end of this file.

Adding generators, filters and smart masks goes through the layer stack's right-click menu
with no default key; the shelf (drag and drop) is faster there than Kando.

## Adobe Substance 3D Designer — `appName: "Substance 3D Designer"`

The process is `Adobe Substance 3D Designer.exe` (Adobe's install-path docs). Use
`Substance 3D Designer` as the condition; `Designer` alone also matches other apps.
Checked against Adobe's Designer 16.0 docs (Experience League, 2026); sources in `sources.md`.

| Action | Default key | Kando hotkey |
|---|---|---|
| Node menu (add a node) | Space in the Graph view | `Space` |
| Node finder | Ctrl+F | `ControlLeft+KeyF` |
| Fit in view / focus selection | F | `KeyF` |
| Reset zoom | Z | `KeyZ` |
| Align horizontally / vertically / snap to grid | H / V / S | `KeyH` / `KeyV` / `KeyS` |
| Duplicate / duplicate without links | Ctrl+D / Ctrl+Shift+D | `ControlLeft+KeyD` / `ControlLeft+ShiftLeft+KeyD` |
| Disable node | Shift+D | `ShiftLeft+KeyD` |
| Open reference in context (or edit a Pixel Processor / FX-Map function) | Ctrl+E | `ControlLeft+KeyE` |
| Link creation mode: standard / material / compact | 1 / 2 / 3 | `Digit1` / `Digit2` / `Digit3` |
| New Substance graph | Ctrl+N | `ControlLeft+KeyN` |
| Save package / save all | Ctrl+S / Ctrl+Shift+S | `ControlLeft+KeyS` / `ControlLeft+ShiftLeft+KeyS` |
| Publish .sbsar | Ctrl+P | `ControlLeft+KeyP` |
| Cancel rendering / suspend engine / switch engine | Esc / Shift+Esc / F9 | `Escape` / `ShiftLeft+Escape` / `F9` |
| 2D view: tiled display / fit / 1:1 | Space / F / Z | `Space` / `KeyF` / `KeyZ` |
| 3D view: focus mesh / reset camera | F / R | `KeyF` / `KeyR` |

Designer's keys act on the panel that has focus, and some letters mean different things in
the Graph, 2D and 3D views (Space adds a node in the graph but toggles tiling in the 2D view).
Kando gives focus back to Designer when the menu closes, so the key lands in the panel you
were last working in. Put graph actions in one menu and keep 2D/3D view actions out of it,
or put them in a submenu named for the view. Adobe lists Ctrl+P with the Explorer's right-click menu
and the toolbar, so try it once with your graph open. Export outputs, frames and comments have no default key;
bind one in Preferences first.

**Node palette.** Designer has no default key for adding a particular node, but Preferences →
Shortcuts lets you give "any node" one, library and custom library nodes included, for
Substance, function and FX-Map graphs (Adobe's Preferences page). A key that clashes with
another shortcut is highlighted and does nothing until fixed. Bind your eight most-used nodes
to Ctrl+Alt+1…8, then put them on a ring; the examples' Up submenu does that, and its center
click opens the full node menu (Space). Open the menu over the Graph view. Designer 16.0 removed Iray (the GPU Pathtracer replaces it).

## Unreal Engine 5 — `appName: "UnrealEditor"`

| Action | Default key | Kando hotkey |
|---|---|---|
| Play in editor | Alt+P | `AltLeft+KeyP` |
| Simulate | Alt+S | `AltLeft+KeyS` |
| Lit / unlit / wireframe view | Alt+4 / Alt+3 / Alt+2 | `AltLeft+Digit4` / `AltLeft+Digit3` / `AltLeft+Digit2` |
| Detail lighting / lighting only | Alt+5 / Alt+6 | `AltLeft+Digit5` / `AltLeft+Digit6` |
| Light complexity / shader complexity | Alt+7 / Alt+8 | `AltLeft+Digit7` / `AltLeft+Digit8` |
| Lightmap density | Alt+0 | `AltLeft+Digit0` |
| Content drawer | Ctrl+Space | `ControlLeft+Space` |
| Save all | Ctrl+Shift+S | `ControlLeft+ShiftLeft+KeyS` |
| Open console | ` | `Backquote` |
| Game view toggle | G | `KeyG` |

**View-mode pie.** The eight view modes with a default key (Epic's "Viewport Modes" page,
checked 2026-10) are a natural ring. At the root they fill all eight directions. Inside a
submenu, one direction is the way back, so space them 40° apart around it, as the Unreal menu
in `examples/3d-work-menus.json` does: opened from Right, the back link is Left, and the modes
sit at 30, 70 … 350 with Lit at 350 (Up), the lighting views down the right side and the
optimization views (shader complexity, lightmap density) on the left. Use letters for their
quick-select keys, not the Alt digits; digits already pick items by position.
Reflections, Stationary Light Overlap and the buffer views have no default key.

Note: Ctrl+0..9 set camera bookmarks in Unreal; a Kando shortcut on Ctrl+<digit> takes that
key over while Unreal is focused.

Console-command items (pattern in menus-json.md §5): `stat fps`, `stat unit`,
`show collision`, `slomo 0.25` / `slomo 1`, `pause`. To see why a Chaos simulation jitters
or explodes, record it with `p.Chaos.StartVDRecording` / `p.Chaos.StopVDRecording` and open the
recording in the Chaos Visual Debugger (Epic's Chaos Visual Debugger guide, UE 5.5).

Asset-name snippet items (set-clipboard + Ctrl+V while renaming with F2): `M_`, `MI_`, `MF_`,
`T_`, `SM_`, `SK_`, `BP_`, `WBP_`, `NS_`, suffixes `_BC`, `_N`, `_ORM`.

**Physics test pie** (`examples/sim-and-render.json`): physics and VFX work is a loop of
test, slow down, look closer, record. Play (Alt+P), Simulate (Alt+S), Game view (G),
`slomo 0.25` / `slomo 1`, `stat unit`, and a Chaos recording submenu with
`p.Chaos.StartVDRecording` / `p.Chaos.StopVDRecording` for the Chaos Visual Debugger. Record
clip is Windows Game Bar (Win+Alt+R), a global key. It's on Ctrl+F14 because Ctrl+digit sets
camera bookmarks in Unreal. Eject (to leave the possessed pawn during Play) is F8 on one Epic
page and F10 on another, so check Editor Preferences > Keyboard Shortcuts before adding it.
Fracture mode and the Niagara Debugger have no default key: bind one first if you want a slice.

## Blender — `appName: "blender"`

Checked against Blender's default keymap source (`scripts/presets/keyconfig/keymap_data/blender_default.py`)
and command-line source (`source/creator/creator_args.cc`), 2026-10.

| Action | Default key | Kando hotkey |
|---|---|---|
| Render image / render animation | F12 / Ctrl+F12 | `F12` / `ControlLeft+F12` |
| Show last render | F11 | `F11` |
| Maximize area / fullscreen area (hides panels) | Ctrl+Space / Ctrl+Alt+Space | `ControlLeft+Space` / `ControlLeft+AltLeft+Space` |
| Next / previous workspace | Ctrl+Page Down / Ctrl+Page Up | `ControlLeft+PageDown` / `ControlLeft+PageUp` |
| Quick Favorites | Q | `KeyQ` |
| Repeat last / adjust last operation | Shift+R / F9 | `ShiftLeft+KeyR` / `F9` |
| Add menu / snap pie | Shift+A / Shift+S | `ShiftLeft+KeyA` / `ShiftLeft+KeyS` |
| Frame selected | Numpad . | `NumpadDecimal` |
| Local view (isolate) | Numpad / | `NumpadDivide` |
| Shading pie | Z | `KeyZ` |
| Toggle wireframe / X-ray / overlays | Shift+Z / Alt+Z / Alt+Shift+Z | `ShiftLeft+KeyZ` / `AltLeft+KeyZ` / `AltLeft+ShiftLeft+KeyZ` |
| Edit / object mode | Tab | `Tab` |
| Duplicate | Shift+D | `ShiftLeft+KeyD` |
| Apply transform menu | Ctrl+A | `ControlLeft+KeyA` |
| Move to collection | M | `KeyM` |
| Save | Ctrl+S | `ControlLeft+KeyS` |

Blender already has pies on Z, Shift+S and ` (view), so a Kando slice that sends Z just opens
a pie inside a pie. Kando earns its place for render, maximize, workspaces, cross-app actions
and operators the user searches for with F3. Workspaces have no key of their own, only
next / previous, so put **Next** on Right and **Previous** on Left rather than a workspace
submenu that would just cycle. Keys act on the area under the pointer, and Kando opens at the
pointer, so open the menu over the viewport you mean.

Numpad keys: without a numpad, turn on Preferences → Input → Emulate Numpad, or bind other
keys. Shortcut clash: in Object mode Ctrl+1–5 set the subdivision level, so a Kando menu on
Ctrl+<digit> takes that away while Blender is focused. Prefer Ctrl+F13 or similar.

**Background jobs** (`execute-command`, Blender keeps working while they run). `-b` is
background, `-f 1` renders frame 1, `-a` renders the animation, `--python-expr` runs one line
of Python. Arguments run in order, so put `-f` / `-a` last. Use the full path to
`blender.exe`, since it isn't on PATH by default, and save first (the job reads the saved file):

```json
[{"type":"close-menu"},{"type":"simulate-hotkey","hotkey":"ControlLeft+KeyS"},{"type":"delay","duration":1},
 {"type":"execute-command","command":"\"C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe\" -b \"C:\\Projects\\scene.blend\" --python-expr \"import bpy; bpy.ops.export_scene.fbx(filepath=bpy.data.filepath[:-6] + '.fbx')\""}]
```

That writes `scene.fbx` next to the .blend. For glTF use `bpy.ops.export_scene.gltf`. The file
path is fixed in the item, so make one item per project, or put it in a "Batch" submenu.
*(The export line is from Blender's Python API; run it once by hand first.)*

## ZBrush — `appName: "ZBrush"`

Checked against Maxon's ZBrush shortcut sheet (help.maxon.net, `ZBrush-Shortcuts.pdf`), 2026-10.

| Action | Default key | Kando hotkey |
|---|---|---|
| Draw / Move / Scale / Rotate | Q / W / E / R | `KeyQ` / `KeyW` / `KeyE` / `KeyR` |
| Edit mode on/off | T | `KeyT` |
| Show/hide Polyframe and polygroups | Shift+F | `ShiftLeft+KeyF` |
| Divide / higher res / lower res | Ctrl+D / D / Shift+D | `ControlLeft+KeyD` / `KeyD` / `ShiftLeft+KeyD` |
| Activate symmetry | X | `KeyX` |
| Brush pop-up | B | `KeyB` |
| Group masked and clear mask | Ctrl+W | `ControlLeft+KeyW` |
| LightBox | , | `Comma` |
| Save project / save tool | Ctrl+S / Ctrl+Shift+T | `ControlLeft+KeyS` / `ControlLeft+ShiftLeft+KeyT` |
| Gizmo ↔ TransPose | Y *(verify)* | `KeyY` |
| Solo, Transp, Ghost, ZRemesher | none | bind one first (below) |

ZBrush has no pie menu of its own, and many people sculpt with a pen and no keyboard, so this
is where Kando helps most among the 3D apps. Good pies: **Display** (Polyframe, Symmetry,
Solo, Transp) and **Subdiv** (higher Up, lower Down, Divide to the side).

To give Solo, Transp or ZRemesher a key: Ctrl+Alt+click the button in ZBrush, press the new
key, then save hotkeys in Preferences → Hotkeys. Three-modifier keys such as
Ctrl+Alt+Shift+S rarely clash with ZBrush's own. Mouse gestures (DynaMesh's Ctrl+drag on the
background) can't be sent by Kando.

## Adobe Photoshop — `appName: "Photoshop"`

| Action | Default key | Kando hotkey |
|---|---|---|
| Move / Brush | V / B | `KeyV` / `KeyB` |
| Free Transform | Ctrl+T | `ControlLeft+KeyT` |
| Fit on screen | Ctrl+0 | `ControlLeft+Digit0` |
| Brush size smaller / larger | [ / ] | `BracketLeft` / `BracketRight` |
| New layer (dialog) | Ctrl+Shift+N | `ControlLeft+ShiftLeft+KeyN` |
| Stamp visible (merge visible to a new layer) | Ctrl+Shift+Alt+E *(verify)* | `ControlLeft+ShiftLeft+AltLeft+KeyE` |
| Export As | Alt+Shift+Ctrl+W *(verify)* | `AltLeft+ShiftLeft+ControlLeft+KeyW` |
| Quick Export as PNG | none | bind one in Edit → Keyboard Shortcuts |
| Save | Ctrl+S | `ControlLeft+KeyS` |

Adobe's shortcut pages load with scripts and couldn't be read for this table; the rows
without *(verify)* are Photoshop's long-standing defaults. Check Edit → Keyboard Shortcuts.

- **Text-field trap:** while you are typing in a text layer, a single-letter tool key types the
  letter. Commit the text first (Ctrl+Enter), then flick the tool.
- **Actions beat long macros.** Record a multi-step job once as a Photoshop Action, give it an
  F-key in the Actions panel, and let the Kando item press that F-key. It's sturdier than a
  long `execute-macro`.
- Brush size [ / ] would be a nice "click it again" item, but app keys only repeat with
  `keepInputFocus` on (see menus-json.md §4), so keep it one-shot or skip it.

## Adobe Illustrator — `appName: "Illustrator"`

Checked against Adobe's "Default keyboard shortcuts" page for Illustrator, 2026-10.

| Action | Default key | Kando hotkey |
|---|---|---|
| Selection / Direct Selection / Pen | V / A / P | `KeyV` / `KeyA` / `KeyP` |
| Shape Builder | Shift+M | `ShiftLeft+KeyM` |
| Outline ↔ preview | Ctrl+Y | `ControlLeft+KeyY` |
| Export for Screens | Alt+Ctrl+E | `AltLeft+ControlLeft+KeyE` |
| Group / ungroup | Ctrl+G / Shift+Ctrl+G | `ControlLeft+KeyG` / `ShiftLeft+ControlLeft+KeyG` |
| Make / release clipping mask | Ctrl+7 / Alt+Ctrl+7 | `ControlLeft+Digit7` / `AltLeft+ControlLeft+Digit7` |
| View all artboards in window | Alt+Ctrl+0 | `AltLeft+ControlLeft+Digit0` |
| Save | Ctrl+S | `ControlLeft+KeyS` |

Same text-field trap as Photoshop: press Esc to leave the text first *(verify on your
version)*. For icon work, Outline view, Shape Builder and Export for Screens are the three
that save the most trips to the menus.

## Marvelous Designer — `appName: "Marvelous"` *(verify the process name)*

No radial menu of its own and lots of keys, so Kando helps. Rebind in Settings > User Settings
> Shortcuts; the Active Tool Hotkey Viewer lists the keys for the current tool.

| Action | Key |
|---|---|
| Simulation on / off | Space |
| Freeze / Deactivate | Ctrl+K / Ctrl+J |
| Strengthen (temporary stiffness) | Ctrl+H |
| Hide 3D pattern | Shift+Q |
| Transform / Edit pattern (2D) | A / Z *(verify in 2025)* |
| Zoom to selected | F |
| Camera: front, back, left, right | 2, 8, 4, 6 |
| Camera: three-quarter, top, bottom | 3 and 1, 5, 0 |

**Camera pie:** put each view where the camera looks from. Front (2) at the bottom, toward
you, Back (8) at the top, Left and Right at the sides, the three-quarter views on the lower
diagonals, Top and Bottom in a submenu. The example uses numpad keys; if your Marvelous wants the
number row, change `NumpadN` to `DigitN`. A text field with focus eats number keys, so click the
3D window first. A Garment submenu holds Simulate, Freeze, Deactivate, Strengthen and Hide.

## Marmoset Toolbag 5 — `appName: "toolbag"` *(verify the process name)*

No radial menu of its own. Hotkeys are editable in Edit > Hotkeys since 5.02, including
viewport modes, render passes and workspaces (camera navigation keys can't be rebound).

| Action | Key |
|---|---|
| Save scene | Ctrl+S |
| Frame selection | Ctrl+F |
| Hide / show selection | Ctrl+H |
| Bake all | Ctrl+B |
| Render viewport image | F10 |
| Copy viewport to clipboard | F9 |
| Render all images / all videos | F11 / F5 |

**Present pie:** the order of a portfolio render: Bake, Render image, Render all images and
videos, Copy viewport, Save at Down-left like every work menu. "Viewport to Discord" chains F9
→ focus Discord → Ctrl+V, so you can post a grab for feedback without saving a file (works the
same for PureRef). Turntables are a once-per-asset setup (Scene > Add Object > Turntable, Sync
Loop Speed, then Render Video), so they belong in a note, not a slice.

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
  `appName` of each other app in the pipeline (Maya → Designer → Painter → Unreal).
- **Material pipeline**: build in Designer, publish the .sbsar (Ctrl+P), switch to Painter or
  Unreal, which both load .sbsar files. Put publish in Designer on the same flick as export
  in Painter, so "send it out" feels the same in both apps.
- **Search selected text** in the browser from any app (Ctrl+C → focus browser → Ctrl+T →
  paste → Enter).
- **Open the project folder**: `open-file` with the folder path (keep personal paths out of
  anything shared).
- **Export then switch**: an item that exports (Painter Ctrl+Shift+E) and a neighbour that
  jumps to the engine, so a handoff is two flicks.

## Live menus: recent scenes and projects

A static menu can't list today's files. `scripts/kando_live.py` builds a pie at the moment you
open it and shows it through Kando's IPC (`show-custom-menu`), then opens the file you pick:

- `pythonw kando_live.py maya`: the 8 most recent scenes from Maya's `RecentFilesList`
  (newest `Documents/maya/<version>/prefs/userPrefs.mel`) *(verify on your Maya version)*.
- `pythonw kando_live.py recent "D:/Projects" --ext .spp`: the 8 newest Painter projects in a
  folder. The same works for `.uproject`, `.sbs`, `.blend`, `.ztl`.

Put it in a button as `close-menu` then `execute-command` (detached). It takes a moment to
appear (the script has to start), so it suits "open a recent scene", not things you do every
minute. Kando must be running; the pie uses Kando's own theme.

## Cross-app macros: save everything, colour picker

These use `focus-window` to act on several apps from one item. Two facts from Kando's source
(`src/main/actions/focus-window.ts`) shape them:

- `focus-window` brings the **first** matching window forward (it restores a minimized one).
  Windows lists windows front to back, so with a regex like `/Painter|Designer/` the one you
  used last wins. *(Order inferred from how Windows lists windows; test it.)*
- If **no** window matches, Kando only logs a warning and the workflow carries on, so the next
  keys go to whatever is in front. Order the steps so a missing app does no harm, and add a
  short `delay` after each focus so the window is ready for keys.

**Save everything before a break** (Maya, Painter, Designer, Unreal):

```json
[{"type":"close-menu"},
 {"type":"focus-window","appName":"maya"},{"type":"delay","duration":0.3},
 {"type":"simulate-hotkey","hotkey":"ControlLeft+KeyS"},{"type":"delay","duration":0.5},
 {"type":"focus-window","appName":"Painter"},{"type":"delay","duration":0.3},
 {"type":"simulate-hotkey","hotkey":"ControlLeft+KeyS"},{"type":"delay","duration":0.5},
 {"type":"focus-window","appName":"Substance 3D Designer"},{"type":"delay","duration":0.3},
 {"type":"simulate-hotkey","hotkey":"ControlLeft+KeyS"},{"type":"delay","duration":0.5},
 {"type":"focus-window","appName":"UnrealEditor"},{"type":"delay","duration":0.3},
 {"type":"simulate-hotkey","hotkey":"ControlLeft+ShiftLeft+KeyS"}]
```

Every app gets Ctrl+S except Unreal, where Ctrl+Shift+S saves all levels and assets. Limits
to tell the user plainly:
- A file that was never saved opens a "Save as" dialog, which waits for them.
- If Unreal isn't open, its Ctrl+Shift+S goes to the app in front. In Maya that is "Save
  Scene As"; press Esc. Unreal is last so the others are already saved. For a setup without
  Unreal, drop the last three actions.
- Add or remove apps the same way: focus, short delay, that app's save key.

When every app in the chain saves with Ctrl+S, a missing app is harmless: the key just saves
the app in front once more. `examples/design-3d-macros.json` uses that for ZBrush, Blender,
Photoshop and Illustrator.

**Colour picker, then paste the hex** (PowerToys Color Picker; default key Win+Shift+C, copies
HEX by default; checked in Microsoft's PowerToys docs). Picking is interactive, so this is
two items, not one:
1. **Pick colour:** `close-menu` → `simulate-hotkey` `MetaLeft+ShiftLeft+KeyC`. Middle-click
   picks and closes the picker; left-click opens its editor.
2. **Paste colour:** `close-menu` → `focus-window` `/painter|designer/i` → `delay 0.3` →
   `ControlLeft+KeyV` → `Enter`.

Before picking, click the hex field of the colour you want to change in Painter or Designer;
the app keeps that field focused while you pick elsewhere. Kando can't click the field for
you. Check whether the app wants the leading `#` (PowerToys' HEX format can drop it in its
settings). *(Paste step inferred; test once.)*

A good home for both is a **Studio** submenu in the same direction in every work menu (the
examples use Down), so "save everything" is the same flick in every app.
