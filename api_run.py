#!/usr/bin/env python3
"""
VideoExpress end-to-end API run — no browser UI clicks.

Proven live on Nov 17-18 2026 (run 6, sleep-facts-api3, 17.136s ffprobe-verified):
  generate_image_consistent_character -> preview/<job-uuid>.jpg
  -> image2video (lipsync via speech1/isTalkingVideoFromText) -> poll get_media
  -> rebuild project bricks -> POST /render_project/<id> -> poll get_list_output -> download.

Usage:
  python api_run.py run.json            # full run: images + videos + render + download
  python api_run.py run.json --dry-run  # skip generation; re-render existing clips (cheap test)

run.json schema:
{
  "character_ref_media_id": 49209068,
  "project_id": 481590,
  "project_title": "sleep-facts",
  "export_name": "my-video",
  "cookies_file": "cookies.json",
  "scenes": [
    {"image_prompt": "...", "visual_prompt": "...", "actor_direction": "...", "dialogue": "..."}
  ]
}

Rules baked in from live testing:
  - Fire every write ONCE. If a response is lost, poll the library before ever retrying.
  - Generated images do NOT appear in My AI Images (folder = saved-only).
    Verify via https://user-assets.renderplatform.com/preview/<job-uuid>.jpg (note .jpg).
  - Video clips DO appear in My AI Videos on completion (status processing -> completed).
  - Clip length is dialogue-governed (~55-60 chars = ~5s, ~70+ chars = ~6s; max 10s).
  - Brick duration/left are milliseconds; left is the cumulative timeline position.
"""

import argparse
import json
import sys
import time
import os
import urllib.parse
import urllib.request

BASE = "https://app.videoexpress.ai"
CDN = "https://cdn-ny-b.videoexpress.ai"
PREVIEW = "https://user-assets.renderplatform.com/preview"

FOLDER_IMAGES = 355995  # My AI Images (per-account; re-derive via /library/get_categories/4 if needed)
FOLDER_VIDEOS = 355994  # My AI Videos

# HARD RULE (user-mandated): at most 5 concurrent video-generation jobs, ever,
# regardless of run length. Be a polite API citizen — never melt their servers.
MAX_INFLIGHT_VIDEOS = 5


