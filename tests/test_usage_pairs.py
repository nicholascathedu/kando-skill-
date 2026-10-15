"""Tests for the used-together hint in kando_usage.py. Run from the repo root: python -m unittest discover -s tests"""

import unittest

from test_scripts import item, menus  # also puts scripts/ on sys.path
import kando_usage  # noqa: E402


def data():
    maya = menus(item("Frame", 0), item("Isolate", 90), item("Save", 180), item("Export", 270),
                 shortcut="Control+4", conditions={"appName": "maya"})
    maya["menus"][0]["root"]["name"] = "Maya"
    desk = menus(item("Browser", 0), item("Discord", 180), shortcut="Control+Space")
    desk["menus"][0]["root"]["name"] = "Desk"
    maya["menus"] += desk["menus"]
    return maya


def pick(app, path, t):
    return [{"t": t, "ev": "openMenu", "path": [], "app": app},
            {"t": t + 300, "ev": "selectButton", "path": path},
            {"t": t + 301, "ev": "closeMenu", "path": []}]


class UsedTogetherTest(unittest.TestCase):
    def test_quick_pairs_are_found_and_slow_ones_are_not(self):
        rows = []
        for i in range(6):
            t = i * 100000
            rows += pick("maya.exe", [2], t)              # Save ...
            rows += pick("maya.exe", [3], t + 4000)       # ... then Export, 4 s later
            rows += pick("chrome.exe", [1], t + 8000)     # ... then Discord from the desktop menu
            rows += pick("maya.exe", [0], t + 60000)      # Frame, a minute later: not a pair
        counts = kando_usage.follow_ups(rows, kando_usage.menu_list(data()))
        self.assertEqual(counts[(("Maya", "Save"), ("Maya", "Export"))], 6)
        self.assertEqual(counts[(("Maya", "Export"), ("Desk", "Discord"))], 6)
        self.assertNotIn((("Desk", "Discord"), ("Maya", "Frame")), counts)
        lines = " ".join(kando_usage.report(rows, data()))
        self.assertIn("Used together: you picked 'Save' then 'Export' within 10 s 6 times. "
                      "Make one item that does both, or put them next to each other in Maya.", lines)
        self.assertIn("or put 'Discord' in Maya too", lines)

    def test_repeats_and_rare_pairs_are_ignored(self):
        rows = []
        for i in range(30):
            rows += pick("maya.exe", [0], i * 2000)        # Frame again and again
        rows += pick("maya.exe", [2], 100000) + pick("maya.exe", [3], 101000)  # once only
        lines = " ".join(kando_usage.report(rows, data()))
        self.assertNotIn("Used together", lines)


if __name__ == "__main__":
    unittest.main()
