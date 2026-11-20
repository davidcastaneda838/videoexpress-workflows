"""Poll-until-done logic (poll, wait_audio, wait_videos)."""

import json

import pytest

from conftest import FakeResponse, make_vx, url_handler


def test_poll_returns_when_condition_met(monkeypatch, cookies_file):
    import vx.http as H
    sleeps = []
    monkeypatch.setattr(H.time, "sleep", lambda s: sleeps.append(s))
    seq = iter([None, None, "READY"])
    vx = make_vx(cookies_file, lambda req, timeout=60: FakeResponse())
    out = vx.poll(lambda: next(seq), lambda v: v == "READY", timeout_s=10, interval=0)
    assert out == "READY"


def test_poll_timeout_raises(monkeypatch, cookies_file):
    import vx.http as H
    monkeypatch.setattr(H.time, "sleep", lambda s: None)
    import itertools
    fake_clock = itertools.count(start=1_000_000, step=100).__next__  # races ahead
    monkeypatch.setattr(H.time, "time", fake_clock)
    vx = make_vx(cookies_file, lambda req, timeout=60: FakeResponse())
    with pytest.raises(TimeoutError):
        vx.poll(lambda: None, lambda v: v, timeout_s=5, interval=0)


def test_poll_transient_errors_tolerated(monkeypatch, cookies_file):
    import vx.http as H
    monkeypatch.setattr(H.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("transient")
        return 42

    vx = make_vx(cookies_file, lambda req, timeout=60: FakeResponse())
    assert vx.poll(flaky, lambda v: v == 42, timeout_s=10, interval=0) == 42
    assert calls["n"] == 3


def test_wait_audio_falls_back_to_status(monkeypatch, cookies_file):
    """If generated_audio never lists the uuid but /voice_clone/status says
    done with a mediaUrl, wait_audio still completes (fallback path)."""
    import vx.http as H
    monkeypatch.setattr(H.time, "sleep", lambda s: None)
    polls = {"n": 0}

    def handler(req, timeout=60):
        polls["n"] += 1
        if "/voice_clone/generated_audio" in req.full_url:
            return FakeResponse(body=json.dumps({"data": []}).encode())
        assert "/voice_clone/status/" in req.full_url
        body = {"status": "processing"} if polls["n"] < 6 else \
            {"status": "completed", "mediaUrl": "https://cdn/fallback.mp3",
             "mediaId": 9}
        return FakeResponse(body=json.dumps(body).encode())

    vx = make_vx(cookies_file, handler)
    done = vx.wait_audio("uuid-1", timeout_s=60)
    assert done["src"] == "https://cdn/fallback.mp3"
    assert done["media_id"] == 9


def test_wait_audio_verifies_via_generated_audio(monkeypatch, cookies_file):
    """Regression (live-verified Nov 20): /voice_clone/status can stay empty
    after TTS completes. wait_audio must poll /voice_clone/generated_audio,
    match by uuid, and return the real handle {uuid, media_id, src, ...}."""
    import vx.http as H
    monkeypatch.setattr(H.time, "sleep", lambda s: None)
    polls = {"n": 0}

    def handler(req, timeout=60):
        if "/voice_clone/generated_audio" in req.full_url:
            polls["n"] += 1
            assert "query=" in req.full_url and "type=audio" in req.full_url
            if polls["n"] < 3:
                return FakeResponse(body=json.dumps({"data": []}).encode())
            return FakeResponse(body=json.dumps({"data": [
                {"id": 999, "uuid": "other-uuid", "src": "https://cdn/other.mp3",
                 "length": 1.0, "status": "completed"},
                {"id": 1336270, "uuid": "uuid-1",
                 "src": "https://cdn.clonevoice.ai/x.mp3",
                 "length": 4.47, "status": "completed"},
            ]}).encode())
        if "/voice_clone/status/" in req.full_url:
            # Live bug: status stays empty even though audio is done.
            return FakeResponse(body=json.dumps(
                {"success": False, "status": "", "data": []}).encode())
        raise AssertionError(f"unexpected request: {req.full_url}")

    vx = make_vx(cookies_file, handler)
    done = vx.wait_audio("uuid-1", timeout_s=60)
    assert done == {"uuid": "uuid-1", "media_id": 1336270,
                    "src": "https://cdn.clonevoice.ai/x.mp3",
                    "length": 4.47, "title": None, "status": "completed"}
    assert polls["n"] == 3


def test_wait_audio_timeout_no_repost(monkeypatch, cookies_file):
    """Not found within budget -> TimeoutError and create_audio is never
    re-POSTed (write-once rule)."""
    import vx.http as H
    monkeypatch.setattr(H.time, "sleep", lambda s: None)
    import itertools
    monkeypatch.setattr(H.time, "time",
                        itertools.count(start=1_000_000, step=100).__next__)
    posts = []

    def handler(req, timeout=60):
        if req.get_method() == "POST":
            posts.append(req.full_url)
        if "/voice_clone/generated_audio" in req.full_url:
            return FakeResponse(body=json.dumps({"data": []}).encode())
        if "/voice_clone/create_audio" in req.full_url:
            return FakeResponse(body=json.dumps(
                {"success": True, "uuid": "uuid-1"}).encode())
        if "/voice_clone/status/" in req.full_url:
            return FakeResponse(body=json.dumps(
                {"success": False, "status": "", "data": []}).encode())
        raise AssertionError(f"unexpected request: {req.full_url}")

    vx = make_vx(cookies_file, handler)
    vx.create_audio("hi", "voice-1")  # the one allowed POST
    with pytest.raises(TimeoutError):
        vx.wait_audio("uuid-1", timeout_s=5)
    assert len(posts) == 1 and "create_audio" in posts[0]


def test_wait_videos_polls_library(monkeypatch, cookies_file):
    import vx.http as H
    monkeypatch.setattr(H.time, "sleep", lambda s: None)
    polls = {"n": 0}

    def handler(req, timeout=60):
        assert "/api/library/get_media/" in req.full_url
        polls["n"] += 1
        status = "processing" if polls["n"] < 3 else "completed"
        return FakeResponse(body=json.dumps(
            {"results": [{"id": 900, "fileName": "f1", "duration": 5.0,
                          "status": status}]}).encode())

    vx = make_vx(cookies_file, handler)
    done = vx.wait_videos({1}, expected=1, timeout_s=60)
    assert done[0]["id"] == 900 and done[0]["status"] == "completed"
