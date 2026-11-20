#!/usr/bin/env python3
"""Scan 3: actionPath values, TTS/voice/subtitle/translate/stock/avatar endpoints."""
import re

src = open("videoeditor.min.js", encoding="utf8", errors="replace").read()

def show(title, pat, n=120, width=230):
    print("=" * 20, title)
    seen = set()
    for m in re.finditer(pat, src):
        s = max(0, m.start() - 90); e = min(len(src), m.end() + 110)
        seg = src[s:e].replace("\n", " ")
        if seg in seen: continue
        seen.add(seg)
        print("---", seg[:width])
        if len(seen) >= n: break

show("actionPath literals", r'actionPath\s*[:=]\s*["\'][^"\']+["\']')
show("tts/speech", r'(?i)(text_?to_?speech|speech|clone_voice|voice_clone|tts)[a-z_]*')
show("subtitle", r'(?i)subtitl|caption|transcri')
show("translate", r'(?i)translat')
show("remove bg", r'(?i)(remove[_A-Za-z]*background|background[_A-Za-z]*remove|bg[_A-Za-z]*remov)')
show("avatar endpoints", r'(?i)avatar/[a-z_]+|avatar_[a-z_]+')
show("stock endpoints", r'(?i)(stock|getty|pexels|pixabay|unsplash)[a-z_/]{0,40}')
show("youtube/record/import", r'(?i)(import/[a-z_]+|youtube[a-z_]{0,20}|record[a-z_]{0,20})')
show("upscale/repair/enhance", r'(?i)(upscale|enhance|repair|restore|colori[a-z]*|denoise)[a-z_]{0,25}')
show("removal endpoints", r'ai/api/remove[a-z_]*')
show("text2video", r'(?i)(text2video|text_to_video|generate_text2video|script)')
show("templates", r'(?i)template[s]?/[a-z_]+|get_templates|templates?_')
show("baseUrl+", r'baseUrl\+\s*["\'][a-zA-Z][^"\']{2,60}["\']', n=250)
