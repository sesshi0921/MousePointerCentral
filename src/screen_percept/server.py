"""FastMCP server for screen-perception (MCP-B, §6).

Exposes the following tools:
- capture_screen
- get_active_window / focus_window / get_region
- get_accessibility_tree
- preprocess_region
- detect_candidates
- refine_point

All return values carry ``coord_space``.
"""

from __future__ import annotations

from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover – fallback for local tests
    class FastMCP:  # type: ignore[no-redef]
        def __init__(self, name: str):
            self.name = name

        def tool(self):
            def decorator(fn: Any) -> Any:
                return fn
            return decorator


from .accessibility import get_accessibility_tree as _get_ax_tree
from .capture import capture_screen as _capture_screen
from .capture import capture_region as _capture_region
from .coords import CoordSpace, crop_to_screen
from .ensemble import ensemble as _ensemble
from .preprocess import preprocess_region as _preprocess
from .refine import refine_point as _refine
from .windows import (
    get_active_window as _get_active,
    focus_window as _focus,
)

mcp = FastMCP("screen-percept")


@mcp.tool()
def capture_screen(monitor: int = 0) -> dict:
    """Capture the full screen and return a base-64 PNG."""
    return _capture_screen(monitor)


@mcp.tool()
def get_active_window() -> dict:
    """Return the bounding region of the currently active window."""
    info = _get_active()
    if info is None:
        return {"error": "no active window found", "coord_space": CoordSpace.SCREEN}
    return info.to_dict()


@mcp.tool()
def focus_window(title: str) -> dict:
    """Bring *title* to front and return its bounding region."""
    info = _focus(title)
    if info is None:
        return {"error": f"window '{title}' not found", "coord_space": CoordSpace.SCREEN}
    return info.to_dict()


@mcp.tool()
def get_region(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Capture a rectangular region of the screen."""
    return _capture_region(x1, y1, x2, y2)


@mcp.tool()
def get_accessibility_tree(
    pid: int | None = None,
    window_title: str | None = None,
) -> dict:
    """Retrieve the OS accessibility tree (shortcut, §5.1).

    If successful the returned elements already have
    ``coord_space:"screen"`` and skip the CV pipeline.
    """
    tree = _get_ax_tree(pid=pid, window_title=window_title)
    if tree is None:
        return {"elements": None, "coord_space": CoordSpace.SCREEN}
    return {"elements": tree, "coord_space": CoordSpace.SCREEN}


@mcp.tool()
def preprocess_region(image_b64: str, upscale: bool = True, sharpen: bool = False, denoise: bool = True) -> dict:
    """Apply preprocessing (upscale / denoise / sharpen) to a region image."""
    return _preprocess(image_b64, upscale=upscale, sharpen=sharpen, denoise=denoise)


@mcp.tool()
def detect_candidates(image_b64: str, scale_k: float = 1.0) -> dict:
    """Run all four detectors and return the ensembled candidate list.

    *image_b64* should be the **preprocessed** (upscaled) image.
    *scale_k* is the upscale factor so coordinates are mapped back to
    ``crop`` space.
    """
    from .detectors.ocr_detector import detect_ocr
    from .detectors.contour_detector import detect_contours
    from .detectors.mser_detector import detect_mser
    from .detectors.colorseg_detector import detect_colorseg

    all_cands: list[dict[str, Any]] = []
    all_cands.extend(detect_ocr(image_b64, scale_k=scale_k))
    all_cands.extend(detect_contours(image_b64, scale_k=scale_k))
    all_cands.extend(detect_mser(image_b64, scale_k=scale_k))
    all_cands.extend(detect_colorseg(image_b64, scale_k=scale_k))

    ensembled = _ensemble(all_cands)
    return {"candidates": ensembled, "count": len(ensembled), "coord_space": CoordSpace.CROP}


@mcp.tool()
def refine_point(candidate: dict, image_b64: str | None = None) -> dict:
    """Snap *candidate*'s click_target away from edges (§5.5)."""
    return _refine(candidate, image_b64)


if __name__ == "__main__":
    mcp.run()
