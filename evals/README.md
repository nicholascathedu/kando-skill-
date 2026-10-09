# Evals: does the skill actually help?

Eight real Kando tasks. Claude Code's eval runner does each one twice, once with the skill
and once without it, then scores both. The difference between the two is what the skill is worth.

| Case | What it asks | What it checks |
|---|---|---|
| `fix-broken-file` | "Kando stopped picking up my changes, and Save never worked" | Valid JSON again, `Ctrl+S` turned into key codes, nothing else moved |
| `per-app-key` | "Ctrl+4 works in Maya but does nothing in Chrome" | Explains Kando takes the key from every app, moves the shortcut, keeps the Maya menu |
| `share-safely` | "Make a copy I can post on Reddit" | No user folder, email or Discord ID left, items still work |
| `respect-profile` | "Add Blender, Spotify and OBS" | Reads `kando-profile.md`, keeps the locked directions, keeps Spotify out of the root |
| `blender-menu` | "A Blender work menu with a Shading submenu" | Fixed angles, nothing on the way back, key codes, a shortcut Blender doesn't use |
| `theme-preset` | "A teal Deep Sea preset for my theme" | Right folder, right file shape, only colors the theme has, theme left alone |
| `learn-speed` | "How do I get fast without looking?" | Marking and turbo mode explained correctly, no made-up features |
| `no-name-trigger` | Asks for a browser ring without saying "Kando" | The skill still kicks in, writes Kando 3 items, not old 2.x ones |

The files each case starts with live in its `fixture.sh`. Most checks are written as plain
pass or fail rules, so a score can be traced back to the exact rule that failed.

## Running it

You need Claude Code 2.1.269 or later. Every run is a full Claude session on your own account,
so one round (8 cases, with and without, one run each) is 16 sessions plus the grading.

```bash
claude plugin eval . --scaffold --allow-tools Bash Write Edit
```

`--scaffold` lets each case write its starting files, and `--allow-tools` lets Claude edit them
and run the skill's Python scripts. On Linux the Bash sandbox needs `bubblewrap` and `socat`.
For steadier numbers, add `--runs 3` (that's three times the usage).

The report opens as an HTML page with every prompt, every rule and why it passed or failed.
Results land in `evals/results/`, which git ignores.
