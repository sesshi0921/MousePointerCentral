"""Screen capture using mss (§5.2)."""

from __future__ import annotations

import base64
import io
from typing import Optional

from .coords import CoordSpace


def capture_screen(monitor: int = 0) -> dict:
    """Capture the full screen (or a specific monitor) and return metadata.

    Returns a dict with ``image_b64``, ``width``, ``height``, and
    ``coord_space``.  The raw image is a PNG encoded as base-64 so that
    it can be returned via JSON-RPC.
    """
    try:
        import mss  # type: ignore[import-untyped]

        with mss.mss() as sct:
            # monitor 0 = virtual screen, 1 = primary, 2 = secondary …
            mon = sct.monitors[monitor]
            grab = sct.grab(mon)
            from PIL import Image  # type: ignore[import-untyped]

            img = Image.frombytes("RGB", grab.size, grab.rgb)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return {
                "image_b64": base64.b64encode(buf.getvalue()).decode(),
                "width": img.width,
                "height": img.height,
                "coord_space": CoordSpace.SCREEN,
            }
    except Exception as exc:
        return {"error": str(exc), "coord_space": CoordSpace.SCREEN}


def capture_region(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
) -> dict:
    """Capture a specific rectangle of the screen."""
    try:
        import mss  # type: ignore[import-untyped]

        with mss.mss() as sct:
            region = {"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1}
            grab = sct.grab(region)
            from PIL import Image  # type: ignore[import-untyped]

            img = Image.frombytes("RGB", grab.size, grab.rgb)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return {
                "image_b64": base64.b64encode(buf.getvalue()).decode(),
                "width": img.width,
                "height": img.height,
                "coord_space": CoordSpace.CROP,
            }
    except Exception as exc:
        return {"error": str(exc), "coord_space": CoordSpace.CROP}
