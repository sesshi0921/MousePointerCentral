from __future__ import annotations

import time

from .config import CONFIG

try:
    import pyautogui
except Exception:  # pragma: no cover - optional in test env
    pyautogui = None


class Mouse:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        if pyautogui is not None:
            pyautogui.FAILSAFE = CONFIG.failsafe
            pyautogui.PAUSE = CONFIG.pause

    def execute(self, a: dict) -> None:
        if self.dry_run:
            return
        if pyautogui is None:
            raise RuntimeError("pyautogui is required for non-dry-run execution")
        t = a["type"]
        if t == "move":
            pyautogui.moveTo(*a["to"], duration=a.get("duration", 0.3))
        elif t == "wait":
            time.sleep(a["seconds"])
        elif t == "click":
            if a.get("at"):
                pyautogui.moveTo(*a["at"])
            pyautogui.click(button=a.get("button", "left"), clicks=a.get("clicks", 1))
        elif t == "drag":
            pyautogui.moveTo(*a["from"])
            pyautogui.dragTo(*a["to"], duration=a.get("duration", 0.4), button=a.get("button", "left"))
        elif t == "type":
            pyautogui.typewrite(a["text"], interval=a.get("interval", 0.02))
        elif t == "key":
            pyautogui.hotkey(*a["keys"])
        elif t == "scroll":
            if a.get("at"):
                pyautogui.moveTo(*a["at"])
            pyautogui.scroll(a["amount"])
