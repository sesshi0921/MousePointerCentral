"""Image preprocessing for the detection pipeline (§5.2).

Sharpening is OFF by default and flag-controlled.
"""

from __future__ import annotations

import base64
import io

from .config import PERCEPT_CONFIG
from .coords import CoordSpace


def preprocess_region(
    image_b64: str,
    *,
    upscale: bool = True,
    sharpen: bool | None = None,
    denoise: bool = True,
) -> dict:
    """Apply preprocessing to a cropped region image.

    Returns a dict with ``image_b64`` (processed PNG), dimensions, the
    upscale factor *k*, and ``coord_space: "upscaled"``.
    """
    cfg = PERCEPT_CONFIG
    if sharpen is None:
        sharpen = cfg.sharpen

    try:
        import numpy as np  # type: ignore[import-untyped]
        from PIL import Image  # type: ignore[import-untyped]

        raw = base64.b64decode(image_b64)
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        arr = np.array(img)

        scale_k = cfg.upscale_factor if upscale else 1.0

        # Upscale
        if upscale and scale_k != 1.0:
            new_w = int(img.width * scale_k)
            new_h = int(img.height * scale_k)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            arr = np.array(img)

        # Denoise (bilateral filter)
        if denoise:
            try:
                import cv2  # type: ignore[import-untyped]

                arr = cv2.bilateralFilter(
                    arr,
                    cfg.bilateral_d,
                    cfg.bilateral_sigma_color,
                    cfg.bilateral_sigma_space,
                )
            except ImportError:
                pass  # cv2 not available – skip

        # Sharpen (optional)
        if sharpen:
            try:
                import cv2  # type: ignore[import-untyped]

                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
                arr = cv2.filter2D(arr, -1, kernel)
            except ImportError:
                pass

        out_img = Image.fromarray(arr)
        buf = io.BytesIO()
        out_img.save(buf, format="PNG")

        return {
            "image_b64": base64.b64encode(buf.getvalue()).decode(),
            "width": out_img.width,
            "height": out_img.height,
            "scale_k": scale_k,
            "coord_space": CoordSpace.UPSCALED if upscale else CoordSpace.CROP,
        }
    except Exception as exc:
        return {"error": str(exc)}
