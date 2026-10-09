---
type: "regex"
pattern: "\"type\"\\s*:\\s*\"(command|uri|hotkey|empty)\""
match: "not_contains"
target: {"source": "file", "path": "menus.json"}
weight: 2
---
