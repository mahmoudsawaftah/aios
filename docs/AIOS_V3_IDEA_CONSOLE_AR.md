# AIOS v3.0 — Idea Console (first working milestone)

## Scope

This milestone extends Factory v2; it does **not** replace its durable pipeline, SQLite event log, worktree model, build/release approvals, or retry limit.

Owner can type a natural-language idea in a **localhost-only web console**. AIOS creates an **independent local Git repository** under the user's projects directory, saves the goal as a task in Factory v2's SQLite DB, and lets the owner inspect progress, stage handoffs, and decisions from a browser.

The optional one-worker loop runs the existing sequential Codex pipeline. It stops at the build/release gates; it **never** pushes, merges, deploys, registers accounts, spends API money, or publishes content automatically. Extra provider/model usage is **not included by default** in ChatGPT Plus. CLI usage is subject to the user's Codex quota.

## Prerequisites

- Windows/PowerShell, Python 3.11+, Git, and existing AIOS Factory v2 on disk
- Git identity already configured in this AIOS checkout (\`git config user.name\`, \`git config user.email\`)
- Optional autonomous processing: installed Codex CLI and interactive \`codex login\`
- An **empty or separate products directory**. By default \`%USERPROFILE%\AIOS_Projects\`. Set \`AIOS_PROJECTS_ROOT\` to change it.
- Run from a **trusted local user account**. No untrusted users/processes should be allowed access to the machine.

## Start locally (no AI calls)

\`\`\`powershell
cd "C:\Users\ENG_Mahmoud\Documents\aios"
git fetch origin
git switch feat/aios-v3-idea-console
python -m unittest discover -s tests -p "test_*.py" -v
python -m factory.console
\`\`\`

Open **http://127.0.0.1:8765** in the **same machine's** browser. Type the goal, select a delivery methodology, and submit. The idea is stored in local SQLite under \`.factory-runtime/\` and not sent to AI automatically.

The browser app intentionally binds to loopback only. It is not a hosted chat service. Closing the terminal stops the server.

## Enable one automatic Codex worker (consumes usage)

Review the repository and its approval policy. Stop the previous console with Ctrl+C, then run:

\`\`\`powershell
codex --version
codex login
python -m factory.console --auto-run
\`\`\`

The worker processes queued tasks sequentially using the v2 engine and stops at approval gates. The browser can show the reports and record build/release approval. **Build** permits sandboxed writes in a task worktree, while **release signoff is administrative only** (no production deployment). The Codex CLI may require compatible versions; test with a disposable project first. Errors are visible per-task.

If the console crashes or the host restarts, the SQLite task records remain and processing can be resumed by starting the console again with \`--auto-run\`. The interrupted stage may be retried from its beginning. This is **not** guaranteed exactly-once execution, nor a Windows service.

## Security limitations

- Only \`127.0.0.1\` is supported. Never port-forward this prototype, expose through a public reverse proxy, or put it on a shared server.
- Per-process CSRF tokens, origin/host checks, output escaping, body limits, and a restrictive Content Security Policy protect the local forms but **do not constitute user authentication**.
- Goal text, task metadata, and stage handoffs may contain sensitive information. They are stored locally; do not enter confidential client data until access controls, storage encryption, and retention are implemented.
- A trusted browser user can approve gates. The console is meant for one trusted operator only.
- Worker stage prompts may be sent to the selected AI provider when \`--auto-run\` is enabled. Review provider data policies.
- Git repositories are created on local disk only. No GitHub repository is created and no push happens.
- Local machine availability is required: the worker does not run when the machine is off or disconnected.
- Open-source project discovery, license assessment, SaaS billing, social-media publishing, media generation, full multi-agent scheduling, and remote-access authentication are **future milestones**, not features of this milestone.

## Acceptance criteria (v3.0)

1. All Factory v2 tests remain green.
2. A plain-language idea produces a valid separate Git repository and durable task.
3. New task can be viewed in the dashboard; HTML user/model content is escaped.
4. Browser cannot change state using GET; POST requires a local request token and origin/host checks.
5. Default launch does not invoke a model or external service.
6. Optional worker honors v2 approval gates and retry limits.
7. Restarts retain tasks and events; this has not yet been load/chaos tested.

## Next planned milestones

- v3.1: reliable scheduler, leases, idempotency, graceful shutdown, actual crash-recovery tests
- v3.2: automated open-source research, licensing and dependency audit with cited evidence
- v3.3: GitHub PR automation with least privilege, staging previews, CI evidence
- v3.4: marketing content workflows and sanctioned social integrations
- v3.5: client portal, usage metering, subscription lifecycle, compliant payments
- v3.6: multi-agent pool, observability, encrypted remote access and cost policies

**Do not declare end-to-end autonomous production readiness based on passing the v3.0 tests alone.**
