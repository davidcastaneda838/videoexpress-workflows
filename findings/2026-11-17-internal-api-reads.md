# Verified: VideoExpress internal API reads (no more screenshot polling)

Date: Nov 17 2026
Setup: user's real Chrome profile, CDP-attached (see skill for browser recipe). Login persistent.

## Verified endpoints (same-origin `fetch()` from the logged-in app page)

1. **Folder list** — `GET /library/get_categories/4`
   - `{data:[{id,name,title,libraryId,userId,sortOrder}]}`
   - NOTE: NO `/api` prefix (public workflow docs say `/api/library/get_categories` — that 404s; the real path was captured from the app's own XHR).
   - Folder ids are per-account. Ours (userId 44136): My AI Videos=355994, My AI Images=355995, My AI Audio=386152, My Videos=355992, Default=355990, audio=355991, my_images=604116, my_artistly_images=358328.
2. **Folder contents** — `GET /api/library/get_media/4?categoryId=<id>&page=1&start=0&limit=N&query=&orderBy=id&orderDir=desc&filter=`
   - `{total, results:[{id, name(=prompt caption), status, duration(ms), uuid, ...}]}`
   - `status: "completed"` vs `null` (still generating) — a clean completion signal.
   - `duration` ≈ planned seconds × 1000 + ~42ms (e.g. 10s clip → 10041.667ms).
3. **Exports** — `GET /api/get_list_output`
   - `{daysLeft, results:[{id,title,filename,path,filesize,mediaPath}]}`; `mediaPath` = direct CDN mp4 URL.
   - Verified against run-4's export `sleep-facts-30s-v2` (19.90 MB, hosted until 01/01/2027).

## Live cross-validation (one JSON call)

My AI Videos listed 24 items. Among them:
- Run-4 Lipsync clips: `duration` ≈ 6041.667ms (~6s) — the app's own data confirms the dialogue-governed duration rule.
- Run-3 non-lipsync test clips (idents 49242882 / 49243649 / 49243801): 10041.667ms (~10s) — idents match the session record exactly.

## Endpoint discovery method (reusable)

In the logged-in page:
```js
new PerformanceObserver(l=>{for(const e of l.getEntries())
  if(['fetch','xmlhttprequest'].includes(e.initiatorType)) window.__xhr.push(e.name);
}).observe({entryTypes:['resource']});
// ...click the UI element you care about...
JSON.stringify(window.__xhr)   // the app's true endpoint URLs + params
```

## What this changes for future runs

- Every poll loop (30s screenshot polls, folder counting, percent tiles), duplicate checks, tile identification and export verification = one instant JSON call.
- Writes (Create dialogs, submits, timeline drags) still go through the browser UI — write APIs from outside the browser hit CSRF (Laravel 419) errors per the sibling workflow docs.
- This is the foundation for hour-long orchestration: deterministic state reads across hundreds of clips.

## Rules

- Read-only GETs via fetch; never expose or store credentials; never call write endpoints outside the browser.
