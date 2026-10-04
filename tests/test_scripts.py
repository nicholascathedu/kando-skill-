"""Tests for the Kando skill scripts. Run from the repo root: python -m unittest -v"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "skills", "kando", "scripts")
EXAMPLES = os.path.join(HERE, "..", "skills", "kando", "examples")
sys.path.insert(0, SCRIPTS)

import kando_check  # noqa: E402
from kando_layout import compute_item_angles, fix_fixed_angles, levels  # noqa: E402


def item(name, angle=None, kind="button", children=None, actions=None, key=None):
    it = {"type": kind, "name": name, "icon": "x", "iconTheme": "material-symbols-rounded"}
    if angle is not None:
        it["angle"] = angle
    if kind == "submenu":
        it["children"] = children or []
    else:
        wf = {"actions": actions if actions is not None else [{"type": "close-menu"}]}
        if key:
            wf["quickSelectKey"] = key
        it["selectWorkflow"] = wf
    return it


def menus(*children, shortcut="Control+Space", conditions=None):
    m = {"root": {"type": "root", "name": "Test", "icon": "x", "iconTheme": "x",
                  "children": list(children)}, "shortcut": shortcut}
    if conditions is not None:
        m["conditions"] = conditions
    return {"version": "3.0.0", "menus": [m], "collections": []}


def report(data):
    rep = kando_check.Report()
    kando_check.check_menus(data, rep)
    return rep


def messages(rep, level):
    return [m for lv, _, m in rep.items if lv == level]


class LayoutPort(unittest.TestCase):
    """Expected values follow Kando's computeItemAngles / fixFixedAngles."""

    def test_no_fixed_angles_spread_evenly_from_top(self):
        self.assertEqual(compute_item_angles([None] * 4), [0, 90, 180, 270])

    def test_fixed_angles_wrap_forward(self):
        items = [{"angle": 90}, {"angle": 270}, {"angle": 0}]
        self.assertEqual(fix_fixed_angles(items), [90, 270, 360])

    def test_equal_and_full_lap_angles_are_dropped(self):
        self.assertEqual(fix_fixed_angles([{"angle": 10}, {"angle": 10}]), [10, None])
        self.assertEqual(fix_fixed_angles([{"angle": 10}, {"angle": 200}, {"angle": 380}]),
                         [10, 200, None])

    def test_auto_items_avoid_the_parent_link(self):
        angles = compute_item_angles([None, None, None], parent_angle=180)
        self.assertEqual(sorted(round(a) for a in angles), [0, 90, 270])

    def test_levels_report_back_direction(self):
        data = menus(item("Sub", 90, "submenu", [item("A"), item("B")]))
        lv = list(levels(data["menus"][0]))
        self.assertEqual(lv[1][2], 270)


class Checker(unittest.TestCase):
    def test_examples_are_clean(self):
        for name in os.listdir(EXAMPLES):
            if name.endswith(".json"):
                with open(os.path.join(EXAMPLES, name), encoding="utf-8") as f:
                    rep = report(json.load(f))
                self.assertEqual(rep.count("ERROR") + rep.count("WARN"), 0, name)

    def test_key_names_in_hotkeys_are_errors(self):
        rep = report(menus(item("Save", 0, actions=[{"type": "close-menu"},
                                                    {"type": "simulate-hotkey", "hotkey": "Ctrl+S"}])))
        errs = " ".join(messages(rep, "ERROR"))
        self.assertIn("ControlLeft", errs)
        self.assertIn("KeyS", errs)

    def test_key_codes_in_shortcut_are_errors(self):
        rep = report(menus(item("A", 0), shortcut="ControlLeft+KeyK"))
        self.assertTrue(any("key name" in m for m in messages(rep, "ERROR")))

    def test_hotkey_before_close_menu_warns(self):
        rep = report(menus(item("A", 0, actions=[{"type": "simulate-hotkey", "hotkey": "KeyF"},
                                                 {"type": "close-menu"}])))
        self.assertTrue(any("close-menu first" in m for m in messages(rep, "WARN")))

    def test_child_on_back_link_warns_even_with_auto_submenu(self):
        # The submenu has no fixed angle; Kando puts it at 0, so "back" is 180.
        sub = item("Sub", None, "submenu", [item("Up", 0), item("Down", 180)])
        rep = report(menus(sub, item("Right", 90), item("Left", 270)))
        self.assertTrue(any("'Down'" in m and "way back" in m for m in messages(rep, "WARN")))

    def test_conditions_only_shortcut_gets_fallback_tip(self):
        rep = report(menus(item("A", 0), conditions={"appName": "maya"}))
        self.assertTrue(any("fallback" in m for m in messages(rep, "TIP")))
        rep = report(menus(item("A", 0), conditions={"appName": "", "windowName": ""}))
        self.assertFalse(any("fallback" in m for m in messages(rep, "TIP")))

    def test_kando2_item_type_is_error(self):
        rep = report(menus({"type": "command", "name": "Old", "icon": "x", "iconTheme": "x"}))
        self.assertTrue(any("Kando 2.x" in m for m in messages(rep, "ERROR")))

    def test_malformed_values_do_not_crash(self):
        data = menus(item("A", 0))
        data["menus"][0]["root"]["activateWorkflow"] = ["oops"]
        data["menus"].append("not a menu")
        report(data)  # must not raise

    def test_privacy_scan(self):
        rep = kando_check.Report()
        kando_check.scan_privacy(json.dumps({"c": "C:\\Users\\alice\\x.lnk", "t": "me#1a2b 123456789012"}), rep)
        found = " ".join(messages(rep, "WARN"))
        self.assertIn("alice", found)
        self.assertIn("123456789012", found)
        self.assertIn("#1a2b", found)


class CommandLine(unittest.TestCase):
    def run_script(self, *args):
        env = dict(os.environ, PYTHONIOENCODING="cp1252")  # simulate a legacy Windows console
        return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", env=env)

    def test_preview_writes_html_and_survives_legacy_console(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "sheet.html")
            r = self.run_script(os.path.join(SCRIPTS, "kando_preview.py"),
                                os.path.join(EXAMPLES, "3d-work-menus.json"), "--html", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Switch app", r.stdout)
            with open(out, encoding="utf-8") as f:
                self.assertIn("<svg", f.read())

    def test_checker_exit_codes(self):
        r = self.run_script(os.path.join(SCRIPTS, "kando_check.py"),
                            os.path.join(EXAMPLES, "desktop-launcher.json"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("{ not json")
        try:
            r = self.run_script(os.path.join(SCRIPTS, "kando_check.py"), f.name)
            self.assertEqual(r.returncode, 1)
            self.assertIn("Not valid JSON", r.stdout)
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
