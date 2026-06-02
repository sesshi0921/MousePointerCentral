"""Window management (§4).

Priority order:
1. pywinctl (cross-platform)
2. OS-specific API as supplement
3. CV-based fallback (placeholder)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .coords import CoordSpace


@dataclass
class RegionInfo:
    """Describes a window / monitor region (§7 RegionInfo)."""

    bounds: tuple[int, int, int, int]  # (x1, y1, x2, y2)
    origin: tuple[int, int]            # window top-left in screen coords
    is_fullscreen: bool
    dpi_scale: float
    coord_space: str = CoordSpace.SCREEN

    def to_dict(self) -> dict:
        return {
            "bounds": list(self.bounds),
            "origin": list(self.origin),
            "is_fullscreen": self.is_fullscreen,
            "dpi_scale": self.dpi_scale,
            "coord_space": self.coord_space,
        }


def _try_pywinctl_active() -> Optional[RegionInfo]:
    """Use pywinctl to get the active window rectangle."""
    try:
        import pywinctl  # type: ignore[import-untyped]

        win = pywinctl.getActiveWindow()
        if win is None:
            return None
        left, top = int(win.left), int(win.top)
        right, bottom = int(win.left + win.width), int(win.top + win.height)
        return RegionInfo(
            bounds=(left, top, right, bottom),
            origin=(left, top),
            is_fullscreen=_check_fullscreen(left, top, int(win.width), int(win.height)),
            dpi_scale=_get_dpi_scale(),
        )
    except Exception:
        return None


def _try_pywinctl_by_title(title: str) -> Optional[RegionInfo]:
    """Find a window whose title contains *title*."""
    try:
        import pywinctl  # type: ignore[import-untyped]

        wins = pywinctl.getWindowsWithTitle(title)
        if not wins:
            return None
        win = wins[0]
        left, top = int(win.left), int(win.top)
        right, bottom = int(win.left + win.width), int(win.top + win.height)
        return RegionInfo(
            bounds=(left, top, right, bottom),
            origin=(left, top),
            is_fullscreen=_check_fullscreen(left, top, int(win.width), int(win.height)),
            dpi_scale=_get_dpi_scale(),
        )
    except Exception:
        return None


def _check_fullscreen(x: int, y: int, w: int, h: int) -> bool:
    """Heuristic: window is fullscreen if origin ≈ (0,0) and large."""
    return x <= 0 and y <= 0 and w >= 1280 and h >= 720


def _get_dpi_scale() -> float:
    """Return the display DPI scale factor (best-effort)."""
    try:
        import platform

        if platform.system() == "Darwin":
            # Quartz – NSScreen.mainScreen().backingScaleFactor
            from AppKit import NSScreen  # type: ignore[import-untyped]

            return float(NSScreen.mainScreen().backingScaleFactor())
        if platform.system() == "Windows":
            import ctypes  # noqa: S404

            return ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100.0  # type: ignore[attr-defined]
    except Exception:
        pass
    return 1.0


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def get_active_window() -> Optional[RegionInfo]:
    """Return the active (foreground) window region, or *None*."""
    return _try_pywinctl_active()


def get_window_by_title(title: str) -> Optional[RegionInfo]:
    return _try_pywinctl_by_title(title)


def focus_window(title: str) -> Optional[RegionInfo]:
    """Bring window matching *title* to front and return its region."""
    try:
        import pywinctl  # type: ignore[import-untyped]

        wins = pywinctl.getWindowsWithTitle(title)
        if not wins:
            return None
        win = wins[0]
        try:
            win.activate()
        except Exception:
            pass
        left, top = int(win.left), int(win.top)
        right, bottom = int(win.left + win.width), int(win.top + win.height)
        return RegionInfo(
            bounds=(left, top, right, bottom),
            origin=(left, top),
            is_fullscreen=_check_fullscreen(left, top, int(win.width), int(win.height)),
            dpi_scale=_get_dpi_scale(),
        )
    except Exception:
        return None
