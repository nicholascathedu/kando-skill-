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
        "name": "Main",
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
            "name": "Discord DMs",
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
                  "command": "start \"\" discord://-/channels/@me/918273645546372819",
                  "detached": true,
                  "isolated": false
                }
              ]
            }
          },
          {
            "name": "Notes",
            "icon": "circle",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 90,
            "selectWorkflow": {
              "quickSelectKey": "N",
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "execute-command",
                  "command": "notepad \"C:\\Users\\alexr\\Documents\\notes.txt\"",
                  "detached": true,
                  "isolated": false
                }
              ]
            }
          },
          {
            "name": "Mail Jo",
            "icon": "circle",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 180,
            "selectWorkflow": {
              "quickSelectKey": "M",
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "open-uri",
                  "uri": "mailto:alex.rivera.art@example.com"
                }
              ]
            }
          },
          {
            "name": "Blender",
            "icon": "circle",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 270,
            "selectWorkflow": {
              "quickSelectKey": "B",
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "execute-command",
                  "command": "\"C:\\Users\\alexr\\AppData\\Local\\Blender\\blender.exe\"",
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
