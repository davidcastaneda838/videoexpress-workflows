"""Composite Vx client: HTTP core + all capability mixins."""
from .auth import cookies_file_from
from .http import VxHttp
from .images import ImagesMixin
from .videos import VideosMixin
from .audio import AudioMixin
from .library import LibraryMixin
from .projects import ProjectsMixin
from .render import RenderMixin
from .tasks import TasksMixin
from .limiter import VideoJobLimiter, MAX_INFLIGHT_VIDEOS


class Vx(VxHttp, ImagesMixin, VideosMixin, AudioMixin, LibraryMixin,
         ProjectsMixin, RenderMixin, TasksMixin):
    """VideoExpress client.

    Usage:
        vx = Vx("cookies.json")            # or Vx() with VX_COOKIES env set
        img = vx.generate_image_consistent("a smiling chef", 49209068)
        vx.wait_image(img["uuid"])
        with vx.video_limiter.slot():      # HARD RULE: max 5 concurrent videos
            handle = vx.generate_video(img["uuid"], iprompt, vprompt, dialogue)
            clips = vx.wait_videos(handle["baseline_ids"])
    """

    def __init__(self, cookies_file=None, opener=None):
        resolved = cookies_file_from(arg=cookies_file)
        super().__init__(resolved, opener=opener)
        self.video_limiter = VideoJobLimiter()
