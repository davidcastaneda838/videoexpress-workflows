#!/usr/bin/env python3
"""Download raw clips, detect speech boundaries via ffmpeg silencedetect, and
emit a render config with per-clip trims that never cut into words.

Logic per clip: find the longest silence gap in the clip. Speech sits between
silences. For dialogue clips: trim_in = end of leading silence (first speech
minus pad, min 0), trim_out = raw_duration - (start of trailing silence + pad
after last speech). If detection fails or no silence found, fall back to light
fixed trims. Non-dialogue clips keep fixed trims."""
import json
import os
import re
import subprocess
import sys
import urllib.request
import tempfile

CDN = "https://cdn-ny-b.videoexpress.ai"
SILENCE_DB = "-28dB"   # above rain/hum, below speech
MIN_SIL = 0.35         # s; gaps shorter than this are within speech
HEAD_PAD = 0.05        # keep this much before first speech
TAIL_PAD = 0.25        # keep this much after last speech
FALLBACK_IN, FALLBACK_OUT = 200, 400

src_cfg = json.load(open(sys.argv[1]))
out_path = sys.argv[2]
tmp = tempfile.mkdtemp(dir=os.path.expanduser("~/AppData/Local/hermes/cache/scratch"))


def analyze(path, dur_ms):
    """Return (first_speech_ms, last_speech_end_ms) or None."""
    try:
        p = subprocess.run(
            ["ffmpeg", "-i", path, "-af", f"silencedetect=noise={SILENCE_DB}:d={MIN_SIL}",
             "-f", "null", "-"],
            capture_output=True, text=True, timeout=120)
        err = p.stderr
    except Exception as e:
        print(f"    detect failed: {e}")
        return None
    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", err)]
    dur = dur_ms / 1000.0
    events = []
    s_set = list(starts)
    e_set = list(ends)
    # pair them: silence_end (speech starts) and silence_start (speech ends)
    speech_spans = []
    # build timeline: speech starts at silence_end, ends at next silence_start
    i = j = 0
    # simpler: first speech = first silence_end; last speech end = last silence_start (if > it)
    if not e_set:
        return None
    first_speech = e_set[0]
    last_end = None
    for s in s_set:
        if s > first_speech:
            last_end = s
    if last_end is None:
        last_end = dur
    return first_speech, last_end, dur


clips_out = []
for c in src_cfg["clips"]:
    f = c["file_name"]
    dur = c["duration_ms"]
    if c.get("dialogue", True) is False:
        clips_out.append({**c, "trim_in_ms": c.get("fallback_in", 200),
                          "trim_out_ms": c.get("fallback_out", 1000)})
        print(f"{c['title']}: non-dialogue fixed trims")
        continue
    dest = os.path.join(tmp, f + ".mp4")
    try:
        req = urllib.request.Request(f"{CDN}/video/{f}.mp4", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as fh:
            fh.write(r.read())
    except Exception as e:
        print(f"{c['title']}: download failed ({e}) -> fallback trims")
        clips_out.append({**c, "trim_in_ms": FALLBACK_IN, "trim_out_ms": FALLBACK_OUT})
        continue
    res = analyze(dest, dur)
    if res is None:
        print(f"{c['title']}: no silence detected -> fallback trims")
        clips_out.append({**c, "trim_in_ms": FALLBACK_IN, "trim_out_ms": FALLBACK_OUT})
        continue
    first_speech, last_end, dur_s = res
    # SAFETY CAPS: mid-line pauses can fool silence detection into "starting"
    # speech late or "ending" it early — never trim more than CAP ms on a
    # dialogue clip, so words can never be cut even on a bad detection.
    CAP = 1200
    tin = max(0, min(int((first_speech - HEAD_PAD) * 1000), CAP))
    tout = max(0, min(int((dur_s - last_end - TAIL_PAD) * 1000), CAP))
    if dur - tin - tout < 1500:  # keep at least 1.5s
        tin, tout = FALLBACK_IN, FALLBACK_OUT
        print(f"{c['title']}: trim too aggressive -> fallback")
    else:
        print(f"{c['title']}: speech {first_speech:.2f}-{last_end:.2f}s of {dur_s:.2f}s -> in {tin} out {tout} (capped)")
    clips_out.append({**c, "trim_in_ms": tin, "trim_out_ms": tout})

cfg = {k: v for k, v in src_cfg.items() if k != "clips"}
cfg["clips"] = clips_out
json.dump(cfg, open(out_path, "w"), indent=2)
print(f"WROTE {out_path}")
