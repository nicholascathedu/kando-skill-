"""Tests for kando_mode.py. Run from the repo root: python -m unittest discover -s tests"""

import json
import os
import tempfile
import unittest
from unittest import mock

from test_scripts import SCRIPTS  # noqa: F401 (puts scripts/ on sys.path)
import kando_mode  # noqa: E402


def folder_with(modes, cfg=None):
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "config.json"), "w") as f:
        json.dump(cfg or {"version": "3.0.0"}, f)
    with open(os.path.join(d, kando_mode.MODES), "w") as f:
        json.dump(modes, f)
    return d


class ModeTest(unittest.TestCase):
    def test_problems_name_each_bad_step(self):
        d = folder_with({})
        self.assertEqual(kando_mode.problems({"kando": "speed", "windows": "dark",
                                              "apps": [["maya.exe", "C:\\maya.exe"]],
                                              "layout": ["maya=left"]}, d), [])
        bad = kando_mode.problems({"wallpapr": "x.png", "windows": "purple", "kando": "fast",
                                   "apps": ["maya.exe"], "layout": ["maya"]}, d)
        self.assertEqual(len(bad), 5)
        self.assertTrue(any("wallpapr" in b for b in bad))
        self.assertTrue(any("fast" in b for b in bad))

    def test_kando_step_uses_presets_and_settings(self):
        d = folder_with({})
        done, failed = kando_mode.run("work", {"kando": "speed"}, d)
        self.assertEqual((done, failed), (["Kando preset"], []))
        with open(os.path.join(d, "config.json")) as f:
            self.assertEqual(json.load(f)["fadeOutDuration"], 70)
        kando_mode.run("play", {"kando": {"fadeOutDuration": 150}}, d)
        with open(os.path.join(d, "config.json")) as f:
            self.assertEqual(json.load(f)["fadeOutDuration"], 150)
        backups = os.listdir(os.path.join(d, "claude-backups"))
        self.assertTrue(any("before-mode-play" in b for b in backups))

    def test_refused_settings_fail_the_step_not_the_mode(self):
        d = folder_with({})
        done, failed = kando_mode.run("x", {"kando": {"sameShortcutBehavior": "explode"}}, d)
        self.assertEqual(done, [])
        self.assertEqual(len(failed), 1)

    def test_layout_waits_only_after_starting_an_app(self):
        if os.name != "nt":
            self.skipTest("apps and layout are Windows only")
        d = folder_with({})
        with mock.patch.object(kando_mode, "start_apps", return_value=["maya.exe"]), \
                mock.patch.object(kando_mode, "place_windows", return_value=[]) as place:
            kando_mode.run("work", {"apps": [["maya.exe", "m"]], "layout": ["maya=left"]}, d)
        place.assert_called_once_with(["maya=left"], kando_mode.WAIT)

    def test_place_windows_gives_up_after_the_wait(self):
        with mock.patch.object(kando_mode.kando_windows, "open_windows", return_value=[]), \
                mock.patch.object(kando_mode.time, "sleep") as sleep, \
                mock.patch.object(kando_mode.time, "monotonic", side_effect=[0, 0, 1, 2]):
            self.assertEqual(kando_mode.place_windows(["maya=left"], 1.5), ["maya"])
        self.assertEqual(sleep.call_count, 2)

    def test_place_windows_moves_what_it_finds(self):
        win = [(7, "maya.exe", "crate.mb - Autodesk Maya")]
        with mock.patch.object(kando_mode.kando_windows, "open_windows", return_value=win), \
                mock.patch.object(kando_mode.kando_windows, "work_area", return_value=(0, 0, 2000, 1000)), \
                mock.patch.object(kando_mode.kando_windows, "move") as move:
            self.assertEqual(kando_mode.place_windows(["maya=left", "PureRef=right"], 0), ["PureRef"])
        move.assert_called_once_with(7, (0, 0, 1000, 1000))

    def test_cli_show_and_list(self):
        d = folder_with({"work": {"kando": "speed", "layout": ["maya=left"]}})
        with mock.patch("sys.stdout") as out:
            self.assertEqual(kando_mode.main(["show", "work", "--dir", d]), 0)
            self.assertEqual(kando_mode.main(["list", "--dir", d]), 0)
        printed = "".join(c.args[0] for c in out.write.call_args_list)
        self.assertIn("Kando preset: speed", printed)
        with open(os.path.join(d, "config.json")) as f:
            self.assertNotIn("fadeOutDuration", json.load(f))  # show changes nothing
        with self.assertRaises(SystemExit):
            kando_mode.main(["nope", "--dir", d])


if __name__ == "__main__":
    unittest.main()
