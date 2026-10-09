---
type: "llm"
focus: {"source": "file", "path": "menus.json"}
weight: 4
---
PASS only if ALL hold for the final menus.json:
1. Valid JSON. The BLESSED menu is still present.
2. A Designer menu exists on shortcut "Control+4" with "conditions" whose "appName" contains "Designer" (for example "Substance 3D Designer").
3. Each of the four work menus (Maya, Painter, Unreal, Designer) has a "Switch app" submenu listing the other three apps.
4. Each app's switch item sits at the same angle in every Switch app ring it appears in (for example "Go to Painter" has one angle everywhere).
5. The three items that sat on a submenu's way back are moved: in Maya > Display, Wireframe is no longer at 270; in Painter > Tools, Projection is no longer at 180; in Unreal > Name prefix, "MF_ function" is no longer at 90.
FAIL if any one is not met.
