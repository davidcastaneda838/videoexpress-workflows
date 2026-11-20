#!/usr/bin/env python3
"""Re-render THE LAST TOKEN (project 482711) after the scene 2 swap.
Fires render, polls to completion, prints output URL."""
import json, time, urllib.error, socket
from api_run import Vx

cfg = json.load(open("run_token.json"))
vx = Vx(cfg["cookies_file"])
pid = cfg["project_id"]

r = vx.post(f"project/render/{pid}", {"quality": "high"})
print("render resp:", json.dumps(r)[:300])
render_id = r.get("render_id") or r.get("id") or r.get("data", {}).get("id")
assert render_id, f"no render id: {r}"

for i in range(90):
    try:
        s = vx.get(f"project/render-status/{pid}?render_id={render_id}")
        st = s.get("status") or s.get("data", {}).get("status")
        print(i, st)
        if st in ("complete", "completed", "done"):
            print("URL:", json.dumps(s.get("output") or s.get("data", {}))[:400])
            break
        if st in ("failed", "error"):
            print("FAILED:", json.dumps(s)[:400]); break
    except (urllib.error.URLError, socket.gaierror) as e:
        print(i, "net err", e)
    time.sleep(20)
