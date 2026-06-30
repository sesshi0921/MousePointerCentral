"""Tests for screen_percept.coords – coordinate transforms."""

import unittest

from screen_percept.coords import (
    CoordSpace,
    Point,
    Rect,
    crop_to_screen,
    crop_to_window,
    window_to_screen,
    screen_to_window,
    window_to_crop,
    upscaled_to_crop,
    crop_to_upscaled,
)


class TestPoint(unittest.TestCase):
    def test_basic(self):
        p = Point(10, 20)
        self.assertEqual(p.x, 10)
        self.assertEqual(p.y, 20)


class TestRect(unittest.TestCase):
    def test_properties(self):
        r = Rect(10, 20, 110, 70)
        self.assertEqual(r.width, 100)
        self.assertEqual(r.height, 50)
        self.assertEqual(r.center, Point(60, 45))

    def test_as_tuple(self):
        r = Rect(0, 0, 50, 50)
        self.assertEqual(r.as_tuple(), (0, 0, 50, 50))


class TestTransforms(unittest.TestCase):
    def test_crop_to_window_no_scale(self):
        self.assertEqual(crop_to_window([100, 200], 1.0), (100, 200))

    def test_crop_to_window_retina(self):
        self.assertEqual(crop_to_window([200, 400], 2.0), (100, 200))

    def test_window_to_screen(self):
        self.assertEqual(window_to_screen([50, 60], [100, 200]), (150, 260))

    def test_crop_to_screen(self):
        self.assertEqual(
            crop_to_screen([200, 400], window_origin=[100, 50], dpi_scale=2.0),
            (200, 250),
        )

    def test_screen_to_window(self):
        self.assertEqual(screen_to_window([150, 260], [100, 200]), (50, 60))

    def test_window_to_crop(self):
        self.assertEqual(window_to_crop([50, 60], 2.0), (100, 120))

    def test_upscaled_to_crop(self):
        self.assertEqual(upscaled_to_crop([200, 400], 2.0), (100, 200))

    def test_crop_to_upscaled(self):
        self.assertEqual(crop_to_upscaled([100, 200], 2.0), (200, 400))

    def test_roundtrip(self):
        orig = (123, 456)
        up = crop_to_upscaled(orig, 3.0)
        back = upscaled_to_crop(up, 3.0)
        self.assertEqual(back, orig)


class TestCoordSpace(unittest.TestCase):
    def test_values(self):
        self.assertEqual(CoordSpace.SCREEN, "screen")
        self.assertEqual(CoordSpace.CROP, "crop")
        self.assertEqual(CoordSpace.UPSCALED, "upscaled")


if __name__ == "__main__":
    unittest.main()
