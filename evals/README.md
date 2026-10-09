# Evals: does the skill actually help?

Twelve real Kando tasks. Claude Code's eval runner does each one twice, once with the skill
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
| `maya-work-menu` | A 19-action Maya menu from scratch | Submenus of 12 or fewer, fixed angles in order, a clear way back, key codes |
| `ignored-angle` | "Steam is set to 0 but shows up top left" | Knows Kando drops an angle smaller than the one before it, reorders the items |
| `mouse-button-turbo` | "Open it with my side mouse button, no clicking" | A helper sends an unused combo like Ctrl+F13, turbo mode holds the modifier |
| `theme-from-words` | "Smoke and amethyst" on the Default theme | Color overrides under the theme's id, only names the theme has, dark glass, violet hover |

The files each case starts with live in its `fixture.sh`. Most checks are written as plain
pass or fail rules, so a score can be traced back to the exact rule that failed.

## Running it

You need Claude Code 2.1.269 or later. Every run is a full Claude session on your own account,
so one round (12 cases, with and without, one run each) is 24 sessions plus the grading.

```bash
claude plugin eval . --scaffold --allow-tools Bash Write Edit
```

`--scaffold` lets each case write its starting files, and `--allow-tools` lets Claude edit them
and run the skill's Python scripts. On Linux the Bash sandbox needs `bubblewrap` and `socat`.
For steadier numbers, add `--runs 3` (that's three times the usage).

The report opens as an HTML page with every prompt, every rule and why it passed or failed.
Results land in `evals/results/`, which git ignores.

## Full benchmark (2026-10-09)

All twelve cases, three runs each, with and without the skill. Claude Code 2.1.296, default
model and judge, $6.83 in total. A cell is the share of runs that passed, partial credit
included.

| Case | With the skill | Without |
|---|---|---|
| `blender-menu` | 3/3 | 0/3 |
| `maya-work-menu` | 3/3 | 1/3 |
| `theme-preset` | 3/3 | 1.4/3 |
| `respect-profile` | 3/3 | 2.25/3 |
| `theme-from-words` | 2/3 | 0/3 |
| `learn-speed` | 2/3 | 0/3 |
| `fix-broken-file` | 3/3 | 3/3 |
| `ignored-angle` | 3/3 | 3/3 |
| `per-app-key` | 3/3 | 3/3 |
| `share-safely` | 3/3 | 3/3 |
| `no-name-trigger` | 3/3 | 3/3 |
| `mouse-button-turbo` | 1/3 | 2/3 |
| **Mean score** | **0.89** | **0.60** |

Honest reading:

- The skill wins where Kando's own rules decide the outcome: placing items on the compass,
  submenus and the way back, where theme presets live, which color names a theme has, and
  reading the saved profile. Plain Claude got the 19-action Maya menu right once in three.
- On general know-how (fixing JSON, scrubbing personal data, the ignored-angle fix) plain
  Claude does just as well. Those cases check the skill doesn't make things worse.
- `mouse-button-turbo` is the one case where the skill scored lower. The skill's failed
  answers were correct and more careful (they warn that most mouse apps send a quick tap,
  which ends turbo mode, and give an AutoHotkey script that holds Ctrl), but the default
  judge split its votes on them. Cases graded on a written explanation are noisy with the
  default judge; `--judge-model sonnet` is the next thing to try.
- `no-name-trigger` timed out in its first attempt and passed on a clean re-run.

## First results (2026-10-09)

The first eight cases, one run each, Claude Code 2.1.296, default model, $1.43 in total.

| Case | With the skill | Without |
|---|---|---|
| `blender-menu` | 1.00 | 0.00 |
| `theme-preset` | 1.00 | 0.20 |
| `respect-profile` | 1.00 | 0.75 |
| `fix-broken-file` | 1.00 | 1.00 |
| `share-safely` | 1.00 | 1.00 |
| `no-name-trigger` | 1.00 | 1.00 |
| `per-app-key` | 0.40 | 0.40 |
| `learn-speed` | 0.00 | 0.00 |
| **Mean** | **0.80** | **0.54** |

What it showed:

- The skill's real edge is Kando-specific layout and theme knowledge. Without it, Claude listed
  the Blender Shading submenu at 180° after an item at 288° (Kando ignores that angle), put
  Wireframe on the way back out of it, and didn't write the Deep Sea preset where Kando looks.
- Plain Claude already handles JSON fixes, privacy scrubbing and recognising a pie menu, so
  those cases mostly guard against the skill making things worse.
- `per-app-key` failed in both arms. With the skill, Claude added a fallback menu, which
  doesn't give Chrome its Ctrl+4 back (it did offer the right fix as an alternative). The
  checker's tip pointed it that way, so the tip and SKILL.md now say to move the shortcut
  when another app needs the key.
- `learn-speed` failed in both arms on a rule that was stricter than Kando's own docs (it
  required the "pause or sharp turn" detail). The rule was loosened after this run, so the
  next run will show whether that was the only reason.

One run per case is a smoke test, not a final score. Run `--runs 3` before quoting numbers.

## Harder cases, first run (2026-10-09)

The four cases tagged `hard`, one run each, $0.80.

| Case | With the skill | Without |
|---|---|---|
| `maya-work-menu` | 1.00 | 0.00 |
| `theme-from-words` | 1.00 | 0.00 |
| `mouse-button-turbo` | 1.00 | 1.00 |
| `ignored-angle` | 1.00 | 1.00 |

`ignored-angle` first scored 0.40 in both arms although both files were right: the LLM judge
got the angle order wrong. That rule is now an exact pattern match, and the table shows the
re-scored result. Without the skill, the Maya menu and the color overrides were wrong in
Kando-specific ways, which is where the skill earns its place.
