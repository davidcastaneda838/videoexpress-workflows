#!/usr/bin/env python3
"""Scan 4: context for key endpoints with full param dumps."""
import re, json

src = open("videoeditor.min.js", encoding="utf8", errors="replace").read()

targets = ["import/text_to_speech", "text_to_speech_talking_video", "video_fix_subtitles",
           "avatar/import_tts", "avatar/content_tts", "get_templates_list",
           "import/youtube", "download_stock_media", "import_from_artistly",
           "voice_clone", "create_audio_voice_change", "audio_split",
           "create_talking_video", "generate_text2video_dialog", "image2video_talking",
           "generate_image2video2", "slideshow_project", "save_media", "extract_audio",
           "separate_audio_video", "human_background_replace", "inpainting_image",
           "outpainting_image", "inpainting_video", "extend_prompt/", "video_length_booster",
           "result_ai_fix", "face_swap_image", "get_media_prompt_data"]

def ctx(pat, before=100, after=700, n=3):
    out = []
    for m in re.finditer(re.escape(pat), src):
        s = max(0, m.start() - before); e = min(len(src), m.end() + after)
        out.append(src[s:e].replace("\n", " "))
        if len(out) >= n: break
    return out

res = {}
for t in targets:
    res[t] = ctx(t)
json.dump(res, open("scan4_ctx.json", "w", encoding="utf8"), indent=1)
for t, v in res.items():
    print("\n#### " + t)
    for seg in v:
        print("  ", seg[:850])
        print("  ---")
