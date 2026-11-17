# Run Report: Duration Rules & Feature Training — Nov 17, 2026

Two controlled runs in VideoExpress 3.5: a 3-scene ~30s "sleep fact" video (end-to-end) and a
user-directed step-by-step duration experiment. Everything below was verified live.

## Run 2 — 3-scene sleep-fact video (end-to-end)

- Character: 32yo blonde woman, lavender sweater, fairy-lit bedroom (AI-generated, vertical 9:16)
- 3 scenes × 10s target, emotional wave: Shocked → Curious → Excited
- Character consistency: **perfect** across all clips (frozen character bible + reference photo)
- Audio: perfect; timeline placement and editing: perfect (user verdict)
- Export: downloaded mp4 verified with ffprobe — but only **13.8s** (see Duration Rules below)
- Final output got **Fast Cut transitions** (see run 3 findings) — user rated the editing perfect

## The duration rules of VideoExpress 3.5 (the big finding)

**1. The hard ceiling: 10 seconds per clip.** The Manual Video Length slider (3–10) is the max.
Occasionally an 11–12s clip slips out, but never count on it.

**2. Lipsync HD clips are trimmed to the dialogue.** If the spoken line is ~4s, the clip comes
out ~4s — regardless of the Manual Video Length slider. A controlled test (Manual Length = 10,
89-char dialogue ≈ 5s spoken) still rendered a ~6s clip. No "dead stare" filler.

**3. Non-lipsync clips honor the slider fully.** Without Lipsync HD, Manual Video Length = 10
produced exact 10.0s clips (measured on the timeline: brick width ÷ ruler px-per-second).

**4. The embedded-dialogue pattern (discovered today).** Without Lipsync HD, putting the speech
directly into the *Video and Audio Prompt* like:

    ... cozy room ambience. The woman says "My cat Max steals my socks every morning."

produces a full-length clip in which the character **speaks the line correctly**.
- If you *don't* embed a line, the engine improvises **gibberish speech**.
- This bypasses the 100-char "Actor 1 Script" limit that caps Lipsync HD dialogue at ~5-6s.
- Trade-off: Lipsync HD still gives true lip sync; the embedded pattern's lip movement
  wasn't critically examined yet. Pick per video: Lipsync HD for close-up talking heads,
  embedded pattern for narration-style clips where duration matters.

**Practical consequence for long videos:** at a hard 10s/clip ceiling, an hour-long video needs
**~360 clips minimum** — orchestration/batching is the core engineering problem, not clip length.

## Verified technique: measuring clip duration without downloading

Drag a library tile onto an empty timeline, measure the brick's pixel width, and divide by the
ruler's pixels-per-second (read the x-positions of two ruler marks). Works every time, no download.

## UI traps discovered (all verified live)

- **Two stacked aspect-ratio switches** exist in the modal DOM (one hidden). Toggle only the
  visible one; a DOM `active` read on the hidden one lies.
- **`#opt_prompt` id collision**: the generator's Image Prompt AND the lipsync dialog's own
  Video Prompt are both `textarea[name=prompt]#opt_prompt` (generator first in DOM order).
  The dialog's is `querySelectorAll('textarea[name=prompt]#opt_prompt')[1]`.
- **Trim handles**: synthetic DOM events and small (<~20px) mouse drags silently fail to resize
  timeline bricks. Real CDP mouse drags with a large overshoot work; the edge snaps to the mouse
  landing (quantized — overshoot then ease back). Zoom the timeline in for sub-second precision.
- **Auto Align Clips** moves only video bricks — audio layers don't follow; drag them into place.
- **Save** opens a required project-name dialog (`#modalFieldName`, stacked duplicates — use the
  last visible one).
- The modal resets both prompt fields after every submission — re-fill and re-verify each scene.
- Image Prompt is rewritten by auto-enhance after submit (expected, not corruption).

## Feature training (user-taught)

- **Creative mode**: wider visual-style range, better artistry/realism balance, slower generation.
- **Narration Video (Choose my Audio)**: advanced narration builder (Text-to-Speech with
  language/voice/emotions/speed/pitch, CloneVoice.ai, Voice Recording, Import Audio). Tutorial pending.
- **Aspect default 16:9 is deliberate** (YouTube is the common case). Choose at project start:
  landscape = YouTube, vertical = TikTok/Shorts/Reels.
- **Enhance Prompt**: for weak prompt writers; unnecessary when the agent writes good prompts.
- **Good/Bad rating buttons**: feedback to the generation engine on prompt adherence — rate clips.
- **Fast Cut Toggle**: applies fast-cut transitions between clips; affects the export silently.
  Intent-dependent — right for punchy content, wrong for slow/cinematic pacing.

## Infrastructure lesson

A persistent browser profile (`browser.user_data_dir`) must be set BEFORE the first run — without
it every session starts logged out. Set once, login survives crashes and relaunches.
