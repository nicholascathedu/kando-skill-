"""Tests for the "menu doesn't open" notes in navigation.md. Run from the repo root: python -m unittest discover -s tests"""

import os
import re
import unittest

from test_scripts import SCRIPTS  # also puts scripts/ on sys.path

REFS = os.path.join(SCRIPTS, "..", "references")


def read(name):
    with open(os.path.join(REFS, name), encoding="utf-8") as f:
        return f.read()


class MenuDoesNotOpenTest(unittest.TestCase):
    def setUp(self):
        nav = read("navigation.md")
        start = nav.index("## When the menu sometimes doesn't open")
        self.section = nav[start:nav.index("\n## ", start + 1)]
        self.nav = nav
        self.settings = read("settings.md")

    def test_settings_it_names_are_documented_with_the_same_default(self):
        defaults = {"sameShortcutBehavior": "nothing", "hideOnFocusOut": "true"}
        for key, default in defaults.items():
            self.assertIn(key, self.section)
            row = re.search(rf"\| `{key}` \| (\S+) \|", self.settings)
            self.assertIsNotNone(row, key)
            self.assertEqual(row.group(1), default, key)

    def test_re_open_is_a_documented_value(self):
        self.assertIn('"re-open"', self.section)
        self.assertRegex(self.settings, r"`sameShortcutBehavior`.*re-open")

    def test_cli_flags_it_uses_are_listed(self):
        cli = next(line for line in self.nav.splitlines() if line.startswith("- **CLI**"))
        for flag in ("--menu", "--close-menu"):
            self.assertIn(flag, self.section)
            self.assertIn(flag, cli)

    def test_mouse_button_script_it_names_exists(self):
        self.assertIn("kando-mouse-buttons.ps1", self.section)
        self.assertTrue(os.path.isfile(os.path.join(SCRIPTS, "windows", "kando-mouse-buttons.ps1")))


if __name__ == "__main__":
    unittest.main()
