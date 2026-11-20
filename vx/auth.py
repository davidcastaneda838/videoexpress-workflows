"""Cookie-file auth for VideoExpress (cookies.json = browser cookie export)."""
import json
import os


def load_cookies(path):
    """Load a cookie jar exported as [{name, value}, ...] and return a dict."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict):  # already a name->value map
        return {str(k): str(v) for k, v in raw.items()}
    return {c["name"]: c["value"] for c in raw}


def cookie_header(cookies):
    """Build the Cookie request-header value from a name->value dict."""
    return "; ".join(f"{name}={value}" for name, value in cookies.items())


class CookieAuth:
    """Holds the cookie jar and builds request headers."""

    def __init__(self, cookies_file):
        if not cookies_file:
            raise ValueError("cookies_file is required (or set VX_COOKIES)")
        self.cookies_file = cookies_file
        self.cookies = load_cookies(cookies_file)

    def reload(self):
        self.cookies = load_cookies(self.cookies_file)

    def headers(self, content_type=None, extra=None):
        h = {
            "Cookie": cookie_header(self.cookies),
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0",
        }
        if content_type:
            h["Content-Type"] = content_type
        if extra:
            h.update(extra)
        return h


def cookies_file_from(env=None, arg=None):
    """Resolve the cookies file: explicit arg > VX_COOKIES env > None."""
    return arg or (env or os.environ.get("VX_COOKIES")) or None
