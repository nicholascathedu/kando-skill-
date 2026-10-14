"""Tests for kando_overlay.py. Run from the repo root: python -m unittest discover -s tests"""

import copy
import json
import os
import unittest

from test_scripts import EXAMPLES, report  # also puts scripts/ on sys.path
import kando_overlay  # noqa: E402


def find(menu_root, *path):
    node = menu_root
    for name in path:
        node = next(c for c in node["children"] if c["name"] == name)
    return node


class OverlayTest(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(EXAMPLES, "3d-work-menus.json"), encoding="utf-8") as f:
            self.base = json.load(f)
        self.maya = next(m for m in self.base["menus"] if m["root"]["name"] == "Maya")

    def tweak(self, data):
        """What a user might do in the editor: rename one item, drop one, add one, rebind."""
        mine = copy.deepcopy(data)
        maya = next(m for m in mine["menus"] if m["root"]["name"] == "Maya")
        kids = maya["root"]["children"]
        kids[0]["icon"] = "star"
        dropped = kids.pop()["name"]
        maya["shortcut"] = "Control+F16"
        sub = next(c for c in kids if c["type"] == "submenu")
        sub["children"].append({"name": "My script", "icon": "code", "iconTheme": "x",
                                "type": "button", "angle": 0 if not any(c.get("angle") == 0 for c in sub["children"]) else 1,
                                "selectWorkflow": {"actions": [{"type": "close-menu"}]}})
        if all("angle" in c for c in sub["children"]):
            sub["children"].sort(key=lambda c: c["angle"])  # the editor keeps them in order
        return mine, dropped, kids[0]["name"], sub["name"]

    def test_round_trip_reproduces_the_tweaked_menus(self):
        mine, *_ = self.tweak(self.base)
        overlay = kando_overlay.extract(self.base, mine)
        self.assertEqual([m["root"]["name"] for m in overlay["menus"]], ["Maya"])
        self.assertEqual(kando_overlay.apply(self.base, overlay), mine)

    def test_tweaks_survive_a_new_base(self):
        mine, dropped, first, sub = self.tweak(self.base)
        overlay = kando_overlay.extract(self.base, mine)
        new_base = copy.deepcopy(self.base)  # the skill ships an update to the Maya menu
        new_maya = next(m for m in new_base["menus"] if m["root"]["name"] == "Maya")
        new_maya["root"]["children"][1]["icon"] = "bolt"
        merged = kando_overlay.apply(new_base, overlay)
        maya = next(m for m in merged["menus"] if m["root"]["name"] == "Maya")
        names = [c["name"] for c in maya["root"]["children"]]
        self.assertNotIn(dropped, names)
        self.assertEqual(find(maya["root"], first)["icon"], "star")
        self.assertEqual(maya["root"]["children"][1]["icon"], "bolt")  # the update stays
        self.assertIn("My script", [c["name"] for c in find(maya["root"], sub)["children"]])
        self.assertEqual(maya["shortcut"], "Control+F16")
        self.assertEqual(report(merged).count("ERROR"), 0)


if __name__ == "__main__":
    unittest.main()
