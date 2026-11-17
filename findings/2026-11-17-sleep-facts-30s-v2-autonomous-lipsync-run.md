# Run 4 — sleep-facts-30s-v2: first fully autonomous 6-scene Lipsync run (2026-11-17)

**Goal:** full ~30s talking video, run end-to-end by Hermes with the updated skill — no step-by-step user instruction.
**Route:** Lipsync HD (dialogue-governed clips) · 6 scenes · Vertical 9:16 · Creative mode OFF · same blonde/lavender-sweater character as run 2.
**Result:** ✅ Export verified: `sleep-facts-30s-v2.mp4` — 1080×1920, h264/aac, **36.73s**, 19.9 MB (ffprobe-checked).

## Script (6 sleep facts, ~82–88 char lines)

| # | Emotion | Line |
|---|---------|------|
| 1 | Amazed | "You'll spend twenty-six years of your life asleep. That's ten years just dreaming." |
| 2 | Curious | "While you dream, your brain replays what you learned that day, etching it into memory." |
| 3 | Surprised | "One bad night of sleep slows your reaction time more than a couple of drinks does." |
| 4 | Intrigued | "Snoozing right after you learn locks it in. Snoozing before you learn clears the desk." |
| 5 | Playful | "Nightmares aren't random either. Your brain rehearses threats at night, like practice." |
| 6 | Excited | "So tonight, protect your sleep like your grades depend on it. Because they truly do." |

Clip idents (My AI Videos): scene 1 `49248659` (+ spare `49248579`), 2 `49248937`, 3 `49249662`, 4 `49250468`, 5 `49251409`, 6 `49251505` (+ spare `49251590`).

## What the updated skill changed vs run 2

- **Reference photo slot, not just preview:** "Use from Library" shows the image in the preview but does NOT attach it. The slot-1 "Reference Photo" button + library picker + Choose is what actually binds it (user caught this live).
- **Generator field map corrected:** Image Prompt = `#opt_prompt`, Video/Audio Prompt = `#opt_video_prompt` (they are separate elements — run 2's stacked-duplicate finding only applies inside the Lipsync dialog).
- **Lipsync dialog state registration:** writing the text into the dialog's textareas via JS isn't enough — the app state (Total characters counter) only updates when *all* duplicated textarea instances get input/change/keyup events. The Create button then needs a real CDP click (mousemove → press → release); synthetic clicks silently no-op.
- **Timeline drag & drop decoded:** an invisible `.drop-panel` overlay covers the media tiles, so native CDP mousedown never reaches them. Working recipe: synthetic mousedown dispatched on the tile element + real CDP mousemove steps to the track + CDP release. All 6 clips placed on track 1 in story order first try with this recipe.
- **Fast Cut Toggle** enabled deliberately this time (punchy facts style) — skill now documents it's intent-dependent.

## Numbers / corrections

- Dialogue-governed clips ran **~6s each** with 82–88-char lines → 6 scenes = **36.7s**, not 30. For a true 30s target: ~5 scenes or shorter lines. (Run 3's "Manual Video Length governs non-lipsync" rule still stands; this run was all-Lipsync.)
- Timeline ruler scale in this zoom was **~19 px/s** (earlier estimate 23) — ruler math is approximate; always ffprobe the export.
- Image generation slowed to 5–10 min per scene mid-run (vs ~1 min in run 2). Poll generously, never re-click Create Image.
- A synthetic submit followed by a real retry can **land twice** → two identical exports. Two spares this run; harmless, but check the My Videos modal for duplicates.
- Editor tab crashed mid-export-wait (`about:blank`), and re-navigation hit the login wall (session cookie dropped). Server-side project/clip state survived; user logged back in manually.

## Verdict

Pipeline is now fully autonomous for the standard talking-facts format: script → reference bind → per-scene image → per-scene lipsync clip → timeline assembly → save → export → ffprobe verification, with no user clicks needed except the manual login after the tab crash.
