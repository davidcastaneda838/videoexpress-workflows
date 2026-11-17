# Playbook Improvements — live-verified corrections to SYSTEM_PROMPT_full_length.md

Date: Nov 17 2026 (after runs 1–4)
Basis: four live runs on VideoExpress 3.5 (3-scene video, duration experiments, user-guided 10s tests, first fully autonomous 6-scene run with ffprobe-verified export).
Deliverable: an annotated/improved copy of the playbook at `SYSTEM_PROMPT_full_length_improved.md` in this repo. The original stays untouched as the pristine upstream reference.

The upstream playbook (`strontiumplatform/VideoExpress.ai-Full-Length-Consistent-Character-Realistic-Talking-Avatar-Video-Workflow`) is strong on structure and reliability rules, but several of its assumptions are wrong or unverified against the current live UI. Here is everything we'd change, ordered by impact.

---

## 1. Correctness fixes (playbook facts that our runs contradicted)

### 1a. Duration is DIALOGUE-governed, not slider-governed (biggest fix)
- Playbook claim: set the Manual Video Length slider to 8 for each scene; 7 scenes x 8s ~= 60s.
- Verified live (run 3, twice; reconfirmed run 4):
  - **Lipsync HD clips are trimmed to the spoken-dialogue length.** The slider sets a MAX, not the actual length. A 100-char Actor 1 Script speaks in ~5–6s, so Lipsync clips come out ~6s, not 8s. Manual Video Length = 10 + Lipsync HD + 89-char dialogue still rendered a ~6s clip.
  - **Non-lipsync clips honor the slider** (full 10s confirmed twice on the timeline).
  - **Hard ceiling: 10s per clip, always** (occasionally 11–12s by luck; not reliable).
- Consequence for the ~60s target: 7 x 8s is wrong math. Correct plans:
  - Lipsync HD route: **~10 scenes x ~6s** (dialogue-governed), or
  - Non-lipsync route: **~6 scenes x 10s** using the embedded-dialogue pattern (see 1c).
- The playbook's fallback ("if the slider doesn't render, write ~11 scenes") is accidentally right for the wrong reason — the scene count must go up because of dialogue trimming, not slider absence.

### 1b. Gallery checkbox default
- Playbook claim: `input[name="shared"]` ships CHECKED BY DEFAULT (Trap 1).
- Verified: on this account it ships **UNCHECKED**. The trap's mechanism (silent reset on modal reopen) is real, but the correct, safe rule is state-based, not default-based:
  - **Read the checkbox's state before every Create Image and every Create Video; untick only if ticked; re-read after any modal reopen.** Never assume either default.

### 1c. The embedded-dialogue pattern (missing from the playbook entirely)
- Without Lipsync HD, writing `The woman says "<line>"` in the Video and Audio Prompt makes the character speak that line correctly at the FULL slider length (verified by ear).
- Without any embedded line, the non-lipsync engine improvises **gibberish speech** — a silent failure mode the playbook never mentions.
- Trade-off: bypasses the 100-char Actor 1 Script limit and fills the full 10s; lip-sync quality is lower than Lipsync HD (lipsync HD = perfect lips, dialogue-capped length).
- This gives two proven routes per video; choose per project (lip accuracy vs. fewer scenes/faster run).

### 1d. Slider + checkbox reset on every modal reopen
- The generator modal resets to: slider = 5, aspect = Landscape 16:9, every reopen. The playbook mentions nothing resetting except the gallery checkbox.
- Rule: re-verify the FULL settings checklist (aspect 9:16, slider, advanced mode, manual length, consistent character, gallery) before **every** Create — not once per session.

### 1e. Completion signal
- Playbook marks folder-count polling "UNVERIFIED." Verified: in-progress tiles in My AI Videos show a percentage (e.g. "34%"), and the button-disabled state marks an in-flight job. Folder count + percent tiles = a clean poll loop.

## 2. Kill the double-submit / duplicate-export bug class (new trap)
- Observed: run 4 produced TWO identical exports (a synthetic submit attempt followed by a real one both landed).
- New rule: after ANY Create/submit click, **verify the expected result (dialog closed / counter registered / folder count incremented) before ever retrying**. "Dialog still open" means the click didn't land — re-click with the full event sequence, but never blind-fire a second submit while the first may have registered.

## 3. Trim step (STEP 6) — automate measurement, lock the layers
- Waveform + hand-dragging both layers is the slowest, most failure-prone part. Improvements:
  - Measure silence from the waveform image programmatically (px-per-second ruler math: read two ruler marks' x positions; at 3x zoom ~40px/s; export ruler is ~19px/s in default 3x — calibrate per session). Do not rely on play-and-watch timing.
  - Trim both layers by the SAME pixel delta, then verify: screenshot + confirm both brick edges align on the ruler after each clip. Mismatched layers = lips out of sync.
  - Trim handles ignore synthetic DOM events and small drags. Working method: real CDP mouse press/move/release, buttons=1, LARGE drag distance (~20px+); the handle snaps to the landing point (quantized — overshoot, ease back). Trim at 3x zoom for sub-second precision.

## 4. Batch speed & asset identification
- Image generation can slow to **5–10 min per scene**. During a slow batch, NEVER re-click Create Image — a double submit creates duplicate image pairs that pollute the carousel and the scene mapping.
- Tile captions/titles are ellipsis-truncated in the DOM. The playbook's caption-matching idea is right but fragile; better: map tiles by `data-image` thumbnail URL — download thumbnails, composite one labeled grid (PIL), identify all scenes in a single vision pass. Tiles also carry `data-ident` as a stable handle.

## 5. Crash recovery — two casualties the playbook's R8 misses
- A scene whose **Create Lipsync Audio dialog was open at crash time is LOST** even if Create was clicked inside the dialog. Verify the expected clip count in My AI Videos after every batch; a missing scene needs a full re-run (image + video + dialog).
- After a crash/reopen, the modal comes back **Landscape 16:9** — every clip generated from that reopen comes out 1920x1080. Re-select 9:16 and verify before each Create.
- Keep the scene plan (bible, actions, lines, idents) in a workspace JSON file so recovery never depends on page state.

## 6. Scaling to hour-long videos — structural gaps
The doc covers ONE ~60s run (2 batches x 5). An hour needs ~360 clips at 10s. Required upgrades:
- **Batch-wave orchestration**: scene-plan JSON -> waves of 5 -> verify folder counts between waves -> auto-assemble by ident (not caption).
- **Programmatic timeline assembly + trimming**: at 360 clips, manual drags are impossible. This is the single biggest lever.
- **Checkpointing**: Save the project after every batch; a crash must never cost more than one batch.
- **Cost/time awareness**: 360 clips x 1–3 min each ~= 6–18 hours of generation plus credits. Run plans should state the budget up front.

## 7. Model guidance (agrees with us)
- The playbook reports lightweight models failed 3x live and mid-tier models pass. Matches our experience — the workflow's reliability rules matter more than raw model size, but they cannot rescue a model that skips verification steps.

---

## Recommended defaults for OUR runs (supersedes the playbook where they differ)
- Read (never assume) the gallery checkbox state before every generation.
- Aspect 9:16 verified before EVERY Create; slider re-set every reopen.
- Lipsync clips: expect dialogue-length clips; plan scene counts on ~6s.
- Non-lipsync talking clips: embed the line in the Video and Audio Prompt; expect full slider length.
- Verify dialog closed after every submit; check for duplicate exports/imports.
- ffprobe every export; expected duration = sum of clip lengths.
- After every run: push findings to both repos (workflows + skill).
