#!/usr/bin/env python3
"""Render THE LAST TOKEN (project 482711) from clips config with the DNS-resilient
Vx wrapper. Dry-run only (clips already generated). Downloads to ~/Downloads."""
import json
import os
import time
from dns_vx import Vx
from api_run import CDN

cfg = json.load(open("run_token_render.json"))
vx = Vx(cfg["cookies_file"])
out_dir = os.path.expanduser("~/Downloads")

clips = cfg["clips"]
print(f"Rendering {len(clips)} bricks, total {sum(c['duration_ms'] for c in clips)/1000:.1f}s...")


def _head_ok(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200 and int(r.headers.get("Content-Length") or 0) > 100_000
    except Exception:
        return False


import urllib.request
for c in clips:
    url = f"{CDN}/video/{c['file_name']}.mp4"
    for i in range(30):
        if _head_ok(url):
            break
        print(f"  propagate {c['file_name'][-12:]}: waiting ({i})")
        time.sleep(10)
    else:
        raise TimeoutError(f"CDN propagation failed for {c['file_name']}")

baseline_out = {o["id"] for o in vx.outputs()}
r, left = vx.render(cfg["project_id"], clips, cfg["export_name"],
                    cfg.get("project_title"), cfg.get("aspect", "9:16"))
print(f"  queued: {r}")
o = vx.wait_output(baseline_out)
assert o is not None
dest = os.path.join(out_dir, cfg["export_name"] + ".mp4")
vx.download(o["mediaPath"], dest)
print(f"DONE: {dest} ({o['filesize']}) — verify with ffprobe: expected {left/1000:.1f}s")
