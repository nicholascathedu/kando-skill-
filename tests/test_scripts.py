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
import kando_profile  # noqa: E402
from kando_layout import angle_problems, compute_item_angles, levels, raw_angle  # noqa: E402


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


def angles_of(*raw, parent=None):
    """Kando's placement for one ring, from raw `angle` values (None = no angle)."""
    items = [{} if a is None else {"angle": a} for a in raw]
    return [round(a, 6) for a in compute_item_angles([raw_angle(i) for i in items], parent)]


class LayoutPort(unittest.TestCase):
    """Expected values come from Kando's computeItemAngles (src/common/math/index.ts),
    run on the raw angles exactly as the live menu does (src/menu-renderer/menu.ts)."""

    def test_extreme_and_non_numeric_angles_do_not_hang(self):
        items = [{"angle": 1e308}, {"angle": float("nan")}, {"angle": True}, {"angle": "90"},
                 {"angle": None}, {"angle": 90}]
        fixed = [raw_angle(i) for i in items]
        self.assertEqual(fixed[1:5], [None, None, None, None])
        self.assertEqual(len(compute_item_angles(fixed)), 6)
        self.assertEqual(len(compute_item_angles(fixed, parent_angle=45)), 6)

    def test_no_fixed_angles_spread_evenly_from_top(self):
        self.assertEqual(compute_item_angles([None] * 4), [0, 90, 180, 270])

    def test_out_of_order_angle_is_ignored(self):
        # 30 is smaller than 270 before it, so Kando ignores it and auto-places the item.
        self.assertEqual(angles_of(270, 30, 350, None), [270, 310, 350, 130])

    def test_negative_angle_is_ignored(self):
        self.assertEqual(angles_of(-30, None, None), [0, 120, 240])

    def test_equal_angles_are_both_kept(self):
        self.assertEqual(angles_of(90, 90), [90, 90])

    def test_fixed_angle_on_the_parent_link_is_nudged(self):
        # Inside a submenu opened from the left, the way back is at 90. A child fixed at 90
        # moves to 90.1 and the others fill the ring around it.
        self.assertEqual(angles_of(90, None, None, parent=90), [90.1, 180.1, 270.1])

    def test_angles_past_a_full_turn_are_kept_as_given(self):
        self.assertEqual(angles_of(180, 240, 300, 360), [180, 240, 300, 360])

    def test_angle_problems(self):
        ignored, stacked, lapped = angle_problems([{"angle": 270}, {"angle": 30}, {"angle": -5}, {}])
        self.assertEqual(ignored, [(1, 30, "smaller", 270), (2, -5, "negative", 270)])
        self.assertEqual((stacked, lapped), ([], []))
        _, stacked, _ = angle_problems([{"angle": 0}, {"angle": 90}, {"angle": 360}])
        self.assertEqual(stacked, [[0, 2]])
        _, _, lapped = angle_problems([{"angle": 90}, {"angle": 200}, {"angle": 460}])
        self.assertEqual(lapped, [(2, 90)])

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

    def test_angle_rules_match_kando(self):
        rep = report(menus(item("A", 270), item("B", 30), item("C", 350), item("D", -30)))
        warns = " ".join(messages(rep, "WARN"))
        self.assertIn("'B' (30\u00b0) comes after an item fixed at 270\u00b0", warns)
        self.assertIn("'D' has angle -30\u00b0", warns)
        self.assertEqual(warns.count("Kando ignores this angle and places the item automatically"), 2)
        self.assertEqual(rep.count("ERROR"), 0)
        self.assertNotIn("wrap", warns)

    def test_equal_angles_are_an_error_that_does_not_block_loading(self):
        rep = report(menus(item("A", 90), item("B", 90), item("C", 450)))
        errs = messages(rep, "ERROR")
        self.assertEqual(len(errs), 1)
        self.assertIn("'A', 'B', 'C' all point at 90", errs[0])
        self.assertEqual(rep.load_errors, 0)

    def test_angle_past_a_full_lap_warns(self):
        rep = report(menus(item("A", 90), item("B", 200), item("C", 460)))
        self.assertTrue(any("'C' (460\u00b0) is a full turn" in m for m in messages(rep, "WARN")))
        rep = report(menus(item("A", 180), item("B", 240), item("C", 300), item("D", 360)))
        self.assertEqual(rep.count("WARN") + rep.count("ERROR"), 0)  # same wedges as 0

    def test_schema_types(self):
        rep = report(menus(item("A", True), item("B", 90, key=5)))
        errs = " ".join(messages(rep, "ERROR"))
        self.assertIn("'angle' must be a number", errs)
        self.assertIn("quickSelectKey must be a string", errs)
        self.assertFalse(messages(report(menus(item("A", 0, key="Backspace"))), "ERROR"))

    def test_fixed_position_out_of_range_is_a_warning(self):
        data = menus(item("A", 0))
        data["menus"][0]["fixedMenuPosition"] = {"x": 1.5, "y": 0.5}
        rep = report(data)
        self.assertEqual(rep.count("ERROR"), 0)
        self.assertTrue(any("fixedMenuPosition.x is 1.5" in m for m in messages(rep, "WARN")))
        data["menus"][0]["fixedMenuPosition"] = {"x": "left", "y": 0.5}
        self.assertTrue(any("must be a number" in m for m in messages(report(data), "ERROR")))

    def test_newer_major_version_warns(self):
        data = menus(item("A", 0))
        data["version"] = "4.0.0"
        warns = " ".join(messages(report(data), "WARN"))
        self.assertIn("default settings", warns)
        data["version"] = "3.2.0"
        self.assertFalse(messages(report(data), "WARN"))

    def test_collections_need_name_icon_and_theme(self):
        data = menus(item("A", 0))
        data["collections"] = [{"name": "Work", "icon": "work", "iconTheme": "material-symbols-rounded"},
                               {"name": "Bad", "tags": "x"}, "nope"]
        errs = messages(report(data), "ERROR")
        self.assertEqual(len(errs), 3)
        self.assertIn("'icon', 'iconTheme'", errs[0])

    def test_config_schema(self):
        rep = kando_check.Report()
        kando_check.check_config({"zoomFactor": "big", "fadeOutDuration": "slow", "fadeInDuration": -1,
                                  "wlrootsPointerGetTimeoutDefaultBehavior": "middle",
                                  "settingsWindowColorScheme": ["dark"], "gamepadBackButton": -1,
                                  "menuThemeColors": {"t": {"accent": 3}}, "version": "9.0.0"}, rep)
        errs = " ".join(w for lv, w, _ in rep.items if lv == "ERROR")
        for key in ("zoomFactor", "fadeOutDuration", "fadeInDuration",
                    "wlrootsPointerGetTimeoutDefaultBehavior", "settingsWindowColorScheme",
                    "menuThemeColors"):
            self.assertIn(key, errs)
        self.assertNotIn("gamepadBackButton", errs)
        self.assertTrue(any("newer major" in m for m in messages(rep, "WARN")))

    def test_odd_names_and_deep_nesting_do_not_crash(self):
        data = menus(item(["list"]), item({"a": 1}), item(["list"]))
        data["menus"][0]["root"]["name"] = ["x"]
        data["menus"].append(json.loads(json.dumps(data["menus"][0])))
        report(data)  # must not raise
        node = item("leaf")
        for i in range(400):
            node = item(f"s{i}", None, "submenu", [node])
        rep = report(menus(node))
        self.assertTrue(any("checker stops here" in m for m in messages(rep, "WARN")))
        lv = list(levels(menus(node)["menus"][0]))
        self.assertEqual(len(lv), 401)

    def test_privacy_scan(self):
        rep = kando_check.Report()
        kando_check.scan_privacy(json.dumps({"c": "C:\\Users\\alice\\x.lnk", "t": "me#1a2b 123456789012"}), rep)
        found = " ".join(messages(rep, "WARN"))
        self.assertIn("alice", found)
        self.assertIn("123456789012", found)
        self.assertIn("#1a2b", found)


