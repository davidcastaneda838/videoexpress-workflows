# Run 11 — first 60s-class production: "The Caller — Inside" (20 shots)

Date: Nov 18 2026 (evening). Follow-up to Run 10's 10-shot "The Caller".
Goal: reuse the Caller's setup (same two reference portraits, same two locations,
same script structure) at the next rung — a 60s-class, 20-shot film.

## Deliverable (per the user's standing delivery flow)

- 20/20 clips generated, completed and left in **My AI Videos** — NO render, NO export,
  NO download. The user does final editing manually.
- Timeline assembled on project 482711 in story order and verified server-side after
  save: 20 bricks R01→R20, total **90.84s raw** (10 dialogue shots @5041.667ms + 10
  non-dialogue @4041.667ms). Clip naming for manual editing: brick_titles carry the
  RNN beat names.

## Script authoring (new layer of the workflow)

Story written BY the agent (not copied from a playbook) by template-filling:

- shots = length / 3 (60s -> 20 shots), ~1/3 dialogue-free (10/10 here)
- dialogue shots video_length 5, non-dialogue 4
- structure: hook R01, one escalation beat per shot through the middle, twist at ~70%
  (R15), payoff/cliffhanger last 1-2 shots (R20)
- the twist: ghost reveal ("I died in that car, sweetheart") continuing Run 10's
  cliffhanger "the call is coming from inside the building"; R20 bookends the original
  film's opening line ("You're live. Who's calling in?")
- per-shot prompts from stock blocks: image_prompt = style tag + framing + verbatim
  character description + World Lock sentence + counted props + "No text, logos or
  watermark"; actor_direction = CC dialogue standard (Short Tag, camera, motion-first
  "Initially... then...", Voice Lock verbatim, double-quoted line after a breath,
  sound in closing prose, ends "no music", ZERO negative phrases)
- config: run_caller_inside.json (brick_titles give the 20 beat names)

## NEW LESSON 1 — the wave limit applies to IMAGES too (user-mandated)

Firing all 20 scene image gens in one burst got the 20th REJECTED:
`{'success': False, 'uuid': '', 'message': '... Error. Please try again later.'}`.
gen_drama_place.py now runs images through the same MAX_INFLIGHT_VIDEOS=5 slot
limiter (live image jobs counted by HEAD on preview URLs: 404 = still generating).
Root cause was the script, not the account: only videos had the limiter.

## NEW LESSON 2 — mid-run video gen rejections + resumability

The same transient rejection hit video 15 mid-run. Recovery pattern (resume_caller3.py):

- identify ALREADY-FIRED clips by the `RNN — ` shot-tag prefix in the library item's
  `name` field (names start with the shot tag from actor_direction) — no duplicates,
  no guessing from thumbnails
- fire ONLY the missing scenes, with one 60s-delayed retry on rejection
- a rejection with empty `uuid` created NO job — safe to retry. Never retry a
  response that returned a uuid (double-submit rule).

## NEW LESSON 3 — DNS flakes keep hitting the final save

The known `getaddrinfo failed` transient killed the project/save after all generation
succeeded (third occurrence across runs). This time urllib retries also failed, so the
placement was redone entirely as same-origin fetch() from the logged-in browser tab
(GET /project/open -> build bricks in JS -> POST /project/save -> re-open and verify).
The full assembly is ~40 lines of page JS and works as a complete urllib-free fallback.

## Safety net worth keeping

Before reusing a project (gen_drama_place replaces the video track), snapshot the
existing timeline: `project_482711_caller_timeline_backup.json` holds Run 10's
10-brick timeline, restorable via /project/save. The exported mp4 is safe regardless.

## Run 10 stragglers also closed here

- `the-caller-final.mp4` = 33.62s ffprobe-verified (true 30s target MET, thread closed)
- `the-caller-no-trim.mp4` = 46.42s raw variant
- trim_calc.py audio-measured trims fixed the hardcoded-trim dialogue clipping
