# <project> - agent instructions

This file is the project's local source of truth. This repository is independent; do not assume Codex can load instructions or skills from its parent AIOS repository.

## Project setup
- Stack: TODO
- Run locally: TODO
- Checks (exact commands): TODO
- Deploy: see the project's deployment directive; never deploy without authorization
- Gotchas: TODO

## Codex workflow
- Read this file, the README, and relevant project docs before editing.
- New feature or multi-stage change: use `$aios-plan`; for tasks spanning more than 3 files or changing architecture, data, or security boundaries, keep the active plan in `PLANS.md`.
- Implement an authorized task with `$aios-implement`; the task request authorizes in-scope edits.
- Bug or failing check: use `$aios-debug`.
- Before claiming completion: use `$aios-verify`, inspect this project's scripts and CI, run applicable real checks, and report actual results.
- Before commit or PR: use `$aios-review`.
- At session end: use `$aios-session-log` and update the existing project tracker or notes.

Skills must be discoverable from this repository's `.agents/skills/` or the user's `~/.agents/skills/`. Confirm with Codex `/skills`; parent AIOS skills are not inherited. If a skill is unavailable, follow the workflow above manually.

## Safety and scope
- Keep changes within the requested project and task.
- Ask before destructive changes, production/live actions, push/merge/deploy, permission changes, secret handling, or scope expansion.
- Never put secrets in code, logs, plans, or memory.
