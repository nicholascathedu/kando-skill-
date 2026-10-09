#!/usr/bin/env bash
# Writes this case's starting files into the empty workspace.
set -euo pipefail
cat > 'menus.json' <<'KANDO_EOF'
{
  "version": "3.0.0",
  "menus": [
    {
      "shortcut": "Control+Space",
      "shortcutID": "",
      "useFixedPosition": false,
      "fixedMenuPosition": {
        "x": 0.5,
        "y": 0.5
      },
      "anchored": false,
      "hoverMode": false,
      "tags": [],
      "root": {
        "name": "Desktop",
        "icon": "apps",
        "iconTheme": "material-symbols-rounded",
        "type": "root",
        "activateWorkflow": {
          "quickSelectKey": "Backspace",
          "actions": [
            {
              "type": "close-menu"
            }
          ]
        },
        "children": [
          {
            "name": "Discord",
            "icon": "circle",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 0,
            "selectWorkflow": {
              "quickSelectKey": "D",
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "execute-command",
                  "command": "start \"\" discord://",
                  "detached": true,
                  "isolated": false
                }
              ]
            }
          },
          {
            "name": "Browser",
            "icon": "circle",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 45,
            "selectWorkflow": {
              "quickSelectKey": "B",
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "execute-command",
                  "command": "start \"\" chrome",
                  "detached": true,
                  "isolated": false
                }
              ]
            }
          },
          {
            "name": "Clipboard",
            "icon": "folder",
            "iconTheme": "material-symbols-rounded",
            "type": "submenu",
            "angle": 90,
            "children": [
              {
                "name": "Copy",
                "icon": "circle",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 0,
                "selectWorkflow": {
                  "quickSelectKey": "C",
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyC"
                    }
                  ]
                }
              },
              {
                "name": "Paste",
                "icon": "circle",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 180,
                "selectWorkflow": {
                  "quickSelectKey": "V",
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyV"
                    }
                  ]
                }
              }
            ],
            "activateWorkflow": {
              "quickSelectKey": "Backspace",
              "actions": [
                {
                  "type": "close-submenu"
                }
              ]
            },
            "openWorkflow": {
              "quickSelectKey": "C",
              "actions": []
            }
          },
          {
            "name": "Files",
            "icon": "circle",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 180,
            "selectWorkflow": {
              "quickSelectKey": "F",
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "execute-command",
                  "command": "start \"\" explorer",
                  "detached": true,
                  "isolated": false
                }
              ]
            }
          },
          {
            "name": "Steam",
            "icon": "circle",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 270,
            "selectWorkflow": {
              "quickSelectKey": "S",
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "execute-command",
                  "command": "start \"\" steam://open/main",
                  "detached": true,
                  "isolated": false
                }
              ]
            }
          }
        ]
      }
    }
  ]
}
KANDO_EOF
