#!/usr/bin/env python3
"""Fetch the logged-in app HTML and enumerate its script/css bundles."""
import json, re, urllib.request

BASE = "https://app.videoexpress.ai"
cookies = json.load(open("cookies.json"))
h = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

def get(url):
    req = urllib.request.Request(url, headers={"Cookie": h, "User-Agent": "Mozilla/5.0",
                                               "X-Requested-With": "XMLHttpRequest"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf8", errors="replace")

html = get(BASE + "/")
open("app.html", "w", encoding="utf8").write(html)
print("app.html", len(html))
for m in re.findall(r'src="([^"]+\.js[^"]*)"', html):
    print("SCRIPT", m)
for m in re.findall(r'href="([^"]+\.(?:css|js)[^"]*)"', html):
    print("LINK", m)
