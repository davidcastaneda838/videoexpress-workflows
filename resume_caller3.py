#!/usr/bin/env python3
"""Final resume for the 20-shot Caller film: identify fired clips by the
'RNN -' prefix in their library name; fire only missing scenes (max 5
concurrent videos; one polite 60s-delayed retry on a transient rejection);
wait for all 20; assemble the timeline in story order.
Usage: resume_caller3.py <config> <jobs-json>"""
import json
import re
import sys
import time
from api_run import Vx, CDN, FOLDER_VIDEOS, MAX_INFLIGHT_VIDEOS


def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    jobs = {int(k): v for k, v in json.load(open(sys.argv[2], encoding="utf-8")).items()}
    vx = Vx(cfg["cookies_file"])
    scenes = cfg["scenes"]

    def tag(i):
        return f"R{i+1:02d}"

    def existing():
        out = {}
        for m in vx.media_list(FOLDER_VIDEOS, limit=100):
            m2 = re.match(r"R(\d\d) ", m.get("name") or "")
            if m2:
                n = int(m2.group(1))
                if 1 <= n <= len(scenes):
                    out[n - 1] = m
        return out

    have = existing()
    print("already fired:", sorted(k + 1 for k in have))

    # fire missing videos with the 5-slot limiter + one retry on transient rejection
    for i, s in enumerate(scenes):
        if i in have:
            continue

        def inflight():
            items = vx.media_list(FOLDER_VIDEOS, limit=100)
            mine = [m for m in items if re.match(r"R(\d\d) ", m.get("name") or "")]
            return sum(1 for m in mine if m.get("status") not in (None,) and m.get("status") != "completed")

        # status semantics: completed | processing(None?) - count non-completed of ours
        def inflight2():
            items = vx.media_list(FOLDER_VIDEOS, limit=100)
            cnt = 0
            for m in items:
                if not re.match(r"R(\d\d) ", m.get("name") or ""):
                    continue
                st = m.get("status")
                if st != "completed":
                    cnt += 1
            return cnt

        n = inflight2()
        if n >= MAX_INFLIGHT_VIDEOS:
            print(f"  {n} in flight (max {MAX_INFLIGHT_VIDEOS}) - waiting for a slot...")
            vx.poll(inflight2, lambda c: c < MAX_INFLIGHT_VIDEOS, 3600, interval=15, label="slot-wait")
        attempt = 0
        while True:
            try:
                vx.generate_video(
                    jobs[i], s["visual_prompt"], s["actor_direction"], s.get("dialogue", ""),
                    video_length=s.get("video_length", 5), lipsync=s.get("lipsync", False),
                    enhance_video_prompt=s.get("enhance_video_prompt", 0))
                print(f"  video {i+1} ({tag(i)}) queued")
                break
            except RuntimeError as e:
                attempt += 1
                if attempt >= 3:
                    raise
                print(f"  video {i+1} rejected (attempt {attempt}), retrying after 60s: {e}")
                time.sleep(60)

    # wait until all 20 exist and are completed
    def all_done():
        have = existing()
        if len(have) < len(scenes):
            return None
        for m in have.values():
            if m.get("status") != "completed":
                return None
        return have

    have = vx.poll(all_done, lambda h: h is not None, 3600, interval=20, label="wait-20-clips")
    print(f"All {len(have)} clips completed")

    # ---- assemble timeline ----
    clips = []
    for i in range(len(scenes)):
        m = have[i]
        clips.append((int(m["id"]), m["fileName"], round(float(m["duration"] or 5000))))
    pid = cfg["project_id"]
    proj = vx.project(pid)
    src = proj["data"] if isinstance(proj["data"], list) else [
        proj["data"][k] for k in proj["data"] if k != "data"]
    vtrack = next((t for t in src if any(b.get("type") == "video" for b in t.get("bricks", []))), None)
    if vtrack is None:
        vtrack = next(t for t in src if t.get("index") == 0)
    tpl = (vtrack.get("bricks") or [{}])[0]
    left = 0
    bricks = []
    titles = cfg.get("brick_titles")
    for i, (media_id, file_name, dur) in enumerate(clips):
        nb = json.loads(json.dumps(tpl)) if tpl else {}
        nb.update({
            "id": str(910 + i), "media_id": media_id, "type": "video", "fileName": file_name,
            "path": f"{CDN}/video/{file_name}.mp4", "videoUrl": f"{CDN}/video/{file_name}.mp4",
            "imageUrl": f"{CDN}/image/{file_name}.jpg", "imagePath": f"{CDN}/image/{file_name}.jpg",
            "thumbUrl": f"{CDN}/thumbnail/{file_name}_small.jpg",
            "duration": dur, "duration_time": dur, "start_time": 0, "left": left,
            "track_id": vtrack["id"],
            "title": titles[i],
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
    print(f"VERIFY: timeline bricks={tl}")
    assert [b[0] for b in tl] == [c[0] for c in clips], "timeline mismatch after save"
    print(f"DONE: {len(clips)} clips placed on project {pid}, total {left/1000:.1f}s - NO export")


if __name__ == "__main__":
    main()
