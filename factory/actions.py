"""Shared local dashboard actions for research, marketing and GitHub checks."""
from __future__ import annotations

import json
from pathlib import Path
import re

from factory import cli
from factory.intake import idea_detail

ACTIONS = ("research", "marketing", "github-preflight")


def perform(task_id: str, action: str, query: str = "") -> dict:
    if not isinstance(task_id, str) or not re.fullmatch(r"[0-9a-f]{12}", task_id):
        raise ValueError("Invalid task ID.")
    if action not in ACTIONS:
        raise ValueError("Unsupported action.")
    idea = idea_detail(task_id)
    if action == "research":
        from factory.oss_research import search_open_source
        lookup = query.strip() if query else Path(idea["project"]).name.rsplit("-", 1)[0].replace("-", " ")
        result = search_open_source(lookup[:150], 6)
    elif action == "marketing":
        from factory.marketing import generate_marketing_plan
        result = generate_marketing_plan(task_id)
    else:
        from factory.github_ops import preflight
        result = preflight(task_id)
    destination = cli.STATE / "extras" / task_id
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / (action + ".json")
    tmp = destination / (action + ".tmp")
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    with cli.managed_connect() as db:
        cli.event(db, task_id, "local_action_completed", action)
    return {"action": action, "report": str(path), "result": result}


def extra_outputs(task_id: str) -> list[dict]:
    if not re.fullmatch(r"[0-9a-f]{12}", task_id):
        return []
    location = cli.STATE / "extras" / task_id
    outputs = []
    for name in ACTIONS:
        path = location / (name + ".json")
        if path.is_file():
            content = path.read_text(encoding="utf-8", errors="replace")[-12000:]
            outputs.append({"stage": name, "content": content})
    return outputs
