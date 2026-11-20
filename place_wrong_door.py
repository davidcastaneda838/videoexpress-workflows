#!/usr/bin/env python3
"""Place-only recovery for run_wrong_door: all 12 clips exist in My AI Videos;
only the project/save step failed on transient DNS. Re-save using dns_vx.Vx."""
import json
from dns_vx import Vx
from api_run import CDN, FOLDER_VIDEOS

cfg = json.load(open("run_wrong_door.json", encoding="utf-8"))
vx = Vx(cfg["cookies_file"])
pid = cfg["project_id"]

media = vx.media_list(FOLDER_VIDEOS, limit=40)
completed = [m for m in media if m.get("status") == "completed"]
newest12 = sorted(completed, key=lambda m: m["id"], reverse=True)[:12]
clips = [(m["id"], m["fileName"], round(m["duration"])) for m in sorted(newest12, key=lambda m: m["id"])]
print("clips to place:", [c[0] for c in clips])
assert len(clips) == 12, f"expected 12 completed clips, found {len(clips)}"

proj = vx.project(pid)
src = proj["data"] if isinstance(proj["data"], list) else [
    proj["data"][k] for k in proj["data"] if k != "data"]
vtrack = next(t for t in src if any(b.get("type") == "video" for b in t.get("bricks", [])))
tpl = (vtrack.get("bricks") or [{}])[0]
left = 0
bricks = []
titles = cfg["brick_titles"]
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
r = vx.post(f"project/save/{pid}", fields)
if not r.get("success"):
    raise RuntimeError(f"save rejected: {r}")

proj2 = vx.project(pid)
src2 = proj2["data"] if isinstance(proj2["data"], list) else [
    proj2["data"][k] for k in proj2["data"] if k != "data"]
tl = [(b["id"], b["media_id"], b["left"]) for t in src2 for b in t.get("bricks", [])]
print(f"VERIFY: {r} timeline={tl}")
assert [b[1] for b in tl] == [c[0] for c in clips], "timeline mismatch after save"
print(f"DONE: {len(clips)} clips placed on project {pid} timeline, total {left/1000:.1f}s — NO export")
