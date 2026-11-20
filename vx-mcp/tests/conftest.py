"""Shared fakes: mock HTTP transport + Vx client factory (no live calls)."""

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)


class FakeResponse:
    def __init__(self, status=200, body=b"{}", headers=None):
        self.status = status
        self._body = body if isinstance(body, bytes) else body.encode()
        self.headers = headers or {}

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeOpener:
    """Records every request; handler(req, timeout) -> FakeResponse or raises."""

    def __init__(self, handler):
        self.handler = handler
        self.requests = []

    def open(self, req, timeout=60):
        self.requests.append(req)
        return self.handler(req, timeout)


@pytest.fixture
def cookies_file(tmp_path):
    p = tmp_path / "cookies.json"
    p.write_text(json.dumps([
        {"name": "session", "value": "abc123"},
        {"name": "csrftoken", "value": "xyz789"},
    ]))
    return str(p)


def make_vx(cookies_file, handler):
    from vx import Vx
    return Vx(cookies_file, opener=FakeOpener(handler))


def url_handler(routes):
    """routes: list of (predicate(req), responder) tried in order."""

    def handler(req, timeout=60):
        for pred, resp in routes:
            if pred(req):
                r = resp(req)
                if isinstance(r, Exception):
                    raise r
                return r
        raise AssertionError(f"unexpected request: {req.full_url}")

    return handler
