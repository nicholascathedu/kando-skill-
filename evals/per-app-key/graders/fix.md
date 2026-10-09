---
type: "llm"
focus: {"source": "file", "path": "menus.json"}
weight: 3
---
PASS only if ALL hold for the final menus.json:
1. Valid JSON, still Kando 3 format ("version" and "menus").
2. The Maya menu still has conditions with appName "maya" and still has its items Save (0), Frame (90), Undo (180), Redo (270).
3. The Maya menu's shortcut is no longer "Control+4" / "Ctrl+4". It moved to a combination Chrome does not use, for example "Control+F13", "Control+Shift+4" or "Alt+4".
FAIL otherwise.
