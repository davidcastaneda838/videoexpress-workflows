"""Tool implementations for the vx-mcp server. Each returns real handles
(media_id / uuid / output URL) or raises — results are never fabricated."""

import json
import os

from vx import Vx, estimate_clip_seconds, clamp_video_length

# Tool name -> (description, input_schema, handler)
# Handlers receive (vx, args) and return a JSON-serializable dict.


def _require(args, *keys):
    missing = [k for k in keys if not args.get(k)]
    if missing:
        raise ValueError(f"missing required arg(s): {', '.join(missing)}")
    return args


# ---------- generation ----------

def t_generate_image(vx, args):
    _require(args, "prompt")
    r = vx.generate_image(args["prompt"], type_=args.get("type", "photorealistic"),
                          aspect=args.get("aspect", "9:16"))
    return {"uuid": r["uuid"], "preview_url": r["url"]}


def t_generate_image_consistent(vx, args):
    _require(args, "prompt", "ref_media_id")
    r = vx.generate_image_consistent(args["prompt"], args["ref_media_id"],
                                     aspect=args.get("aspect", "9:16"))
    return {"uuid": r["uuid"], "preview_url": r["url"]}


def t_image2video(vx, args):
    """Lipsync video from a generated image. Holds a 5-slot limiter slot."""
    _require(args, "image_uuid", "image_prompt", "video_prompt")
    with vx.video_limiter.slot():
        before = vx.video_folder_ids()
        handle = vx.generate_video(
            args["image_uuid"], args["image_prompt"], args["video_prompt"],
            args.get("dialogue", ""), aspect=args.get("aspect", "9:16"),
            video_length=(args.get("video_length") or None) and clamp_video_length(args["video_length"]),
            lipsync=args.get("lipsync", True),
            enhance_video_prompt=args.get("enhance_video_prompt", 1),
            dialogue_in_prompt=args.get("dialogue_in_prompt", False))
        baseline = set(handle["baseline_ids"]) | before
        if not args.get("wait", True):
            return {"baseline_size": len(baseline), "video_length_s": handle["video_length_s"],
                    "note": "poll via vx_library_list for status"}
        done = vx.wait_videos(baseline, expected=args.get("expected", 1),
                              timeout_s=args.get("timeout_s", 1500))
    return {"clips": [{"media_id": m["id"], "file_name": m["fileName"],
                       "duration_ms": round(m["duration"]), "status": m.get("status")}
                      for m in done]}


def t_text2video(vx, args):
    _require(args, "prompt")
    r = vx.generate_text2video(args["prompt"], dialogue=args.get("dialogue", ""),
                               aspect=args.get("aspect", "9:16"),
                               video_length=(args.get("video_length") or None),
                               enhance_video_prompt=args.get("enhance_video_prompt", 1))
    return {"uuid": r["uuid"], "video_length_s": r["video_length_s"], "response": r["response"]}


def t_tts(vx, args):
    """TTS via /voice_clone/create_audio; completion is verified by polling
    /voice_clone/generated_audio (the /voice_clone/status endpoint is
    unreliable for TTS). Returns {uuid, media_id, src, length, title}."""
    _require(args, "text", "voice")
    r = vx.create_audio(args["text"], args["voice"], language=args.get("language"),
                        language_code=args.get("language_code"),
                        translate=args.get("translate", 0),
                        boost_similarity=args.get("boost_similarity", 0),
                        project_id=args.get("project_id"))
    if args.get("wait", True):
        done = vx.wait_audio(r["uuid"], timeout_s=args.get("timeout_s", 600))
        out = {"uuid": r["uuid"], "media_id": done.get("media_id"),
               "src": done.get("src"), "length": done.get("length"),
               "title": done.get("title"), "status": done.get("status")}
        if args.get("import"):
            out["import"] = vx.import_generated_audio(
                [{"id": done.get("media_id"), "uuid": r["uuid"],
                  "src": done.get("src"), "title": done.get("title")}])
        return out
    return {"uuid": r["uuid"]}


def t_list_voices(vx, args):
    return vx.list_voices(category=args.get("category", "system"),
                          language=args.get("language"),
                          language_code=args.get("language_code"))


def t_create_sound(vx, args):
    _require(args, "prompt")
    return vx.create_sound(args["prompt"], duration=args.get("duration", 10),
                           media_id=args.get("media_id", "0"))


def t_extend_prompt(vx, args):
    _require(args, "prompt")
    return {"prompt": vx.extend_prompt(args["prompt"], mode=args.get("mode", "image"),
                                       type_=args.get("type"), style=args.get("style"))}


# ---------- library ----------

def t_library_list(vx, args):
    items = vx.media_list(args.get("category_id", vx.FOLDER_VIDEOS),
                          limit=args.get("limit", 50), page=args.get("page", 1),
                          query=args.get("query", ""))
    return {"results": [{"id": m.get("id"), "fileName": m.get("fileName"),
                         "status": m.get("status"), "duration": m.get("duration"),
                         "mediaPath": m.get("mediaPath")} for m in items]}


