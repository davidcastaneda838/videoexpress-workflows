"""DNS-resilient wrapper for api_run.Vx: every get/post retries through
transient DNS failures and falls back to direct-IP POST with a Host header.
Import `Vx` from here instead of api_run when DNS is flaky."""
import json
import ssl
import socket
import time
import urllib.request
import urllib.parse
import urllib.error

from api_run import Vx as _Vx, BASE

HOST = "app.videoexpress.ai"
FALLBACK_IP = "64.140.170.98"


def _dns_resilient(fn, kind):
    for attempt in range(1, 8):
        try:
            return fn()
        except (urllib.error.URLError, socket.gaierror) as e:
            print(f"  [{kind}] attempt {attempt}: DNS/URLError {e} — retrying in 10s")
            time.sleep(10)
    # fall back to direct-IP POST with Host header
    ip = FALLBACK_IP
    print(f"  [{kind}] DNS still failing — direct-IP fallback to {ip}")
    return fn(ip_override=ip)


class Vx(_Vx):
    def get(self, path):
        def go(ip_override=None):
            host = ip_override or HOST
            url = f"https://{host}{path}"
            headers = self._headers()
            if ip_override:
                headers["Host"] = HOST
            if ip_override:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
                    return json.loads(r.read().decode())
            return _Vx.get(self, path)
        return _dns_resilient(go, "get")

    def post(self, path, fields=None, json_body=None):
        def go(ip_override=None):
            if json_body is not None:
                data = json.dumps(json_body).encode()
                ct = "application/json"
            else:
                data = urllib.parse.urlencode(fields or {}).encode()
                ct = "application/x-www-form-urlencoded; charset=UTF-8"
            headers = self._headers(ct)
            if ip_override:
                headers["Host"] = HOST
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(f"https://{ip_override}{path}", data=data,
                                             headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
                    return json.loads(r.read().decode())
            return _Vx.post(self, path, fields, json_body)
        return _dns_resilient(go, "post")
