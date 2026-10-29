"""Question limits for the public app, kept in server memory so a page reload doesn't reset them.

Two limits over a sliding window: one per visitor (by IP address) and one for all visitors
together, which protects the shared free Gemini quota. A server restart (Streamlit Cloud sleeps
after 12 h without visitors and restarts on every deploy) resets both. Fine for a demo.
"""

import threading
import time
from collections import defaultdict, deque


class QuestionLimits:
    def __init__(self, per_visitor: int, total: int, window_s: float):
        self.per_visitor, self.total, self.window_s = per_visitor, total, window_s
        self._visitors: dict[str, deque[float]] = defaultdict(deque)  # visitor -> question times
        self._all: deque[float] = deque()
        self._lock = threading.Lock()  # each browser session runs in its own thread

    def _forget_old(self, now: float) -> None:
        cutoff = now - self.window_s
        for times in (self._all, *self._visitors.values()):
            while times and times[0] <= cutoff:
                times.popleft()
        for visitor in [v for v, times in self._visitors.items() if not times]:
            del self._visitors[visitor]

    def left(self, visitor: str, now: float | None = None) -> tuple[int, int]:
        """Questions left in the window: (for this visitor, for all visitors together)."""
        now = time.time() if now is None else now
        with self._lock:
            self._forget_old(now)
            return self.per_visitor - len(self._visitors.get(visitor, ())), self.total - len(self._all)

    def free_again_in(self, visitor: str, now: float | None = None) -> float:
        """Seconds until this visitor's oldest question leaves the window (0 if they have none)."""
        now = time.time() if now is None else now
        with self._lock:
            times = self._visitors.get(visitor)
            return max(0.0, times[0] + self.window_s - now) if times else 0.0

    def record(self, visitor: str, now: float | None = None) -> int:
        """Count one answered question. Returns how many all visitors have used in the window."""
        now = time.time() if now is None else now
        with self._lock:
            self._visitors[visitor].append(now)
            self._all.append(now)
            return len(self._all)
