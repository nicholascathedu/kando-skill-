---
type: "regex"
pattern: "\"name\":\\s*\"Steam\"[\\s\\S]*?\"angle\":\\s*0[,\\s}][\\s\\S]*?\"name\":\\s*\"Discord\"[\\s\\S]*?\"angle\":\\s*90[,\\s}][\\s\\S]*?\"name\":\\s*\"Files\"[\\s\\S]*?\"angle\":\\s*180[,\\s}]"
target: {"source": "file", "path": "menus.json"}
weight: 3
---
