#!/usr/bin/env python3
"""Swap scene 2's regenerated clip (49587735) onto the project 482711 timeline,
replacing the defective one (49586410), then re-open + verify."""
import json
from api_run import Vx, CDN

cfg = json.load(open("run_token.json"))
vx = Vx(cfg["cookies_file"])
pid = cfg["project_id"]
OLD = 49586410
NEW = 49587735
NEW_FILE = "1795155550_6affe65e87c54"
NEW_DUR = 5042

proj = vx.project(pid)
src = proj["data"] if isinstance(proj["data"], list) else [
    proj["data"][k] for k in proj["data"] if k != "data"]
swapped = 0
for t in src:
    for b in t.get("bricks", []):
        if b.get("media_id") == OLD:
            b.update({
                "media_id": NEW, "fileName": NEW_FILE,
                "path": f"{CDN}/video/{NEW_FILE}.mp4",
                "videoUrl": f"{CDN}/video/{NEW_FILE}.mp4",
                "imageUrl": f"{CDN}/image/{NEW_FILE}.jpg",
                "imagePath": f"{CDN}/image/{NEW_FILE}.jpg",
                "thumbUrl": f"{CDN}/thumbnail/{NEW_FILE}_small.jpg",
                "duration": NEW_DUR, "duration_time": NEW_DUR,
            })
            swapped += 1
assert swapped == 1, f"expected 1 brick swap, got {swapped}"

fields = {k: ("" if proj.get(k) is None else proj[k]) for k in
          ("id", "title", "aspect", "aspectValue", "zoom", "quality", "size",
           "format", "isTemplate", "baseUrl")}
fields["save_new"] = "0"
fields["data"] = json.dumps(src)

# DNS-resilient save: retry through transient failures, then IP-fallback POST
import ssl, socket, time, urllib.request, urllib.parse, urllib.error
HOST = "app.videoexpress.ai"
body = urllib.parse.urlencode(fields).encode()

def post_ip_fallback():
    try:
        ip = socket.gethostbyname(HOST)
    except Exception:
        ip = "64.140.170.98"
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(f"https://{ip}/project/save/{pid}", data=body,
                                 headers=dict(vx._headers("application/x-www-form-urlencoded; charset=UTF-8"),
                                              Host=HOST), method="POST")
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        return json.loads(r.read().decode())

for attempt in range(1, 8):
    try:
        r = vx.post(f"project/save/{pid}", fields)
        break
    except (urllib.error.URLError, socket.gaierror) as e:
        print(f"attempt {attempt}: DNS/URLError {e} — retrying in 10s")
        time.sleep(10)
else:
    print("DNS still failing — posting to IP directly")
    r = post_ip_fallback()
assert r.get("success"), f"save rejected: {r}"

proj2 = vx.project(pid)
src2 = proj2["data"] if isinstance(proj2["data"], list) else [
    proj2["data"][k] for k in proj2["data"] if k != "data"]
tl = [(b.get("title"), b["media_id"]) for t in src2 for b in t.get("bricks", [])]
print("VERIFY timeline:", tl)
assert [b[1] for b in tl] == [49586406, NEW, 49586414, 49586422, 49586425, 49586523, 49586525], "swap mismatch"
print("DONE: scene 2 swapped in, timeline verified — NO export")
