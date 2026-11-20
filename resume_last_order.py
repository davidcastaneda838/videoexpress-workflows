#!/usr/bin/env python3
"""Resume run_last_order: fire ONLY scene 15's video (image uuid known from the
failed run's log), wait for all 15 clips, then assemble the timeline in story
order. Scenes 1-14 were already fired in fire order 1..14; scene 15 fires last,
so id-ascending order still equals story order."""
import json
import time
import sys
from api_run import Vx, CDN, FOLDER_VIDEOS

cfg = json.load(open("run_last_order.json"))
pid = cfg["project_id"]
vx = Vx(cfg["cookies_file"])

# scene 15 image generation uuid (from the crashed run's log)
s15_uuid = "b750de25-c6fd-468b-8e09-a8b31dcdc998"
s = cfg["scenes"][14]

baseline = {m["id"] for m in vx.media_list(FOLDER_VIDEOS)}

def inflight():
    # GLOBAL count: all non-completed video jobs on the account, regardless of
    # baseline — the resume script must respect the cap even though scenes 1-14
    # were fired by a previous process.
    return sum(1 for m in vx.media_list(FOLDER_VIDEOS, limit=100)
               if m.get("status") != "completed")

fired = False
for attempt in range(6):
    n = inflight()
    if n >= 5:
        print(f"  {n} videos in flight — waiting for a slot...")
        vx.poll(inflight, lambda c: c < 5, 3600, interval=15, label="slot-wait")
    try:
        vx.generate_video(
            s15_uuid, s["visual_prompt"], s["actor_direction"], s.get("dialogue", ""),
            video_length=s.get("video_length", 5), lipsync=s.get("lipsync", False),
            enhance_video_prompt=s.get("enhance_video_prompt", 0))
        fired = True
        print(f"video 15 queued (attempt {attempt + 1})")
        break
    except RuntimeError as e:
        print(f"  attempt {attempt + 1} rejected: {e}")
        time.sleep(90)
if not fired:
    raise SystemExit("scene 15 video never accepted after 6 attempts")

# wait for scene 15 (the only item newer than baseline), then identify ALL 15
# drama clips by their 'R## —' shot-tag prefix in the library name field
done = vx.wait_videos(baseline, expected=1)
import re
tags = {f"R{i:02d}": i for i in range(1, 16)}
drama = []
for m in vx.media_list(FOLDER_VIDEOS, limit=100):
    mt = re.match(r"^R(\d{2})\s*—", m.get("name") or "")
    if mt and f"R{mt.group(1)}" in tags and m.get("status") == "completed":
        drama.append((tags[f"R{mt.group(1)}"], m))
assert len(drama) == 15, f"found {len(drama)} of 15 drama clips: {[d[0] for d in drama]}"
drama.sort(key=lambda x: x[0])
clips = [(m["id"], m["fileName"], round(m["duration"])) for _, m in drama]
print(f"All 15 clips completed in story order: " + ", ".join(str(c[0]) for c in clips))

# ---- assemble timeline (same as gen_drama_place) ----
proj = vx.project(pid)
src = proj["data"] if isinstance(proj["data"], list) else [
    proj["data"][k] for k in proj["data"] if k != "data"]
vtrack = next((t for t in src if any(b.get("type") == "video" for b in t.get("bricks", []))), None)
if vtrack is None:
    vtrack = next(t for t in src if t.get("index") == 0)
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
