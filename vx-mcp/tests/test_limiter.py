"""5-slot video-job limiter: HARD RULE max 5 concurrent video jobs."""

import threading
import time

import pytest

from vx.limiter import VideoJobLimiter, MAX_INFLIGHT_VIDEOS


def test_max_is_five():
    assert MAX_INFLIGHT_VIDEOS == 5


def test_five_slots_then_blocks():
    lim = VideoJobLimiter()
    held = []
    for _ in range(5):
        cm = lim.slot()
        cm.__enter__()
        held.append(cm)
    assert lim.in_use == 5
    # 6th must NOT be acquirable (non-blocking probe)
    got = []
    t = threading.Thread(target=lambda: got.append(_try(lim)))
    t.start()
    t.join(1.0)
    assert got == [False]


def _try(lim):
    try:
        with lim.slot(timeout=0.2):
            return True
    except TimeoutError:
        return False


def test_release_frees_slot():
    lim = VideoJobLimiter()
    with lim.slot():
        assert lim.in_use == 1
    assert lim.in_use == 0
    with lim.slot():  # slot reusable after release
        pass


def test_parallel_threads_never_exceed_five():
    lim = VideoJobLimiter()
    peak = []
    lock = threading.Lock()

    def work():
        with lim.slot():
            with lock:
                peak.append(lim.in_use)
            time.sleep(0.01)

    threads = [threading.Thread(target=work) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert max(peak) <= 5
