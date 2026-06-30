"""Colour-segmentation detector (§5.4).

Uses k-means on pixel colours to find homogeneous regions that may be
buttons, toggles or other UI controls.

Returns Candidate dicts with ``coord_space:"crop"``.
"""

from __future__ import annotations

from typing import Any

import base64
import io

from ..config import PERCEPT_CONFIG
from ..coords import CoordSpace


def detect_colorseg(image_b64: str, *, scale_k: float = 1.0) -> list[dict[str, Any]]:
    """Segment the image by colour and emit candidates for each blob."""
    cfg = PERCEPT_CONFIG
    candidates: list[dict[str, Any]] = []

    try:
        import cv2  # type: ignore[import-untyped]
        import numpy as np  # type: ignore[import-untyped]
        from PIL import Image  # type: ignore[import-untyped]

        img = Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB")
        arr = np.array(img, dtype=np.float32)
        h_img, w_img = arr.shape[:2]

        # k-means colour clustering
        pixels = arr.reshape(-1, 3)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, _ = cv2.kmeans(pixels, cfg.colorseg_k, None, criteria, 3, cv2.KMEANS_PP_CENTERS)
        labels = labels.reshape(h_img, w_img)

        idx = 0
        for k in range(cfg.colorseg_k):
            mask = np.uint8(labels == k) * 255
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < cfg.colorseg_min_area:
                    continue
                x, y, w, h = cv2.boundingRect(cnt)
                cx = round((x + w / 2) / scale_k)
                cy = round((y + h / 2) / scale_k)
                x1 = round(x / scale_k)
                y1 = round(y / scale_k)
                x2 = round((x + w) / scale_k)
                y2 = round((y + h) / scale_k)
                candidates.append({
                    "id": f"cseg_{idx:03d}",
                    "type": "unknown",
                    "click_target": [cx, cy],
                    "anchors": [[x1, y1, x2, y2]],
                    "text": [],
                    "conf": 0.4,
                    "sources": ["colorseg"],
                    "to_vision": False,
                    "coord_space": CoordSpace.CROP,
                })
                idx += 1
    except ImportError:
        pass

    return candidates
