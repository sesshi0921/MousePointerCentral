from __future__ import annotations

import platform
import subprocess
from pathlib import Path

from .config import CONFIG


class Recorder:
    def __init__(self):
        self.proc: subprocess.Popen | None = None

    def _platform_input(self) -> list[str]:
        system = platform.system().lower()
        if system == "darwin":
            return ["-f", "avfoundation", "-i", "1:none"]
        if system == "windows":
            return ["-f", "gdigrab", "-i", "desktop"]
        return ["-f", "x11grab", "-i", ":0.0"]

    def start(self, out_path: str | Path, fps: int = CONFIG.fps) -> None:
        out = str(out_path)
        cmd = [CONFIG.ffmpeg, "-y", *self._platform_input(), "-r", str(fps), "-pix_fmt", "yuv420p", out]
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop(self) -> None:
        if not self.proc:
            return
        if self.proc.poll() is not None:
            self.proc = None
            return
        try:
            self.proc.communicate(input=b"q", timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        finally:
            self.proc = None
