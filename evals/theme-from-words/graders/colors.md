---
type: "llm"
focus: {"source": "file", "path": "config.json"}
weight: 4
---
PASS only if ALL hold for the final config.json:
1. Valid JSON, and "menuTheme" is still "default".
2. "menuThemeColors" has a "default" object (keyed by the theme id) with color overrides inside it.
3. The color names used are ones Kando's Default theme declares, such as background-color, text-color, border-color, hover-color, wedge-color, wedge-highlight-color. No invented names.
4. The background is dark and partly transparent (an alpha below 1), and hover-color is violet or purple.
FAIL if any one is not met.
