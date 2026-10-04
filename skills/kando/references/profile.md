# The Kando profile: remembering the person

A pie menu only gets fast when nothing moves. The same is true of help with it. If every
session starts from zero, Claude suggests a layout that undoes last week's habits, picks
colors the person already turned down, and names things in a voice that isn't theirs.

The profile fixes that. It is one short Markdown file that sits next to the menus and
holds what Claude has learned about this person's setup and taste. It starts as a draft
from their files and grows a little with each change they accept.

## Contents
1. Where it lives
2. What goes in it
3. The loop
4. How to use it while working
5. What never goes in it

## 1. Where it lives

Save it as `kando-profile.md` in Kando's config folder, next to `menus.json`:

| OS | File |
|---|---|
| Windows | `%APPDATA%\kando\kando-profile.md` |
| macOS | `~/Library/Application Support/kando/kando-profile.md` |
| Linux | `~/.config/kando/kando-profile.md` (Flatpak: `~/.var/app/menu.kando.Kando/config/kando/`) |

Kando ignores files it doesn't know, so the profile is safe there. It travels with the
config when the person backs it up or moves to a new PC.

If Claude can't reach their disk, the person can keep the file anywhere and paste it in at
the start of a session.

## 2. What goes in it

Two kinds of things.

**Facts from the files.** `scripts/kando_profile.py` writes these:

- Which shortcut opens which menu, under which conditions, and whether a key has a fallback.
- The top ring of each menu: direction and item, using Kando's real placement, so auto-placed
  items show where they really land.
- Anchors: items with the same name in the same direction in two or more menus. These are
  gestures the hand already knows.
- Drift: items with the same name in different directions. Each one is a gesture learned twice.
- The apps the menus touch (per-app conditions, launched programs, sites, app links). Only
  program names, never paths.
- From `config.json`: menu theme, dark theme, color overrides, and selection settings such
  as marking mode, turbo mode, stroke length and fade times. Only keys that are in the file.

**Things only the person can tell you.** The script leaves these as headings:

- **Taste and voice.** Palette words ("deep violet glass, soft glow, no neon green"),
  naming style (short verbs? Title Case? playful?), icon style (filled or outlined, brand
  icons or not).
- **Workflows I care about.** What they actually do day to day, in their words.
  "Retopo in Maya, then bake in Painter." "Stream setup on Fridays."
- **Things I said no to.** Ideas they turned down, with a few words on why if they gave one.

Keep the whole file short. One screen is a good size. Cut what no longer matters.

## 3. The loop

1. **At the start of any Kando task**, look for `kando-profile.md` next to `menus.json` and
   read it if it exists.
2. **If there is none**, offer to make one the first time it would help. Run:

   ```
   python scripts/kando_profile.py menus.json --config config.json
   ```

   Show the person the draft. Ask a few short questions for the human sections, then ask
   before saving it. Use `--out kando-profile.md` to write it; the script won't replace an
   existing file unless you pass `--force`.
3. **After each change the person accepts**, update the profile. Add new anchors and apps,
   a palette word they used, a workflow they mentioned, an idea they turned down. Show the
   few lines you plan to change and ask before writing. Rerunning the script is fine for the
   facts, but merge by hand so their own notes stay.
4. **When the person corrects you**, write the correction down. That is the most useful
   line in the file.

## 4. How to use it while working

- **Keep anchors fixed.** Never move an anchor to make room for something new. Put the new
  item somewhere else, or ask.
- **Fix drift only with consent.** Point it out once, suggest the direction most menus
  already use, and let them decide. Some drift is on purpose.
- **Reuse their voice.** Name new items the way they name items. Match their capitals,
  length and tone.
- **Reuse their palette.** For themes and color overrides, start from their palette words
  and current colors. Don't swap in your own taste.
- **Don't re-suggest what they said no to.** If a rejected idea really seems right now,
  say why in one line and drop it if they still say no.
- **Build on their workflows.** When they ask for something new, check the workflows
  section first. The best menu items often come from a step they repeat there.

## 5. What never goes in it

- Passwords, tokens, API keys or anything secret.
- Account numbers, friend codes, phone numbers or other long IDs.
- Email addresses, real names of other people, user names from folder paths.
- Full file paths. Write the program name ("Blender"), not where it lives.

The script already strips paths, emails and long numbers from what it writes. Apply the
same rule to anything you add by hand. If a note can't be written without one of these,
leave it out.
