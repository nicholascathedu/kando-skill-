"""Tests for kando_windows.py. Run from the repo root: python -m unittest discover -s tests"""

import os
import unittest

from test_scripts import SCRIPTS  # noqa: F401 (puts scripts/ on sys.path)
import kando_windows  # noqa: E402

WINDOWS = [(1, "Adobe Substance 3D Painter.exe", "crate_v3 - Adobe Substance 3D Painter"),
           (2, "PureRef.exe", "PureRef"), (3, "maya.exe", "Autodesk Maya 2026 - crate.mb")]


class WindowLayoutTest(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(kando_windows.parse("Painter=left"), ("Painter", "", (0, 0, 50, 100)))
        self.assertEqual(kando_windows.parse("maya@crate=0,0,60,100"), ("maya", "crate", (0, 0, 60, 100)))
        for bad in ("Painter", "=left", "Painter=sideways", "Painter=50,0,60,100", "x=0,0,0,100"):
            with self.assertRaises(ValueError, msg=bad):
                kando_windows.parse(bad)

    def test_halves_and_thirds_share_edges(self):
        work = (0, 0, 2561, 1400)  # odd width: rounding must not leave a gap
        left = kando_windows.place(kando_windows.SPOTS["left"], work)
        right = kando_windows.place(kando_windows.SPOTS["right"], work)
        self.assertEqual(left[0] + left[2], right[0])
        self.assertEqual(right[0] + right[2], 2561)
        thirds = [kando_windows.place(kando_windows.SPOTS[k], (100, 40, 1100, 940))
                  for k in ("left-third", "middle-third", "right-third")]
        self.assertEqual([t[0] for t in thirds], [100, 433, 767])
        self.assertEqual(thirds[-1][0] + thirds[-1][2], 1100)
        self.assertEqual(thirds[0], (100, 40, 333, 900))

    def test_pick_uses_kando_matching(self):
        self.assertEqual(kando_windows.pick(WINDOWS, "painter", "")[0], 1)
        self.assertEqual(kando_windows.pick(WINDOWS, "/^pure/i", "")[0], 2)
        self.assertEqual(kando_windows.pick(WINDOWS, "maya", "crate.mb")[0], 3)
        self.assertIsNone(kando_windows.pick(WINDOWS, "/^Pure/", "nope"))
        self.assertIsNone(kando_windows.pick(WINDOWS, "blender", ""))

    @unittest.skipUnless(os.name == "nt", "Windows only")
    def test_lists_windows_and_reads_work_area(self):
        windows = kando_windows.open_windows()
        self.assertIsInstance(windows, list)
        if windows:
            l, t, r, b = kando_windows.work_area(windows[0][0])
            self.assertGreater(r, l)
            self.assertGreater(b, t)


if __name__ == "__main__":
    unittest.main()
