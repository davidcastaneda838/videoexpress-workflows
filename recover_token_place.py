#!/usr/bin/env python3
"""Recovery for THE LAST TOKEN: generation already succeeded (videos completed
server-side); the process died at project/save on transient DNS. This script
pulls the 7 completed clips from My AI Videos and redoes ONLY the placement."""
import json
from api_run import Vx, FOLDER_VIDEOS, CDN

cfg = json.load(open("run_token.json"))
vx = Vx(cfg["cookies_file"])
pid = cfg["project_id"]

done = [m for m in vx.media_list(FOLDER_VIDEOS, limit=100) if m.get("status") == "completed"]
done.sort(key=lambda m: m["id"])
clips = [(m["id"], m["fileName"], round(m["duration"])) for m in done[-7:]]
print("Recovered clips (oldest->newest of the 7 newest completed):")
for c in clips:
    print(f"  media_id={c[0]} file={c[1]} dur={c[2]}ms")
assert len(clips) == 7

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
        "track_id": vtrack["id"],
        "title": cfg["brick_titles"][i],
    })
    left += dur
    bricks.append(nb)
vtrack["bricks"] = bricks

fields = {k: ("" if proj.get(k) is None else proj[k]) for k in
          ("id", "title", "aspect", "aspectValue", "zoom", "quality", "size",
           "format", "isTemplate", "baseUrl")}
fields["save_new"] = "0"
fields["data"] = json.dumps(src)
r = vx.post(f"project/save/{pid}", fields)
if not r.get("success"):
    raise RuntimeError(f"save rejected: {r}")

proj2 = vx.project(pid)
src2 = proj2["data"] if isinstance(proj2["data"], list) else [
    proj2["data"][k] for k in proj2["data"] if k != "data"]
tl = [(b["id"], b["media_id"], b["left"]) for t in src2 for b in t.get("bricks", [])]
print(f"VERIFY: timeline={tl}")
assert [b[1] for b in tl] == [c[0] for c in clips], "timeline mismatch after save"
print(f"DONE: 7 clips placed on project {pid}, total {left/1000:.1f}s — NO export")
