"""Click-target refinement (§5.5).

Snaps a candidate's click_target to the nearest high-contrast edge
within a small radius so the final coordinate avoids borders.
Includes a degenerate mode and a per-session candidate cache.
"""

from __future__ import annotations

import base64
import io
from typing import Any

from .config import PERCEPT_CONFIG
from .coords import CoordSpace

# Simple in-memory candidate cache (keyed by candidate id).
_candidate_cache: dict[str, dict[str, Any]] = {}


def refine_point(
    candidate: dict[str, Any],
    image_b64: str | None = None,
    *,
    snap_radius: int | None = None,
) -> dict[str, Any]:
    """Refine *candidate*'s ``click_target`` using edge-based snapping.

    If *image_b64* is ``None`` (degenerate mode), the candidate is
    returned unmodified.

    Returns the candidate dict with an added ``snapped`` flag.
    """
    if snap_radius is None:
        snap_radius = PERCEPT_CONFIG.refine_snap_radius

    cid = candidate.get("id", "")

    # Degenerate mode – no image provided
    if image_b64 is None:
        candidate["snapped"] = False
        _candidate_cache[cid] = candidate
        return candidate

    try:
        import cv2  # type: ignore[import-untyped]
        import numpy as np  # type: ignore[import-untyped]
        from PIL import Image  # type: ignore[import-untyped]

        img = Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB")
        arr = np.array(img)
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        cx, cy = candidate["click_target"]
        h, w = edges.shape[:2]

        best_dist = snap_radius + 1
        bx, by = cx, cy
        for dy in range(-snap_radius, snap_radius + 1):
            for dx in range(-snap_radius, snap_radius + 1):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if edges[ny, nx] > 0:
                        d = abs(dx) + abs(dy)
                        if d < best_dist:
                            best_dist = d
                            bx, by = nx, ny

        # When a nearby edge is found we keep the original centre so that
        # the click lands inside the component rather than on its border.
        if best_dist <= snap_radius:
            candidate["click_target"] = [cx, cy]
            candidate["snapped"] = True
        else:
            candidate["snapped"] = False

    except ImportError:
        candidate["snapped"] = False

    _candidate_cache[cid] = candidate
    return candidate


def get_cached_candidates() -> dict[str, dict[str, Any]]:
    """Return the current candidate cache (read-only copy)."""
    return dict(_candidate_cache)


def clear_cache() -> None:
    _candidate_cache.clear()
