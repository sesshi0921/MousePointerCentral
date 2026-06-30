"""Contour-based component detector (§5.4).

Returns Candidate dicts with ``coord_space:"crop"``.
"""

from __future__ import annotations

from typing import Any

import base64
import io

from ..config import PERCEPT_CONFIG
from ..coords import CoordSpace


def detect_contours(image_b64: str, *, scale_k: float = 1.0) -> list[dict[str, Any]]:
    """Find rectangular contours that may correspond to UI components."""
    cfg = PERCEPT_CONFIG
    candidates: list[dict[str, Any]] = []

    try:
        import cv2  # type: ignore[import-untyped]
        import numpy as np  # type: ignore[import-untyped]

        raw = base64.b64decode(image_b64)
        arr = np.frombuffer(raw, np.uint8)
        # Decode from PNG buffer
        from PIL import Image  # type: ignore[import-untyped]

        img = Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB")
        arr = np.array(img)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        idx = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < cfg.contour_min_area or area > cfg.contour_max_area:
                continue
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, cfg.contour_approx_epsilon * peri, True)
            if len(approx) < 4:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            cx = round((x + w / 2) / scale_k)
            cy = round((y + h / 2) / scale_k)
            x1 = round(x / scale_k)
            y1 = round(y / scale_k)
            x2 = round((x + w) / scale_k)
            y2 = round((y + h) / scale_k)
            candidates.append({
                "id": f"cnt_{idx:03d}",
                "type": "unknown",
                "click_target": [cx, cy],
                "anchors": [[x1, y1, x2, y2]],
                "text": [],
                "conf": 0.5,
                "sources": ["contour"],
                "to_vision": False,
                "coord_space": CoordSpace.CROP,
            })
            idx += 1
    except ImportError:
        pass

    return candidates
