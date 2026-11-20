# VideoExpress Bridge — Plan (from IDEA.md, Nov 19 2026)

## Goal
Turn `api_run.py` (basic, hard-coded run script) into a robust, installable
**Hermes plugin**: a local MCP server wrapping the full VideoExpress 3.5
feature set, so **videoexpress-bot** (or any agent) can call tools to generate
images/videos, edit projects, build timelines, render, and export — using ALL
the features David pays for, not just the four endpoints we've proven.

Resources:
- App (no public API/MCP/webhook): https://app.videoexpress.ai/
- Workflows library: https://community.dualup.com/
- Tutorials (full feature catalog): https://videoexpress.ai/tutorials/

## Architecture: hybrid API + browser
1. **API layer (primary)** — the app's own XHR endpoints (what api_run.py
   already speaks). Fast, reliable, no UI flake. We *discover* more endpoints.
2. **Browser layer (gap-filler)** — Chrome CDP via real profile for anything
   with no discovered endpoint (timeline drag-editing, some editors, previews).
3. **MCP layer (integration)** — a local MCP server (`vx-mcp`) exposing each
   capability as a named tool; installs into Hermes via the Connectors catalog.

## Phases

### Phase 0 — Recon (discover the real API surface)
- Capture network traffic while a human/agent clicks each VideoExpress feature
  once (text2video, avatar/lipsync, editor actions, templates, TTS, etc.).
- Decompile the app JS bundle to extract endpoint list (@rea-bot).
- Catalog features from tutorials/community.dualup.com (@researcher-bot).
- **Output:** `docs/API_SURFACE.md` — every endpoint, params, auth requirements.

### Phase 1 — Core library (`vx/` package)
- Refactor `api_run.py`'s `Vx` class into a proper package:
  `vx/auth.py, vx/images.py, vx/videos.py, vx/projects.py, vx/render.py, vx/library.py, vx/poll.py`
- Keep the hard rules: max 5 inflight video jobs; write-once + poll-before-retry;
  verify via artifact URL, never trust response alone.
- Every function returns verifiable handles (media_id, job uuid, output URL).

### Phase 2 — MCP server (`vx-mcp/`)
- FastMCP-style local server exposing one tool per capability
  (e.g. `vx_generate_image`, `vx_image2video`, `vx_render_project`,
  `vx_add_brick`, `vx_list_media`, …).
- Guardrails inside the server: 5-slot limiter, cookie auth from file,
  dry-run mode, spend/edit actions gated to explicit confirmation.

### Phase 3 — Browser fallback layer
- Chrome CDP drivers for features with no endpoint (editors, previews).
- Reuse real-profile launch recipe (port 9222, persistent login).

### Phase 4 — Wire up & train
- Install `vx-mcp` into Hermes catalog; attach to videoexpress-bot.
- Update `videoexpress-playbooks` skill: bot now has real tools, not just recipes.
- Validation runs: single-shot smoke test → 3-shot mini run → compare vs Run 11.

## Crew assignments
| Task | Owner |
|---|---|
| JS bundle endpoint extraction | @rea-bot |
| Feature catalog from tutorials | @researcher-bot |
| `vx/` package + MCP server | @coder-bot |
| Code review gate | @code-review-bot |
| End-to-end test consumer | @videoexpress-bot |
| Browser fallback drivers | @coder-bot + boss-bot |

## Acceptance criteria (definition of done)
1. videoexpress-bot calls an MCP tool and a REAL artifact comes back
   (image URL / rendered clip, ffprobe-verified), not a promise.
2. Feature coverage ≥ every tool David lists from tutorials.
3. 5-slot limiter + write-once rules hold under a multi-wave run.
4. Installable: one command / catalog entry adds it to Hermes.
