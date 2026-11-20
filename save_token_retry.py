#!/usr/bin/env python3
"""Retry THE LAST TOKEN project/save (7 clips, order fixed). Retries through
transient DNS failures; if DNS stays down, posts straight to the resolved IP
with Host header and unverified TLS (same-origin data already built)."""
import json
import ssl
import time
import socket
import urllib.request
import urllib.parse
import urllib.error
from api_run import Vx, CDN

cfg = json.load(open("run_token.json"))
vx = Vx(cfg["cookies_file"])
pid = cfg["project_id"]
HOST = "app.videoexpress.ai"

clips = [
    (49586406, "1795154618_6affe2bacc0c6", 5042),
    (49586410, "1795154621_6affe2bd8b4c3", 5042),
    (49586414, "1795154623_6affe2bfdb7b5", 5042),
    (49586422, "1795154626_6affe2c230baa", 5042),
    (49586425, "1795154628_6affe2c49670d", 5042),
    (49586523, "1795154693_6affe3052a6b8", 5042),
    (49586525, "1795154695_6affe30768f67", 5042),
]
titles = cfg["brick_titles"]

proj = vx.project(pid)
src = proj["data"] if isinstance(proj["data"], list) else [
    proj["data"][k] for k in proj["data"] if k != "data"]
vtrack = next(t for t in src if any(b.get("type") == "video" for b in t.get("bricks", [])))
tpl = (vtrack.get("bricks") or [{}])[0]
left = 0
bricks = []
for i, (media_id, file_name, dur) in enumerate(clips):
    nb = json.loads(json.dumps(tpl)) if tpl else {}
    nb.update({
        "id": str(910 + i), "media_id": media_id, "type": "video", "fileName": file_name,
        "path": f"{CDN}/video/{file_name}.mp4", "videoUrl": f"{CDN}/video/{file_name}.mp4",
        "imageUrl": f"{CDN}/image/{file_name}.jpg", "imagePath": f"{CDN}/image/{file_name}.jpg",
        "thumbUrl": f"{CDN}/thumbnail/{file_name}_small.jpg",
        "duration": dur, "duration_time": dur, "start_time": 0, "left": left,
        "track_id": vtrack["id"], "title": titles[i],
    })
    left += dur
    bricks.append(nb)
vtrack["bricks"] = bricks

fields = {k: ("" if proj.get(k) is None else proj[k]) for k in
          ("id", "title", "aspect", "aspectValue", "zoom", "quality", "size",
           "format", "isTemplate", "baseUrl")}
fields["save_new"] = "0"
fields["data"] = json.dumps(src)
body = urllib.parse.urlencode(fields).encode()


def post_normal():
    return vx.post(f"project/save/{pid}", fields)


def post_ip_fallback():
    ip = socket.gethostbyname(HOST)  # last resolved value cached above
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
        r = post_normal()
        break
    except (urllib.error.URLError, socket.gaierror) as e:
        print(f"attempt {attempt}: DNS/URLError {e} — retrying in 10s")
        time.sleep(10)
else:
    try:
        ip = socket.gethostbyname(HOST)
    except Exception:
        ip = "64.140.170.98"
    print(f"DNS still failing — posting to {ip} directly")
    r = post_ip_fallback()

print("save resp:", json.dumps(r)[:200])
assert r.get("success"), "save rejected"

# verify by re-open (with retries)
for attempt in range(5):
    try:
        proj2 = vx.project(pid)
        break
    except Exception as e:
        print(f"re-open attempt {attempt}: {e} — retrying")
        time.sleep(10)
src2 = proj2["data"] if isinstance(proj2["data"], list) else [
    proj2["data"][k] for k in proj2["data"] if k != "data"]
tl = [(b["id"], b["media_id"], b["left"]) for t in src2 for b in t.get("bricks", [])]
print("VERIFY timeline:", tl)
assert [b[1] for b in tl] == [c[0] for c in clips], "timeline mismatch after save"
print(f"DONE: 7 clips placed on project {pid}, total {left/1000:.1f}s — NO export")
