# Capabilities and limits — Codex edition

## Included
- Project-specific Codex instructions and short routing skills.
- Role checklists for discovery, requirements, architecture, backlog, implementation, QA, security, and release planning.
- A product brief that separates known direction from open decisions.
- A single plan and handoff file, security boundaries, and explicit evidence rules.
- A blank Item Space placeholder.

## Not provided by this package
- No background worker, durable task queue, scheduler, automatic restart, or 24/7 service.
- No guaranteed custom subagent pool. The primary Codex agent can delegate only if the active runtime exposes subagent tools.
- No automatic Git commits, GitHub publishing, deployment, production access, or secrets management.
- No test or security result until Codex runs the actual project checks and records their output.

## Why the original factory runtime is not copied here
The supplied original archive contains a Python/SQLite factory, local console, worker/MCP bridge, approval pipeline, tests, backups, and cached bytecode. Its own handoff labels the runtime an integration candidate and records gaps such as no verified Windows integration, no concurrent worker pool, no exactly-once resume, and no production readiness. This Codex-first edition carries over its useful stage model and safety lessons, but does not represent the prototype runtime as verified or required for Antigravity work.

If the owner later wants the queue/worker console, review that runtime as a separate project: inspect its source and dependencies, test it on a disposable project, verify sandbox and recovery behavior, then decide whether to adopt it.
