#!/usr/bin/env python3
"""Generate N scenes (images + videos, CC dialogue style), then place ALL clips
on a project's timeline in story order. No render, no export, no download."""
import json
import sys
from api_run import Vx, CDN, FOLDER_VIDEOS, MAX_INFLIGHT_VIDEOS


def main():
    cfg = json.load(open(sys.argv[1]))
    pid = cfg["project_id"]
    vx = Vx(cfg["cookies_file"])
    baseline = {m["id"] for m in vx.media_list(FOLDER_VIDEOS)}

    def inflight():
        return sum(1 for m in vx.media_list(FOLDER_VIDEOS, limit=100)
                   if m["id"] not in baseline and m.get("status") != "completed")

    # fire all image gens first (parallel server-side), then videos
    jobs = []
    for i, s in enumerate(cfg["scenes"], 1):
        print(f"Scene {i}: generating image...")
        job = vx.generate_image(s["image_prompt"], s["ref_media_id"])
        jobs.append(job)
        print(f"  queued: {vx.image_url(job)}")
    for i, job in enumerate(jobs, 1):
        vx.wait_image(job)
        if cfg.get("save_images", True):
            vx.save_image(job)
        print(f"  image {i} ready: {vx.image_url(job)}")

    print("Generating videos...")
    for i, (job, s) in enumerate(zip(jobs, cfg["scenes"]), 1):
        n = inflight()
        if n >= MAX_INFLIGHT_VIDEOS:
            print(f"  {n} videos in flight (max {MAX_INFLIGHT_VIDEOS}) — waiting for a slot...")
            vx.poll(inflight, lambda c: c < MAX_INFLIGHT_VIDEOS, 3600, interval=15, label="slot-wait")
        vx.generate_video(
            job, s["visual_prompt"], s["actor_direction"], s.get("dialogue", ""),
            video_length=s.get("video_length", 5), lipsync=s.get("lipsync", False),
            enhance_video_prompt=s.get("enhance_video_prompt", 0))
        print(f"  video {i} queued")
    done = vx.wait_videos(baseline, expected=len(cfg["scenes"]))
    done.sort(key=lambda m: m["id"])  # fire order == scene order
    clips = [(m["id"], m["fileName"], round(m["duration"])) for m in done]
    print(f"All {len(clips)} clips completed: " + ", ".join(str(c[0]) for c in clips))

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
            "track_id": vtrack["id"],
            "title": cfg.get("brick_titles", [f"scene{n}" for n in range(1, 10)])[i],
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


if __name__ == "__main__":
    main()
