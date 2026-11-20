#!/usr/bin/env python3
"""Scan 5: remaining gaps — bg removal, TTS import form fields, project endpoints, websocket."""
import re

src = open("videoeditor.min.js", encoding="utf8", errors="replace").read()

def show(title, pat, n=40, before=120, after=420):
    print("=" * 20, title)
    seen = set()
    for m in re.finditer(pat, src):
        s = max(0, m.start() - before); e = min(len(src), m.end() + after)
        seg = src[s:e].replace("\n", " ")
        if seg in seen: continue
        seen.add(seg)
        print("---", seg[:width] if (width := 540) else seg)
        if len(seen) >= n: break

show("remove background action", r'(?i)(removeBackground|remove_background|background_remove)')
show("TTS import form fields", r'button_import_tts\.ladda\("start"\)', after=900)
show("voice clone create_audio fields", r'voice_clone/create_audio', after=500, before=700)
show("project/export", r'(?i)project/export')
show("project/upload dropzone", r'project/upload', after=200)
show("websocket subscription", r'createSubscription\s*[:=]', after=500)
show("check_availability", r'check_availability', after=200)
show("get_title", r'project/get_title', after=250)
show("project/save form", r'project/save/', after=300, before=500)
show("voice demo", r'voice_clone/[a-z_]+|tts_voice[a-z_]*|speech[a-z_]*demo', n=60)
show("youtube categories", r'import/youtube', after=400, before=200)
show("get_restrictions", r'get_restrictions[a-z_/]*', after=200)
show("daily-restrictions", r'daily-restrictions', after=250)
show("show_log", r'show_log', after=150)
show("save_image project", r'project/[\w$]+/save_image', after=250)
show("artistly", r'artistly', n=25)
