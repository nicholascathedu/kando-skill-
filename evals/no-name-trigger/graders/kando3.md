---
type: "llm"
focus: {"source": "file", "path": "menus.json"}
weight: 3
---
PASS only if ALL hold for the final menus.json:
1. Valid JSON, and the five original root items Discord (0), Browser (45), Clipboard (90), Files (180), Steam (270) are still there at those angles, or Browser was replaced by the new Browsers submenu at 45.
2. A submenu (type "submenu") holds Chrome, Firefox and Edge as items of type "button".
3. Each of those buttons has a selectWorkflow whose actions run "close-menu" and then "execute-command".
4. Every new item has an explicit "angle", and no child of the new submenu sits at the angle opposite the submenu's own angle (the way back).
FAIL if any one is not met.
