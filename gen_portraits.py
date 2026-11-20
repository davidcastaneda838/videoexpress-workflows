#!/usr/bin/env python3
"""Generate character reference portraits (generate_image_plain), save them,
and print the newest My AI Images media ids + preview URLs for approval."""
import json
import sys
from api_run import Vx, FOLDER_IMAGES

cfg = json.load(open(sys.argv[1]))
vx = Vx(cfg["cookies_file"])
for p in cfg["portraits"]:
    print(f"Portrait {p['tag']}: generating...")
    job = vx.generate_image_plain(p["prompt"], type_="photorealistic")
    vx.wait_image(job)
    vx.save_image(job)
    print(f"  saved: {vx.image_url(job)}")
print("Newest My AI Images (id desc):")
for m in vx.media_list(FOLDER_IMAGES, limit=5):
    print(f"  id={m['id']} name={m.get('name')}")
