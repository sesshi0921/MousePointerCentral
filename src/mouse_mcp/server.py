from __future__ import annotations

import datetime as dt
import os
import platform
from pathlib import Path

from .actions import validate_actions
from .config import CONFIG
from .mouse import Mouse
from .recorder import Recorder
from .report import generate_report
from .worker import Worker

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover - fallback for local tests
    class FastMCP:  # type: ignore[override]
        def __init__(self, name: str):
            self.name = name

        def tool(self):
            def decorator(fn):
                return fn

            return decorator


def _screen_size() -> tuple[int, int, float]:
    if platform.system().lower() == "linux" and not os.getenv("DISPLAY"):
        return 1920, 1080, 1.0
    try:
        import pyautogui

        width, height = pyautogui.size()
    except Exception:
        width, height = (1920, 1080)
    return int(width), int(height), 1.0


mcp = FastMCP("mouse-mcp")
_mouse = Mouse(dry_run=False)
_worker = Worker(_mouse, CONFIG.max_queue)
_worker.start()
_recorder = Recorder()
_recording_dir: Path | None = None
_recording = False


def _new_output_dir(name: str | None = None) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = f"-{name}" if name else ""
    target = CONFIG.output_dir / f"{stamp}{suffix}"
    target.mkdir(parents=True, exist_ok=True)
    return target


@mcp.tool()
def get_screen_info() -> dict:
    width, height, scale = _screen_size()
    return {"width": width, "height": height, "scale": scale, "platform": platform.system()}


@mcp.tool()
def enqueue_actions(actions: list[dict]) -> dict:
    width, height, _ = _screen_size()
    accepted, rejected = validate_actions(actions, width, height)
    for action in accepted:
        _worker.q.put(action)
    return {"accepted": len(accepted), "rejected": rejected, "queue_size": _worker.q.qsize()}


@mcp.tool()
def peek_queue() -> dict:
    actions = list(_worker.q.queue)
    return {"queue_size": _worker.q.qsize(), "actions": actions}


@mcp.tool()
def clear_queue() -> dict:
    cleared = _worker._drain()
    return {"cleared": cleared}


@mcp.tool()
def start_recording(name: str | None = None) -> dict:
    global _recording_dir, _recording
    _recording_dir = _new_output_dir(name)
    path = _recording_dir / "recording.mp4"
    _recorder.start(path)
    _recording = True
    return {"recording_path": str(path)}


@mcp.tool()
def stop_recording() -> dict:
    global _recording
    if _recording_dir is None:
        return {"video_path": None, "html_path": None}
    _recorder.stop()
    _recording = False
    html_path = generate_report(_recording_dir, _recording_dir.name, _worker.log)
    return {"video_path": str(_recording_dir / "recording.mp4"), "html_path": str(html_path)}


@mcp.tool()
def execute(record: bool = True, name: str | None = None, dry_run: bool = False) -> dict:
    global _mouse
    _mouse.dry_run = dry_run
    _worker.done_event.clear()
    started = None
    if record:
        started = start_recording(name)
    _worker.run_event.set()
    _worker.done_event.wait()
    video_path = None
    html_path = None
    if record:
        stopped = stop_recording()
        video_path = stopped["video_path"]
        html_path = stopped["html_path"]
    return {
        "status": "completed",
        "recording_path": started["recording_path"] if started else None,
        "video_path": video_path,
        "html_path": html_path,
        "log": _worker.log,
    }


@mcp.tool()
def abort() -> dict:
    _worker.abort_flag.set()
    _worker.run_event.set()
    return {"aborted": True}


@mcp.tool()
def get_status() -> dict:
    state = "running" if _worker.run_event.is_set() else "idle"
    return {"worker_state": state, "queue_size": _worker.q.qsize(), "recording": _recording}
