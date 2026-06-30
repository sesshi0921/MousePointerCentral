"""OCR-based text detector (§5.4).

Returns Candidate dicts with ``coord_space:"crop"``.
"""

from __future__ import annotations

import base64
import io
from typing import Any

from ..config import PERCEPT_CONFIG
from ..coords import CoordSpace


def detect_ocr(image_b64: str, *, scale_k: float = 1.0) -> list[dict[str, Any]]:
    """Run OCR on the image and emit one candidate per text region."""
    cfg = PERCEPT_CONFIG
    candidates: list[dict[str, Any]] = []

    try:
        raw = base64.b64decode(image_b64)
        from PIL import Image  # type: ignore[import-untyped]

        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        return candidates

    try:
        import pytesseract  # type: ignore[import-untyped]

        data = pytesseract.image_to_data(img, lang=cfg.ocr_lang, output_type=pytesseract.Output.DICT)
        n = len(data["text"])
        idx = 0
        for i in range(n):
            text = data["text"][i].strip()
            conf_raw = data["conf"][i]
            try:
                conf = float(conf_raw) / 100.0
            except (ValueError, TypeError):
                continue
            if not text or conf < cfg.ocr_conf_threshold:
                continue
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            # Convert from upscaled coords back to crop coords
            cx = round((x + w / 2) / scale_k)
            cy = round((y + h / 2) / scale_k)
            x1 = round(x / scale_k)
            y1 = round(y / scale_k)
            x2 = round((x + w) / scale_k)
            y2 = round((y + h) / scale_k)
            candidates.append({
                "id": f"ocr_{idx:03d}",
                "type": "unknown",
                "click_target": [cx, cy],
                "anchors": [[x1, y1, x2, y2]],
                "text": [text],
                "conf": round(conf, 3),
                "sources": ["ocr"],
                "to_vision": False,
                "coord_space": CoordSpace.CROP,
            })
            idx += 1
    except ImportError:
        pass  # tesseract not installed

    return candidates
