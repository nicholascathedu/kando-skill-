#!/usr/bin/env python3
"""Compare what the checker knows with Kando's own settings schemas.

    python .github/scripts/kando_drift.py path/to/kando-checkout

Prints what Kando has that the checker doesn't (or the other way round) and exits 1 when
anything differs, so the weekly workflow (.github/workflows/kando-drift.yml) can open an
issue. It reads the zod schemas in src/common/settings-schemata as text, so a change in how
Kando writes them can also show up as drift: then this script needs updating, not the checker.
Standard library only.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "skills", "kando", "scripts"))

import kando_check  # noqa: E402

SCHEMAS = os.path.join("src", "common", "settings-schemata")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def newest(folder, prefix):
    """The highest-numbered <prefix>-vN.ts, as (N, path)."""
    found = [(int(m.group(1)), os.path.join(folder, n)) for n in os.listdir(folder)
             for m in [re.fullmatch(re.escape(prefix) + r"-v(\d+)\.ts", n)] if m]
    return max(found) if found else (0, None)


def keys(source, schema):
    """Field names of `export const <schema> = ...({ ... })`, two spaces deep."""
    body = re.split(r"(?:export )?const %s = " % schema, source, maxsplit=1)[1].split("\n});", 1)[0]
    return set(re.findall(r"^  (?:get )?(\w+)(?::|\(\))", body, re.M))


def compare(what, theirs, ours):
    return ([f"New in Kando, unknown to the checker: {what} `{k}`" for k in sorted(theirs - ours)] +
            [f"Known to the checker, gone from Kando: {what} `{k}`" for k in sorted(ours - theirs)])


def drift(kando):
    folder = os.path.join(kando, SCHEMAS)
    lines = []
    general_v, general = newest(folder, "general-settings")
    menus_v, menus = newest(folder, "menu-settings")
    if (general_v, menus_v) != (1, 2):
        lines.append(f"New schema version: general-settings-v{general_v}, menu-settings-v{menus_v} "
                     "(the checker knows v1 and v2). Check what changed before anything else.")
        return lines
    lines += compare("config.json setting", keys(read(general), "GENERAL_SETTINGS_SCHEMA_V1"),
                     kando_check.CONFIG_KEYS)
    src = read(menus)
    lines += compare("menu field", keys(src, "MENU_SCHEMA_V2"), kando_check.MENU_KEYS)
    actions = dict(re.findall(r"const (\w+_ACTION_SCHEMA_V2) = z\.object\(\{\s*type: z\.literal\('([\w-]+)'\)",
                              src))
    lines += compare("action type", set(actions.values()), set(kando_check.ACTION_FIELDS))
    for schema, kind in sorted(actions.items(), key=lambda kv: kv[1]):
        if kind in kando_check.ACTION_FIELDS:
            lines += compare(f"{kind} field", keys(src, schema) - {"type"},
                             set(kando_check.ACTION_FIELDS[kind]))
    base = keys(src, "BASE_MENU_ITEM_SCHEMA_V2")
    for kind in ("root", "button", "submenu"):
        theirs = base | keys(src, f"{kind.upper()}_MENU_ITEM_SCHEMA_V2")
        lines += compare(f"{kind} item field", theirs, kando_check.ITEM_KEYS[kind])
    return lines


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        sys.exit(__doc__)
    try:
        lines = drift(argv[0])
    except (OSError, IndexError, TypeError, ValueError) as e:
        print(f"Couldn't read Kando's schemas ({e!r}). Kando may have moved or reshaped them; "
              "update this script.", file=sys.stderr)
        return 2
    for line in lines:
        print("- " + line)
    if not lines:
        print("The checker matches Kando's schemas.")
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main())
