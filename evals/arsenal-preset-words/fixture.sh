#!/usr/bin/env bash
# Writes this case's starting files into the empty workspace.
set -euo pipefail
mkdir -p "menu-themes/amethyst-arsenal"
cat > 'menu-themes/amethyst-arsenal/theme.json5' <<'KANDO_EOF'
// SPDX-FileCopyrightText: Nicholas (github.com/nicholascathedu)
// SPDX-License-Identifier: CC0-1.0

// Amethyst Arsenal, a menu theme for Kando 3.0.
// Inspired by the weapon selection wheel of Ratchet & Clank Future: A Crack in Time.

{
  name: 'Amethyst Arsenal',
  author: 'nicholascathedu',
  license: 'CC0-1.0',
  themeVersion: '1.1.0',
  description: 'Weapon-wheel hex tiles with see-through purple faces and a soft gold aura on the selected tile.',

  // Kando 3.0 uses theme engine version 1.
  engineVersion: 1,

  // How close to a screen edge the menu may open, in pixels from the menu's center.
  // Worked out from the "Tweak me" block in theme.css for a menu of 12 items:
  //   tiles sit max(104px, 11px x 12) = 132px out,
  //   the hovered tile grows 1.22 times, so its middle moves to 132 x 1.22 = 161px,
  //   half its height adds 69 / 2 x 1.22 = 42px, which makes 203px,
  //   and the outer gold aura reaches about 20px further: 223px.
  // Menus with more than 12 items can still touch the screen edge with the hovered tile.
  // If you make tiles, spacing, hover scale or aura bigger in theme.css, raise this too.
  maxMenuRadius: 225,

  // Width of the center text. Fits inside the center tile's flat sides.
  centerTextWrapWidth: 68,

  drawChildrenBelow: true,
  drawCenterText: true,

  // Both only show when "Draw item wedges" is turned on in Kando's Menu Themes dialog.
  drawSelectionWedges: true,
  drawWedgeSeparators: true,

  // Every color below can be changed in Kando's settings. Any CSS color works,
  // including transparency, for example 'rgb(40 22 68 / 0.40)'.
  colors: {
    // Tiles
    'frame-color': 'rgb(14 10 20 / 0.92)',        // dark outer frame
    'line-color': 'rgb(214 206 232 / 0.85)',      // thin line inside the frame
    'glass-color': 'rgb(40 22 68 / 0.40)',        // see-through face of each item
    'center-color': 'rgb(24 14 40 / 0.78)',       // face of the center tile

    // Selected tile
    'glass-hover-color': 'rgb(10 6 16 / 0.90)',   // dark face
    'bloom-color': 'rgb(130 70 220 / 0.38)',      // purple light in the middle
    'rim-hover-color': 'rgb(255 238 214)',        // cream frame
    'aura-color': 'rgb(255 166 64 / 0.85)',       // gold glow around it

    // Text and icons
    'icon-color': 'rgb(244 238 255)',             // single-color icons
    'text-color': 'rgb(255 255 255)',             // item name in the center

    // Extras
    'connector-color': 'rgb(214 206 232 / 0.45)', // line to the previous menu
    'wedge-color': 'rgb(12 4 24 / 0.25)',         // selection wedges
    'wedge-highlight-color': 'rgb(140 84 255 / 0.22)',
    'separator-color': 'rgb(196 160 255 / 0.16)', // lines between wedges
    'badge-color': 'rgb(14 8 24 / 0.92)',         // quick-select key chip
    'badge-text-color': 'rgb(255 255 255)',
  },

  // Drawn top to bottom: the key chip, the submenu marker, then the hex tile with its
  // icon. The key chip only appears when "Draw quick-select key" is turned on in Kando's
  // Menu Themes dialog. The submenu marker is an empty layer that theme.css shows on
  // items that open a submenu; delete its line here and its block in theme.css to drop it.
  layers: [
    { class: 'quick-key', content: 'quick-select-key' },
    { class: 'submenu-mark', content: 'none' },
    { class: 'icon-layer', content: 'icon' },
  ],
}
KANDO_EOF
