#!/usr/bin/env python3
"""Place-only recovery for run_last_order: generation is DONE (all 15 clips
completed in the library); redo ONLY the timeline placement with retries."""
import json
import re
import time
from api_run import Vx, CDN, FOLDER_VIDEOS

cfg = json.load(open("run_last_order.json"))
pid = cfg["project_id"]
vx = Vx(cfg["cookies_file"])

tags = {f"R{i:02d}": i for i in range(1, 16)}
drama = []
for attempt in range(4):
    drama = []
    try:
        for m in vx.media_list(FOLDER_VIDEOS, limit=100):
            mt = re.match(r"^R(\d{2})\s*—", m.get("name") or "")
            if mt and f"R{mt.group(1)}" in tags and m.get("status") == "completed":
                drama.append((tags[f"R{mt.group(1)}"], m))
        break
    except Exception as e:
        print(f"  media_list attempt {attempt + 1} failed: {e}")
        time.sleep(20)
assert len(drama) == 15, f"found {len(drama)} of 15 drama clips: {[d[0] for d in drama]}"
drama.sort(key=lambda x: x[0])
clips = [(m["id"], m["fileName"], round(m["duration"])) for _, m in drama]
print("Clips in story order: " + ", ".join(f"R{i:02d}->{c[0]}" for (i, _), c in zip(drama, clips)))

# ---- assemble timeline ----
proj = vx.project(pid)
src = proj["data"] if isinstance(proj["data"], list) else [
    proj["data"][k] for k in proj["data"] if k != "data"]
vtrack = next((t for t in src if any(b.get("type") == "video" for b in t.get("bricks", []))), None)
if vtrack is None:
    vtrack = next(t for t in src if t.get("index") == 0)
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
        "track_id": vtrack["id"], "title": cfg["brick_titles"][i],
    })
    left += dur
    bricks.append(nb)
vtrack["bricks"] = bricks

fields = {k: ("" if proj.get(k) is None else proj[k]) for k in
          ("id", "title", "aspect", "aspectValue", "zoom", "quality", "size",
           "format", "isTemplate", "baseUrl")}
fields["save_new"] = "0"
fields["data"] = json.dumps(src)

# retry the save against transient DNS; final fallback = DNS-free curl --resolve
r = None
for attempt in range(5):
    try:
        r = vx.post(f"project/save/{pid}", fields)
        break
    except Exception as e:
        print(f"  save attempt {attempt + 1} failed: {e}")
        time.sleep(15)
if r is None or not r.get("success"):
    print("Falling back to DNS-free curl --resolve...")
    ip = "64.140.170.98"
    with open("last_order_save_payload.txt", "w", encoding="utf-8") as f:
        import urllib.parse
        f.write(urllib.parse.urlencode(fields))
    out = f"last_order_save_resp.json"
    cmd = (f'curl -s --resolve app.videoexpress.ai:443:{ip} -X POST '
           f'"https://app.videoexpress.ai/project/save/{pid}" '
           f'-H "X-Requested-With: XMLHttpRequest" '
           f'-H "Content-Type: application/x-www-form-urlencoded; charset=UTF-8" '
           f'--cookie "$(cat vx_cookie_header.txt)" --data-binary @last_order_save_payload.txt -o {out}')
    import subprocess
    subprocess.run(["bash", "-c", cmd], check=True)
    r = json.load(open(out))
    if not r.get("success"):
        raise RuntimeError(f"curl save rejected: {r}")

proj2 = vx.project(pid)
src2 = proj2["data"] if isinstance(proj2["data"], list) else [
    proj2["data"][k] for k in proj2["data"] if k != "data"]
tl = [(b["id"], b["media_id"], b["left"]) for t in src2 for b in t.get("bricks", [])]
print(f"VERIFY: {r} timeline={tl}")
assert [b[1] for b in tl] == [c[0] for c in clips], "timeline mismatch after save"
print(f"DONE: {len(clips)} clips placed on project {pid} timeline, total {left/1000:.1f}s — NO export")
