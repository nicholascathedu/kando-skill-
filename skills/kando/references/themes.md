# Theming Kando: colors, presets, full menu themes, icons, sounds

Sources: kando.menu/create-menu-themes, kando.menu/menu-themes, kando.menu/icon-themes,
the built-in themes in github.com/kando-menu/kando/tree/main/assets/menu-themes.

## Contents
1. Pick the lightest route
2. From a vibe to a palette
3. Route A: recolor a built-in theme (no files)
4. Route B: a color preset
5. Route C: a new menu theme
6. CSS cheat sheet
7. Icons
8. Sounds
9. Publishing a theme

## 1. Pick the lightest route

| Want | Route | Effort |
|---|---|---|
| Different colors, same shapes | A: `menuThemeColors` in config.json (or the editor's color pickers) | Minutes |
| Reusable / shareable color set for a theme | B: a preset file in the theme's `presets/` | Minutes |
| Different shapes, glow, layout, animation | C: new theme folder (theme.json5 + theme.css) | An hour+ |

Built-in themes (3.0): `default`, `clean-circle`, `neon-lights`, `rainbow-labels`,
`purity` (dark ring with colored wedges and key badges). Community themes:
github.com/kando-menu/menu-themes.

## 2. From a vibe to a palette

When a user describes a mood ("dark purple, transparent, glassy", "clean light", "neon
cyberpunk"), turn it into tokens before touching any file:

| Token | Role | Example: dark purple glass |
|---|---|---|
| surface | item / center fill, usually translucent | `rgb(24 12 42 / 0.74)` |
| surface-hover | hovered item | `rgb(92 44 160 / 0.82)` |
| rim | thin border, low alpha | `rgb(196 160 255 / 0.30)` |
| accent | active ring, connectors, key badges | `rgb(181 128 255)` |
| glow | box-shadow / drop-shadow color | `rgb(150 90 255 / 0.65)` |
| text / icon | high contrast on surface | `rgb(246 240 255)` |
| wedge / wedge-highlight | selection wedge fill | `rgb(12 4 24 / 0.28)` / `rgb(140 84 255 / 0.30)` |

Rules of thumb:
- Translucency: 0.6–0.85 alpha on surfaces keeps text readable over any wallpaper. Below
  0.5 icons get lost on busy backgrounds.
- Contrast: text/icons should reach at least 4.5:1 against the surface color *composited on
  a dark and a light wallpaper*. Check both.
- One accent. Use it for state (active, hovered, connector), not decoration.
- Glow > hard shadow for dark themes; soft drop shadow for light ones.
- Selection wedges help while learning; keep them subtle (alpha ≤ 0.3).
- Preview the palette with `kando_preview.py --html sheet.html --accent "<accent>"` before
  writing CSS: it uses the same surface/accent logic.

## 3. Route A: recolor a built-in theme

Each theme declares named colors in its `theme.json5` (`colors: {...}`). Override them per
theme in config.json, separately for light and dark mode:

```json
"menuTheme": "default",
"darkMenuTheme": "default",
"enableDarkModeForMenuThemes": true,
"darkMenuThemeColors": {
  "default": {
    "background-color": "rgb(24 12 42 / 0.74)",
    "text-color": "rgb(246 240 255)",
    "border-color": "rgb(196 160 255 / 0.30)",
    "hover-color": "rgb(92 44 160 / 0.82)",
    "wedge-color": "rgb(12 4 24 / 0.28)",
    "wedge-highlight-color": "rgb(140 84 255 / 0.30)"
  }
}
```

Only names the theme declares have an effect. Find them in the theme's `theme.json5` (built-in
themes ship inside the install folder at `resources/app/.webpack/renderer/assets/menu-themes/`;
read, don't edit) or in the editor's theme color pickers. For selection wedges also set
`"enableSelectionWedges": true`.

## 4. Route B: a color preset

A preset is a JSON file in `<theme>/presets/`, e.g. `presets/Amethyst.json`:

```json
{ "colors": { "background-color": "rgb(24 12 42 / 0.74)", "hover-color": "rgb(92 44 160 / 0.82)" } }
```

It appears as a one-click choice in the editor's color settings for that theme.

## 5. Route C: a new menu theme

Folder: `<config>/menu-themes/<theme-id>/` containing:
- `theme.json5` (or `theme.json`): metadata, colors, layers
- `theme.css`: the styling
- `preview.jpg`: square screenshot, ~700×700, shown in the editor
- optional `presets/`, `assets/` (fonts, images), `REUSE.toml` (licenses)

Fastest start: copy the built-in `default` theme folder and change it. Restart Kando after
adding a theme; while editing, the editor's Development tab has "Reload Menu Theme" (or run
`kando --reload-menu-theme`). CSS reloads live; theme.json5 changes need the menu reopened.
The Development tab also has an inspector to explore the DOM.

### theme.json5 keys

```json5
{
  name: 'My Theme', author: 'you', license: 'CC0-1.0', themeVersion: '1.0',
  description: 'One line',
  engineVersion: 1,            // theme engine version (still 1 in Kando 3.0)
  maxMenuRadius: 150,          // px kept free from screen edges
  centerTextWrapWidth: 90,     // px
  drawChildrenBelow: true,     // children rendered below their parent
  drawCenterText: true,
  drawSelectionWedges: false,  // theme supports wedge highlight
  drawWedgeSeparators: false,  // theme draws lines between wedges
  colors: { 'background-color': 'rgb(255 255 255)', /* user-editable, become CSS vars */ },
  layers: [                    // top-most first
    { class: 'icon-layer', content: 'icon' },          // content: none | icon | name | quick-select-key
  ],
}
```

Every `colors` entry becomes `var(--<name>)` in CSS and gets a color picker in the editor.

### Minimal theme.css skeleton (glass disc + glow)

```css
.menu-node {
  --child-distance: 100px; --center-size: 96px; --child-size: 52px; --grandchild-size: 14px;
  --t: all 220ms cubic-bezier(0.775, 1.325, 0.535, 1);
  transition: var(--t);

  &.child {
    transform: translate(calc(max(var(--child-distance), 10px * var(--sibling-count)) * var(--dir-x)),
                         calc(max(var(--child-distance), 10px * var(--sibling-count)) * var(--dir-y)));
  }
  &.grandchild { transform: translate(calc(24px * var(--dir-x)), calc(24px * var(--dir-y))); }
  &.dragged { transition: none; }

  .icon-layer { position: absolute; border-radius: 50%; transition: var(--t);
    background: var(--background-color); border: 1px solid var(--border-color);
    backdrop-filter: blur(10px); }
  .icon-container { opacity: 0; color: var(--text-color); margin: 18%; width: 64% !important; height: 64% !important; }

  &.active > .icon-layer { top: calc(var(--center-size) / -2); left: calc(var(--center-size) / -2);
    width: var(--center-size); height: var(--center-size);
    box-shadow: 0 0 24px var(--glow-color, transparent); }
  &.parent > .icon-layer, &.child > .icon-layer { top: calc(var(--child-size) / -2); left: calc(var(--child-size) / -2);
    width: var(--child-size); height: var(--child-size); }
  &.grandchild > .icon-layer { top: calc(var(--grandchild-size) / -2); left: calc(var(--grandchild-size) / -2);
    width: var(--grandchild-size); height: var(--grandchild-size); background: var(--border-color); }
  &.active > .icon-layer > .icon-container, &.child > .icon-layer > .icon-container,
  &.parent > .icon-layer > .icon-container { opacity: 1; }
  &.child.hovered > .icon-layer, &.parent.hovered > .icon-layer, &.active.hovered > .icon-layer {
    background: var(--hover-color); }

  .connector { height: 4px; top: -2px; background: var(--border-color); transition: var(--t); }
  &:has(.dragged) > .connector { transition: none; }
  &.active > .connector { background: var(--hover-color); }
}
.center-text { color: var(--text-color); font-size: 14px; }
```

(`--glow-color` here is an extra color you'd add to `colors`.)

A finished example is **Amethyst Arsenal**, in `themes/amethyst-arsenal/` of this skill's
GitHub repo (github.com/nicholascathedu/kando-skill-). It shows hex tiles drawn with
`clip-path`, a glow on the hovered item, quick-select key badges, presets, and a "Tweak me"
block of CSS variables at the top of `theme.css` for sizes and speed. Read it when someone
wants a game-HUD look or a well-commented theme to start from.

## 6. CSS cheat sheet

**Node classes**: `.menu-node` plus `.level-0..n`, `.type-root|submenu|button`,
state `.active` (current center), `.child`, `.grandchild`, `.parent`, `.hovered`,
`.clicked`, `.dragged`, direction `.top|.right|.bottom|.left`.
Select by item name: `.menu-node[data-name='Save']`.

**Other elements**: `.connector` (lines to submenus), `.center-text`,
`.selection-wedges` (full-screen, `.hovered` when a wedge is active),
`.wedge-separators > .separator`.

**Custom properties** set by Kando:

| Property | On | Meaning |
|---|---|---|
| `--dir-x`, `--dir-y` | non-root nodes | unit direction from parent |
| `--angle` | non-root nodes | item angle, 0 = up, clockwise |
| `--start-angle`, `--end-angle` | non-root nodes | its wedge |
| `--sibling-count` | non-root nodes | number of siblings (the docs spell it `--siblings-count`; the built-in CSS uses `--sibling-count`) |
| `--parent-angle` | level 2+ | angle of the parent item |
| `--parent-start-angle`, `--parent-end-angle` | `.parent` | back-navigation wedge |
| `--angle-diff` | `.child` | angle to the pointer (fisheye effects) |
| `--pointer-angle`, `--hover-angle`, `--hovered-child-angle` | layers of `.active` | rotate a halo toward the pointer / hovered item |
| `--center-x`, `--center-y`, `--start-angle`, `--end-angle` | `.selection-wedges` | for a conic-gradient wedge |

Useful selectors:
```css
.menu-node.active:has(> .hovered) {}        /* center while a child is hovered */
.menu-node.active:has(.hovered) > .child {} /* all children while one is hovered */
```

Performance: fewer layers render faster; `backdrop-filter` and big blurs cost GPU, so test
on the user's machine. When `enableMenuAnimations` is off, Kando keeps a `no-transitions`
class on the menu container, so don't rely on transitions for anything functional.

## 7. Icons

- Icon themes: `material-symbols-rounded` (fonts.google.com/icons names), `simple-icons` and
  `simple-icons-colored` (simpleicons.org slugs), `emoji`, `system` (installed apps), `base64`.
- Custom icon theme: a folder of SVGs in `<config>/icon-themes/<name>/` (subfolders ok),
  restart Kando. Use `fill="currentColor"` in the SVGs so icons follow the theme's text/icon color.
- For a cohesive look, stick to one icon family per menu; monochrome Material Symbols suit
  glassy themes, colored brand icons suit launchers.

## 8. Sounds

Sound themes live in `<config>/sound-themes/<name>/` with `theme.json` and audio files (the
format changed in 3.0; copy the built-in `simple-clicks` as a template). Pick one under
General Settings → Menu Sounds; `soundVolume` 0–1. More at github.com/kando-menu/sound-themes.

## 9. Publishing a theme

- Add SPDX headers to text files and a `REUSE.toml` for images/fonts. CC0-1.0 for config,
  CC-BY-4.0 for artwork is the docs' suggestion.
- Credit what you based it on (e.g. "based on Kando's Default theme by Simon Schneegans").
- Share on Kando's Discord (#menu-themes) or open a PR to github.com/kando-menu/menu-themes.
