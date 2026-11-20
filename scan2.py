#!/usr/bin/env python3
"""Deeper scan: dynamic URL construction, ajax wrappers, script loads."""
import re

src = open("videoeditor.min.js", encoding="utf8", errors="replace").read()

def show(title, pat, n=60, width=200):
    print("=" * 20, title)
    seen = set()
    for m in re.finditer(pat, src):
        s = max(0, m.start() - 120); e = min(len(src), m.end() + 140)
        seg = src[s:e].replace("\n", " ")
        if seg in seen: continue
        seen.add(seg)
        print("---", seg[:width])
        if len(seen) >= n: break

# URL-builder literals
show("ai/api concat", r'["\'](?:/)?(?:ai/api|api/)[A-Za-z0-9_/.-]*["\']')
show("ai/api usage ctx", r'ai/api')
show("library paths", r'["\'](?:/)?library/[A-Za-z0-9_/.-]*')
show("project paths", r'["\'](?:/)?project/[A-Za-z0-9_/.-]*')
show("speech/tts", r'(?i)(speech|tts|voice|eleven|azure|polly)')
show("subtitle/caption", r'(?i)(subtitle|caption|transcript|translat)')
show("avatar", r'(?i)(avatar)')
show("bg remove", r'(?i)(rembg|background[_ -]?remov|removeBackground)')
show("render/export", r'(?i)(render_project|renderproject|render/|export)')
show("stock", r'(?i)(stock|pexels|pixabay)')
show("upload", r'(?i)upload')
show("record/screen", r'(?i)(screen.?record|getDisplayMedia|MediaRecorder)')
show("template", r'(?i)template')
show("ajax type:", r'type\s*:\s*["\'](POST|PUT|DELETE|PATCH)["\']')
show("fetch( calls", r'fetch\(\s*["\'`]')
show("script loads", r'\.js["\']')
