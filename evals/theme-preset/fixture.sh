#!/usr/bin/env bash
# Writes this case's starting files into the empty workspace.
set -euo pipefail
mkdir -p "menu-themes/glass-ring"
cat > 'menu-themes/glass-ring/theme.json5' <<'KANDO_EOF'
{
  name: 'Glass Ring',
  author: 'someone',
  engineVersion: 1,
  maxMenuRadius: 160,
  colors: {
    'background-color': 'rgb(24 12 42 / 0.74)',
    'text-color': 'rgb(246 240 255)',
    'accent-color': 'rgb(176 124 255)',
    'glow-color': 'rgb(176 124 255 / 0.5)',
  },
  layers: [{ class: 'icon-layer', content: 'icon' }],
}
KANDO_EOF
