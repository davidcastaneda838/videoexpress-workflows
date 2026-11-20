#!/usr/bin/env python3
"""Generate ONLY the scene images (5-slot wave limit), wait, save, print preview
URLs. Stops before firing videos — for the text-verification gate."""
import json
import sys
from api_run import Vx

cfg = json.load(open(sys.argv[1]))
vx = Vx(cfg["cookies_file"])
jobs = []
for i, s in enumerate(cfg["scenes"], 1):
    print(f"Scene {i}: generating image...")
    job = vx.generate_image(s["image_prompt"], s["ref_media_id"], aspect=cfg.get("aspect", "9:16"))
    jobs.append(job)
    print(f"  queued: {vx.image_url(job)}")
for i, job in enumerate(jobs, 1):
    vx.wait_image(job)
    if cfg.get("save_images", True):
        vx.save_image(job)
    print(f"  image {i} ready: {vx.image_url(job)}")
print("DONE-IMAGES: all scene images ready + saved. Verify text before firing videos.")
