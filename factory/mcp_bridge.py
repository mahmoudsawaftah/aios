"""Item Space AI: local MCP stdio gateway for Codex CLI and IDE.

MCP provides explicit tools, NOT unrestricted shell access. Side effects are confined
to creating local project repositories and local queue artifacts. Human approvals
remain enforced by the separate v2 orchestration worker.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import uuid

from factory import cli
from factory.intake import create_idea, idea_detail, list_ideas

PROTOCOL = "2025-06-18"
MAX_MESSAGE = 1_000_000
INSTRUCTIONS = (
    "Item Space AI manages independent software projects. For a user request to build "
    "or plan a project, call submit_idea or submit_existing_project; inspect with "
    "list_tasks/get_task. Never claim queued work is finished. The background "
    "worker is separate; approval gates cannot be bypassed from MCP. "
    "Use search_open_source for license-aware GitHub candidates. Never publish, "
    "deploy, handle customer credentials, or spend money without owner authorization."
)


def _tool(name: str, description: str, properties: dict, required=()) -> dict:
    return {
        "name": name, "description": description,
        "inputSchema": {"type": "object", "properties": properties,
                        "required": list(required), "additionalProperties": False},
    }


TOOLS = [
    _tool("submit_idea", "Create an independent LOCAL Git project and durable queue entry; does not start Codex.",
          {"idea": {"type": "string", "minLength": 1, "maxLength": 4000},
           "title": {"type": "string", "maxLength": 100},
           "methodology": {"type": "string", "enum": ["hybrid", "agile", "traditional"]}}, ("idea",)),
    _tool("submit_existing_project",
          "Queue a goal for an EXISTING independent local Git repository. Use when Codex is already editing a project in the IDE.",
          {"project_path": {"type": "string", "minLength": 1},
           "goal": {"type": "string", "minLength": 1, "maxLength": 4000},
           "methodology": {"type": "string", "enum": ["hybrid", "agile", "traditional"]}},
          ("project_path", "goal")),
    _tool("list_tasks", "Show local Item Space AI queue and states; does not start workers.",
          {"limit": {"type": "integer", "minimum": 1, "maximum": 30}}),
    _tool("get_task", "Inspect a task, stage outputs and approval requirements (read-only).",
          {"task_id": {"type": "string", "pattern": "^[0-9a-f]{12}$"}}, ("task_id",)),
    _tool("search_open_source",
          "Search public GitHub projects, flag license concerns and save an evidence-backed report; never clone or run repositories.",
          {"query": {"type": "string", "minLength": 2, "maxLength": 150},
           "limit": {"type": "integer", "minimum": 1, "maximum": 10}}, ("query",)),
    _tool("generate_marketing_plan",
          "Generate an OFFLINE draft content calendar and launch checklist; does not publish, send DMs or create fake engagement.",
          {"task_id": {"type": "string", "pattern": "^[0-9a-f]{12}$"}}, ("task_id",)),
    _tool("github_preflight",
          "Read-only GitHub publishing readiness check: credentials, repository, risky files. No push or creation.",
          {"task_id": {"type": "string", "pattern": "^[0-9a-f]{12}$"}}, ("task_id",)),
]


def _submit_existing(args: dict) -> dict:
    project = cli.project_path(args["project_path"])
    goal = args["goal"].strip()
    methodology = args.get("methodology", "hybrid")
    if not goal or len(goal) > 4000 or methodology not in ("hybrid", "agile", "traditional"):
        raise ValueError("Invalid goal or methodology.")
    tid = uuid.uuid4().hex[:12]
    with cli.managed_connect() as db:
        ts = cli.utcnow()
        db.execute(
            "INSERT INTO tasks(id,project,goal,methodology,status,created_at,updated_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (tid, str(project), goal, methodology, "PENDING", ts, ts),
        )
        cli.event(db, tid, "idea_submitted_from_ide", "Queued via local MCP gateway.")
    return {"id": tid, "project": str(project), "status": "PENDING",
            "note": "Queued in SQLite. The separate Item Space AI worker must be running to execute it."}


def call(name: str, args: dict) -> dict:
    if not isinstance(args, dict):
        raise ValueError("Tool arguments must be an object.")
    if name == "submit_idea":
        return create_idea(args["idea"], args.get("title", ""), args.get("methodology", "hybrid"))
    if name == "submit_existing_project":
        return _submit_existing(args)
    if name == "list_tasks":
        return {"tasks": list_ideas(int(args.get("limit", 20)))}
    if name == "get_task":
        d = idea_detail(args["task_id"])
        d["outputs"] = [{**o, "content": o["content"][-6000:]} for o in d["outputs"]]
        return d
    if name == "search_open_source":
        from factory.oss_research import search_open_source
        return search_open_source(args["query"], int(args.get("limit", 6)))
    if name == "generate_marketing_plan":
        from factory.marketing import generate_marketing_plan
        return generate_marketing_plan(args["task_id"])
    if name == "github_preflight":
        from factory.github_ops import preflight
        return preflight(args["task_id"])
    raise ValueError("Unknown Item Space AI tool.")


def handle(message: dict) -> dict | None:
    if not isinstance(message, dict):
        return {"jsonrpc": "2.0", "id": None,
                "error": {"code": -32600, "message": "Invalid Request"}}
    if "id" not in message:
        return None  # MCP notifications have no reply.
    request_id = message["id"]
    method = message.get("method")
    params = message.get("params") or {}
    try:
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": request_id,
                    "result": {"protocolVersion": PROTOCOL,
                               "capabilities": {"tools": {"listChanged": False}},
                               "serverInfo": {"name": "item-space-ai", "version": "3.1.0"},
                               "instructions": INSTRUCTIONS}}
        if method == "ping":
            return {"jsonrpc": "2.0", "id": request_id, "result": {}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
        if method == "tools/call":
            name = params.get("name")
            if name not in {t["name"] for t in TOOLS}:
                raise ValueError("Unrecognized tool.")
            args = params.get("arguments") or {}
            result = call(name, args)
            return {"jsonrpc": "2.0", "id": request_id,
                    "result": {"content": [{"type": "text",
                                           "text": json.dumps(result, ensure_ascii=False)}]}}
        return {"jsonrpc": "2.0", "id": request_id,
                "error": {"code": -32601, "message": "Method not found"}}
    except (KeyError, TypeError, ValueError, OSError, RuntimeError) as exc:
        # Avoid echoing prompts, environment variables or private paths in logs.
        safe_type = type(exc).__name__
        if method == "tools/call":
            return {"jsonrpc": "2.0", "id": request_id,
                    "result": {"isError": True,
                               "content": [{"type": "text",
                                            "text": safe_type + ": " + str(exc)[:250]}]}}
        return {"jsonrpc": "2.0", "id": request_id,
                "error": {"code": -32602, "message": safe_type}}


def serve(stdin=None, stdout=None) -> int:
    """Serve UTF-8 JSON-RPC over binary stdio streams.

    Windows Python uses a locale code page for redirected text stdout, which
    can fail on Arabic and non-ASCII text with UnicodeEncodeError. MCP requires
    UTF-8, so never write protocol payloads through sys.stdout's text encoder.
    The optional binary streams support deterministic in-memory protocol tests.
    """
    input_stream = sys.stdin.buffer if stdin is None else stdin
    output_stream = sys.stdout.buffer if stdout is None else stdout
    for raw in input_stream:
        if len(raw) > MAX_MESSAGE:
            continue
        try:
            incoming = json.loads(raw.decode("utf-8"))
            reply = handle(incoming)
        except (ValueError, UnicodeError, TypeError):
            reply = {"jsonrpc": "2.0", "id": None,
                     "error": {"code": -32700, "message": "Parse error"}}
        if reply is not None:
            payload = (json.dumps(reply, ensure_ascii=False, separators=(",", ":"))
                       + "\n").encode("utf-8")
            output_stream.write(payload)
            output_stream.flush()
    return 0

if __name__ == "__main__":
    raise SystemExit(serve())
