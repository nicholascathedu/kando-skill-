"""Tests for the Learn item: kando_preview.py --open. Run from the repo root: python -m unittest discover -s tests"""

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

from test_scripts import EXAMPLES  # also puts scripts/ on sys.path
import kando_preview  # noqa: E402


class LearnItemTest(unittest.TestCase):
    def test_open_writes_one_menu_and_opens_it(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "kando maya.html")  # a space, like most Windows paths
            argv = ["kando_preview.py", os.path.join(EXAMPLES, "3d-work-menus.json"),
                    "--menu", "Maya", "--html", out, "--open"]
            with mock.patch.object(sys, "argv", argv), \
                    mock.patch.object(kando_preview.webbrowser, "open") as opened, \
                    redirect_stdout(io.StringIO()):
                kando_preview.main()
            url = opened.call_args[0][0]
            self.assertTrue(url.startswith("file:"))
            self.assertIn("kando%20maya.html", url)
            with open(out, encoding="utf-8") as f:
                self.assertIn("Maya", f.read())


if __name__ == "__main__":
    unittest.main()
