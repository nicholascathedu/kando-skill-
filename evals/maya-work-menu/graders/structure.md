---
type: "llm"
focus: {"source": "file", "path": "menus.json"}
weight: 4
---
PASS only if ALL hold for the final menus.json:
1. Valid JSON; the "Desktop" menu is still there with Discord 0, Browser 45, Clipboard 90, Files 180, Steam 270.
2. A new menu has "conditions" with "appName" matching Maya (for example "maya").
3. No ring (the root or any submenu) has more than 12 children, and the 19 actions are grouped into submenus rather than all in the root.
4. Every item has an explicit "angle" from 0 to 359, and in each ring the angles strictly increase in the order listed.
5. In every submenu, no child sits at the angle opposite the submenu's own angle (submenu angle + 180, modulo 360), and none within 30 degrees of it.
6. Every key press uses "simulate-hotkey" with key codes (such as "ControlLeft+KeyS", "KeyF", "KeyW", "Digit4"), never names like "Ctrl+S", and "close-menu" comes before it.
FAIL if any one is not met.
