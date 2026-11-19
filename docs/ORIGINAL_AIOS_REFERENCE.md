# Reference from the supplied original AIOS archive

**Status:** historical reference. This file records what the original archive documented; it does not claim that its runtime was installed, tested, or production-ready. Current operating instructions are in the root `AGENTS.md`.

## Useful operating design retained
- AIOS is a control plane; each product should have its own Git repository and working history.
- Major work can pass through discovery, requirements, architecture, backlog, implementation, QA, security review, and release planning.
- Work should be isolated from the user's original checkout, with actual evidence reviewed before acceptance.
- Build approval and release signoff are different; neither should silently push, merge, or deploy.
- Tasks should be restartable and report the exact stage, blocker, and next step.
- The primary agent may use separate role perspectives, but those role files do not mean separate processes ran.

## Original runtime described in the archive
The original files describe an experimental Python/SQLite Factory v2 and Item Space AI v3 local console. They refer to:
- A sequential Codex CLI worker, local task queue and state database.
- Optional MCP bridge from Codex/Antigravity into the local queue.
- Separate product worktrees, stage handoffs, retries, and manual build/release approvals.
- GitHub OSS search and draft marketing text, plus a GitHub preflight/private PR path.
- Local-only browser console bound to `127.0.0.1`; running the computer is required.

These are descriptions from the archive, not verified capabilities of this clean Codex edition. The runtime required Python, Git, Codex CLI/login, local worker processes, and additional setup.

## Limits explicitly reported by the original handoff
The supplied v3.1 handoff calls itself an integration candidate, not production-ready. It reports that Windows integration and CI were not fully verified, that concurrent worker pools and a crash/restore drill were absent, and that legal/license/dependency review, customer authentication, full publishing, and production deployment were incomplete. A stage interrupted during work could be rerun from its beginning; the docs do not promise exactly-once execution or a 24/7 service.

## False-completion lesson
The archive documents an earlier false-completion failure: a model stage could be marked complete without proving the required product behavior existed. The acceptance-gate design correctly separates stage output from acceptance and calls for evidence tied to real files and executed checks. This clean edition carries that lesson in `item-space-acceptance` and the evidence rules, but it does not include the original deterministic verifier or claim an automated gate.

## Excluded from this clean edition
The archive contains runtime source, local installer scripts, cached `__pycache__` bytecode, and `.aios-update-backups` with prior code states. This edition does not copy them into the active Codex setup. The bytecode and old backups are not source-of-truth. The runtime should be integrated only as a separate, reviewed project after testing on a disposable repository and checking sandbox, recovery, and approval behavior.
