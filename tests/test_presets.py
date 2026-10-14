"""Tests for kando_presets.py. Run from the repo root: python -m unittest discover -s tests"""

import json
import os
import tempfile
import unittest

from test_scripts import SCRIPTS  # noqa: F401 (puts scripts/ on sys.path)
import kando_presets  # noqa: E402


def write(folder, cfg):
    with open(os.path.join(folder, "config.json"), "w") as f:
        json.dump(cfg, f)


def read(folder):
    with open(os.path.join(folder, "config.json")) as f:
        return json.load(f)


class PresetTest(unittest.TestCase):
    def test_apply_touches_only_preset_settings_and_backs_up(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, {"version": "3.0.0", "menuTheme": "amethyst-arsenal", "fadeOutDuration": 100})
            cfg = os.path.join(d, "config.json")
            diff, backup = kando_presets.apply(d, "speed", cfg)
            now = read(d)
            self.assertEqual(now["menuTheme"], "amethyst-arsenal")
            self.assertEqual(now["fadeOutDuration"], 70)
            self.assertIn(("fadeOutDuration", 100, 70), diff)
            with open(backup) as f:
                self.assertEqual(json.load(f)["fadeOutDuration"], 100)
            self.assertEqual(kando_presets.apply(d, "speed", cfg), ([], None))  # already on it
            kando_presets.apply(d, "kando", cfg)
            self.assertEqual(read(d)["fixedStrokeLength"], 0)
            self.assertEqual(read(d)["menuTheme"], "amethyst-arsenal")

    def test_bad_own_preset_is_refused_before_writing(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, {"version": "3.0.0"})
            with open(os.path.join(d, "claude-presets.json"), "w") as f:
                json.dump({"broken": {"sameShortcutBehavior": "explode"}}, f)
            with self.assertRaises(SystemExit):
                kando_presets.apply(d, "broken", os.path.join(d, "config.json"))
            self.assertEqual(read(d), {"version": "3.0.0"})

    def test_save_keeps_current_values(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, {"version": "3.0.0", "gesturePauseTimeout": 180})
            saved = kando_presets.save(d, "mine", os.path.join(d, "config.json"))
            self.assertEqual(saved["gesturePauseTimeout"], 180)
            self.assertEqual(saved["fadeInDuration"], 75)  # missing = Kando's default
            self.assertIn("mine", kando_presets.all_presets(d))
            with self.assertRaises(SystemExit):
                kando_presets.save(d, "speed", os.path.join(d, "config.json"))


if __name__ == "__main__":
    unittest.main()
