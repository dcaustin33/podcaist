# podcaist/progress.py
from typing import Callable, Dict, Optional

StepHandler = Callable[[Dict[str, str]], None]

class Progress:
    """
    Report progress of a N‑step pipeline through an arbitrary callback.
    The callback receives a JSON‑serialisable dict, e.g.
    {"current": 3, "total": 7, "message": "Generating audio"}.
    """
    def __init__(self, total: int, cb: Optional[StepHandler]):
        self.total = total
        self.i = 0
        self.cb = cb

    def step(self, message: str) -> None:
        self.i += 1
        if self.cb:
            self.cb({"current": self.i, "total": self.total, "message": message})