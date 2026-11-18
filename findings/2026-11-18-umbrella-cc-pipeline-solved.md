# Run 9 — Umbrella Rebuild: the pipeline is solved (Nov 18, 2026)

## Result
3-scene "Umbrella" drama rebuilt on the CC dialogue standard. User verdict on all three
clips: **flawless** — scenes, character consistency, dialogue, mood, atmosphere, "hardly
any AI drift", scene-to-scene consistency. Assembled on project 482711 timeline (911@0,
912@5042, 913@10084; 15.1s raw), awaiting user-approved render.

## What this run proves (each previously-unsolved problem now closed)
1. **Character consistency**: reference portraits (Maya 49366306, Dane 49366308) +
   `generate_image_consistent_character` per scene → same faces everywhere.
2. **Dialogue**: ai-playbooks realistic-consistent-character-videos architecture on the
   NATIVE route (Lipsync HD OFF, line in the video prompt): Short Tag speaker ID →
   Voice Lock (fixed voice+accent phrase, verbatim every clip) → line in DOUBLE QUOTES →
   spoken after a quick breath → flowing prose, sound woven in, ends "no music".
   Verified flawless TWICE on single-clip tests, then 3/3 in the drama.
3. **Captions**: caused by negative phrases ("No subtitles. No on-screen text.") —
   the text encoder latches onto 'subtitles'/'text' and renders them. Zero negative
   phrases → zero burned-in text. Quoting dialogue (quoted or not) also paints captions;
   the CC style above never quoted the line outside the Voice Lock sentence pattern.
4. **Scene coherence**: mood/lighting/setting held across independently generated clips
   by reusing the same location block in every image prompt (World Lock concept).
5. **Automation**: 100% API, zero UI clicks. New reusable script: gen_drama_place.py
   (generate N scenes → place clips on project timeline in order, NO render/export).
   gen_only.py = single-clip generation only. NOTE: urllib POST to project/save hit
   transient DNS failures twice (getaddrinfo failed) at the final save step; recovery =
   read media ids from the library, place via same-origin fetch() in the browser tab.

## Scripts (repo: davidcastaneda838/videoexpress-workflows)
- gen_only.py — generate 1 clip (image+video), leave in My AI Videos, no export
- gen_drama_place.py — generate N scenes, assemble project timeline, no export
- run_umbrella_cc.json — the flawless 3-scene config (CC dialogue standard reference)
- api_run.py — full pipeline incl. render/export (unchanged)

## Next
- Render "umbrella test" (3 bricks, ~14.5s after 200/300ms trims) on user approval.
- Scale: hour-long = ~360 clips via rolling 5-slot waves; orchestration is now the only
  remaining workstream.