class Vx:
    def __init__(self, cookies_file):
        self.opener = urllib.request.build_opener()
        self.load_cookies(cookies_file)

    def load_cookies(self, path):
        with open(path) as f:
            cookies = json.load(f)
        self.cookie_header = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

    def _headers(self, content_type=None):
        h = {"X-Requested-With": "XMLHttpRequest", "Cookie": self.cookie_header,
             "User-Agent": "Mozilla/5.0"}
        if content_type:
            h["Content-Type"] = content_type
        return h

    def get(self, path):
        req = urllib.request.Request(BASE + path, headers=self._headers())
        with self.opener.open(req, timeout=60) as r:
            return json.loads(r.read().decode())

    def post(self, path, fields=None, json_body=None):
        if json_body is not None:
            data = json.dumps(json_body).encode()
            ct = "application/json"
        else:
            data = urllib.parse.urlencode(fields or {}).encode()
            ct = "application/x-www-form-urlencoded; charset=UTF-8"
        req = urllib.request.Request(BASE + path, data=data, headers=self._headers(ct), method="POST")
        with self.opener.open(req, timeout=60) as r:
            return json.loads(r.read().decode())

    def poll(self, fetch_fn, until, timeout_s, interval=15, label=""):
        """fetch_fn() -> value; until(value) -> True when done."""
        deadline = time.time() + timeout_s
        i = 0
        while time.time() < deadline:
            try:
                v = fetch_fn()
                if until(v):
                    return v
            except Exception as e:
                print(f"  [{label}] poll {i}: transient error {e}")
            print(f"  [{label}] poll {i}: waiting...")
            time.sleep(interval)
            i += 1
        raise TimeoutError(f"{label}: timed out after {timeout_s}s")

    # ---------- reads ----------

    def media_list(self, folder, limit=50):
        return self.get(f"/api/library/get_media/4?categoryId={folder}&page=1&start=0"
                        f"&limit={limit}&query=&orderBy=id&orderDir=desc&filter=")["results"]

    def outputs(self):
        return self.get("/api/get_list_output")["results"]

    def projects(self):
        return self.get("/project/get_list")["results"]

    def project(self, pid):
        return self.get(f"/project/open/{pid}")

    def save_image(self, job_uuid):
        """Save a generated image into My AI Images (the library only holds saved
        images — generation alone never creates a library item). Fire ONCE."""
        r = self.post("/ai/api/save_generated_image", {
            "uuid": job_uuid, "isShared": "0", "generatorName": "create_from_prompt"})
        if not r.get("success"):
            raise RuntimeError(f"save_generated_image rejected: {r}")
        return r

    def delete_item(self, media_id):
        """DELETE /library/delete_item/<id> — removes a library item permanently."""
        req = urllib.request.Request(f"{BASE}/library/delete_item/{media_id}",
                                     headers=self._headers(), method="DELETE")
        with self.opener.open(req, timeout=60) as r:
            return r.status

    # ---------- step 1: images ----------

    def generate_image(self, prompt, ref_media_id, aspect="9:16", ref2_media_id=None):
        """Returns the job uuid; image lands at PREVIEW/<uuid>.jpg. Fire ONCE.
        ref2_media_id anchors a SECOND character (mediaId2) — proven for
        two-character scenes in the same frame."""
        fields = {
            "prompt": prompt, "type": "human", "mediaId": ref_media_id,
            "aspect": aspect, "generatorName": "create_from_prompt"}
        if ref2_media_id:
            fields["mediaId2"] = ref2_media_id
        r = self.post("/ai/api/generate_image_consistent_character", fields)
        if not r.get("success"):
            raise RuntimeError(f"image gen rejected: {r}")
        return r["uuid"]

    def generate_image_plain(self, prompt, type_="photorealistic", aspect="9:16", enhance_prompt=0):
        """No reference image — consistency comes from the prompt text itself
        (Mini Dramas Character Bible pattern). Fire ONCE."""
        r = self.post("/ai/api/generate_image", {
            "prompt": prompt, "enhancePrompt": str(enhance_prompt), "type": type_,
            "uuid": "", "mediaId": "0", "seed": "", "aspect": aspect,
            "generatorName": "create_from_prompt"})
        if not r.get("success"):
            raise RuntimeError(f"plain image gen rejected: {r}")
        return r["uuid"]

    def image_url(self, job_uuid):
        return f"{PREVIEW}/{job_uuid}.jpg"

    def wait_image(self, job_uuid, timeout_s=900):
        """Image is ready when its preview URL returns 200."""
        def check():
            req = urllib.request.Request(self.image_url(job_uuid), method="HEAD",
                                         headers={"User-Agent": "Mozilla/5.0"})
            try:
                with self.opener.open(req, timeout=30) as r:
                    return r.status == 200
            except Exception:
                return False
        return self.poll(check, lambda ok: ok, timeout_s, interval=20, label=f"image {job_uuid[:8]}")

    # ---------- step 2: video + lipsync ----------

    def generate_video(self, image_uuid, image_prompt, video_prompt, dialogue,
                       aspect="9:16", video_length=10, lipsync=True,
                       enhance_video_prompt=1, dialogue_in_prompt=False):
        """Fire ONCE. Returns the library-id baseline set for the poller.
        lipsync=False + dialogue_in_prompt=False -> no speech at all.
        lipsync=False + dialogue_in_prompt=True -> dialogue embedded in video_prompt
        (Mini Dramas pattern: the engine makes the character speak it)."""
        before = {m["id"] for m in self.media_list(FOLDER_VIDEOS)}
        fields = {
            "type": "human", "imagePrompt": image_prompt, "prompt": video_prompt,
            "uuid": image_uuid, "mediaId": "0", "audioMediaId": "0", "isShared": "0",
            "aspect": aspect, "enhanceHumanFace": "0",
            "isTalkingVideoFromText": "1" if lipsync else "0",
            "isNarrationVideo": "0", "enhanceVideoPrompt": str(enhance_video_prompt),
            "videoOnly": "0", "speed": "", "generatorName": "create_from_prompt",
            "faceImageMediaId": "0", "faceSwap": "0", "mode": "",
            "videoLength": str(video_length),
            "speech1": dialogue if lipsync else "", "speech2": "",
        }
        r = self.post("/ai/api/image2video", fields)
        if not r.get("success"):
            raise RuntimeError(f"video gen rejected: {r}")
        return before  # baseline set for the poller

    def wait_videos(self, baseline_ids, expected=1, timeout_s=1500):
        def check():
            new = [m for m in self.media_list(FOLDER_VIDEOS) if m["id"] not in baseline_ids]
            done = [m for m in new if m.get("status") == "completed"]
            print(f"  new={len(new)} completed={len(done)}")
            return done if len(done) >= expected else None
        result = self.poll(check, lambda v: v is not None, timeout_s, interval=20, label="videos")
        assert result is not None
        return result

    # ---------- step 3: timeline + render ----------

    def render(self, project_id, clips, export_name, project_title=None, aspect="9:16"):
        """clips: [{media_id, file_name, duration_ms}] in story order. Fire ONCE."""
        proj = self.project(project_id)
        d = proj["data"]
        if isinstance(d, dict):  # saved timelines may come back keyed by index
            d = [d[k] for k in d if k != "data" and isinstance(d[k], dict)]
        video_track = next(t for t in d if any(
            b.get("type") == "video" for b in t.get("bricks", [])))
        audio_track = next(t for t in d if t is not video_track)
        tpl = video_track["bricks"][0]
        left = 0
        bricks = []
        for i, c in enumerate(clips):
            b = json.loads(json.dumps(tpl))
            f = c["file_name"]
            in_ms = c.get("trim_in_ms", 0)
            dur = c["duration_ms"] - in_ms - c.get("trim_out_ms", 0)
            if dur <= 0:
                raise ValueError(f"clip {i}: trim leaves {dur}ms")
            b.update({
                "id": str(900 + i), "media_id": c["media_id"], "type": "video",
                "fileName": f, "path": f"{CDN}/video/{f}.mp4", "videoUrl": f"{CDN}/video/{f}.mp4",
                "imageUrl": f"{CDN}/image/{f}.jpg", "imagePath": f"{CDN}/image/{f}.jpg",
                "thumbUrl": f"{CDN}/thumbnail/{f}_small.jpg",
                "duration": dur, "duration_time": dur,
                "start_time": in_ms, "left": left, "track_id": "45", "title": c.get("title", f"scene{i+1}"),
            })
            left += dur
            bricks.append(b)
        payload = {
            "options": {"name": export_name, "quality": "high", "size": "1080",
                        "format": "mp4", "aspect": aspect, "project_id": project_id,
                        "project_title": project_title or export_name},
            "data": [{**video_track, "bricks": bricks}, audio_track],
        }
        r = self.post(f"/render_project/{project_id}", json_body=payload)
        if not r.get("success"):
            raise RuntimeError(f"render rejected: {r}")
        return r, left

    def wait_output(self, baseline_ids, timeout_s=900):
        def check():
            new = [o for o in self.outputs() if o["id"] not in baseline_ids]
            return new[0] if new else None
        return self.poll(check, lambda v: v is not None, timeout_s, interval=15, label="render")

    def download(self, url, dest):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with self.opener.open(req, timeout=300) as r, open(dest, "wb") as f:
            f.write(r.read())
        return dest


