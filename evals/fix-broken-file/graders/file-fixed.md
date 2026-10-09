---
type: "llm"
focus: {"source": "file", "path": "menus.json"}
weight: 3
---
PASS only if ALL of these hold for the final menus.json:
1. It is valid JSON (no missing or extra commas).
2. The "Save" item's simulate-hotkey action uses physical key codes, e.g. "ControlLeft+KeyS" (or ControlRight+KeyS). "Ctrl+S" or "Control+S" is a FAIL.
3. In each button's actions, "close-menu" comes before "simulate-hotkey".
4. The four items Save (angle 0), Frame (90), Undo (180), Redo (270) all still exist with those angles, and the menu still has shortcut "Control+4" and conditions appName "maya".
FAIL if any one of them is not met.