def t_library_download(vx, args):
    _require(args, "media_id")
    dest = args.get("dest") or os.path.join(os.path.expanduser("~"), "Downloads")
    if os.path.isdir(dest):
        item = vx.media_item(args["media_id"])
        dest = os.path.join(dest, str(item.get("fileName") or f"{args['media_id']}.mp4"))
    item = vx.media_item(args["media_id"])
    path = vx.download_media(item, dest)
    return {"path": path}


# ---------- projects / render ----------

def t_project_list(vx, args):
    return {"results": vx.project_list(search=args.get("search", ""))}


def t_project_open(vx, args):
    _require(args, "project_id")
    return vx.project_open(args["project_id"])


def t_project_save(vx, args):
    _require(args, "project_id", "title", "timeline")
    tracks = args["timeline"]
    if isinstance(tracks, str):
        tracks = json.loads(tracks)
    return vx.project_save(args["project_id"], args["title"], tracks,
                           save_new=args.get("save_new", 0))


def t_render_project(vx, args):
    """Render a project from clips (dialogue-governed lengths; ms brick math)."""
    _require(args, "project_id", "export_name", "clips")
    clips = args["clips"]
    for c in clips:
        if not c.get("duration_ms") and c.get("dialogue"):
            c["duration_ms"] = estimate_clip_seconds(c["dialogue"]) * 1000
    baseline = {o["id"] for o in vx.outputs()}
    for c in clips:  # CDN propagation guard before firing the render write
        vx.wait_clip_propagation(c["file_name"], timeout_s=300)
    r = vx.render_project(args["project_id"], clips, args["export_name"],
                          project_title=args.get("project_title"),
                          aspect=args.get("aspect", "9:16"))
    if args.get("wait", True):
        out = vx.wait_output(baseline, timeout_s=args.get("timeout_s", 900))
        return {"render": r["response"], "total_duration_ms": r["total_duration_ms"],
                "output": out, "output_url": out.get("mediaPath")}
    return {"render": r["response"], "total_duration_ms": r["total_duration_ms"],
            "baseline_size": len(baseline)}


def t_get_outputs(vx, args):
    return {"results": vx.outputs()}


# ---------- tasks ----------

def t_task_status(vx, args):
    _require(args, "uuid")
    return vx.task_status(args["uuid"])


def t_cancel(vx, args):
    _require(args, "uuid")
    return vx.cancel_task(args["uuid"])


def t_retry(vx, args):
    _require(args, "task_id")
    return vx.retry_task(args["task_id"])


