"""Tests for screen_percept.ensemble."""

import unittest

from screen_percept.ensemble import ensemble, classify, _iou


class TestIoU(unittest.TestCase):
    def test_no_overlap(self):
        self.assertAlmostEqual(_iou([0, 0, 10, 10], [20, 20, 30, 30]), 0.0)

    def test_full_overlap(self):
        self.assertAlmostEqual(_iou([0, 0, 10, 10], [0, 0, 10, 10]), 1.0)

    def test_partial_overlap(self):
        val = _iou([0, 0, 10, 10], [5, 5, 15, 15])
        self.assertGreater(val, 0.0)
        self.assertLess(val, 1.0)


class TestClassify(unittest.TestCase):
    def test_button_keyword(self):
        c = {"id": "t1", "type": "unknown", "text": ["Save"], "conf": 0.9}
        result = classify(c)
        self.assertEqual(result["type"], "text_button")

    def test_toggle_keyword(self):
        c = {"id": "t2", "type": "unknown", "text": ["ON"], "conf": 0.9}
        result = classify(c)
        self.assertEqual(result["type"], "toggle")

    def test_low_conf_defers_to_vision(self):
        c = {"id": "t3", "type": "unknown", "text": ["OK"], "conf": 0.3, "to_vision": False}
        result = classify(c, min_conf=0.5)
        self.assertTrue(result["to_vision"])

    def test_already_classified(self):
        c = {"id": "t4", "type": "button", "text": ["Save"], "conf": 0.9}
        result = classify(c)
        self.assertEqual(result["type"], "button")


class TestEnsemble(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(ensemble([]), [])

    def test_merges_overlapping(self):
        c1 = {
            "id": "a", "type": "unknown", "click_target": [50, 50],
            "anchors": [[40, 40, 60, 60]], "text": ["OK"], "conf": 0.8,
            "sources": ["ocr"], "to_vision": False, "coord_space": "crop",
        }
        c2 = {
            "id": "b", "type": "unknown", "click_target": [50, 50],
            "anchors": [[42, 42, 58, 58]], "text": [], "conf": 0.5,
            "sources": ["contour"], "to_vision": False, "coord_space": "crop",
        }
        result = ensemble([c1, c2])
        self.assertEqual(len(result), 1)
        self.assertIn("ocr", result[0]["sources"])
        self.assertIn("contour", result[0]["sources"])


if __name__ == "__main__":
    unittest.main()
