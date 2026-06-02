"""MSER-based text-region detector (§5.4).

Returns Candidate dicts with ``coord_space:"crop"``.
"""

from __future__ import annotations

from typing import Any

import base64
import io

from ..config import PERCEPT_CONFIG
from ..coords import CoordSpace


def detect_mser(image_b64: str, *, scale_k: float = 1.0) -> list[dict[str, Any]]:
    """Detect stable text / icon regions via MSER."""
    cfg = PERCEPT_CONFIG
    candidates: list[dict[str, Any]] = []

    try:
        import cv2  # type: ignore[import-untyped]
        import numpy as np  # type: ignore[import-untyped]
        from PIL import Image  # type: ignore[import-untyped]

        img = Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB")
        arr = np.array(img)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)

        mser = cv2.MSER_create(
            delta=cfg.mser_delta,
            min_area=cfg.mser_min_area,
            max_area=cfg.mser_max_area,
        )
        regions, _ = mser.detectRegions(gray)

        idx = 0
        for region in regions:
            x, y, w, h = cv2.boundingRect(region)
            cx = round((x + w / 2) / scale_k)
            cy = round((y + h / 2) / scale_k)
            x1 = round(x / scale_k)
            y1 = round(y / scale_k)
            x2 = round((x + w) / scale_k)
            y2 = round((y + h) / scale_k)
            candidates.append({
                "id": f"mser_{idx:03d}",
                "type": "unknown",
                "click_target": [cx, cy],
                "anchors": [[x1, y1, x2, y2]],
                "text": [],
                "conf": 0.5,
                "sources": ["mser"],
                "to_vision": False,
                "coord_space": CoordSpace.CROP,
            })
            idx += 1
    except ImportError:
        pass

    return candidates
