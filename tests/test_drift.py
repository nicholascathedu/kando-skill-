"""Tests for the weekly Kando update check. Run from the repo root: python -m unittest discover -s tests"""

import os
import sys
import tempfile
import unittest

from test_scripts import SCRIPTS  # noqa: F401 (puts scripts/ on sys.path)
import kando_check  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".github", "scripts"))
import kando_drift  # noqa: E402


def fake_kando(folder, extra_action=None):
    """A Kando checkout whose schemas match the checker, written the way Kando writes them."""
    schemas = os.path.join(folder, "src", "common", "settings-schemata")
    os.makedirs(schemas)

    def obj(name, fields, export=True, head="z.object({"):
        lines = "".join(f"  {f}: z.string(),\n" for f in sorted(fields))
        return f"{'export ' if export else ''}const {name} = {head}\n{lines}}});\n\n"

    general = obj("GENERAL_SETTINGS_SCHEMA_V1", kando_check.CONFIG_KEYS)
    menus = ""
    actions = dict(kando_check.ACTION_FIELDS, **({extra_action: {}} if extra_action else {}))
    for kind, fields in actions.items():
        name = kind.upper().replace("-", "_") + "_ACTION_SCHEMA_V2"
        menus += f"export const {name} = z.object({{\n  type: z.literal('{kind}'),\n" + \
                 "".join(f"  {f}: z.string(),\n" for f in fields) + "});\n\n"
    menus += obj("BASE_MENU_ITEM_SCHEMA_V2", {"name", "icon", "iconTheme"}, export=False)
    for kind, fields in kando_check.ITEM_KEYS.items():
        rest = fields - {"name", "icon", "iconTheme", "type", "children"}
        menus += (f"export const {kind.upper()}_MENU_ITEM_SCHEMA_V2 = BASE_MENU_ITEM_SCHEMA_V2.extend({{\n"
                  f"  type: z.literal('{kind}'),\n" + "".join(f"  {f}: W.optional(),\n" for f in rest) +
                  ("  get children() {\n    return z.array(X);\n  },\n" if "children" in fields else "") +
                  "});\n\n")
    menus += obj("MENU_SCHEMA_V2", kando_check.MENU_KEYS)
    for name, text in (("general-settings-v1.ts", general), ("menu-settings-v1.ts", ""),
                       ("menu-settings-v2.ts", menus)):
        with open(os.path.join(schemas, name), "w", encoding="utf-8") as f:
            f.write(text)
    return schemas


class DriftTest(unittest.TestCase):
    def test_matching_schemas_report_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            fake_kando(d)
            self.assertEqual(kando_drift.drift(d), [])

    def test_new_action_and_new_version_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            fake_kando(d, extra_action="run-script")
            self.assertEqual(kando_drift.drift(d),
                             ["New in Kando, unknown to the checker: action type `run-script`"])
        with tempfile.TemporaryDirectory() as d:
            schemas = fake_kando(d)
            open(os.path.join(schemas, "menu-settings-v3.ts"), "w").close()
            self.assertIn("menu-settings-v3", kando_drift.drift(d)[0])
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(kando_drift.main([d]), 2)  # no schemas at all: a script problem


if __name__ == "__main__":
    unittest.main()
