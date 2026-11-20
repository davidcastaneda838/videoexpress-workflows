# VideoExpress 3.5 — Feature Catalog

Sources: https://videoexpress.ai/tutorials/ (full tutorial library, single page, fetched 2026-11-19) and https://community.dualup.com/ (workflow library, 19 workflows). Tutorial page is a single anchor-navigated page; all features cite it (anchors where available).

## AI Generation

| # | Feature | Description | Inputs | Output | Tutorial URL |
|---|---------|-------------|--------|--------|--------------|
| 1 | Text-to-Video | Generate cinematic video clips from a text prompt (SORA-like). | Text prompt, duration, style/model options | Video clip (MP4) in media library | https://videoexpress.ai/tutorials/#v3 ("3.0: Text to Video") |
| 2 | Create Video from Prompt | Prompt-driven guided video creation workflow. | Prompt (possibly multi-part guided) | Video clip | https://videoexpress.ai/tutorials/#v3 ("3.0: Create Video from Prompt") |
| 3 | Image-to-Video | Animate a still image into video. | Source image + optional prompt/motion | Video clip | https://videoexpress.ai/tutorials/ (Core Library, "2.0: Image to Video") |
| 4 | First Frame / Last Frame | Keyframe interpolation: supply start & end frames, AI generates the in-between motion. | First-frame image, last-frame image, prompt | Video clip transitioning between frames | https://videoexpress.ai/tutorials/#v3 ("3.0: First Frame, Last Frame") |
| 5 | Voice Prompts | Generate video from a spoken/voice prompt (audio as the prompt input). | Audio recording or voice clip + text prompt | Video clip guided by voice | https://videoexpress.ai/tutorials/ ("2.0: Voice Prompts") |
| 6 | Creative Mode | v3.5 creative/guided generation mode for more expressive prompt control. | Prompt + creative mode settings | Video clip | https://videoexpress.ai/tutorials/#v3 ("3.5: Using Creative Mode") |

## Characters, Avatars & Lipsync

| 7 | Human Talking Video (AI Avatars / Talking Photos) | Make a photo speak with selectable language, speaker voice and emotion. | Portrait image, language, voice/speaker, emotion, speech text | Talking-head video | https://videoexpress.ai/tutorials/ ("2.0: Human Talking Video") |
| 8 | Lipsync Video | Sync existing video/audio to a character's mouth; supports up to 5-min clips, HD lipsync. | Video or image + audio track (or speech text) | Lipsynced video | https://videoexpress.ai/tutorials/#v3 ("3.0: Lipsync Video") |
| 9 | Consistent Characters | Create a character once and reuse it across scenes/videos. | Character description/reference image | Saved consistent character usable in all generations | https://videoexpress.ai/tutorials/ ("2.0: How to Make Consistent Characters") |
| 10 | Stylize Character | Restyle an existing character/image (3D, realistic, cartoon, animal etc.). | Source character image + style choice | Stylized character image/video | https://videoexpress.ai/tutorials/#v3 ("3.0: Stylize Character") |

## Image Editing

| 11 | Inpainting | Erase/redraw parts of an image with AI. | Image + masked region + prompt | Edited image | https://videoexpress.ai/tutorials/ ("2.0: Inpainting") |
| 12 | Outpainting | Extend an image beyond its borders. | Image + target aspect/extension | Expanded image | https://videoexpress.ai/tutorials/ ("2.0: Outpainting") |
| 13 | Object Removal | Remove objects from images/video frames. | Image/video + selection of object | Cleaned image/video | https://videoexpress.ai/tutorials/ ("Object Removal") |
| 14 | Green Screen | Remove/replace background (chroma-key style background removal). | Image/video with background to key | Foreground-only or composited clip | https://videoexpress.ai/tutorials/ ("Green Screen") |
| 15 | Opacity Filter (v3.5) | Adjust clip opacity / overlay blending. | Clip + opacity setting | Composited clip | https://videoexpress.ai/tutorials/#v3 ("3.5: Opacity Filter") |

