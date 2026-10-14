# Examples

| File | What it is |
|---|---|
| `desktop-launcher.json` | A general launcher on Ctrl+Space: games, browser, clipboard tools, files, 3D apps, settings, media, screenshot. Every ring uses fixed angles, and most items have quick-select keys. |
| `3d-work-menus.json` | Maya, Substance Painter, Substance Designer and Unreal menus that all open on Ctrl+4. Which one you get depends on the app in front. Down is "Studio" in all four, with app switching (Down twice goes from Painter to Designer and back), Save everything (Down-left) and Pick colour (Down-right). Designer's Up is a palette of eight favourite nodes on Ctrl+Alt+1–8, which you bind first in Designer's Preferences → Shortcuts. Its Left publishes the .sbsar, the same way Left exports textures in Painter. Painter also has Bake mesh maps, a Views submenu (F1–F4) and the Smudge and Clone tools, and Unreal's View mode has all eight view modes. You'll want a menu with no conditions on Ctrl+4 too, such as the launcher, for every other app. |
| `design-3d-macros.json` | ZBrush, Blender, Photoshop and Illustrator menus on Ctrl+4, again picked by the app in front. Down opens the same Studio submenu in all four, with Save everything (one Ctrl+S per app), Pick colour (PowerToys) and Paste colour into Painter or Designer. Save is Down-left, like in the work menus. ZBrush has Display and Subdiv pies, but Solo and Transp only work after you bind a key for them in ZBrush. Blender has render, maximize and next / previous workspace. |

To add one menu without editing JSON, split a file into importable menus and use Import in
Kando's editor:

```
python ../scripts/kando_split.py 3d-work-menus.json --out importable
```

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
