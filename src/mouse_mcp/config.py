from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    output_dir: Path
    ffmpeg: str
    fps: int
    failsafe: bool
    pause: float
    max_queue: int


CONFIG = Config(
    output_dir=Path(os.getenv("MOUSE_MCP_OUTPUT_DIR", "./output")),
    ffmpeg=os.getenv("MOUSE_MCP_FFMPEG", "ffmpeg"),
    fps=int(os.getenv("MOUSE_MCP_FPS", "15")),
    failsafe=_as_bool(os.getenv("MOUSE_MCP_FAILSAFE"), True),
    pause=float(os.getenv("MOUSE_MCP_PAUSE", "0.1")),
    max_queue=int(os.getenv("MOUSE_MCP_MAX_QUEUE", "500")),
)
