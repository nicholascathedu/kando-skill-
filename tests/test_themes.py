"""Checks for the shipped menu themes. Run from the repo root: python -m unittest discover -s tests"""

import json
import os
import re
import unittest

THEMES = os.path.join(os.path.dirname(__file__), "..", "themes")


def colors(json5_text):
    return dict(re.findall(r"'([a-z-]+-color)':\s*'([^']+)'", json5_text))


class ThemeFilesTest(unittest.TestCase):
    """Every theme's colors, CSS and presets agree, so no color picker is dead and no
    preset leaves a color unset."""

    def themes(self):
        for name in sorted(os.listdir(THEMES)):
            folder = os.path.join(THEMES, name)
            if os.path.isfile(os.path.join(folder, "theme.json5")):
                yield name, folder

    def test_found_themes(self):
        names = [n for n, _ in self.themes()]
        self.assertIn("amethyst-arsenal", names)
        self.assertIn("gunmetal-arsenal", names)

    def test_css_uses_only_declared_colors_and_every_color_is_used(self):
        for name, folder in self.themes():
            with self.subTest(theme=name):
                with open(os.path.join(folder, "theme.json5"), encoding="utf-8") as f:
                    declared = set(colors(f.read()))
                with open(os.path.join(folder, "theme.css"), encoding="utf-8") as f:
                    used = set(re.findall(r"var\(--([a-z-]+-color)\)", f.read()))
                self.assertEqual(used - declared, set(), "used in theme.css but not in theme.json5")
                self.assertEqual(declared - used, set(), "in theme.json5 but never used in theme.css")

    def test_presets_set_exactly_the_theme_colors(self):
        for name, folder in self.themes():
            with open(os.path.join(folder, "theme.json5"), encoding="utf-8") as f:
                declared = set(colors(f.read()))
            for preset in sorted(os.listdir(os.path.join(folder, "presets"))):
                with self.subTest(theme=name, preset=preset):
                    with open(os.path.join(folder, "presets", preset), encoding="utf-8") as f:
                        self.assertEqual(set(json.load(f)["colors"]), declared)

    def test_gunmetal_radius_covers_the_name_plate(self):
        folder = os.path.join(THEMES, "gunmetal-arsenal")
        with open(os.path.join(folder, "theme.json5"), encoding="utf-8") as f:
            text = f.read()
        with open(os.path.join(folder, "theme.css"), encoding="utf-8") as f:
            css = f.read()
        px = lambda var: float(re.search(r"--%s:\s*([\d.]+)" % var, css).group(1))
        # Plate top as theme.css computes it for menus of up to 8 items, plus about 34px of
        # plate height, at the plate's corner.
        top = (px("child-distance") + px("child-h") / 2) * px("hover-scale") + px("plate-gap")
        half_width = int(re.search(r"centerTextWrapWidth:\s*(\d+)", text).group(1)) / 2
        corner = (half_width ** 2 + (top + 34) ** 2) ** 0.5
        radius = int(re.search(r"maxMenuRadius:\s*(\d+)", text).group(1))
        self.assertGreaterEqual(radius, corner - 1)


if __name__ == "__main__":
    unittest.main()
