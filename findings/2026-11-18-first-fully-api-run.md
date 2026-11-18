# Run 6: first fully API-driven run — sleep-facts-api3, 17.136s verified

Date: Nov 17-18 2026 (overnight). Zero UI clicks for generation, lipsync, timeline, export.

## Result

- 3 scenes (9:16 lipsync): night lamp hook -> moonlight deep-sleep -> dawn payoff.
- Clips: 5.04s + 6.04s + 6.04s (dialogue-governed: 73/69/69-char lines).
- Export: `sleep-facts-api3.mp4` — ffprobe **17.136s, 1080x1920, h264+aac** (expected 17.126s).
- Scripted re-render (dry-run) reproduced a byte-equivalent 17.136s export.

## THE FALSE-ALARM TRAP: generated images never appear in My AI Images

Every image job returned `{success:true, uuid}` but the folder total stayed at 2 —
we nearly concluded the API was silently failing. It wasn't:

- **The library folder only holds images a user explicitly SAVED.** Even images generated
  via the UI (modal carousel) do not appear in the folder until the icon-only save click.
- **The generated image is always at**
  `https://user-assets.renderplatform.com/preview/<job-uuid>.jpg` — verify with a HEAD
  request (200 = ready). NOTE: without the `.jpg` suffix you get 404 (cost us an hour).
- The modal carousel is session-scoped: close the modal and unsaved generations are gone
  from the UI, but still retrievable via the preview URL.
- Corollary: verification rule for images = poll the preview URL, never the folder.

## New verified facts

1. `GET /project/open/<id>` returns the FULL project JSON incl. all tracks + bricks
   (path/baseUrl/data). The last missing read for a 100% API pipeline.
2. `GET /project/get_list` lists all projects (id, title, aspect, quality, size, format).
3. UI fires `generate_image_consistent_character` TWICE per click — that is the "pair".
   A single API post yields ONE image. mediaId in the captured UI call was 49209068
   (the slot-1 image actually loaded), not 49227282 as previously assumed.
4. `image2video` with `isTalkingVideoFromText=1, speech1=<line>` works headless; 3 jobs
   fired in one sequence landed as 3 sequential ids (49304940/48/56) — fire order ==
   scene order, and processing took ~1-4 min each.
5. get_media for completed videos now exposes everything a brick needs: fileName,
   duration (ms), frameSize, frameRate, uuid, imagePath, thumbUrl, mediaPath (null for
   library clips; the CDN path is `https://cdn-ny-b.videoexpress.ai/video/<fileName>.mp4`).
6. Library modal reads go over XHR, not fetch — a fetch-only interceptor misses them.
   Patch both when capturing.

## THE SCRIPT

`api_run.py` (this repo) runs the whole pipeline from a JSON config:

    python api_run.py run_sleep_facts.json           # full run
    python api_run.py run_dry_test.json --dry-run    # re-render existing clips (no credits)

Auth: cookies.json (PHPSESSID + REMEMBERME exported from the logged-in browser via CDP
Network.getCookies; gitignored). Session cookies expire — re-export when runs start 401ing.

Known script limitation: for a full run it polls only the videos FOLDER to find the new
clips (images are preview-URL-verified directly). If another device/job writes to the
account concurrently, the id-baseline poll could mismatch — fine for solo use.

## Next

- Scale: N scenes per config; parallel image jobs; batch waves toward hour-long runs.
- The dry-run mode is the cheap validator after any refactor.
