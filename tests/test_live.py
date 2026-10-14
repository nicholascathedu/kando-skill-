"""Tests for kando_live.py. Run from the repo root: python -m unittest discover -s tests"""

import os
import tempfile
import unittest

from test_scripts import SCRIPTS  # noqa: F401 (puts scripts/ on sys.path)
import kando_check  # noqa: E402
import kando_live  # noqa: E402


class LiveMenuTest(unittest.TestCase):
    def test_maya_recent_reads_prefs_newest_first(self):
        with tempfile.TemporaryDirectory() as home:
            scenes = []
            for n in ("a.mb", "b.ma", "c.mb"):
                scenes.append(os.path.join(home, n).replace("\\", "/"))
                open(scenes[-1], "w").close()
            prefs = os.path.join(home, "Documents", "maya", "2026", "prefs")
            os.makedirs(prefs)
            with open(os.path.join(prefs, "userPrefs.mel"), "w") as f:
                for p in scenes + [home + "/gone.mb"]:
                    f.write(f'-sva "RecentFilesList" "{p}"\n')
            self.assertEqual([os.path.basename(p) for p in kando_live.maya_recent(home)],
                             ["c.mb", "b.ma", "a.mb"])

    def test_show_opens_the_picked_file(self):
        sent, opened = [], []

        class FakeSocket:
            replies = [{"type": "menu-interaction", "interaction": "hoverButton", "path": [0]},
                       {"type": "menu-interaction", "interaction": "selectButton", "path": [1]}]
            def send(self, m): sent.append(m)
            def receive(self): return self.replies.pop(0)
            def close(self): pass

        real, kando_live.open_file = kando_live.open_file, opened.append
        try:
            picked = kando_live.show("Recent", ["/x/one.mb", "/x/two.mb"], FakeSocket)
        finally:
            kando_live.open_file = real
        self.assertEqual((picked, opened), ("/x/two.mb", ["/x/two.mb"]))
        menu = sent[0]["menu"]
        self.assertEqual([c["name"] for c in menu["children"]], ["one", "two"])
        rep = kando_check.Report()
        kando_check.check_menus({"version": "3.0.0", "menus": [{"root": menu, "shortcut": ""}]}, rep)
        self.assertEqual(rep.count("ERROR"), 0)


if __name__ == "__main__":
    unittest.main()
