#!/usr/bin/env python3
"""Scan videoeditor.min.js for API endpoint strings and AJAX call sites."""
import re, json, collections

src = open("videoeditor.min.js", encoding="utf8", errors="replace").read()
print("bytes:", len(src))

# 1) all quoted strings that look like paths
strs = re.findall(r'"((?:/[A-Za-z0-9_./-]{2,80}))"', src) + \
       re.findall(r"'((?:/[A-Za-z0-9_./-]{2,80}))'", src)
paths = collections.Counter(s for s in strs
    if not s.startswith("/bundle") and not re.match(r"^/[a-z]+$", s)
    and re.search(r"[a-z]", s))
out = [p for p, c in sorted(paths.items()) if c >= 1]
for p in out:
    print("PATH", p, paths[p])
print("total distinct:", len(out))

# 2) ajax contexts: for each interesting path, grab surrounding code
key = ["/api/", "library/", "project", "render", "speech", "voice", "tts",
       "subtitle", "translat", "avatar", "template", "background", "rembg",
       "upload", "export", "stock", "record", "screen"]
ctx = {}
for p in out:
    for m in re.finditer(re.escape(p), src):
        s = max(0, m.start()-260); e = min(len(src), m.end()+160)
        ctx.setdefault(p, []).append(src[s:e].replace("\n", " "))
        if len(ctx[p]) >= 4: break

with open("endpoint_contexts.json", "w", encoding="utf8") as f:
    json.dump(ctx, f, indent=1)
print("contexts for", len(ctx), "paths -> endpoint_contexts.json")

# 3) method hints near ajax calls
for m in re.finditer(r'\.(ajax|post|get)\((.{0,400})', src):
    seg = m.group(2)
    if re.search(r'url\s*:', seg) or '"/' in seg or "'/" in seg:
        pass
# find type:"POST"/"PUT"/"DELETE" occurrences with url nearby
for m in re.finditer(r'url\s*:\s*([\'"][^\'"]+[\'"])', src):
    print("AJAXURL", m.group(1))
