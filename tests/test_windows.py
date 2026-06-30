"""Tests for screen_percept.windows (unit-level, no real window system)."""

import unittest

from screen_percept.windows import _check_fullscreen, RegionInfo
from screen_percept.coords import CoordSpace


class TestCheckFullscreen(unittest.TestCase):
    def test_fullscreen(self):
        self.assertTrue(_check_fullscreen(0, 0, 1920, 1080))

    def test_not_fullscreen(self):
        self.assertFalse(_check_fullscreen(100, 100, 800, 600))


class TestRegionInfo(unittest.TestCase):
    def test_to_dict(self):
        r = RegionInfo(
            bounds=(0, 0, 1920, 1080),
            origin=(0, 0),
            is_fullscreen=True,
            dpi_scale=2.0,
        )
        d = r.to_dict()
        self.assertEqual(d["coord_space"], CoordSpace.SCREEN)
        self.assertEqual(d["dpi_scale"], 2.0)
        self.assertTrue(d["is_fullscreen"])


if __name__ == "__main__":
    unittest.main()