## Audio & Voice

| 16 | Text-to-Speech | Built-in TTS voiceover generation. | Text, voice selection, language | Audio/voiceover clip | https://videoexpress.ai/tutorials/ ("Import Media: Text to Speech") |
| 17 | Add Voiceovers | Record or add voiceover tracks to the timeline. | Recorded/imported audio | Video with voiceover | https://videoexpress.ai/tutorials/ ("Add Voiceovers") |
| 18 | Voice Changer & Save Audio | Transform a voice recording to another voice; save audio assets. | Audio clip + target voice | Transformed audio file | https://videoexpress.ai/tutorials/#v3 ("3.0: Voice Changer and Save Audio") |
| 19 | AI Sound Maker | Generate background sound effects/ambience matched to the video. | Video clip or mood description | Sound/audio track | https://videoexpress.ai/tutorials/ ("2.0: AI Sound Maker") |
| 20 | Audio Waves Visualization | Add animated audio-wave overlays to videos. | Video + audio track | Video with waveform overlay | https://videoexpress.ai/tutorials/#v3 ("3.0: Add audio waves to your videos") |
| 21 | Separate Audio and Video | Extract/split audio from a video clip. | Video clip | Separate audio file + silent video | https://videoexpress.ai/tutorials/#v3 ("3.0: Seperate Audio and Video") |
| 22 | Automatic Audio Cutter | Auto-split audio across multiple scenes. | Audio + scene list | Per-scene audio segments | https://videoexpress.ai/tutorials/ ("Automatic Audio Cutter for Multiple Scenes") |
| 23 | Fade Audio Filter | Fade audio in/out on the timeline. | Clip + fade settings | Edited audio | https://videoexpress.ai/tutorials/ ("Filters: Camera Pan, Zoom in, Fade Audio") |

## Editing & Timeline (editor basics)

| 24 | Timeline Editor | Multi-track timeline for arranging clips/media. | Clips, images, audio | Project timeline | https://videoexpress.ai/tutorials/ ("Exploring the Timeline") |
| 25 | Auto Align Clips | Snap/align clips on the timeline automatically. | Timeline clips | Aligned timeline | https://videoexpress.ai/tutorials/ ("Auto Align Clips") |
| 26 | Scene Length Extenders | Extend a video scene's duration. | Clip + extension settings | Longer clip | https://videoexpress.ai/tutorials/ ("Video Scene Length Extenders") |
| 27 | Smart Edit v2 | AI-assisted editing of generated clips. | Clip + edit instructions | Edited clip | https://videoexpress.ai/tutorials/#v3 ("3.0: Smart Edit v2") |
| 28 | Fix Videos | AI repair/remaster of problematic clips. | Broken/problem clip | Fixed clip | https://videoexpress.ai/tutorials/#v3 ("3.0: Fix Videos") |
| 29 | Filters: Camera Pan / Zoom In | Add camera-motion filters to clips. | Clip + filter params | Motion-filtered clip | https://videoexpress.ai/tutorials/ ("Filters: Camera Pan, Zoom in, Fade Audio") |
| 30 | Change Speed Filter | Change clip playback speed. | Clip + speed factor | Speed-adjusted clip | https://videoexpress.ai/tutorials/ ("Change Speed Filter") |
| 31 | Resize and Move Video | Reposition/scale clips in the frame. | Clip + transform values | Repositioned clip | https://videoexpress.ai/tutorials/ ("Resize and Move Video") |
| 32 | Transitions | Add transitions between clips. | Adjacent clips + transition type | Transitioned timeline | https://videoexpress.ai/tutorials/ ("Transitions") |
| 33 | Transition Between Effects | Transition between effects/styles within a clip. | Clip + effect choices | Clip with in-clip effect transitions | https://videoexpress.ai/tutorials/#v3 ("3.0: Transition Between Effects") |
| 34 | Titles | Add title text elements. | Text + style | Title overlay | https://videoexpress.ai/tutorials/ ("Titles") |
| 35 | Text Animations | Animated text/captions presets. | Text + animation preset | Animated text overlay | https://videoexpress.ai/tutorials/ ("Text Animations") |
| 36 | Fix Subtitles | Auto-generate/repair subtitle tracks. | Video + audio (or existing subs) | Corrected subtitle track | https://videoexpress.ai/tutorials/#v3 ("3.0: Fix Subtitles") |
| 37 | VidSubtitle Integration | Push videos to VidSubtitle for advanced subtitling/translation. | Video | Subtitled/translated video | https://videoexpress.ai/tutorials/ ("VideoExpress.ai and VidSubtitle Integration") |

