"""Tests for kando_backup.py. Run from the repo root: python -m unittest discover -s tests"""

import json
import os
import tempfile
import unittest

from test_scripts import SCRIPTS  # noqa: F401 (puts scripts/ on sys.path)
import kando_backup  # noqa: E402


class BackupTest(unittest.TestCase):
    def test_save_list_restore_and_undo(self):
        with tempfile.TemporaryDirectory() as d:
            menus = os.path.join(d, "menus.json")
            with open(menus, "w") as f:
                json.dump(menus_obj := {"version": "3.0.0", "menus": []}, f)
            with open(os.path.join(d, "config.json"), "w") as f:
                f.write("{}")
            dest, files = kando_backup.save(d, "before maya!")
            self.assertTrue(os.path.basename(dest).endswith("-before-maya"))
            self.assertEqual(files, ["menus.json", "config.json"])
            with open(menus, "w") as f:
                f.write('{"version": "3.0.0", "menus": [1]}')
            restored, undo = kando_backup.restore(d, os.path.basename(dest))
            self.assertEqual(restored, ["config.json", "menus.json"])
            with open(menus) as f:
                self.assertEqual(json.load(f), menus_obj)
            with open(os.path.join(undo, "menus.json")) as f:
                self.assertIn("[1]", f.read())

    def test_broken_backup_is_not_restored(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "menus.json"), "w") as f:
                f.write('{"version": "3.0.0", "menus": []}')
            dest, _ = kando_backup.save(d)
            with open(os.path.join(dest, "menus.json"), "w") as f:
                f.write("{broken")
            with self.assertRaises(SystemExit):
                kando_backup.restore(d)


if __name__ == "__main__":
    unittest.main()
