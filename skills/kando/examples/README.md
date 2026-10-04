# Examples

| File | What it is |
|---|---|
| `desktop-launcher.json` | A general launcher on Ctrl+Space: games, browser, clipboard tools, files, 3D apps, settings, media, screenshot. Every ring uses fixed angles, and most items have quick-select keys. |
| `3d-work-menus.json` | Maya, Substance Painter and Unreal menus that all open on Ctrl+4, chosen by the app in front. "Switch app" is Down in all three. Add a menu without conditions on Ctrl+4 as the fallback (e.g. the launcher). |

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
