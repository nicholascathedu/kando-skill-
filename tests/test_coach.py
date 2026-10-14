"""Tests for kando_coach.py. Run from the repo root: python -m unittest discover -s tests"""

import json
import os
import tempfile
import unittest

from test_scripts import SCRIPTS  # noqa: F401 (puts scripts/ on sys.path)
import kando_coach  # noqa: E402


class CoachTest(unittest.TestCase):
    STATS = {"selections": 400, "clickSelections": 300, "gestureSelections": 80,
             "keyboardSelections": 20, "cancels": 100,
             "selectionsSpeed1Depth1": 200, "selectionsSpeed4Depth1": 20,
             "selectionsSpeed1Depth2": 100, "selectionsSpeed3Depth2": 10}

    def test_advice_follows_the_numbers(self):
        tips = " ".join(kando_coach.advice(kando_coach.summary(self.STATS)))
        for words in ("75% of your picks are clicks", "10% of your first-ring picks",
                      "10% of your submenu picks", "20% of the menus"):
            self.assertIn(words, tips)
        self.assertIn("fewer than 50", kando_coach.advice(kando_coach.summary({"selections": 3}))[0])

    def test_junk_values_and_history_round_trip(self):
        s = kando_coach.summary({"selections": "x", "clickSelections": True, "selectionsSpeed1Depth1": 0})
        self.assertEqual((s["selections"], s["ways"]["click"], s["speed"]), (0, 0, {}))
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "achievements.json")
            with open(path, "w") as f:
                json.dump(self.STATS, f)
            self.assertEqual(kando_coach.main([path, "--save"]), 0)
            self.assertTrue(os.path.isfile(os.path.join(d, kando_coach.HISTORY)))
            self.assertEqual(kando_coach.main([path]), 0)


if __name__ == "__main__":
    unittest.main()
