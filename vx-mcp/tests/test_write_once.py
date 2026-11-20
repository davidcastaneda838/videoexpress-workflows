"""Write-once policy: a lost response must be verified via reads before any retry."""

import json

import pytest

import vx.http as _vxhttp

from conftest import FakeResponse, make_vx, url_handler


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(_vxhttp.time, "sleep", lambda s: None)
    # fast-forward clock so 60s verify-timeouts expire instantly
    import itertools
    monkeypatch.setattr(_vxhttp.time, "time",
                        itertools.count(step=10).__next__)


def _post_target(req):
    return req.full_url.endswith("/ai/api/save_generated_image") and req.method == "POST"


def test_write_success_fires_exactly_once(cookies_file):
    calls = {"n": 0}

    def handler(req, timeout=60):
        if _post_target(req):
            calls["n"] += 1
            return FakeResponse(body=json.dumps({"success": True}).encode())
        raise AssertionError("unexpected")

    vx = make_vx(cookies_file, handler)
    r = vx.write_once(lambda: vx.post("/ai/api/save_generated_image",
                                      {"uuid": "u1"}), description="save")
    assert r["success"] is True
    assert calls["n"] == 1  # fired ONCE


def test_lost_response_then_found_in_library_no_retry(cookies_file):
    """POST raises -> exists() finds the item -> the write is NOT re-fired."""
    calls = {"post": 0, "exists": 0}

    def handler(req, timeout=60):
        if _post_target(req):
            calls["post"] += 1
            raise ConnectionResetError("response lost")
        if "library" in req.full_url:
            calls["exists"] += 1
            return FakeResponse(body=json.dumps(
                {"results": [{"id": 77, "uuid": "u1"}]}).encode())
        raise AssertionError("unexpected")

    vx = make_vx(cookies_file, handler)
    result = vx.write_once(
        lambda: vx.post("/ai/api/save_generated_image", {"uuid": "u1"}),
        exists=lambda: (lambda items: items[0] if items else None)(
            [m for m in vx.get("/library/get_media/4")["results"] if m["uuid"] == "u1"]),
        description="save")
    assert result == {"id": 77, "uuid": "u1"}  # real existing handle
    assert calls["post"] == 1   # NEVER re-fired
    assert calls["exists"] >= 1  # verified via library read


def test_lost_response_verified_absent_single_retry(cookies_file):
    """POST raises -> library read confirms absent -> exactly one retry."""
    calls = {"post": 0, "exists": 0}

    def handler(req, timeout=60):
        if _post_target(req):
            calls["post"] += 1
            if calls["post"] == 1:
                raise ConnectionResetError("response lost")
            return FakeResponse(body=json.dumps({"success": True, "attempt": 2}).encode())
        if "library" in req.full_url:
            calls["exists"] += 1
            return FakeResponse(body=json.dumps({"results": []}).encode())
        raise AssertionError("unexpected")

    vx = make_vx(cookies_file, handler)
    result = vx.write_once(
        lambda: vx.post("/ai/api/save_generated_image", {"uuid": "u1"}),
        exists=lambda: None if not vx.get("/library/get_media/4")["results"] else True,
        description="save")
    assert result["attempt"] == 2
    assert calls["post"] == 2  # original + exactly one verified retry


def test_no_verify_raises_without_retry(cookies_file):
    calls = {"n": 0}

    def handler(req, timeout=60):
        if _post_target(req):
            calls["n"] += 1
            raise ConnectionResetError("boom")
        raise AssertionError("unexpected")

    vx = make_vx(cookies_file, handler)
    with pytest.raises(ConnectionResetError):
        vx.write_once(lambda: vx.post("/ai/api/save_generated_image", {}))
    assert calls["n"] == 1  # no blind retry
