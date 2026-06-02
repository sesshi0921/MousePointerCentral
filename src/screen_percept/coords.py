"""Coordinate-space definitions and transforms (§2).

Every coordinate value in the system carries a ``coord_space`` tag.
All conversions MUST go through the helpers in this module so that
MCP-A and MCP-B stay in sync.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class CoordSpace(str, Enum):
    """Coordinate spaces used across MCP-A / MCP-B."""

    SCREEN = "screen"        # virtual-desktop origin, logical px
    DISPLAY = "display"      # single-monitor origin, logical px
    WINDOW = "window"        # window-local origin, logical px
    CROP = "crop"            # cropped image origin, image px
    UPSCALED = "upscaled"    # crop × k, image px


# ---------------------------------------------------------------------------
# Lightweight point / rectangle types
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Point:
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class Rect:
    """Axis-aligned rectangle expressed as (x1, y1, x2, y2)."""

    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    @property
    def center(self) -> Point:
        return Point((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def as_tuple(self) -> tuple[int, int, int, int]:
        return (self.x1, self.y1, self.x2, self.y2)


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------

def crop_to_window(point: Sequence[int], dpi_scale: float = 1.0) -> tuple[int, int]:
    """Convert *crop* image-px → *window* logical-px."""
    return (round(point[0] / dpi_scale), round(point[1] / dpi_scale))


def window_to_screen(
    point: Sequence[int],
    window_origin: Sequence[int],
) -> tuple[int, int]:
    """Convert *window* logical-px → *screen* logical-px."""
    return (point[0] + window_origin[0], point[1] + window_origin[1])


def crop_to_screen(
    point: Sequence[int],
    window_origin: Sequence[int],
    dpi_scale: float = 1.0,
) -> tuple[int, int]:
    """Convenience: *crop* → *window* → *screen* in one call."""
    wx, wy = crop_to_window(point, dpi_scale)
    return window_to_screen((wx, wy), window_origin)


def screen_to_window(
    point: Sequence[int],
    window_origin: Sequence[int],
) -> tuple[int, int]:
    return (point[0] - window_origin[0], point[1] - window_origin[1])


def window_to_crop(point: Sequence[int], dpi_scale: float = 1.0) -> tuple[int, int]:
    return (round(point[0] * dpi_scale), round(point[1] * dpi_scale))


def upscaled_to_crop(point: Sequence[int], scale_k: float) -> tuple[int, int]:
    """Convert *upscaled* → *crop* by dividing by the upscale factor *k*."""
    return (round(point[0] / scale_k), round(point[1] / scale_k))


def crop_to_upscaled(point: Sequence[int], scale_k: float) -> tuple[int, int]:
    return (round(point[0] * scale_k), round(point[1] * scale_k))
