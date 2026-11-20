#!/usr/bin/env python3
"""Regenerate scene 2's image + video (marquee garbled 'MENORY LANE' in motion
on the first render pass). Single clip, no render/export."""
import json
from api_run import Vx, FOLDER_VIDEOS, CDN

cfg = json.load(open("run_token.json"))
vx = Vx(cfg["cookies_file"])
s = cfg["scenes"][1]

print("Scene 2: regenerating image (marquee fix)...")
job = vx.generate_image(s["image_prompt"], s["ref_media_id"], aspect=cfg.get("aspect", "9:16"))
vx.wait_image(job)
vx.save_image(job)
print(f"  image ready: {vx.image_url(job)}")

baseline = {m["id"] for m in vx.media_list(FOLDER_VIDEOS)}
print("Generating video (native dialogue, lipsync OFF)...")
vx.generate_video(
    job, s["visual_prompt"], s["actor_direction"], "",
    video_length=s.get("video_length", 5), lipsync=False,
    enhance_video_prompt=s.get("enhance_video_prompt", 0))
done = vx.wait_videos(baseline, expected=1)
m = sorted(done, key=lambda x: x["id"])[0]
print(f"DONE-GENERATING: media_id={m['id']} file={m['fileName']} "
      f"duration={m['duration']}ms status={m.get('status')} — in My AI Videos, no export")
