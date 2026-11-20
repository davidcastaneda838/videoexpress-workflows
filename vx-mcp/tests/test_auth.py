"""Auth header building from a cookie file."""

import vx.auth as auth


def test_load_cookies_list(cookies_file):
    cookies = auth.load_cookies(cookies_file)
    assert cookies == {"session": "abc123", "csrftoken": "xyz789"}


def test_load_cookies_dict(tmp_path):
    p = tmp_path / "c.json"
    p.write_text('{"session": "tok"}')
    assert auth.load_cookies(str(p)) == {"session": "tok"}


def test_cookie_header_format():
    h = auth.cookie_header({"a": "1", "b": "2"})
    assert h == "a=1; b=2"


def test_headers_content():
    a = auth.CookieAuth(cookies_file := None) if False else None
    # build via real file
    import json, os
    p = os.path.join(os.path.dirname(__file__), "..", "..")
    from vx.auth import CookieAuth
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump([{"name": "sid", "value": "S"}], f)
        path = f.name
    a = CookieAuth(path)
    h = a.headers()
    assert h["Cookie"] == "sid=S"
    assert h["X-Requested-With"] == "XMLHttpRequest"
    h2 = a.headers(content_type="application/json")
    assert h2["Content-Type"] == "application/json"
    os.unlink(path)


def test_cookies_file_from_env(monkeypatch, tmp_path):
    import vx.auth as A
    monkeypatch.delenv("VX_COOKIES", raising=False)
    assert A.cookies_file_from() is None
    monkeypatch.setenv("VX_COOKIES", "x.json")
    assert A.cookies_file_from() == "x.json"
    assert A.cookies_file_from(arg="y.json") == "y.json"
