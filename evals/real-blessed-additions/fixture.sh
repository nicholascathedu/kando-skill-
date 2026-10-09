#!/usr/bin/env bash
# Writes this case's starting files into the empty workspace.
set -euo pipefail
cat > 'menus.json' <<'KANDO_EOF'
{
  "version": "3.0.0",
  "menus": [
    {
      "root": {
        "name": "BLESSED",
        "icon": "apachenetbeanside",
        "iconTheme": "simple-icons-colored",
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
            "name": "Games and more",
            "icon": "distrobox",
            "iconTheme": "simple-icons-colored",
            "type": "submenu",
            "angle": 0,
            "activateWorkflow": {
              "quickSelectKey": "Backspace",
              "actions": [
                {
                  "type": "close-submenu"
                }
              ]
            },
            "children": [
              {
                "name": "Discord",
                "icon": "discord",
                "iconTheme": "simple-icons-colored",
                "type": "button",
                "angle": 30,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "execute-command",
                      "command": "start \"\" discord",
                      "detached": true,
                      "isolated": false
                    },
                    {
                      "type": "close-menu"
                    }
                  ]
                }
              },
              {
                "name": "Steam",
                "icon": "steam",
                "iconTheme": "simple-icons-colored",
                "type": "button",
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "execute-command",
                      "command": "start \"\" steam",
                      "detached": true,
                      "isolated": false
                    },
                    {
                      "type": "close-menu"
                    }
                  ]
                }
              },
              {
                "name": "Dead by Daylight",
                "icon": "apps",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 330,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "execute-command",
                      "command": "start \"\" deadbydaylight",
                      "detached": true,
                      "isolated": false
                    },
                    {
                      "type": "close-menu"
                    }
                  ]
                }
              }
            ]
          },
          {
            "name": "Media",
            "icon": "debian",
            "iconTheme": "simple-icons-colored",
            "type": "submenu",
            "activateWorkflow": {
              "quickSelectKey": "Backspace",
              "actions": [
                {
                  "type": "close-submenu"
                }
              ]
            },
            "children": [
              {
                "name": "Twitch",
                "icon": "twitch",
                "iconTheme": "simple-icons-colored",
                "type": "button",
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "open-uri",
                      "uri": "https://example.com/twitch"
                    },
                    {
                      "type": "close-menu"
                    }
                  ]
                }
              },
              {
                "name": "YouTube",
                "icon": "youtube",
                "iconTheme": "simple-icons-colored",
                "type": "button",
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "execute-command",
                      "command": "start \"\" youtube",
                      "detached": true,
                      "isolated": false
                    },
                    {
                      "type": "close-menu"
                    }
                  ]
                }
              }
            ],
            "angle": 45
          },
          {
            "name": "Google Chrome",
            "icon": "googlechrome",
            "iconTheme": "simple-icons-colored",
            "type": "button",
            "angle": 90,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "execute-command",
                  "command": "start \"\" googlechrome",
                  "detached": true,
                  "isolated": false
                },
                {
                  "type": "close-menu"
                }
              ]
            }
          },
          {
            "name": "File Explorer",
            "icon": "files",
            "iconTheme": "simple-icons-colored",
            "type": "button",
            "selectWorkflow": {
              "actions": [
                {
                  "type": "execute-command",
                  "command": "start \"\" fileexplorer",
                  "detached": true,
                  "isolated": false
                },
                {
                  "type": "close-menu"
                }
              ]
            },
            "angle": 180
          },
          {
            "name": "Settings",
            "icon": "grapheneos",
            "iconTheme": "simple-icons-colored",
            "type": "button",
            "selectWorkflow": {
              "actions": [
                {
                  "type": "execute-command",
                  "command": "start \"\" settings",
                  "detached": true,
                  "isolated": false
                },
                {
                  "type": "close-menu"
                }
              ]
            },
            "angle": 225
          },
          {
            "name": "Creativity",
            "icon": "sagemath",
            "iconTheme": "simple-icons-colored",
            "type": "submenu",
            "angle": 270,
            "activateWorkflow": {
              "quickSelectKey": "Backspace",
              "actions": [
                {
                  "type": "close-submenu"
                }
              ]
            },
            "children": [
              {
                "name": "Adobe Substance 3D Painter",
                "icon": "apps",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 180,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "execute-command",
                      "command": "start \"\" adobesubstance3dpainter",
                      "detached": true,
                      "isolated": false
                    },
                    {
                      "type": "close-menu"
                    }
                  ]
                }
              },
              {
                "name": "Blender",
                "icon": "blender",
                "iconTheme": "simple-icons-colored",
                "type": "button",
                "angle": 240,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "execute-command",
                      "command": "start \"\" blender",
                      "detached": true,
                      "isolated": false
                    },
                    {
                      "type": "close-menu"
                    }
                  ]
                }
              },
              {
                "name": "Unreal Engine",
                "icon": "unrealengine",
                "iconTheme": "simple-icons-colored",
                "type": "button",
                "angle": 300,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "execute-command",
                      "command": "start \"\" unrealengine",
                      "detached": true,
                      "isolated": false
                    },
                    {
                      "type": "close-menu"
                    }
                  ]
                }
              },
              {
                "name": "Maya 2027",
                "icon": "autodeskmaya",
                "iconTheme": "simple-icons-colored",
                "type": "button",
                "angle": 360,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "execute-command",
                      "command": "start \"\" maya2027",
                      "detached": true,
                      "isolated": false
                    },
                    {
                      "type": "close-menu"
                    }
                  ]
                }
              }
            ]
          }
        ]
      },
      "shortcut": "Control+4",
      "shortcutID": "",
      "useFixedPosition": false,
      "fixedMenuPosition": {
        "x": 0.5,
        "y": 0.5
      },
      "anchored": false,
      "hoverMode": false,
      "tags": [
        "My PC"
      ]
    },
    {
      "root": {
        "name": "Maya",
        "icon": "autodeskmaya",
        "iconTheme": "simple-icons-colored",
        "type": "root",
        "children": [
          {
            "name": "Frame selected",
            "icon": "center_focus_strong",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 0,
            "selectWorkflow": {
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
            "name": "Isolate selected",
            "icon": "filter_center_focus",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 45,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "ControlLeft+Digit1"
                }
              ]
            }
          },
          {
            "name": "Display",
            "icon": "visibility",
            "iconTheme": "material-symbols-rounded",
            "type": "submenu",
            "angle": 90,
            "children": [
              {
                "name": "Smooth preview",
                "icon": "blur_on",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 0,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Digit3"
                    }
                  ]
                }
              },
              {
                "name": "Shaded",
                "icon": "circle",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 90,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Digit5"
                    }
                  ]
                }
              },
              {
                "name": "Use all lights",
                "icon": "lightbulb",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 135,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Digit7"
                    }
                  ]
                }
              },
              {
                "name": "Textured",
                "icon": "texture",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 180,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Digit6"
                    }
                  ]
                }
              },
              {
                "name": "Wireframe",
                "icon": "grid_on",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 270,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Digit4"
                    }
                  ]
                }
              },
              {
                "name": "Rough",
                "icon": "hexagon",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 315,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Digit1"
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
            }
          },
          {
            "name": "Delete history",
            "icon": "delete_sweep",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 135,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "AltLeft+ShiftLeft+KeyD"
                }
              ]
            }
          },
          {
            "name": "Switch app",
            "icon": "swap_horiz",
            "iconTheme": "material-symbols-rounded",
            "type": "submenu",
            "angle": 180,
            "children": [
              {
                "name": "Go to Painter",
                "icon": "texture",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 90,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "focus-window",
                      "appName": "Painter",
                      "windowName": ""
                    }
                  ]
                }
              },
              {
                "name": "Go to Unreal",
                "icon": "unrealengine",
                "iconTheme": "simple-icons-colored",
                "type": "button",
                "angle": 270,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "focus-window",
                      "appName": "UnrealEditor",
                      "windowName": ""
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
            }
          },
          {
            "name": "Save",
            "icon": "save",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 225,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "ControlLeft+KeyS"
                }
              ]
            }
          },
          {
            "name": "Group",
            "icon": "folder",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 270,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "ControlLeft+KeyG"
                }
              ]
            }
          },
          {
            "name": "Duplicate",
            "icon": "content_copy",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 315,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "ControlLeft+KeyD"
                }
              ]
            }
          }
        ],
        "activateWorkflow": {
          "quickSelectKey": "Backspace",
          "actions": [
            {
              "type": "close-menu"
            }
          ]
        }
      },
      "shortcut": "Control+4",
      "shortcutID": "",
      "useFixedPosition": false,
      "fixedMenuPosition": {
        "x": 0.5,
        "y": 0.5
      },
      "anchored": false,
      "hoverMode": false,
      "conditions": {
        "appName": "maya"
      },
      "tags": [
        "3D Work"
      ]
    },
    {
      "root": {
        "name": "Painter",
        "icon": "apps",
        "iconTheme": "material-symbols-rounded",
        "type": "root",
        "children": [
          {
            "name": "Tools",
            "icon": "brush",
            "iconTheme": "material-symbols-rounded",
            "type": "submenu",
            "angle": 0,
            "children": [
              {
                "name": "Paint",
                "icon": "brush",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 0,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Digit1"
                    }
                  ]
                }
              },
              {
                "name": "Eraser",
                "icon": "ink_eraser",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 90,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Digit2"
                    }
                  ]
                }
              },
              {
                "name": "Projection",
                "icon": "photo_camera",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 180,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Digit3"
                    }
                  ]
                }
              },
              {
                "name": "Polygon fill",
                "icon": "format_color_fill",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 270,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Digit4"
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
            }
          },
          {
            "name": "3D + 2D view",
            "icon": "splitscreen",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 45,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "F1"
                }
              ]
            }
          },
          {
            "name": "3D only",
            "icon": "view_in_ar",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 90,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "F2"
                }
              ]
            }
          },
          {
            "name": "Material view",
            "icon": "palette",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 135,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "KeyM"
                }
              ]
            }
          },
          {
            "name": "Switch app",
            "icon": "swap_horiz",
            "iconTheme": "material-symbols-rounded",
            "type": "submenu",
            "angle": 180,
            "children": [
              {
                "name": "Go to Maya",
                "icon": "autodeskmaya",
                "iconTheme": "simple-icons-colored",
                "type": "button",
                "angle": 90,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "focus-window",
                      "appName": "maya",
                      "windowName": ""
                    }
                  ]
                }
              },
              {
                "name": "Go to Unreal",
                "icon": "unrealengine",
                "iconTheme": "simple-icons-colored",
                "type": "button",
                "angle": 270,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "focus-window",
                      "appName": "UnrealEditor",
                      "windowName": ""
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
            }
          },
          {
            "name": "Save",
            "icon": "save",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 225,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "ControlLeft+KeyS"
                }
              ]
            }
          },
          {
            "name": "Export textures",
            "icon": "file_export",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 270,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "ControlLeft+ShiftLeft+KeyE"
                }
              ]
            }
          },
          {
            "name": "Channel view",
            "icon": "layers",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 315,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "KeyC"
                }
              ]
            }
          }
        ],
        "activateWorkflow": {
          "quickSelectKey": "Backspace",
          "actions": [
            {
              "type": "close-menu"
            }
          ]
        }
      },
      "shortcut": "Control+4",
      "shortcutID": "",
      "useFixedPosition": false,
      "fixedMenuPosition": {
        "x": 0.5,
        "y": 0.5
      },
      "anchored": false,
      "hoverMode": false,
      "conditions": {
        "appName": "Painter"
      },
      "tags": [
        "3D Work"
      ]
    },
    {
      "root": {
        "name": "Unreal",
        "icon": "unrealengine",
        "iconTheme": "simple-icons-colored",
        "type": "root",
        "children": [
          {
            "name": "Play",
            "icon": "play_arrow",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 0,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "AltLeft+KeyP"
                }
              ]
            }
          },
          {
            "name": "Simulate physics",
            "icon": "science",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 45,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "AltLeft+KeyS"
                }
              ]
            }
          },
          {
            "name": "View mode",
            "icon": "visibility",
            "iconTheme": "material-symbols-rounded",
            "type": "submenu",
            "angle": 90,
            "children": [
              {
                "name": "Lit",
                "icon": "light_mode",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 0,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "AltLeft+Digit4"
                    }
                  ]
                }
              },
              {
                "name": "Unlit",
                "icon": "dark_mode",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 120,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "AltLeft+Digit3"
                    }
                  ]
                }
              },
              {
                "name": "Wireframe",
                "icon": "grid_on",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 240,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "AltLeft+Digit2"
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
            }
          },
          {
            "name": "Physics debug",
            "icon": "bug_report",
            "iconTheme": "material-symbols-rounded",
            "type": "submenu",
            "angle": 135,
            "children": [
              {
                "name": "Show collision",
                "icon": "select_all",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 0,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "set-clipboard",
                      "text": "show collision"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Backquote"
                    },
                    {
                      "type": "delay",
                      "duration": 0.2
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyV"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Enter"
                    }
                  ]
                }
              },
              {
                "name": "FPS",
                "icon": "speed",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 120,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "set-clipboard",
                      "text": "stat fps"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Backquote"
                    },
                    {
                      "type": "delay",
                      "duration": 0.2
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyV"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Enter"
                    }
                  ]
                }
              },
              {
                "name": "Frame timings",
                "icon": "timer",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 240,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "set-clipboard",
                      "text": "stat unit"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Backquote"
                    },
                    {
                      "type": "delay",
                      "duration": 0.2
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyV"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "Enter"
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
            }
          },
          {
            "name": "Switch app",
            "icon": "swap_horiz",
            "iconTheme": "material-symbols-rounded",
            "type": "submenu",
            "angle": 180,
            "children": [
              {
                "name": "Go to Maya",
                "icon": "autodeskmaya",
                "iconTheme": "simple-icons-colored",
                "type": "button",
                "angle": 90,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "focus-window",
                      "appName": "maya",
                      "windowName": ""
                    }
                  ]
                }
              },
              {
                "name": "Go to Painter",
                "icon": "texture",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 270,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "focus-window",
                      "appName": "Painter",
                      "windowName": ""
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
            }
          },
          {
            "name": "Content drawer",
            "icon": "inventory_2",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 225,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "ControlLeft+Space"
                }
              ]
            }
          },
          {
            "name": "Name prefix",
            "icon": "sell",
            "iconTheme": "material-symbols-rounded",
            "type": "submenu",
            "angle": 270,
            "children": [
              {
                "name": "M_ material",
                "icon": "content_paste",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 0,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "set-clipboard",
                      "text": "M_"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyV"
                    }
                  ]
                }
              },
              {
                "name": "MI_ instance",
                "icon": "content_paste",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 45,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "set-clipboard",
                      "text": "MI_"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyV"
                    }
                  ]
                }
              },
              {
                "name": "MF_ function",
                "icon": "content_paste",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 90,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "set-clipboard",
                      "text": "MF_"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyV"
                    }
                  ]
                }
              },
              {
                "name": "T_ texture",
                "icon": "content_paste",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 135,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "set-clipboard",
                      "text": "T_"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyV"
                    }
                  ]
                }
              },
              {
                "name": "SM_ static mesh",
                "icon": "content_paste",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 180,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "set-clipboard",
                      "text": "SM_"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyV"
                    }
                  ]
                }
              },
              {
                "name": "SK_ skeletal",
                "icon": "content_paste",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 225,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "set-clipboard",
                      "text": "SK_"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyV"
                    }
                  ]
                }
              },
              {
                "name": "PHYS_ physics",
                "icon": "content_paste",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 270,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "set-clipboard",
                      "text": "PHYS_"
                    },
                    {
                      "type": "simulate-hotkey",
                      "hotkey": "ControlLeft+KeyV"
                    }
                  ]
                }
              },
              {
                "name": "GC_ geo collection",
                "icon": "content_paste",
                "iconTheme": "material-symbols-rounded",
                "type": "button",
                "angle": 315,
                "selectWorkflow": {
                  "actions": [
                    {
                      "type": "close-menu"
                    },
                    {
                      "type": "set-clipboard",
                      "text": "GC_"
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
            }
          },
          {
            "name": "Save all",
            "icon": "save",
            "iconTheme": "material-symbols-rounded",
            "type": "button",
            "angle": 315,
            "selectWorkflow": {
              "actions": [
                {
                  "type": "close-menu"
                },
                {
                  "type": "simulate-hotkey",
                  "hotkey": "ControlLeft+ShiftLeft+KeyS"
                }
              ]
            }
          }
        ],
        "activateWorkflow": {
          "quickSelectKey": "Backspace",
          "actions": [
            {
              "type": "close-menu"
            }
          ]
        }
      },
      "shortcut": "Control+4",
      "shortcutID": "",
      "useFixedPosition": false,
      "fixedMenuPosition": {
        "x": 0.5,
        "y": 0.5
      },
      "anchored": false,
      "hoverMode": false,
      "conditions": {
        "appName": "UnrealEditor"
      },
      "tags": [
        "3D Work"
      ]
    }
  ]
}
KANDO_EOF
cat > 'kando-profile.md' <<'KANDO_EOF'
# Kando profile

## Anchors (never move)
- BLESSED root: Games and more Up (0), Media Up-right (45), Google Chrome Right (90), File Explorer Down (180), Settings Down-left (225), Creativity Left (270). A week of muscle memory, keep every one.
- Work menus: Save Down-left (225) and Switch app Down (180) in every app.

## Naming voice
- Plain app names, no emojis.
KANDO_EOF
