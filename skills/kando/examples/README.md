# Examples

| File | What it is |
|---|---|
| `desktop-launcher.json` | A general launcher on Ctrl+Space: games, browser, clipboard tools, files, 3D apps, settings, media, screenshot. Every ring uses fixed angles, and most items have quick-select keys. |
| `3d-work-menus.json` | Maya, Substance Painter, Substance Designer and Unreal menus that all open on Ctrl+4, chosen by the app in front. "Studio" is Down in all four: switch app (Down twice goes from Painter to Designer and back), Save everything (Down-left) and Pick colour (Down-right). Designer's Up is a palette of eight favourite nodes on Ctrl+Alt+1–8 (bind them in Designer's Preferences → Shortcuts first), and its Left publishes the .sbsar, like Painter's Left exports textures. Painter adds Bake mesh maps, a Views submenu (F1–F4) and Smudge and Clone tools. Unreal's View mode holds all eight view modes. Add a menu without conditions on Ctrl+4 as the fallback (e.g. the launcher). |
| `design-3d-macros.json` | ZBrush, Blender, Photoshop and Illustrator menus on Ctrl+4, chosen by the app in front. Down opens the same **Studio** submenu in all four: Save everything (one Ctrl+S per app), Pick colour (PowerToys) and Paste colour into Painter or Designer. Save is Down-left, as in the work menus. ZBrush has Display and Subdiv pies; Solo and Transp need a key bound in ZBrush first. Blender has render, maximize and next / previous workspace. |

Try them safely without touching your own setup:

```
python ../scripts/kando_check.py desktop-launcher.json
python ../scripts/kando_preview.py 3d-work-menus.json --html sheet.html
kando --config-dir <empty folder>     # then copy one file in as menus.json
```

Launch commands differ per PC. Re-pick apps with the editor's "Choose an app" button rather
than trusting the commands here. Letter hotkeys assume a QWERTY layout.

Theme: the **Amethyst Arsenal** theme in `themes/amethyst-arsenal` pairs with these menus.
See `references/themes.md` for how themes are built.
