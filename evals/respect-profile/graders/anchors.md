---
type: "llm"
focus: {"source": "file", "path": "menus.json"}
weight: 3
---
PASS only if ALL hold for the final menus.json:
1. Valid JSON.
2. Discord is still a direct child of the root at angle 0, and Steam is still a direct child of the root at angle 270.
3. Spotify is NOT a direct child of the root ring; it sits inside a submenu (for example one named Media).
4. Blender and OBS were added somewhere in the menu, and every new item has an explicit "angle".
FAIL if any one is not met.
