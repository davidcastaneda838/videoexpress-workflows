"""HARD RULE: at most 5 concurrent video-generation jobs, ever."""
import threading
from contextlib import contextmanager

MAX_INFLIGHT_VIDEOS = 5


class VideoJobLimiter:
    """Semaphore-based 5-slot limiter for video generation jobs.

    A slot must be held from the moment the generation POST is fired until
    the job is observed finished (or abandoned) in the library.
    """

    def __init__(self, max_inflight=MAX_INFLIGHT_VIDEOS):
        self.max_inflight = max_inflight
        self._sem = threading.BoundedSemaphore(max_inflight)
        self._lock = threading.Lock()
        self.active = 0

    @contextmanager
    def slot(self, timeout=None):
        acquired = (self._sem.acquire(timeout=timeout) if timeout is not None
                    else self._sem.acquire())
        if not acquired:
            raise TimeoutError(f"no free video slot within {timeout}s")
        with self._lock:
            self.active += 1
        try:
            yield self
        finally:
            with self._lock:
                self.active -= 1
            self._sem.release()

    @property
    def in_use(self):
        with self._lock:
            return self.active
