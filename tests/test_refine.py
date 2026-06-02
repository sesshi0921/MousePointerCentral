"""Tests for screen_percept.refine."""

import unittest

from screen_percept.refine import refine_point, get_cached_candidates, clear_cache


class TestRefineDegenerate(unittest.TestCase):
    def setUp(self):
        clear_cache()

    def test_degenerate_no_image(self):
        c = {"id": "r1", "click_target": [100, 200], "type": "button"}
        result = refine_point(c, image_b64=None)
        self.assertFalse(result["snapped"])
        self.assertEqual(result["click_target"], [100, 200])

    def test_cache(self):
        c = {"id": "r2", "click_target": [50, 60], "type": "icon"}
        refine_point(c, image_b64=None)
        cached = get_cached_candidates()
        self.assertIn("r2", cached)


if __name__ == "__main__":
    unittest.main()
