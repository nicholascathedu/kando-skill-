"""Tests for kando_context.py and kando_split.py. Run from the repo root: python -m unittest discover -s tests"""

import json
import os
import unittest

from test_scripts import EXAMPLES, report  # also puts scripts/ on sys.path
import kando_context  # noqa: E402
import kando_split  # noqa: E402


class ContextAndSplitTest(unittest.TestCase):
    def test_path_in_title(self):
        f = kando_context.path_in_title
        self.assertEqual(f("Autodesk Maya 2026: C:\\scenes\\hero rig.mb* - persp"), "C:\\scenes\\hero rig.mb")
        self.assertEqual(f("Maya: /home/me/shots/s01.ma - persp"), "/home/me/shots/s01.ma")
        self.assertIsNone(f("Adobe Substance 3D Painter - hero"))

    def test_split_examples_into_importable_menus(self):
        with open(os.path.join(EXAMPLES, "3d-work-menus.json"), encoding="utf-8") as f:
            data = json.load(f)
        parts = kando_split.split(data)
        self.assertEqual([n for n, _ in parts], ["Maya.json", "Painter.json", "Designer.json", "Unreal.json"])
        for _, exported in parts:
            rep = report(exported)
            self.assertEqual(rep.count("ERROR"), 0)
        dup = {"version": "3.0.0", "menus": [data["menus"][0], data["menus"][0]]}
        self.assertEqual([n for n, _ in kando_split.split(dup)], ["Maya.json", "Maya 2.json"])


if __name__ == "__main__":
    unittest.main()
