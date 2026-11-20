"""Video generation (image2video lipsync, text2video) + dialogue-governed
clip-length math.

HARD RULES baked in here:
  - every generation POST fires ONCE (use http.write_once when a verify-read exists)
  - max 5 concurrent video jobs (vx.limiter.VideoJobLimiter)
  - clip length is dialogue-governed: ~55-60 chars ~ 5s, 70+ chars ~ 6s, max 10s
  - brick duration/left are milliseconds
"""
from .http import CDN


def estimate_clip_seconds(dialogue):
    """Dialogue-governed clip length: ~55-60 chars ~ 5s, 70+ chars ~ 6s, max 10s."""
    n = len((dialogue or "").strip())
    if not n:
        return 5
    if n <= 60:
        return 5
    if n < 70:
        return 6
    return min(10, max(6, round(n / 12)))


def clamp_video_length(seconds):
    """Video length param is capped at 10s by the engine."""
    return max(1, min(10, int(seconds)))


class VideosMixin:
    def video_folder_ids(self):
        return {m["id"] for m in self.media_list(self.FOLDER_VIDEOS, limit=100)}

    def generate_video(self, image_uuid, image_prompt, video_prompt, dialogue,
                       aspect="9:16", video_length=None, lipsync=True,
                       enhance_video_prompt=1, dialogue_in_prompt=False):
        """image2video with optional lipsync (isTalkingVideoFromText).

        Fire ONCE. Returns a handle dict with the library baseline id-set for
        the poller. video_length defaults from the dialogue length (max 10s).
        lipsync=False + dialogue_in_prompt=True embeds dialogue in video_prompt.
        """
        if video_length is None:
            video_length = clamp_video_length(estimate_clip_seconds(dialogue))
        before = self.video_folder_ids()
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
        return {"baseline_ids": before, "video_length_s": int(video_length),
                "dialogue": dialogue or ""}

    def generate_text2video(self, prompt, dialogue="", aspect="9:16",
                            video_length=None, enhance_video_prompt=1):
        """Pure text-to-video (no source image). Fire ONCE."""
        if video_length is None:
            video_length = clamp_video_length(estimate_clip_seconds(dialogue))
        fields = {
            "prompt": prompt, "enhanceVideoPrompt": str(enhance_video_prompt),
            "videoLength": str(video_length), "aspect": aspect,
            "speech1": dialogue, "speech2": "",
            "generatorName": "create_from_prompt",
        }
        r = self.post("/ai/api/generate_text2video_dialog", fields)
        if not r.get("success") and not r.get("uuid"):
            raise RuntimeError(f"text2video rejected: {r}")
        return {"uuid": r.get("uuid"), "video_length_s": int(video_length),
                "response": r}

    def new_videos(self, baseline_ids):
        vids = [m for m in self.media_list(self.FOLDER_VIDEOS, limit=100)
                if m["id"] not in baseline_ids]
        done = [m for m in vids if m.get("status") == "completed"]
        return {"new": len(vids), "completed": done}

    def wait_videos(self, baseline_ids, expected=1, timeout_s=1500):
        """Poll My AI Videos until `expected` new clips are completed."""
        def check():
            res = self.new_videos(baseline_ids)
            return res["completed"] if len(res["completed"]) >= expected else None
        result = self.poll(check, lambda v: v is not None, timeout_s,
                           interval=20, label="videos")
        return sorted(result, key=lambda m: m["id"])

    def inflight_videos(self, baseline_ids):
        """Count unfinished new video jobs (for the 5-slot limiter)."""
        return sum(1 for m in self.media_list(self.FOLDER_VIDEOS, limit=100)
                   if m["id"] not in baseline_ids and m.get("status") != "completed")

    def wait_clip_propagation(self, file_name, timeout_s=300):
        """Render workers fetch clips from the CDN; rendering too early yields
        black bricks. Wait until the clip file is fetchable."""
        url = f"{CDN}/video/{file_name}.mp4"
        return self.poll(lambda: self.head_ok(url, min_bytes=100_000),
                         lambda ok: ok, timeout_s, interval=10,
                         label=f"propagate {file_name[-12:]}")
