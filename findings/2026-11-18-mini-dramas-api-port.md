# Run 7: first community-workflow port — Mini Dramas via API (17.21s verified)

Date: Nov 18 2026. Source: ai-playbooks/realistic-mini-dramas PLAYBOOK.md (fetched raw).
Config: run_mini_dramas.json (5 shots, 2 characters, realistic). Output: mini-dramas-api1.mp4.

## What was new (4 firsts verified in one run)
1. **Plain image generation via API** (`POST /ai/api/generate_image`, type=photorealistic,
   enhancePrompt=0) — first end-to-end verification. Images land at the same
   `renderplatform.com/preview/<uuid>.jpg` pattern. All 5 shot images generated first-try.
2. **image2video WITHOUT lipsync, videoLength honored**: clips came out exactly
   5.04s (videoLength=5) and 4.04s (videoLength=4). The `videoLength` param governs
   non-lipsync clips precisely.
3. **Enhance-video-prompt OFF via API** (enhanceVideoPrompt=0) — needed so the playbook's
   tightly-worded prompts aren't rewritten. Worked.
4. **In-point trimming via API**: brick `start_time` = trim-in (ms) + `duration` = trimmed
   length. Playbook trims applied exactly: dialogue 5s clips -> 4.1s keep (in 300/out 600),
   action 4s clips -> 2.5s keep (in 500/out 1000). Export 17.206s vs 17.51s brick-math —
   frame-boundary quantization at 24fps (~0.3s). Expected, not a bug.

## How the playbook mapped to the API (key discovery)
- Mini Dramas does NOT use consistent-character references: consistency comes from a
  **Character Bible line pasted VERBATIM into every prompt** (their "+ Consistent Character"
  is optional fallback). Our port skipped the reference endpoint entirely — no slot-2
  discovery needed for v1.
- Dialogue is **embedded in the video prompt** ("Immediately, within the first half-second,
  MAYA says, low and fast: \"...\"") with Lipsync HD OFF — the same embedded-dialogue
  pattern we verified in run 3, now driven via API.
- The style tag "shot on a cinema camera" LEAKED INTO IMAGE CONTENT once: S02's man held
  a cinema camera rig. Fixed by regenerating with "BOTH HANDS EMPTY, holding nothing,
  no camera, no filming equipment". LESSON: put explicit negative prop constraints in
  IMAGE prompts when the style tag mentions equipment.

## Known limitation observed
Text-only character consistency anchors COSTUME, not FACE: the same "MAYA" bible line
produced a consistent outfit but different faces across S01/S03/S05. Playbook accepts
this; upgrade path = generate one reference portrait per character and switch those
scenes to generate_image_consistent_character (mediaId per character).

## Script bug fixed during this run
wait_videos baseline: per-scene snapshots absorbed earlier scenes' items, so the
new-items poller could never reach the expected count (stuck at new=1 forever).
Fix: capture ONE library baseline before the batch and pass it to every poll (committed).

## Scorecard
- 5 images: 5/5 first-try usable after 1 regen (S02 prop leak)
- 5 videos: 5/5 completed, durations exact
- Export: ffprobe 17.206s, 1080x1920, h264+aac. Downloads/mini-dramas-api1.mp4.
- API-only except zero UI: 100% API (no browser interaction needed at any step).
