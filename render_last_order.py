#!/usr/bin/env python3
"""Render run_last_order_render.json with DNS pinned for app.videoexpress.ai
(Python resolver intermittently flakes on this host; nslookup/curl work)."""
import runpy
import socket
import sys

VX_IP = "64.140.170.98"
_orig = socket.getaddrinfo


def pinned(host, *a, **kw):
    if host == "app.videoexpress.ai":
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (VX_IP, 443))]
    return _orig(host, *a, **kw)


socket.getaddrinfo = pinned
sys.argv = ["api_run.py", "run_last_order_render.json", "--dry-run"]
runpy.run_path("api_run.py", run_name="__main__")
