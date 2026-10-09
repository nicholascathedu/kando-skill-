---
type: "llm"
focus: {"source": "file", "path": "menus.json"}
weight: 3
---
PASS only if ALL hold for the final menus.json:
1. Valid JSON with the original "Desktop" menu still present and unchanged in its items (Discord 0, Browser 45, Clipboard 90, Files 180, Steam 270).
2. A new menu exists whose "conditions" has "appName" matching Blender (for example "blender").
3. Its "shortcut" is not Ctrl/Control plus a digit 1-5, and not a single plain letter.
4. Every item in the new menu, including the Shading submenu's children, has an explicit "angle" between 0 and 359, and within each ring the angles increase in the order listed.
5. Inside the Shading submenu, no child sits at the angle opposite the submenu's own angle (submenu angle + 180, modulo 360), because that is the way back to the parent.
6. Buttons that press keys use "simulate-hotkey" with key codes such as "ControlLeft+KeyS", "KeyZ", "Tab", "F12" (not names like "Ctrl+S"), and "close-menu" comes before the key press.
FAIL if any one is not met.
