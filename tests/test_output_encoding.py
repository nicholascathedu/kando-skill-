"""Scripts must not crash printing menu names with emoji or Chinese text when Windows pipes
their output with a legacy code page (as when Claude Code runs them). Run from the repo root:
python -m unittest discover -s tests"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

from test_scripts import SCRIPTS, item, menus


class OutputEncodingTest(unittest.TestCase):
    def test_every_script_that_prints_switches_to_utf8(self):
        for name in sorted(os.listdir(SCRIPTS)):
            if not name.endswith(".py"):
                continue
            with open(os.path.join(SCRIPTS, name), encoding="utf-8") as f:
                code = f.read()
            main = re.search(r"\ndef main\(.*?\n((?:    .*\n|\n)*)", code)
            if main and "print(" in code:
                self.assertIn("use_utf8_output()", main.group(1), name)

    def test_usage_report_survives_a_cp1252_pipe(self):
        data = menus(item("Café 🎨", 0), item("渲染", 90), item("Save", 180), item("Export", 270),
                     shortcut="Control+4")
        rows = []
        for i in range(25):
            rows += [{"t": i * 20000, "ev": "openMenu", "path": []},
                     {"t": i * 20000 + 300, "ev": "selectButton", "path": [i % 2]},
                     {"t": i * 20000 + 301, "ev": "closeMenu", "path": []}]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "menus.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            os.makedirs(os.path.join(d, "claude-usage"))
            with open(os.path.join(d, "claude-usage", "usage.jsonl"), "w", encoding="utf-8") as f:
                f.write("".join(json.dumps(r) + "\n" for r in rows))
            run = subprocess.run([sys.executable, os.path.join(SCRIPTS, "kando_usage.py"), "report", path],
                                 capture_output=True, env=dict(os.environ, PYTHONIOENCODING="cp1252"))
        self.assertEqual(run.returncode, 0, run.stderr.decode("utf-8", "replace"))
        self.assertIn("Café 🎨", run.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
