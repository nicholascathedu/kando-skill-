"""Tests for kando_launch.py and the checker's second-copy tip. Run from the repo root: python -m unittest discover -s tests"""

import os
import sys
import unittest

from test_scripts import item, menus, messages, report  # also puts scripts/ on sys.path
import kando_check  # noqa: E402
import kando_launch  # noqa: E402

TASKLIST = ('"Adobe Substance 3D Painter.exe","4120","Console","1","812,004 K"\n'
            '"maya.exe","9984","Console","1","2,145,200 K"\n')


class LaunchTest(unittest.TestCase):
    def test_running_matches_whole_names_case_insensitively(self):
        self.assertTrue(kando_launch.running("Maya.exe", TASKLIST))
        self.assertTrue(kando_launch.running("maya", TASKLIST))
        self.assertTrue(kando_launch.running("adobe substance 3d painter.exe", TASKLIST))
        self.assertFalse(kando_launch.running("may.exe", TASKLIST))
        self.assertFalse(kando_launch.running("blender.exe",
                                              "INFO: No tasks are running which match the specified criteria.\n"))

    @unittest.skipUnless(os.name == "nt", "tasklist is Windows only")
    def test_running_sees_this_python(self):
        self.assertTrue(kando_launch.running(os.path.basename(sys.executable)))
        self.assertFalse(kando_launch.running("no-such-app-3f9a.exe"))

    def test_exe_name(self):
        self.assertEqual(kando_check.exe_name('start "" "C:\\Apps\\Adobe Substance 3D Painter.exe"'),
                         "Adobe Substance 3D Painter.exe")
        self.assertEqual(kando_check.exe_name("start blender.exe"), "blender.exe")
        self.assertIsNone(kando_check.exe_name("notes.txt"))

    def test_second_copy_tip(self):
        launch = [{"type": "close-menu"},
                  {"type": "execute-command", "command": 'start "" "C:\\Maya\\bin\\maya.exe"'}]
        tips = messages(report(menus(item("Maya", 0, actions=launch))), "TIP")
        self.assertTrue(any("second copy" in m and '"maya.exe"' in m for m in tips))
        for safe in (launch[:1] + [{"type": "focus-window", "appName": "maya"}] + launch[1:],
                     launch[:1] + [{"type": "execute-command",
                                    "command": 'pythonw kando_launch.py maya.exe "C:\\Maya\\bin\\maya.exe"'}],
                     launch[:1] + [{"type": "execute-command", "command": "explorer.exe C:\\Work"}]):
            tips = messages(report(menus(item("Maya", 0, actions=safe))), "TIP")
            self.assertFalse(any("second copy" in m for m in tips), safe)


if __name__ == "__main__":
    unittest.main()
