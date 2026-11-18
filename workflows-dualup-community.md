# DualUp Community Workflow Inventory (community.dualup.com)

Captured Nov 18 2026 by scrolling the site's virtual feed until stable (19 unique slugs).
Each workflow page offers a downloadable system prompt for Claude/ChatGPT recreation.

## Pure VideoExpress — Agent Workflows (share our verified primitives)
| Slug | Theme | Integration outlook |
|---|---|---|
| realistic-consistent-character-ai-videos-workflow | consistent character (our PR target repo's base) | READY — images+lipsync+render all verified |
| videoexpress-two-character-video-agent | two characters | MOSTLY READY — needs 2nd reference-slot mapping (mediaId per slot) |
| realistic-mini-dramas-workflow | mini dramas | READY |
| videoexpress-clonevoice-stickman-story-workflow | stickman + CloneVoice voice | PARTIAL — CloneVoice endpoint not yet mapped |
| historical-documentary-video-workflow | documentary | READY |
| vox-style-video-workflow | Vox-style explainer | READY (style prompts only) |
| english-learning-videos-workflow | education | READY |
| full-length-consistent-character-video-with-one-prompt | the ~60s playbook we already ran | READY — our first playbook |
| realistic-talking-video-workflow | talking avatar | READY |

## CloneVoice-flavored (need voice endpoints discovered)
| Slug | Theme |
|---|---|
| ai-kids-music-videos-workflow | kids music |
| clonevoice-videoexpress-narrative-video-workflow | narrative video |

## Custom-GPT / Gemini-Gem workflows (agent-side orchestration, VideoExpress still does the media)
| Slug | Theme |
|---|---|
| motion-graphics-animation-workflow | motion graphics |
| unlimited-viral-shorts-workflow | viral shorts factory |
| idea-to-3d-documentary-workflow | 3D documentary |
| 10-000-hours-into-ai-video-automation | meta/automation course-style |
| first-frame-last-frame-workflow | first/last-frame control — MAY NEED endpoint discovery (frame conditioning) |
| 3d-animated-short-film-workflow | 3D short film |
| gemini-3d-animation-gem | Gemini gem |
| gemini-realistic-video-gem | Gemini gem |

## Integration priority (user's hour-long goal)
1. READY-now set (consistent character, mini dramas, documentary, vox, english) — direct ports onto api_run.py configs.
2. Two-character — small discovery (slot-2 mediaId).
3. Narration Video flow — user-taught; unlocks narration-style + longer speech clips.
4. CloneVoice set — needs endpoint capture (one recorded click each).
5. First-frame/last-frame — verify whether VideoExpress 3.5 UI exposes it at all.
