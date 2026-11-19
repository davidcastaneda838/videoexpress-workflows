import json
from api_run import Vx, CDN

cfg = json.load(open("run_caller_inside.json", encoding="utf-8"))
clips_info = {int(k) - 1: v for k, v in json.load(open("caller60_clips.json", encoding="utf-8")).items()}
vx = Vx("cookies.json")
pid = cfg["project_id"]
clips = [(clips_info[i]["id"], clips_info[i]["fileName"], round(float(clips_info[i]["duration"])))
         for i in range(len(cfg["scenes"]))]

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
tl = [(b["media_id"], b.get("title")) for t in src2 for b in t.get("bricks", [])]
print("VERIFY: timeline bricks:")
for m, t in tl:
    print(" ", m, t)
assert [m for m, _ in tl] == [c[0] for c in clips], "timeline mismatch after save"
print(f"DONE: {len(clips)} clips placed on project {pid}, total {left/1000:.1f}s - NO export")
