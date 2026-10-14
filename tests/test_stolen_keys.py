"""Tests for the checker's shortcut theft and execute-command tips. Run from the repo root: python -m unittest discover -s tests"""

import unittest

from test_scripts import item, menus, messages, report


class StolenKeysTest(unittest.TestCase):
    def test_command_then_keys_gets_wait_tip(self):
        acts = [{"type": "close-menu"}, {"type": "execute-command", "command": "x"},
                {"type": "simulate-hotkey", "hotkey": "ControlLeft+KeyV"}]
        tips = messages(report(menus(item("A", 0, actions=acts))), "TIP")
        self.assertTrue(any("without waiting" in m for m in tips))

    def test_stolen_keys(self):
        rep = report(menus(item("A", 0), shortcut="Control+S"))
        self.assertTrue(any("Save stops working everywhere" in m for m in messages(rep, "WARN")))
        rep = report(menus(item("A", 0), shortcut="Control+2", conditions={"appName": "blender"}))
        self.assertTrue(any("Blender" in m and "subdivision" in m for m in messages(rep, "TIP")))
        rep = report(menus(item("A", 0), shortcut="Control+2"))
        self.assertFalse(any("subdivision" in m for m in messages(rep, "TIP")))


if __name__ == "__main__":
    unittest.main()
