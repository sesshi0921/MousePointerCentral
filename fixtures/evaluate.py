"""Evaluation harness for screen-perception pipeline (§10).

Usage:
    python -m fixtures.evaluate

Reads screenshots from ``fixtures/screenshots/`` and labels from
``fixtures/labels/``, runs the detection pipeline, and reports recall
and click-success metrics.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


FIXTURES_DIR = Path(__file__).resolve().parent
SCREENSHOTS_DIR = FIXTURES_DIR / "screenshots"
LABELS_DIR = FIXTURES_DIR / "labels"


def _load_labels(name: str) -> list[dict]:
    label_path = LABELS_DIR / f"{name}.json"
    if not label_path.exists():
        return []
    with open(label_path) as f:
        return json.load(f)


def _point_in_box(px: int, py: int, box: list[int]) -> bool:
    x1, y1, x2, y2 = box
    return x1 <= px <= x2 and y1 <= py <= y2


def _iou(a: list[int], b: list[int]) -> float:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def evaluate() -> dict:
    """Run evaluation and return a summary dict."""
    if not SCREENSHOTS_DIR.exists() or not LABELS_DIR.exists():
        print("fixtures/screenshots/ or fixtures/labels/ not found – skipping.")
        return {"recall": None, "click_success": None, "note": "no fixtures"}

    total_gt = 0
    matched_gt = 0
    click_hits = 0
    click_total = 0

    for img_path in sorted(SCREENSHOTS_DIR.glob("*.png")):
        name = img_path.stem
        gt = _load_labels(name)
        if not gt:
            continue

        # In a full run, we would call the detection pipeline here.
        # For now, the harness demonstrates the metrics skeleton.
        total_gt += len(gt)

        # Placeholder: no candidates yet
        candidates: list[dict] = []

        for g in gt:
            box = g["bounds"]
            found = any(
                _iou(box, c["anchors"][0]) > 0.3
                for c in candidates
                if c.get("anchors")
            )
            if found:
                matched_gt += 1

        for c in candidates:
            cx, cy = c.get("click_target", [0, 0])
            for g in gt:
                if _point_in_box(cx, cy, g["bounds"]):
                    click_hits += 1
                    break
            click_total += 1

    recall = matched_gt / total_gt if total_gt else None
    click_success = click_hits / click_total if click_total else None

    result = {
        "total_ground_truth": total_gt,
        "matched": matched_gt,
        "recall": recall,
        "click_hits": click_hits,
        "click_total": click_total,
        "click_success": click_success,
    }
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    evaluate()
