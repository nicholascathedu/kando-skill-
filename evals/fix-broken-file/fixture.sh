#!/usr/bin/env bash
# Writes this case's starting files into the empty workspace.
set -euo pipefail
cat > 'menus.json' <<'KANDO_EOF'
{
  "version": "3.0.0",
  "menus": [
    {
      "shortcut": "Control+4",
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
        "name": "Maya work",
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
            "name": "Save",
            "icon": "circle",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 0,
            "selectWorkflow": {
              "quickSelectKey": "S",
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "Ctrl+S"
                }
              ]
            }
          },
          {
            "name": "Frame"
            "icon": "circle",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 90,
            "selectWorkflow": {
              "quickSelectKey": "F",
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "KeyF"
                }
              ]
            }
          },
          {
            "name": "Undo",
            "icon": "circle",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 180,
            "selectWorkflow": {
              "quickSelectKey": "U",
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "ControlLeft+KeyZ"
                }
              ]
            }
          },
          {
            "name": "Redo",
            "icon": "circle",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 270,
            "selectWorkflow": {
              "quickSelectKey": "R",
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "ControlLeft+KeyY"
                }
              ]
            }
          }
        ]
      },
      "conditions": {
        "appName": "maya"
      }
    }
  ]
}
KANDO_EOF
