"""Render: build timeline bricks (ms math), queue render, poll outputs.

HARD RULE: brick duration and left are MILLISECONDS. `left` is the cumulative
timeline position (sum of previous durations).
"""
import json

from .http import CDN


def build_bricks(template_brick, clips, base_id=900, track_id="45"):
    """Build video bricks from a template brick.

    clips: [{media_id, file_name, duration_ms, trim_in_ms=0, trim_out_ms=0, title}]
    Returns (bricks, total_duration_ms). Raises on negative trimmed duration.
    """
    bricks = []
    left = 0
    for i, c in enumerate(clips):
        b = json.loads(json.dumps(template_brick))
        f = c["file_name"]
        in_ms = c.get("trim_in_ms", 0)
        dur = c["duration_ms"] - in_ms - c.get("trim_out_ms", 0)
        if dur <= 0:
            raise ValueError(f"clip {i}: trim leaves {dur}ms")
        b.update({
            "id": str(base_id + i), "media_id": c["media_id"], "type": "video",
            "fileName": f, "path": f"{CDN}/video/{f}.mp4",
            "videoUrl": f"{CDN}/video/{f}.mp4",
            "imageUrl": f"{CDN}/image/{f}.jpg", "imagePath": f"{CDN}/image/{f}.jpg",
            "thumbUrl": f"{CDN}/thumbnail/{f}_small.jpg",
            "duration": dur, "duration_time": dur,
            "start_time": in_ms, "left": left, "track_id": track_id,
            "title": c.get("title", f"scene{i + 1}"),
        })
        left += dur
        bricks.append(b)
    return bricks, left


def build_render_payload(tracks, bricks, export_name, project_id,
                         project_title=None, aspect="9:16"):
    """Assemble the /render_project/<id> JSON body from normalized tracks."""
    video_track = next(t for t in tracks if any(
        b.get("type") == "video" for b in t.get("bricks", [])))
    audio_track = next(t for t in tracks if t is not video_track)
    return {
        "options": {"name": export_name, "quality": "high", "size": "1080",
                    "format": "mp4", "aspect": aspect, "project_id": project_id,
                    "project_title": project_title or export_name},
        "data": [{**video_track, "bricks": bricks}, audio_track],
    }


class RenderMixin:
    def outputs(self):
        return self.get("/api/get_list_output")["results"]

    def render_project(self, project_id, clips, export_name, project_title=None,
                       aspect="9:16"):
        """Rebuild the video track from the project's template brick, then queue
        the render. Fire ONCE. clips: [{media_id, file_name, duration_ms, ...}]."""
        tracks = self.timeline_tracks(project_id)
        video_track = next(t for t in tracks if any(
            b.get("type") == "video" for b in t.get("bricks", [])))
        tpl = video_track["bricks"][0]
        bricks, left = build_bricks(tpl, clips)
        payload = build_render_payload(tracks, bricks, export_name, project_id,
                                       project_title, aspect)
        r = self.post(f"/render_project/{project_id}", json_body=payload)
        if not r.get("success"):
            raise RuntimeError(f"render rejected: {r}")
        return {"response": r, "total_duration_ms": left}

    def wait_output(self, baseline_ids, timeout_s=900):
        """Poll /api/get_list_output until a new export appears."""
        def check():
            new = [o for o in self.outputs() if o["id"] not in baseline_ids]
            return new[0] if new else None
        out = self.poll(check, lambda v: v is not None, timeout_s,
                        interval=15, label="render")
        return out

    def download_output(self, output, dest):
        return self.download(output["mediaPath"], dest)