def _head_ok(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200 and int(r.headers.get("Content-Length") or 0) > 100_000
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--dry-run", action="store_true",
                    help="skip generation; re-render existing clips listed in config.clips")
    ap.add_argument("--out", default=None, help="download dir (default: ~/Downloads)")
    args = ap.parse_args()

    cfg = json.load(open(args.config))
    vx = Vx(cfg["cookies_file"])
    out_dir = args.out or os.path.expanduser("~/Downloads")

    if args.dry_run:
        clips = cfg["clips"]
        print(f"DRY RUN: re-rendering {len(clips)} existing clips")
    else:
        ref = cfg.get("character_ref_media_id")
        clips = []
        # Capture the library baseline ONCE before the batch: per-scene snapshots
        # would absorb earlier scenes' items and break the new-items poller.
        videos_baseline = {m["id"] for m in vx.media_list(FOLDER_VIDEOS)}

        def inflight_videos():
            return sum(1 for m in vx.media_list(FOLDER_VIDEOS, limit=100)
                       if m["id"] not in videos_baseline and m.get("status") != "completed")

        for i, s in enumerate(cfg["scenes"], 1):
            print(f"Scene {i}: generating image...")
            scene_ref = s.get("ref_media_id") or ref
            if scene_ref:
                job = vx.generate_image(
                    s["image_prompt"], scene_ref,
                    aspect=cfg.get("aspect", "9:16"),
                    ref2_media_id=s.get("ref2_media_id"))
            else:
                job =                vx.generate_image_plain(
                    s["image_prompt"], type_=s.get("image_type", "photorealistic"),
                    aspect=cfg.get("aspect", "9:16"))
            vx.wait_image(job)
            if cfg.get("save_images", True):
                vx.save_image(job)
                print(f"  image ready + saved: {vx.image_url(job)}")
            else:
                print(f"  image ready: {vx.image_url(job)}")
            # HARD RULE: max 5 concurrent video jobs — wait for a free slot
            n = inflight_videos()
            if n >= MAX_INFLIGHT_VIDEOS:
                print(f"  {n} videos in flight (max {MAX_INFLIGHT_VIDEOS}) — waiting for a slot...")
                vx.poll(inflight_videos, lambda c: c < MAX_INFLIGHT_VIDEOS,
                        3600, interval=15, label="slot-wait")
            baseline = vx.generate_video(
                job, s["visual_prompt"], s["actor_direction"],
                s.get("dialogue", ""),
                aspect=cfg.get("aspect", "9:16"),
                video_length=s.get("video_length", 10),
                lipsync=s.get("lipsync", True),
                enhance_video_prompt=s.get("enhance_video_prompt", 1))
            clips.append({"baseline": videos_baseline})
        # wait for all videos together (they run in parallel server-side)
        all_base = videos_baseline
        done = vx.wait_videos(all_base, expected=len(clips))
        done.sort(key=lambda m: m["id"])  # fire order == scene order (ids are sequential)
        clips = []
        for i, (m, s) in enumerate(zip(done, cfg["scenes"]), 1):
            clips.append({"media_id": m["id"], "file_name": m["fileName"],
                          "duration_ms": round(m["duration"]),
                          "trim_in_ms": s.get("trim_in_ms", 0),
                          "trim_out_ms": s.get("trim_out_ms", 0),
                          "title": f"scene{i}"})
        print(f"All {len(clips)} clips completed: total {sum(c['duration_ms'] for c in clips)/1000:.1f}s raw")

    baseline_out = {o["id"] for o in vx.outputs()}
    # Propagation guard: the render worker fetches clip files from the CDN;
    # rendering seconds after generation can hit un-propagated files (verified:
    # produced black bricks). Wait until every clip's CDN file is fetchable.
    for c in clips:
        url = f"{CDN}/video/{c['file_name']}.mp4"
        vx.poll(lambda u=url: (_head_ok(u)), lambda ok: ok, 300, interval=10,
                label=f"propagate {c['file_name'][-12:]}")
    total = sum(c["duration_ms"] for c in clips)
    print(f"Rendering {len(clips)} bricks, total {total/1000:.1f}s...")
    r, left = vx.render(cfg["project_id"], clips, cfg["export_name"],
                        cfg.get("project_title"), cfg.get("aspect", "9:16"))
    print(f"  queued: {r}")
    o = vx.wait_output(baseline_out)
    assert o is not None
    dest = os.path.join(out_dir, cfg["export_name"] + ".mp4")
    vx.download(o["mediaPath"], dest)
    print(f"DONE: {dest} ({o['filesize']}) — verify with ffprobe: expected {left/1000:.1f}s")


if __name__ == "__main__":
    main()
