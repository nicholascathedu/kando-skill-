---
type: "llm"
weight: 3
---
PASS only if ALL hold for the final message:
1. It says Kando can't bind a mouse button directly, so a helper is needed: the mouse vendor's software, AutoHotkey, or similar.
2. It has the side button send the menu's keyboard shortcut, ideally a combo nothing else uses such as Ctrl+F13 (or has the helper run `kando --menu "Name"`).
3. It explains the hold-move-release part as turbo mode, which works because the button holds the modifier key (for example Ctrl) down while you move, and releasing it selects.
FAIL if any one is missing or it claims Kando has a built-in mouse-button setting.
