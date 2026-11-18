#!/usr/bin/env python3
"""Generate one clip with a run config's first scene, then place it on a
project's timeline WITHOUT rendering/exporting. Verifies the save by re-reading
the project."""
import json
import sys
from api_run import Vx, CDN, FOLDER_VIDEOS


def main():
    cfg = json.load(open(sys.argv[1]))
    pid = cfg["project_id"]
    vx = Vx(cfg["cookies_file"])

    baseline = {m["id"] for m in vx.media_list(FOLDER_VIDEOS)}

    s = cfg["scenes"][0]
    print("Scene 1: generating image...")
    job = vx.generate_image(s["image_prompt"], s["ref_media_id"])
    vx.wait_image(job)
    vx.save_image(job)
    print(f"  image ready: {vx.image_url(job)}")

    print("Generating video (lipsync)...")
    vx.generate_video(
        job, s["visual_prompt"], s["actor_direction"], s.get("dialogue", ""),
        video_length=s.get("video_length", 5), lipsync=s.get("lipsync", True),
        enhance_video_prompt=s.get("enhance_video_prompt", 0))
    done = vx.wait_videos(baseline, expected=1)
    m = sorted(done, key=lambda x: x["id"])[0]
    media_id, file_name = m["id"], m["fileName"]
    dur = round(m["duration"])
    print(f"  clip completed: media_id={media_id} file={file_name} dur={dur}ms")

    # ---- place on timeline (no render) ----
    proj = vx.project(pid)
    src = proj["data"] if isinstance(proj["data"], list) else [
        proj["data"][k] for k in proj["data"] if k != "data"]
    # video track = the one with video bricks, else index 0
    vtrack = next((t for t in src if any(b.get("type") == "video" for b in t.get("bricks", []))), None)
    if vtrack is None:
        vtrack = next(t for t in src if t.get("index") == 0)
    tpl = (vtrack.get("bricks") or [{}])[0]
    nb = json.loads(json.dumps(tpl)) if tpl else {}
    nb.update({
        "id": "902", "media_id": media_id, "type": "video", "fileName": file_name,
        "path": f"{CDN}/video/{file_name}.mp4", "videoUrl": f"{CDN}/video/{file_name}.mp4",
        "imageUrl": f"{CDN}/image/{file_name}.jpg", "imagePath": f"{CDN}/image/{file_name}.jpg",
        "thumbUrl": f"{CDN}/thumbnail/{file_name}_small.jpg",
        "duration": dur, "duration_time": dur, "start_time": 0,
        "left": max([b.get("left", 0) + b.get("duration", 0) for b in vtrack.get("bricks", [])] + [0]),
        "track_id": vtrack["id"], "title": cfg.get("brick_title", "new-clip"),
    })
    vtrack.setdefault("bricks", []).append(nb)
    vtrack["bricks"].sort(key=lambda b: b.get("left", 0))

    fields = {k: ("" if proj.get(k) is None else proj[k]) for k in
              ("id", "title", "aspect", "aspectValue", "zoom", "quality", "size",
               "format", "isTemplate", "baseUrl")}
    fields["save_new"] = "0"
    fields["data"] = json.dumps(src)
    r = vx.post(f"project/save/{pid}", fields)
    if not r.get("success"):
        raise RuntimeError(f"save rejected: {r}")

    # verify
    proj2 = vx.project(pid)
    src2 = proj2["data"] if isinstance(proj2["data"], list) else [
        proj2["data"][k] for k in proj2["data"] if k != "data"]
    bricks = [b for t in src2 for b in t.get("bricks", [])]
    match = [b for b in bricks if b.get("media_id") == media_id]
    print(f"VERIFY: save={r} bricks={[(b['id'], b['media_id'], b['left']) for b in bricks]}")
    assert match, "new clip not found on timeline after save"
    print(f"DONE: clip {media_id} placed on project {pid} timeline (no export)")


if __name__ == "__main__":
    main()
