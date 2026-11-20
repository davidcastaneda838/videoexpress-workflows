"""vx — VideoExpress API client package.

Hard rules enforced across the package:
  - max 5 concurrent video-generation jobs (VideoJobLimiter)
  - every write fires ONCE; on a lost response, verify via reads before retry
  - never fabricate results: real handles (media_id, uuid, output URL) or errors
  - clip length is dialogue-governed (~55-60 chars ~5s, 70+ ~6s, max 10s)
  - brick duration/left are milliseconds
"""
from .client import Vx
from .http import BASE, CDN, PREVIEW, VxHttp
from .limiter import VideoJobLimiter, MAX_INFLIGHT_VIDEOS
from .videos import estimate_clip_seconds, clamp_video_length

__all__ = ["Vx", "VxHttp", "VideoJobLimiter", "MAX_INFLIGHT_VIDEOS",
           "estimate_clip_seconds", "clamp_video_length",
           "BASE", "CDN", "PREVIEW"]
