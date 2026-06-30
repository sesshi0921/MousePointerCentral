"""Tests for screen_percept.config."""

import unittest

from screen_percept.config import PERCEPT_CONFIG, ScreenPerceptConfig


class TestConfig(unittest.TestCase):
    def test_defaults(self):
        self.assertFalse(PERCEPT_CONFIG.sharpen)
        self.assertEqual(PERCEPT_CONFIG.upscale_factor, 2.0)
        self.assertGreater(PERCEPT_CONFIG.ensemble_iou_threshold, 0)

    def test_frozen(self):
        with self.assertRaises(AttributeError):
            PERCEPT_CONFIG.sharpen = True  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