TOOLS = {
    "vx_generate_image": (
        "Generate a plain text-to-image. Returns job uuid + preview URL.",
        {"type": "object", "properties": {
            "prompt": {"type": "string"}, "type": {"type": "string"},
            "aspect": {"type": "string"}}, "required": ["prompt"]},
        t_generate_image),
    "vx_generate_image_consistent": (
        "Generate a character-consistent image from a reference media_id.",
        {"type": "object", "properties": {
            "prompt": {"type": "string"}, "ref_media_id": {"type": "integer"},
            "aspect": {"type": "string"}}, "required": ["prompt", "ref_media_id"]},
        t_generate_image_consistent),
    "vx_image2video": (
        "Image-to-video with lipsync. Max 5 concurrent video jobs enforced.",
        {"type": "object", "properties": {
            "image_uuid": {"type": "string"}, "image_prompt": {"type": "string"},
            "video_prompt": {"type": "string"}, "dialogue": {"type": "string"},
            "lipsync": {"type": "boolean"}, "video_length": {"type": "integer"},
            "aspect": {"type": "string"}, "wait": {"type": "boolean"},
            "timeout_s": {"type": "integer"}},
            "required": ["image_uuid", "image_prompt", "video_prompt"]},
        t_image2video),
    "vx_text2video": (
        "Pure text-to-video (no source image).",
        {"type": "object", "properties": {
            "prompt": {"type": "string"}, "dialogue": {"type": "string"},
            "video_length": {"type": "integer"}, "aspect": {"type": "string"}},
            "required": ["prompt"]},
        t_text2video),
    "vx_tts": (
        "Text-to-speech via voice_clone/create_audio. Completion is verified by "
        "polling /voice_clone/generated_audio (the /voice_clone/status endpoint "
        "is unreliable for TTS — it can stay empty after completion). Returns "
        "{uuid, media_id, src, length, title}. set import=true to import the "
        "audio into the user library afterwards.",
        {"type": "object", "properties": {
            "text": {"type": "string"}, "voice": {"type": "string"},
            "language": {}, "language_code": {"type": "string"},
            "wait": {"type": "boolean"}, "import": {"type": "boolean"},
            "timeout_s": {"type": "integer"}},
            "required": ["text", "voice"]},
        t_tts),
    "vx_list_voices": (
        "List TTS voices (category: system|designed|public_library|cloned).",
        {"type": "object", "properties": {"category": {"type": "string"},
                                          "language": {}, "language_code": {"type": "string"}}},
        t_list_voices),
    "vx_create_sound": (
        "AI sound/music generation from a prompt.",
        {"type": "object", "properties": {"prompt": {"type": "string"},
                                          "duration": {"type": "integer"}},
         "required": ["prompt"]},
        t_create_sound),
    "vx_extend_prompt": (
        "AI prompt enhancer (mode: image|text_to_video|consistent_character|video|magic|image_to_prompt).",
        {"type": "object", "properties": {"prompt": {"type": "string"},
                                          "mode": {"type": "string"}},
         "required": ["prompt"]},
        t_extend_prompt),
    "vx_library_list": (
        "List media in a library folder (defaults to My AI Videos).",
        {"type": "object", "properties": {"category_id": {"type": "integer"},
                                          "limit": {"type": "integer"},
                                          "query": {"type": "string"}}},
        t_library_list),
    "vx_library_download": (
        "Download a library media item to disk.",
        {"type": "object", "properties": {"media_id": {"type": "integer"},
                                          "dest": {"type": "string"}},
         "required": ["media_id"]},
        t_library_download),
    "vx_project_list": (
        "List VideoExpress projects.",
        {"type": "object", "properties": {"search": {"type": "string"}}},
        t_project_list),
    "vx_project_open": (
        "Open a project timeline (tracks + bricks).",
        {"type": "object", "properties": {"project_id": {"type": "integer"}},
         "required": ["project_id"]},
        t_project_open),
    "vx_project_save": (
        "Save a project timeline (tracks JSON).",
        {"type": "object", "properties": {"project_id": {"type": "integer"},
                                          "title": {"type": "string"},
                                          "timeline": {}},
         "required": ["project_id", "title", "timeline"]},
        t_project_save),
    "vx_render_project": (
        "Queue a final render from clips [{media_id, file_name, duration_ms|dialogue}].",
        {"type": "object", "properties": {
            "project_id": {"type": "integer"}, "export_name": {"type": "string"},
            "clips": {"type": "array"}, "aspect": {"type": "string"},
            "wait": {"type": "boolean"}},
         "required": ["project_id", "export_name", "clips"]},
        t_render_project),
    "vx_get_outputs": (
        "List exported renders (mediaPath CDN mp4 URLs).",
        {"type": "object", "properties": {}},
        t_get_outputs),
    "vx_task_status": (
        "HTTP status poll for an AI task by uuid.",
        {"type": "object", "properties": {"uuid": {"type": "string"}},
         "required": ["uuid"]},
        t_task_status),
    "vx_cancel": (
        "Cancel a running AI task by uuid.",
        {"type": "object", "properties": {"uuid": {"type": "string"}},
         "required": ["uuid"]},
        t_cancel),
    "vx_raw_call": (
        "Generic allowlisted raw endpoint call for coverage gaps. "
        "path may contain <placeholders> filled from path_params.",
        {"type": "object", "properties": {
            "path": {"type": "string"}, "fields": {"type": "object"},
            "json_body": {}, "path_params": {"type": "object"}},
         "required": ["path"]},
        None),  # wired in server.py (needs the allowlist)
}

PROVEN_FALLBACK = [
    {"path": "/ai/api/generate_image", "method": "POST"},
    {"path": "/ai/api/generate_image_consistent_character", "method": "POST"},
    {"path": "/ai/api/image2video", "method": "POST"},
    {"path": "/library/get_categories/<library_id>", "method": "GET"},
    {"path": "/api/library/get_media/<library_id>", "method": "GET"},
    {"path": "/library/delete_item/<id>", "method": "DELETE"},
    {"path": "/project/get_list", "method": "GET"},
    {"path": "/project/open/<id>", "method": "GET"},
    {"path": "/render_project/<id>", "method": "POST"},
    {"path": "/api/get_list_output", "method": "GET"},
]


def load_allowlist(surface_path=None):
    """Load the endpoint allowlist from docs/api_surface.json (path templates
    like /project/open/<id>); fall back to the PROVEN set if unavailable."""
    entries = PROVEN_FALLBACK
    if surface_path and os.path.exists(surface_path):
        with open(surface_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
    allowed = {}
    for e in entries:
        allowed[e["path"]] = e.get("method", "GET")
    return allowed


def resolve_allowlist_path(allowed, path):
    """Match a concrete path against templates like /project/open/<id>."""
    if path in allowed:
        return path
    p_segs = path.split("/")
    for tmpl, method in allowed.items():
        t_segs = tmpl.split("/")
        if len(t_segs) != len(p_segs):
            continue
        ok = True
        for t, p in zip(t_segs, p_segs):
            if t.startswith("<") and t.endswith(">"):
                continue
            if t != p:
                ok = False
                break
        if ok:
            return tmpl
    return None
