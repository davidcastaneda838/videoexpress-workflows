#!/usr/bin/env python3
"""Generate ONE clip (image + video) and stop. No render, no export, no download.
The clip stays in My AI Videos. Verifies completion via the library."""
import json
import sys
from api_run import Vx, FOLDER_VIDEOS


def main():
    cfg = json.load(open(sys.argv[1]))
    vx = Vx(cfg["cookies_file"])
    baseline = {m["id"] for m in vx.media_list(FOLDER_VIDEOS)}

    s = cfg["scenes"][0]
    print("Scene 1: generating image...")
    job = vx.generate_image(s["image_prompt"], s["ref_media_id"])
    vx.wait_image(job)
    vx.save_image(job)
    print(f"  image ready: {vx.image_url(job)}")

    print("Generating video (native dialogue, lipsync OFF)...")
    vx.generate_video(
        job, s["visual_prompt"], s["actor_direction"], "",
        video_length=s.get("video_length", 5), lipsync=False,
        enhance_video_prompt=s.get("enhance_video_prompt", 0))
    done = vx.wait_videos(baseline, expected=1)
    m = sorted(done, key=lambda x: x["id"])[0]
    print(f"DONE-GENERATING: media_id={m['id']} file={m['fileName']} "
          f"duration={m['duration']}ms status={m.get('status')} — in My AI Videos, no export")


if __name__ == "__main__":
    main()
