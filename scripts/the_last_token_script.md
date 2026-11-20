# THE LAST TOKEN — 30s mini-drama (development pass by movie-bot)

**Logline:** A night-shift arcade attendant discovers an old coin-op machine that plays back a stranger's final memory — and spends his last token choosing whether to see it.
**Genre/Tone:** Melancholy sci-fi mini-drama. Quiet, blue-lit, one character on screen almost the whole time. Slow pushes, long holds.
**Status:** Script approved by boss-bot request. Ready for @videoexpress-bot execution. Trim target: ~30s (raw 35s, user edits manually).

## CHARACTER BIBLE
- **MARCUS (lead, all 7 scenes):** Man, late 30s, flannel work jacket over a gray thermal shirt, dark jeans, name tag reading "MARCUS" pinned to the jacket. Carries a flashlight in his right hand and a single silver arcade token in his left. Tired, soft-spoken.
- **THE WOMAN IN THE MACHINE (voice only, Scene 6):** A woman's voice, warm and tired, speaking as if from a phone recording. Never shown on screen.

## ENVIRONMENT BIBLE (paste verbatim into every scene prompt)
> A closed 1990s boardwalk arcade, 2:00 AM. Walls lined with dead cabinets, their screens dark. One machine glows in the center of the room against the back wall: a tall wooden cabinet with a purple-lit marquee reading "MEMORY LANE" and a small brass coin slot. A single hanging bulb above the machine casts warm amber light in a circle; everything beyond it is deep blue shadow. The floor is scuffed checkerboard tile. A counter with a cash register sits at the left edge of frame. Light source: one bulb, one machine. Marcus enters from the left each time.

## SCENE TABLE (7 shots x 5s = 35s raw; twist lands at ~70% in scene 5-6)

| # | Secs | Image prompt (shot description) | Visual prompt (motion/camera) | Dialogue |
|---|------|--------------------------------|-------------------------------|----------|
| 1 | 5s | A dark arcade at 2 AM, rows of dead game cabinets, one wooden machine with a purple marquee reading "MEMORY LANE" glowing in the center under a single hanging amber bulb. Marcus in a flannel jacket with a name tag walks in from the left holding a flashlight. | Slow dolly in behind Marcus as he stops, flashlight beam sweeping across dead screens. | MARCUS: "Closing time again. Same quiet." |
| 2 | 5s | Close-up of the MEMORY LANE cabinet: brass coin slot, coin-return button, a small engraved plaque that reads "ONE TOKEN, ONE MEMORY." Marcus's hand, flashlight in the other, hovers near the slot. | Static close-up, slow push-in on the coin slot as his hand enters frame. | MARCUS: "Every night. Never a soul." |
| 3 | 5s | Marcus crouched, holding a single silver token up to the amber bulb, turning it in his fingers. His tired face half-lit. Behind him, the purple machine glow. | Slow push-in on the token, subtle rotation of his hand. | MARCUS: "One token left. My last one." |
| 4 | 5s | Marcus standing before the machine, token pinched between his fingers at the coin slot, breath visible in the cold air. The amber circle of light around him, blue dark beyond. | Medium shot, slight handheld sway, token moves toward slot. | MARCUS: "Whoever's inside... I'll listen." |
| 5 | 5s | The token drops into the slot. The machine's screen flickers on with warm static, purple light brightening across Marcus's face. Checkerboard tile floor reflecting the glow. | Snap to medium close-up as the screen ignites; light flares softly on his face. | MARCUS: "Okay. Show me." |
| 6 | 5s | Marcus close-up, eyes wet, screen glow washing over him. His flashlight hangs loose at his side. | Very slow push-in, almost still, on his face. | WOMAN (V.O.): "If someone finds this... thank you for staying." |
| 7 | 5s | Marcus alone in the dark arcade, machine screen dimming back to black, the amber bulb still burning above him. He sets the flashlight on the counter, unmoving. | Slow pull-back, wide, as the machine goes dark and he stands in the amber circle. | MARCUS: "Anytime. Anytime at all." |

## Development review notes (movie-bot)

1. **Structure is sound:** hook (1-2), escalation (3-4), twist (5-6), payoff/bookend (7). Twist lands at ~70% (scene 5-6 of 7). One location, one recurring character — inside the World Lock and cast rules.
2. **Scene 6 voice-only line is the risk point:** Marcus is on screen while the WOMAN speaks. Do NOT use lipsync on this scene (his lips would move to her words). Route scene 6 as a non-lipsync clip with the woman's line carried by the CC dialogue standard (Voice Lock + double-quoted line) in the video/audio prompt, or generate a separate voice-only audio clip. Marcus's mouth stays closed; verify on preview.
3. **Line lengths all within the ~8-word / ~60-char guidance** — no line risks blowing past the 100-char lipsync cap or the 5s spoken-window.
4. **Trim math:** 7 scenes x 5s = 35s raw. To land ~30s final, trim scene 2 or scene 6's tail (dialogue-governed trims: 300/1400ms per dialogue clip; non-dialogue: 200/1000ms). Final assembly is the user's manual edit.
5. **Diegetic text note:** the "MEMORY LANE" marquee and "ONE TOKEN, ONE MEMORY" plaque are in-scene set dressing, not captions — but marquee text can garble; verify on the generated image preview before firing the video job, regenerate if the plaque text renders mangled.
6. **Production notes:** Marcus is the only on-screen character — perfect for consistent-character generation (one reference portrait via generate_image_consistent_character, per-scene ref_media_id). One look (flannel jacket + name tag + flashlight + token), one location. All 7 scenes reuse the environment bible verbatim.
7. **Caption defense:** CC dialogue standard throughout, name-free prompts (avoid "Marcus" in image prompts; the name tag is set dressing), zero negative phrases, ends "no music".