def menu(name, *children, shortcut="Control+4", app=None):
    m = {"root": {"type": "root", "name": name, "icon": "x", "iconTheme": "x",
                  "children": list(children)}, "shortcut": shortcut}
    if app:
        m["conditions"] = {"appName": app}
    return m


def section(text, heading):
    """The lines under one '## heading', up to the next heading."""
    lines = text.split("\n")
    start = lines.index(f"## {heading}") + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start:end])


class Profile(unittest.TestCase):
    def build(self, *menu_list, cfg=None):
        return kando_profile.build_profile({"version": "3.0.0", "menus": list(menu_list)}, cfg)

    def test_anchors_and_drift(self):
        text = self.build(
            menu("Maya", item("Frame", 0), item("Save", 225), item("Undo", 270), app="maya"),
            menu("Blender", item("Render", 0), item("Undo", 90), item("save", 225), app="blender"),
            menu("Desktop", item("Undo", 270), item("Files", 90)))
        anchors, drift = section(text, "Anchors"), section(text, "Drift")
        self.assertIn("Save: Down-left in Maya, Blender", anchors)  # case-insensitive match
        self.assertNotIn("Undo", anchors)
        self.assertIn("Undo: Left in Maya, Desktop; Right in Blender", drift)
        self.assertIn("Most use Left", drift)
        self.assertNotIn("Frame", anchors + drift)  # only in one menu
        shortcuts = section(text, "Shortcuts")
        self.assertIn('Maya, when app contains "maya"', shortcuts)
        self.assertIn("Desktop, everywhere (the fallback)", shortcuts)

    def test_missing_fallback_is_named(self):
        text = self.build(menu("Maya", item("A", 0), app="maya"))
        self.assertIn("No fallback", section(text, "Shortcuts"))

    def test_auto_placed_items_get_real_directions(self):
        text = self.build(menu("Auto", item("A"), item("B"), item("C"), item("D")))
        dirs = section(text, "Directions")
        for line in ("Up (0°): A", "Right (90°): B", "Down (180°): C", "Left (270°): D"):
            self.assertIn(line + " (auto-placed)", dirs)

    def test_submenu_items_compare_at_the_same_depth(self):
        sub = lambda: item("Switch", 180, "submenu", [item("Go home", 90)])  # noqa: E731
        text = self.build(menu("One", sub()), menu("Two", sub()))
        self.assertIn("Go home: Right in One > Switch, Two > Switch (inside a submenu)",
                      section(text, "Anchors"))

    def test_malformed_input_does_not_crash(self):
        bad = [
            None, [], "menus", {"menus": "nope"}, {"menu": {"root": {}}},
            {"menus": ["x", 3, {"root": "x"}, {"root": {"children": "x"}},
                       {"shortcut": 5, "conditions": [1], "root": {"name": 7, "children": [
                           None, 4, {"name": "A", "angle": float("nan")}, {"name": "B", "angle": 1e308},
                           {"type": "submenu", "name": "S", "children": [{"selectWorkflow": "x"},
                            {"selectWorkflow": {"actions": [5, {"type": "execute-command", "command": 3},
                                                            {"type": "open-uri", "uri": "http://[::1"}]}}]}]}}]},
        ]
        for data in bad:
            kando_profile.build_profile(data, cfg=["not", "a", "dict"])  # must not raise
        kando_profile.build_profile({"menus": []}, cfg={"menuThemeColors": "x", "fadeInDuration": None})

    def test_apps_are_names_not_paths(self):
        launch = lambda cmd: item("Go", 0, actions=[{"type": "execute-command", "command": cmd}])  # noqa: E731
        text = self.build(menu("M", launch('start "" "%LOCALAPPDATA%\\Discord\\Update.exe" '
                                           '--processStart Discord.exe'),
                               launch("flatpak run org.blender.Blender"),
                               launch('open -a "Visual Studio Code"'),
                               launch("echo pick an app")))
        apps = section(text, "Apps it touches")
        self.assertIn("Launched or focused: Discord, Blender, Visual Studio Code", apps)
        self.assertNotIn("echo", apps)

    def test_privacy(self):
        cmd = '"C:\\Users\\someone\\AppData\\Local\\Programs\\Thing\\thing.exe" --id 123456789012'
        data = {"menus": [menu("Mine 123456789012", item("Call me@example.com", 0, actions=[
            {"type": "execute-command", "command": cmd}]),
            item("C:\\Users\\someone\\Desktop\\notes.txt", 90),
            app="C:\\Users\\someone\\bin\\tool.exe")]}
        text = kando_profile.build_profile(data, {"menuTheme": "/home/someone/themes/glass"})
        for secret in ("someone", "123456789012", "C:\\Users", "me@example.com", "/home/", "AppData"):
            self.assertNotIn(secret, text)
        self.assertIn("thing", section(text, "Apps it touches"))
        self.assertIn("notes.txt", text)

    def test_config_reports_only_present_keys(self):
        cfg = {"menuTheme": "amethyst-arsenal", "enableTurboMode": False, "fadeOutDuration": 70,
               "menuThemeColors": {"amethyst-arsenal": {"accent-color": "#b57bff"}},
               "darkMenuThemeColors": {}}
        look = section(self.build(menu("M", item("A", 0)), cfg=cfg), "Look and feel")
        self.assertIn("menuTheme: amethyst-arsenal", look)
        self.assertIn("accent-color #b57bff", look)
        self.assertIn("darkMenuThemeColors: no overrides", look)
        self.assertIn("enableTurboMode false, fadeOutDuration 70", look)
        self.assertNotIn("enableMarkingMode", look)
        self.assertNotIn("darkMenuTheme:", look)
        self.assertNotIn("Look and feel", self.build(menu("M", item("A", 0))))

    def test_human_sections_are_left_to_fill(self):
        text = self.build(menu("M", item("A", 0)))
        for heading in ("Taste and voice", "Workflows I care about", "Things I said no to"):
            self.assertIn("(add as you learn)", section(text, heading))


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

    def test_profile_survives_legacy_console(self):
        r = self.run_script(os.path.join(SCRIPTS, "kando_profile.py"),
                            os.path.join(EXAMPLES, "3d-work-menus.json"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Switch app: Down in Maya, Painter, Designer, Unreal", r.stdout)
        self.assertIn("(0°)", r.stdout)

    def test_profile_out_does_not_overwrite_notes(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "kando-profile.md")
            args = [os.path.join(SCRIPTS, "kando_profile.py"),
                    os.path.join(EXAMPLES, "desktop-launcher.json"), "--out", out]
            self.assertEqual(self.run_script(*args).returncode, 0)
            with open(out, "a", encoding="utf-8") as f:
                f.write("- my own note\n")
            r = self.run_script(*args)
            self.assertEqual(r.returncode, 1)
            self.assertNotIn(d, r.stdout + r.stderr)  # no full paths in messages
            with open(out, encoding="utf-8") as f:
                self.assertIn("my own note", f.read())
            self.assertEqual(self.run_script(*args, "--force").returncode, 0)

    def bad_files(self, d):
        """Files that used to crash the scripts, by name."""
        files = {
            "latin1.json": b'{"version": "3.0.0", "menus": [{"root": {"name": "Caf\xe9"}}]}',
            "list.json": b"[]",
            "empty.json": b"",
            "names.json": json.dumps(menus(item(["a"]), item({"b": 1}), item("k", key=7))).encode(),
            "nan.json": b'{"menus": [{"root": {"type": "root", "children": [{"angle": NaN}]}}]}',
            "deep.json": ('{"menus": [{"root": ' + '{"children": [' * 3000 + "]}" * 3000 + "}]}").encode(),
        }
        paths = {}
        for name, data in files.items():
            paths[name] = os.path.join(d, name)
            with open(paths[name], "wb") as f:
                f.write(data)
        return paths

    def test_bad_files_give_messages_not_tracebacks(self):
        with tempfile.TemporaryDirectory() as d:
            paths = self.bad_files(d)
            cfg = os.path.join(d, "config.json")
            with open(cfg, "w", encoding="utf-8") as f:
                json.dump({"zoomFactor": "big", "fadeOutDuration": "slow"}, f)
            for name, path in paths.items():
                for script, extra in (("kando_check.py", ["--config", cfg]),
                                      ("kando_preview.py", ["--html", os.path.join(d, "o.html")]),
                                      ("kando_profile.py", [])):
                    r = self.run_script(os.path.join(SCRIPTS, script), path, *extra)
                    self.assertNotIn("Traceback", r.stdout + r.stderr, f"{script} {name}")
            r = self.run_script(os.path.join(SCRIPTS, "kando_check.py"), paths["latin1.json"])
            self.assertIn("Not UTF-8", r.stdout)
            r = self.run_script(os.path.join(SCRIPTS, "kando_check.py"), paths["nan.json"])
            self.assertIn("NaN is not allowed", r.stdout)
            r = self.run_script(os.path.join(SCRIPTS, "kando_preview.py"), paths["names.json"])
            self.assertEqual(r.returncode, 0, r.stderr)
            r = self.run_script(os.path.join(SCRIPTS, "kando_preview.py"), paths["list.json"])
            self.assertIn("No menus found", r.stderr)

    def test_preview_pins_simple_icons(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "sheet.html")
            r = self.run_script(os.path.join(SCRIPTS, "kando_preview.py"),
                                os.path.join(EXAMPLES, "desktop-launcher.json"), "--html", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out, encoding="utf-8") as f:
                sheet = f.read()
            self.assertNotIn("@latest", sheet)

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
