"""Timeline brick math: duration and left are milliseconds."""

import pytest

from vx.render import build_bricks, build_render_payload
from vx.videos import estimate_clip_seconds, clamp_video_length

TPL = {"id": "1", "type": "video", "bricks": [], "track_id": "45"}


def _clip(name, dur_ms, **kw):
    return {"media_id": 1, "file_name": name, "duration_ms": dur_ms, **kw}


def test_brick_duration_and_left_ms():
    clips = [_clip("a", 5000), _clip("b", 6000), _clip("c", 4000)]
    bricks, total = build_bricks(TPL, clips)
    assert [b["duration"] for b in bricks] == [5000, 6000, 4000]
    assert [b["left"] for b in bricks] == [0, 5000, 11000]  # cumulative ms
    assert total == 15000


def test_trims_reduce_duration_ms():
    clips = [_clip("a", 6000, trim_in_ms=500, trim_out_ms=500)]
    bricks, total = build_bricks(TPL, clips)
    assert bricks[0]["duration"] == 5000
    assert bricks[0]["start_time"] == 500  # trim_in becomes start_time
    assert total == 5000


def test_negative_trim_rejected():
    with pytest.raises(ValueError):
        build_bricks(TPL, [_clip("a", 1000, trim_in_ms=800, trim_out_ms=500)])


def test_brick_urls_use_cdn():
    bricks, _ = build_bricks(TPL, [_clip("abc123", 5000)])
    b = bricks[0]
    assert b["path"] == "https://cdn-ny-b.videoexpress.ai/video/abc123.mp4"
    assert b["thumbUrl"].endswith("/thumbnail/abc123_small.jpg")
    assert b["track_id"] == "45"


def test_dialogue_governed_clip_length():
    assert estimate_clip_seconds("") == 5
    assert estimate_clip_seconds("x" * 55) == 5   # ~55-60 chars ~ 5s
    assert estimate_clip_seconds("x" * 60) == 5
    assert estimate_clip_seconds("x" * 70) == 6   # 70+ chars ~ 6s
    assert estimate_clip_seconds("x" * 300) == 10  # max 10s


def test_video_length_capped_at_ten():
    assert clamp_video_length(10) == 10
    assert clamp_video_length(99) == 10
    assert clamp_video_length(0) == 1


def test_build_render_payload_shape():
    tracks = [
        {"bricks": [{"type": "video", "id": "1"}], "track_id": "45"},
        {"bricks": [{"type": "audio", "id": "2"}], "track_id": "46"},
    ]
    bricks, total = build_bricks(TPL, [_clip("a", 5000)])
    payload = build_render_payload(tracks, bricks, "export1", project_id=481590)
    opts = payload["options"]
    assert opts["name"] == "export1" and opts["project_id"] == 481590
    assert opts["format"] == "mp4" and opts["aspect"] == "9:16"
    assert len(payload["data"]) == 2
    assert payload["data"][0]["bricks"][0]["left"] == 0  # ms
