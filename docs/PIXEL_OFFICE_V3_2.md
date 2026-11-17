# Item Space AI v3.2 — Pixel Office (draft)

## What it does

Read-only animated virtual office at `/office` using native Canvas 2D and the
current Item Space AI task database. No Node/Bun, no new work engine, no
external assets, and no copied sprites.

- `/office`: visual workstations for 8 pipeline departments, a review room,
  clickable task characters, and live task counts.
- `/office/state`: bounded task ID/title/status/stage/timestamp + worker status.
  Does not expose goal content, source code, error text, or credentials.
- `/office.js`: polls task state every 4s; animation only if status RUNNING.
- WAITING_APPROVAL is visibly in review area; not a claimed real agent meeting.
- No approve/build/release buttons are introduced; original gates are unchanged.
- Reduced-motion users see a static frame.

## GitHub inspiration and attribution

Pixel Agents: https://github.com/pixel-agents-hq/pixel-agents (MIT)
Agent Office: https://github.com/falkoro/agent-office (MIT, Codex + Antigravity)
Both are references only. This draft uses original Canvas rectangles drawn from scratch.
Review upstream asset licensing/attribution separately before importing artwork.

## Runtime truthfulness

One character represents a task/stage record, NOT a separate coding process.
The present worker may be single-agent, even when several characters are shown.
Next milestone: a real Agent Session Bridge (Codex, Antigravity, subagents) which
only shows agents working if session/process/heartbeat evidence exists.

## Important local safety

The user's false-completion fix 36ebf99 was committed to the user's local
AIOS checkout, not this UI branch. Do NOT pull, switch, reset or merge it
directly into that active checkout. Keep tasks and SQLite untouched.

Preview from a separate clone using LAUNCH_LIVE_STUDIO_READONLY.cmd on port 8877.
The launcher runs the full Python tests before rendering a read-only view
of the active AIOS task database. It never starts a worker, approves a task,
or changes the original working tree.

## Tests

tests/test_pixel_office.py covers read-only snapshots, no prompt/error disclosure,
XSS-safe textContent DOM construction, canvas presence, CSP, real localhost
routes, and POST rejection. Tests are authored but NOT executed on user's PC.
PR remains draft until all regression tests pass.

## Future scope

Agent Session Bridge with per-session state; real meeting and handoff events;
bounded per-slice multiagent worktrees; preserving the Acceptance Gate;
more polished original Pixel Art and optional office customization.
