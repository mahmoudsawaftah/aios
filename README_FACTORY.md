# AIOS Software Factory v2 — Quick Start

This overlay converts AIOS into a **safe single-worker orchestration prototype** for building software in independent repositories, with Hybrid Agile/Traditional method and owner approval gates.

## Requirements
- Python 3.11+, Git and Codex CLI installed on your Windows host / WSL2.
- `codex login` completed interactively.
- `aios` is a Git clone. Keep projects outside `aios`, ideally `C:\Dev\projects\<project>`.
- Never expose credentials in prompts or commit secrets.

### Verify locally (no model use, no cost)
```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
python -m factory.cli list
```

### Create a new independent project repo
```powershell
New-Item -ItemType Directory -Force 'C:\Dev\projects\pilot-app' | Out-Null
git -C 'C:\Dev\projects\pilot-app' init
# Configure Git user.name and user.email first if needed.
git -C 'C:\Dev\projects\pilot-app' commit --allow-empty -m 'Initialize project'
python -m factory.cli create --project 'C:\Dev\projects\pilot-app' --methodology hybrid --goal 'Build a small demo with auth, tests and documented rollback'
```
Take the task ID printed by the command (e.g., abc123).

### Run and resume
```powershell
python -m factory.cli run TASK_ID
python -m factory.cli status TASK_ID
# After inspecting discovery, requirements, architecture and backlog outputs:
python -m factory.cli approve --gate build TASK_ID
python -m factory.cli run TASK_ID
# After inspecting QA/security/release_plan:
python -m factory.cli approve --gate release TASK_ID
python -m factory.cli run TASK_ID
```
Output is recorded in `.factory-runtime/outputs/TASK_ID/`.
Build/QA take place in an **isolated Git worktree** under `C:\Dev\projects\.aios-worktrees\`, on branch `aios/task-TASK_ID`; the original project checkout is left untouched. Inspect that worktree and commit reviewed changes manually.

To resume runnable tasks after reconnecting, run `python -m factory.cli run-pending` (it skips approval-blocked and failed tasks). This command can be scheduled only after the owner explicitly configures Windows Task Scheduler.

Any `INTERRUPTED` stage is retried with another `run`. `FAILED` at the retry limit requires `reset-stage TASK_ID` after review.

## Operational cautions
This MVP is **not a background service**. Its `run-pending` entry point is available for Windows Task Scheduler, but scheduling is NOT installed or enabled automatically. Keep the terminal open while a run is executing. Never run two instances against the same task; a local OS file lock prevents this. Explicitly approve stages only after reviewing the outputs. The model can make mistakes and must be sandboxed.

For legacy references: `python scripts/audit_legacy_projects.py .` (read-only; obsolete references fail, historical records and audit definitions are classified separately). See `directives/control-repository-migration.md` for boundaries and exit codes.

See `docs/COMPANY_OPERATING_MODEL_AR.md`, `docs/AIOS_SOFTWARE_FACTORY.md`, `docs/HYBRID_DELIVERY_METHODOLOGY.md` and `governance/SECURITY_AND_APPROVALS.md`.
