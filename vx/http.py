"""HTTP core for the VideoExpress app endpoints (cookie-session XHR).

Transport is injectable (opener) so tests can mock HTTP without network.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

from .auth import CookieAuth

BASE = "https://app.videoexpress.ai"
CDN = "https://cdn-ny-b.videoexpress.ai"
PREVIEW = "https://user-assets.renderplatform.com/preview"

FORM_CT = "application/x-www-form-urlencoded; charset=UTF-8"


class VxHttp:
    def __init__(self, cookies_file, opener=None):
        self.auth = CookieAuth(cookies_file)
        self.opener = opener or urllib.request.build_opener()

    # ---------- request core ----------

    def _open(self, req, timeout=60):
        return self.opener.open(req, timeout=timeout)

    def get(self, path, timeout=60):
        req = urllib.request.Request(BASE + path, headers=self.auth.headers())
        with self._open(req, timeout) as r:
            return json.loads(r.read().decode())

    def post(self, path, fields=None, json_body=None, timeout=60):
        if json_body is not None:
            data = json.dumps(json_body).encode()
            ct = "application/json"
        else:
            data = urllib.parse.urlencode(fields or {}).encode()
            ct = FORM_CT
        req = urllib.request.Request(
            BASE + path, data=data, headers=self.auth.headers(content_type=ct), method="POST")
        with self._open(req, timeout) as r:
            return json.loads(r.read().decode())

    def delete(self, path, timeout=60):
        req = urllib.request.Request(BASE + path, headers=self.auth.headers(), method="DELETE")
        with self._open(req, timeout) as r:
            return r.status

    def download(self, url, dest, timeout=300):
        req = urllib.request.Request(url, headers=self.auth.headers())
        with self._open(req, timeout) as r, open(dest, "wb") as f:
            f.write(r.read())
        return dest

    def head_ok(self, url, min_bytes=0, timeout=30):
        req = urllib.request.Request(url, method="HEAD", headers=self.auth.headers())
        try:
            with self._open(req, timeout) as r:
                return r.status == 200 and int(r.headers.get("Content-Length") or 0) > min_bytes
        except Exception:
            return False

    # ---------- polling ----------

    def poll(self, fetch_fn, until, timeout_s, interval=15, label=""):
        """Poll fetch_fn until until(value) is truthy or timeout.

        Transient fetch errors are logged and retried until the deadline.
        Raises TimeoutError when the deadline passes.
        """
        deadline = time.time() + timeout_s
        i = 0
        while time.time() < deadline:
            try:
                v = fetch_fn()
                if until(v):
                    return v
            except Exception as e:  # transient network/API hiccups
                print(f"  [{label}] poll {i}: transient error {e}")
            time.sleep(interval)
            i += 1
        raise TimeoutError(f"{label}: timed out after {timeout_s}s")

    # ---------- HARD RULE: write-once policy ----------

    def write_once(self, fire, exists=None, description="write"):
        """Fire a write exactly ONCE.

        If the request errors (response possibly lost), do NOT blindly retry:
        poll the read-only `exists()` handle first. Only when the write is
        verifiably ABSENT is a single retry permitted. If it IS present, the
        real handle is returned instead of re-firing.
        """
        try:
            return fire()
        except Exception:
            if exists is None:
                raise
            try:
                existing = self.poll(exists, lambda v: bool(v), timeout_s=60,
                                     interval=5, label=f"{description} verify-after-loss")
                return existing  # write had landed despite the lost response
            except TimeoutError:
                return fire()  # verified absent -> the one allowed retry
