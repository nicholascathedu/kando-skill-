# Sources and version notes

Everything in this skill comes from Kando's official sources, checked for **Kando 3.0.0**
(released 2026-09-23):

| Source | What it's good for |
|---|---|
| kando.menu (site source: github.com/kando-menu/kando-menu.github.io, `src/content/docs/*.mdx`) | User docs: usage, config files, actions, themes, opening menus, CLI, IPC |
| github.com/kando-menu/kando `src/common/settings-schemata/menu-settings-v2.ts` | The exact menus.json format Kando validates |
| … `general-settings-v1.ts` | The exact config.json format and defaults |
| … `src/common/math/index.ts` | How fixed angles are read and items placed (`computeItemAngles`; the live menu calls it on the raw angles in `src/menu-renderer/menu.ts`) |
| … `src/main/actions/*.ts` | What each action really does |
| … `assets/menu-themes/` | The built-in themes, best starting points for new ones |
| … `docs/changelog.md` | What changed in each version |
| Simon Schneegans' YouTube channel (youtube.com/@simonschneegans) | Kando 3.0 workflows (PhUnN2cx5sI), 2.1 features (wNNS7vrur3M), "How to be FAST" (elHUCarOiXQ) |
| Kando Discord (linked from kando.menu) | Community help, #menu-themes |
| experienceleague.adobe.com/en/docs/substance-3d-designer (Shortcuts, Graph view, 2D view, 3D view, Main toolbar, Node alignment tools, Node finder, Publishing .sbsar, Retrieving the installation path, 16.0 release notes) | Designer's default keys and process name in `app-recipes.md` |

## Where the 3.0 docs and code disagree

| Topic | Docs say | 3.0 code says |
|---|---|---|
| Menu centering | `centered: true` | `useFixedPosition` + `fixedMenuPosition {x,y}` (old key migrated) |
| Fade durations | 150 / 200 ms | 75 / 100 ms |
| `sameShortcutBehavior` | 4 values | adds `re-open` |
| Undocumented settings | — | `hideOnFocusOut`, `triggerCenterClickOnKeyRelease`, `underlineQuickSelectKey`, `drawQuickSelectKey` |
| Actions | 13 pages | 14 types (`send-websocket-message` has no page) |
| CSS sibling count | `--siblings-count` | `--sibling-count` |

## Facts verified in source (not stated in the docs)

- Windows `appName` is the focused process's executable file name (`Native.cpp`,
  `QueryFullProcessImageNameA`).
- Every menu shortcut is registered globally, whatever its conditions; with no matching menu
  the key is swallowed.
- `simulate-hotkey` sends keys to whatever has focus; while the menu is open that's Kando.
- Fixed angles are used as written, in list order: negative angles and angles smaller than
  the previous fixed one are ignored (the item is auto-placed), and equal angles are both
  kept, so those items overlap. Only the settings editor's drag preview runs
  `fixFixedAngles`.
- `warpMouse` moves the pointer when Kando shifts a menu inside the screen edge, and onto
  fixed-position menus.

## Newer Kando versions

If the user runs a version after 3.0, read the changelog first. The schemas above are the
fastest way to confirm a field still exists. `kando --version` prints the version.
