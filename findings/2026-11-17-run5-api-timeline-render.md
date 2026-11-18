# Run 5: sleep-facts-10s — API-assembled timeline + render, verified 10.008s

Date: Nov 17 2026 (evening, survived a power outage mid-run — everything below is outage-proof because it lives server-side).

## What was built
A ~10s vertical video (2 lipsync scenes, sleep-facts topic, run-4 blonde character reused from My AI Images):
- Scene 1 (hook): "Here's a sleep fact that sounds fake: your brain cleans itself at night."
- Scene 2 (payoff): "That deep-clean happens only in deep sleep. Miss it, and waste builds up."
- Export: `sleep-facts-10s-api1.mp4` — ffprobe: **10.007800s, 1080x1920, h264 + aac** (in C:\Users\david\Downloads).

## New endpoints captured (via fetch/XHR monkey-patch interceptor)

### Lipsync HD is NOT a separate endpoint
The lipsync dialog's Create goes through the SAME `POST /ai/api/image2video` with extra fields:
- `isTalkingVideoFromText=1` (the Lipsync HD flag)
- `speech1=<actor script>` and `speech2=` (Actor 2 script)
- `prompt=<lipsync dialog's Video Prompt — actor direction line>`
- `videoLength=10` (the Manual Video Length slider value)

### Consistent-character image variants
- `POST /ai/api/extend_prompt/consistent_character` — `prompt=..&imageType=human&imageMediaId=<reference media id>`
- `POST /ai/api/generate_image_consistent_character` — `prompt=..&type=human&mediaId=<reference media id>&aspect=9:16&generatorName=create_from_prompt`
- One Create Image click produces a PAIR (2 images = 2 calls). The reference media id (ours: 49227282) is passed explicitly — the API knows the face source.

### THE RENDER/EXPORT ENDPOINT — timeline assembly via API
`POST /render_project/<project_id>` (project_id ours: 481590), JSON body:
```
{ "options": { "name", "quality": "high", "size": "1080", "format": "mp4", "aspect": "9:16",
               "project_id": 481590, "project_title": "sleep-facts-10s" },
  "data": [ { "title": "#", "index": 0, "id": "45", "muted": false, "video_disabled": false,
              "fast_cut_enabled": false, "fast_cut_type": "zoom", "timestamp": <ms>,
              "bricks": [ BRICK, BRICK, ... ] },
            { ... track 47 (audio), bricks: [] } ] }
```
BRICK (video): `{ id, media_id, type: "video", fileName, path/videoUrl, imageUrl/imagePath, duration (ms), duration_time (ms), start_time (in-point, ms), left (position on timeline, ms), track_id, title, frameSize, frameRate, thumbUrl, volume, resizable, is_active, deleted, transitionIn/Out, options }`

**Trimming = editing `duration`** (ms). Position = `left` (ms). In-point = `start_time`. Response:
`{"success":true,"action":"pending","queue_size":18}` — then poll `/api/get_list_output` for a result with a NEW id.

## Verified results
1. UI export (before API assembly): 12.097s — 2 clips x 6.0417s (dialogue-governed; ~72-73 char lines = ~6s, NOT 5s — confirmed again).
2. API-assembled render with `duration: 5000` per brick, `left: 0 / 5000`: **exactly 10.0078s**, 1080x1920 h264/aac. TRIM AND POSITION VIA API WORK.
3. To get true 5s clips by dialogue alone, lines must be ~55-60 chars; ~73 chars = ~6s.

## Traps hit this run (all documented in skill)
1. **STUCK DRAG GHOST**: an unresolved mousedown (helper `.ui-draggable-dragging` still in DOM) re-drops the OLD tile on the NEXT drag's mouseup — the second brick was silently a duplicate of scene 1. RULE: after every timeline drag, verify `document.querySelector('.ui-draggable-dragging')` is GONE before the next drag, and verify the placed brick's media_id (the render payload exposed this bug — the DOM had no readable brick ids).
2. **Brick DOM check**: `.brick` elements do NOT contain `<img>` — thumbnail is background; slot/reference checks via `querySelector('img')` return false negatives. Use the render payload or screenshots for verification.
3. **Double UI-POST at render layer**: the UI export dialog fired render_project twice (two buttons stacked?). This time both renders completed (12.097s duplicate export id 795253). Dedupe NOT guaranteed at render layer — check get_list_output for duplicate ids and use the newest unique one.
4. **Auto-enhance corrupts consistent-character prompts**: rewriting the bible into "Portrait of the same woman..." produced one bad abstract generation. Keep the enhancer off for scene prompts (it did NOT run on the second, fixed generation once unticked... note: checkbox state read differently in re-rendered modal).
5. **Power-cut resilience**: login + all server-side state survived a full power outage; reattach = relaunch Chrome with port, clean strays, done.

## Pipeline status after run 5
- Images: API ✓ (generate_image / generate_image_consistent_character)
- Videos + lipsync: API ✓ (image2video + speech1/isTalkingVideoFromText)
- Timeline assembly + trim: API ✓ (render_project payload)
- Export: API ✓ (same endpoint)
- Still UI-only: nothing essential! Remaining UI: reference-photo attach (could map to imageMediaId — already known), project save dialog.
- NEXT: script the full end-to-end API run (N scenes, no clicking) and validate a 3-scene ~18s run, then scale to batches.
