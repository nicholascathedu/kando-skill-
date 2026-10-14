# Examples

| File | What it is |
|---|---|
| `desktop-launcher.json` | A general launcher on Ctrl+Space: games, browser, clipboard tools, files, 3D apps, settings, media, screenshot. Every ring uses fixed angles, and most items have quick-select keys. |
| `3d-work-menus.json` | Maya, Substance Painter, Substance Designer and Unreal menus that all open on Ctrl+4. Which one you get depends on the app in front. Down is "Studio" in all four, with app switching (Down twice goes from Painter to Designer and back), Save everything (Down-left) and Pick colour (Down-right). Designer's Up is a palette of eight favourite nodes on Ctrl+Alt+1–8, which you bind first in Designer's Preferences → Shortcuts. Its Left publishes the .sbsar, the same way Left exports textures in Painter. Painter also has Bake mesh maps, a Views submenu (F1–F4) and the Smudge and Clone tools, and Unreal's View mode has all eight view modes. You'll want a menu with no conditions on Ctrl+4 too, such as the launcher, for every other app. |
| `design-3d-macros.json` | ZBrush, Blender, Photoshop and Illustrator menus on Ctrl+4, again picked by the app in front. Down opens the same Studio submenu in all four, with Save everything (one Ctrl+S per app), Pick colour (PowerToys) and Paste colour into Painter or Designer. Save is Down-left, like in the work menus. ZBrush has Display and Subdiv pies, but Solo and Transp only work after you bind a key for them in ZBrush. Blender has render, maximize and next / previous workspace. |
| `desktop-workflows.json` | Multi-step desktop workflows on Ctrl+F13, the key `kando-mouse-buttons.ps1` sends from a side button. Snip, then Paste into PureRef. Clipboard history, text from the screen (PowerToys), pin a window on top, virtual desktops, a Claude submenu that opens Claude Code in a folder or pastes a ready prompt, and Work mode, which starts Maya, Painter and Spotify in one go (fix the paths for your PC). |
| `sim-and-render.json` | A Physics test pie for Unreal on Ctrl+F14 (Play, Simulate, slow motion and back, `stat unit`, Chaos recording, a Game Bar clip), a Marvelous Designer camera pie with each view where the camera looks from, and a Marmoset Toolbag Present pie that also sends the viewport to Discord. Marvelous and Toolbag's process names are not confirmed yet; check them with the editor's window picker. |
| `text-pie.json` | A text pie on Ctrl+F15 for any app: select text, flick, and it comes back as snake_case, PascalCase, camelCase or kebab-case (asset and variable names), UPPER, lower, Title or Sentence case, joined onto one line or with tidy spaces. Up searches the web for it, up-right translates it. Down opens clipboard history (Win+V, turn it on the first time) and down-left starts Windows dictation (Win+H) in the text field you were in. Uses `kando_text.py`; give it the script's full path. The Claude submenu in `desktop-workflows.json` uses the same trick to start Claude Code on what you copied: *Explain what I copied*, and *Slides from this video* on a YouTube tab (`kando_claude.py`). |

You can try them without touching your own setup:

```
python ../scripts/kando_check.py desktop-launcher.json
python ../scripts/kando_preview.py 3d-work-menus.json --html sheet.html
kando --config-dir <empty folder>     # then copy one file in as menus.json
```

Launch commands are different on every PC, so re-pick the apps with the editor's "Choose an
app" button instead of trusting the commands here. Letter hotkeys assume a QWERTY layout.

These menus go well with the Amethyst Arsenal theme in `themes/amethyst-arsenal`. To learn how
themes are built, see `references/themes.md`.
