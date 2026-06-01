from __future__ import annotations

import queue
import threading
import time


class Worker(threading.Thread):
    def __init__(self, mouse, max_queue: int):
        super().__init__(daemon=True)
        self.q: queue.Queue[dict] = queue.Queue(maxsize=max_queue)
        self.run_event = threading.Event()
        self.done_event = threading.Event()
        self.abort_flag = threading.Event()
        self.mouse = mouse
        self.log: list[dict] = []

    def _drain(self) -> int:
        drained = 0
        while True:
            try:
                self.q.get_nowait()
                drained += 1
            except queue.Empty:
                return drained

    def run(self) -> None:
        while True:
            self.run_event.wait()
            if self.abort_flag.is_set():
                self._drain()
                self.abort_flag.clear()
                self.run_event.clear()
                self.done_event.set()
                continue
            try:
                action = self.q.get(timeout=0.1)
            except queue.Empty:
                self.run_event.clear()
                self.done_event.set()
                continue
            ts = time.time()
            try:
                self.mouse.execute(action)
                self.log.append({"action": action, "t": ts})
            except Exception as exc:  # pragma: no cover - defensive
                self.log.append({"action": action, "t": ts, "error": str(exc)})
