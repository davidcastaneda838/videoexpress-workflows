#!/usr/bin/env python3
"""vx-mcp: local MCP server (JSON-RPC 2.0 over stdio) exposing VideoExpress.

Launch:
    set VX_COOKIES=E:/path/cookies.json      (Windows)
    python vx-mcp/server.py [--cookies cookies.json]

Protocol: newline-delimited JSON-RPC (MCP stdio transport). Supports
initialize, tools/list, tools/call, ping. Every tool returns real handles
(media_id / uuid / output URL) or a tool error — never fabricated results.
"""

import argparse
import json
import os
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import tools as vxtools  # noqa: E402
from vx import Vx  # noqa: E402

_client_lock = threading.Lock()
_client = None
ALLOWLIST = vxtools.load_allowlist(
    os.path.join(ROOT, "docs", "api_surface.json"))


def t_raw_call(vx, args):
    """Generic allowlisted endpoint call (coverage gaps)."""
    path = args["path"]
    tmpl = vxtools.resolve_allowlist_path(ALLOWLIST, path)
    if tmpl is None:
        raise ValueError(f"endpoint not in allowlist: {path}")
    # fill <placeholders> from path_params
    concrete = path
    for seg_tmpl, seg in zip(tmpl.split("/"), path.split("/")):
        pass  # concrete path already given; template only validated shape
    method = ALLOWLIST[tmpl]
    if method == "GET":
        return vx.get(concrete)
    if method == "DELETE":
        return {"status": vx.delete(concrete)}
    if isinstance(args.get("json_body"), (dict, list)):
        return vx.post(concrete, json_body=args["json_body"])
    return vx.post(concrete, fields=args.get("fields") or {})


TOOLS = dict(vxtools.TOOLS)
TOOLS["vx_raw_call"] = (
    "Generic allowlisted raw endpoint call (allowlist from docs/api_surface.json).",
    {"type": "object", "properties": {"path": {"type": "string"},
                                      "fields": {"type": "object"},
                                      "json_body": {},
                                      "path_params": {"type": "object"}},
     "required": ["path"]},
    t_raw_call)


def get_client():
    global _client
    with _client_lock:
        if _client is None:
            cookies = (vxtools.__dict__.get("_cookies_arg")
                       or os.environ.get("VX_COOKIES"))
            if not cookies:
                raise RuntimeError("no cookies file: pass --cookies or set VX_COOKIES")
            _client = Vx(cookies)
        return _client


def tools_list():
    return [{"name": name, "description": desc, "inputSchema": schema}
            for name, (desc, schema, _fn) in TOOLS.items()]


def tools_call(name, arguments):
    entry = TOOLS.get(name)
    if entry is None:
        raise KeyError(f"unknown tool: {name}")
    _desc, _schema, fn = entry
    result = fn(get_client(), arguments or {})
    return {"content": [{"type": "text", "text": json.dumps(result, default=str)}],
            "isError": False}


def handle(msg):
    method = msg.get("method")
    mid = msg.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "vx-mcp", "version": "0.1.0"}}}
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": tools_list()}}
    if method == "tools/call":
        params = msg.get("params") or {}
        try:
            result = tools_call(params["name"], params.get("arguments"))
            return {"jsonrpc": "2.0", "id": mid, "result": result}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": f"error: {e}"}],
                "isError": True}}
    if mid is not None:
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"unknown method: {method}"}}
    return None


def main():
    global _client
    ap = argparse.ArgumentParser(description="vx-mcp VideoExpress MCP server")
    ap.add_argument("--cookies", default=None, help="cookies.json path")
    args, _ = ap.parse_known_args()
    vxtools.__dict__["_cookies_arg"] = args.cookies

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