## Media & Capture

| 38 | Media Library & Multi-Select Management | Browse, download, delete, move AI renders; view in-progress renders. | Library selection actions | Managed media assets | https://videoexpress.ai/tutorials/#v3 ("3.0: Multi-Select Media Gallery"), ("2.0: Renders in Progress") |
| 39 | Public Gallery (Stock/Template Assets) | Browse and use public stock images/videos/templates. | Search/browse | Media asset added to project | https://videoexpress.ai/tutorials/ ("Using the Public Gallery") |
| 40 | Import Media: Webcam, Voice & Screen Recorder | Capture webcam, microphone and screen recordings into the project. | Device selection, recording | Imported media clips | https://videoexpress.ai/tutorials/ ("Import Media: Webcam, Voice, and Screen Recorder") |

## Integrations

| 41 | Artistly.ai Integration | Import images created in Artistly into VideoExpress. | Artistly account/assets | Imported images for image2video | https://videoexpress.ai/tutorials/ ("Artistly & VideoExpress Integration", "Importing From Artistly") |
| 42 | CloneVoice.ai Integration | Voice cloning for voiceovers (used in workflows). | Voice samples/text | Cloned voice audio | https://videoexpress.ai/tutorials/ ("VideoExpress.ai + Artistly.ai + CloneVoice.ai Integration") |

## Workflow Library (community.dualup.com — composite workflows, useful for coverage hints)

Each is an agent/custom-GPT workflow chaining the features above; cite https://community.dualup.com/@videoexpress/workflows/<slug>:

- Realistic Consistent Character AI Videos — consistent character story videos
- AI Cartoon Movies with Agent (two-character agent) — multi-character films
- Realistic Mini Dramas — short drama episodes
- VideoExpress + CloneVoice Stickman Story — stickman narrated stories
- Historical Documentary Video — documentary format videos
- Vox Style Video — explainer/vox-style videos
- English Learning Videos — educational language videos
- AI Kids Music Videos (CloneVoice) — kids music videos
- CloneVoice + VideoExpress Narrative Video — narrated narrative videos
- Full-Length Consistent Character Video With One Prompt — single-prompt long video
- Motion Graphics Animation — motion graphics
- Unlimited Viral Shorts — vertical shorts
- Idea To 3D Documentary — 3D documentary from idea
- 10,000 Hours Into AI Video Automation — automated long-form
- First Frame / Last Frame Workflow — keyframe interpolation workflows
- 3D Animated Short Film — animated shorts
- Gemini 3D Animation Gem / Gemini Realistic Video Gem — external Gemini prompt gems
- Realistic Talking Video Workflow — realistic talking-head videos

Notes: no dedicated "translation" tool appears in the tutorials; multi-language speech is inside Human Talking Video/TTS, and subtitling/translation routes through VidSubtitle. "Templates" appear as Public Gallery assets and the free workflow documents (https://www.videoexpress.ai/workflow/). All tutorial URLs are sections of the single page https://videoexpress.ai/tutorials/ (no page blocks; no login required).
