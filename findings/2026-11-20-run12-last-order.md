# Run 12 — LAST ORDER (Nov 20, 2026)

Mini Dramas playbook port (user-pasted 15-shot script). Delivered end to end:
43.26s trimmed export, 70.6s raw, 1080x1920 h264+aac, 21.74 MB.

## Facts
- Cast: Dara (waitress, ref portrait id 49626593, plain generate_image photorealistic,
  auto-saved); Caller = voice only, voiced as an off-screen wall-phone voice via the CC
  native route ("a tinny voice crackles out of the telephone speaker... says from the
  phone"). Phone-voice dialogue through CC native produced ZERO burned captions
  (verified on 20-frame grid + 18-frame grid).
- 15 images (3 waves of 5) + 15 videos (3 waves of 5), CC standard, video_length 5/4,
  auto-assembled on project 482711 in story order, 70.6s raw.
- Export `last-order-final.mp4` via trim_calc audio-measured trims (capped 1.2s) ->
  44.5s planned, 43.26s actual.

## New failure modes + fixes (all live-verified this run)
1. TRANSIENT REJECTION = CAP, not flake: scene 15's video was rejected twice with
   'Error. Please try again later' (empty uuid). Root cause: the RESUME script's
   slot-checker counted in-flight jobs relative to a baseline taken AFTER the original
   14 fired, so the cap check was a no-op and it fired into a saturated server. FIX:
   resume scripts must count GLOBAL non-completed jobs (all statuses != completed),
   never baseline-diff, for the 5-slot check. Scene 15 accepted on attempt 1 after fix.
2. RESUME CLIP IDENTIFICATION: a resume's wait_videos(baseline, expected=N) only counts
   items newer than baseline — with 14 clips fired by a dead process, expected must be
   1 (the missing scene), and the full 15-clip set must be re-identified by the
   'R## —' shot-tag prefix in the library `name` field (robust against older clips in
   the folder), sorted by tag number. baseline-diff + id-sort is NOT resume-safe.
3. DNS-PINNED RENDER: Python's getaddrinfo flaked through the whole placement save
   (curl/nslookup fine in the same minute — Windows resolver asymmetry). FIX:
   render_last_order.py pins app.videoexpress.ai -> 64.140.170.98 by monkeypatching
   socket.getaddrinfo; render + poll + download ran clean through the flake. Placement
   save succeeded via the curl --resolve fallback (3rd verified save this way).
4. GRID BLACK-TILE ARTIFACT: a select+tile frame grid can show black tiles mid-grid
   that are NOT in the video (sampling math); before diagnosing black frames, run
   `blackdetect=d=0.2:pix_th=0.10` over the whole file. This run: 2 suspicious tiles,
   blackdetect found zero black segments -> artifact, video clean.

## Artifacts
- run_last_order.json (15-scene config), run_last_order_portraits.json (Dara portrait)
- resume_last_order.py (fixed resume: global slot count + R## prefix matching)
- place_last_order.py (place-only recovery with curl --resolve fallback)
- render_last_order.py (DNS-pinned render wrapper — reusable for any run)
- run_last_order_trim_src.json / run_last_order_render.json
- Download: C:/Users/david/Downloads/last-order-final.mp4; CDN mediaPath in get_list_output.
