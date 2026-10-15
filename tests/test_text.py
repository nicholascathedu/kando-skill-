"""Tests for kando_text.py and the text pie example. Run from the repo root: python -m unittest discover -s tests"""

import json
import os
import re
import unittest

from test_scripts import EXAMPLES, report  # also puts scripts/ on sys.path
import kando_claude  # noqa: E402
import kando_text  # noqa: E402


class TextTest(unittest.TestCase):
    def test_naming(self):
        c = kando_text.change
        self.assertEqual(c("snake", "Crate Lid v2"), "crate_lid_v2")
        self.assertEqual(c("pascal", "crate_lid_v2"), "CrateLidV2")
        self.assertEqual(c("camel", "SM_CrateLid_01"), "smCrateLid01")
        self.assertEqual(c("kebab", "HDRMap2 bake"), "hdr-map2-bake")
        self.assertEqual(c("snake", "it's done"), "its_done")

    def test_case_and_lines(self):
        c = kando_text.change
        self.assertEqual(c("title", "it's THE end"), "It's The End")
        self.assertEqual(c("sentence", "HELLO there. new ONE"), "Hello there. New one")
        self.assertEqual(c("join", "one\r\n  two\r\nthree"), "one two three")
        self.assertEqual(c("trim", "  a  \r\n\r\n\r\n\r\nb "), "a\r\n\r\nb")  # keeps CRLF
        self.assertEqual(c("snake", "Crate Lid\nTable Top"), "crate_lid\ntable_top")

    def test_example_uses_real_actions(self):
        path = os.path.join(EXAMPLES, "text-pie.json")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        used = set(re.findall(r"kando_text\.py (\w+)", text))
        self.assertTrue(used)
        self.assertLessEqual(used, set(kando_text.CHANGES) | set(kando_text.SEARCH))
        self.assertEqual(report(json.loads(text)).count("ERROR"), 0)


class ClaudePromptTest(unittest.TestCase):
    def test_prompts_carry_the_clip_and_stay_short(self):
        url = "https://www.youtube.com/watch?v=abc123"
        self.assertIn(url, kando_claude.build(kando_claude.PROMPTS["slides"], "  " + url + "\n"))
        long = kando_claude.build("{clip}", "x" * 20000)
        self.assertLess(len(long), 7000)
        self.assertTrue(long.endswith("longer]"))
        for template in kando_claude.PROMPTS.values():
            self.assertIn("{clip}", template)


if __name__ == "__main__":
    unittest.main()
