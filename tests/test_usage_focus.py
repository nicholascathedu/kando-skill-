"""The usage log names the app you were in, not Kando. Run from the repo root: python -m unittest discover -s tests"""

import unittest

from test_scripts import SCRIPTS  # noqa: F401 (puts scripts/ on sys.path)
import kando_usage  # noqa: E402


class FocusTest(unittest.TestCase):
    def test_kando_taking_focus_keeps_the_app_before_it(self):
        seen = iter(["maya.exe", "Kando.exe", "", "kando.exe", "Adobe Substance 3D Painter.exe", "Kando.exe"])
        focus = kando_usage.FocusTracker(probe=lambda: next(seen))
        self.assertEqual([focus.update() for _ in range(6)],
                         ["maya.exe", "maya.exe", "maya.exe", "maya.exe",
                          "Adobe Substance 3D Painter.exe", "Adobe Substance 3D Painter.exe"])

    def test_nothing_known_yet(self):
        self.assertEqual(kando_usage.FocusTracker(probe=lambda: "Kando.exe").update(), "")


if __name__ == "__main__":
    unittest.main()
