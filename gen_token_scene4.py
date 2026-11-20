#!/usr/bin/env python3
"""Regenerate scene 4's image only (marquee garbled 'MEMOR LANE' on first pass).
No video fired."""
import json
import sys
from api_run import Vx

cfg = json.load(open(sys.argv[1]))
vx = Vx(cfg["cookies_file"])
s = cfg["scenes"][3]
print("Scene 4: regenerating image (marquee fix)...")
job = vx.generate_image(s["image_prompt"], s["ref_media_id"], aspect=cfg.get("aspect", "9:16"))
vx.wait_image(job)
vx.save_image(job)
print(f"  regenerated: {vx.image_url(job)}")
