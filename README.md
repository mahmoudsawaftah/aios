# AIOS Software Factory v2

AIOS is a supervised software delivery control repository for multiple independent
products. It provides reusable role prompts, hybrid Agile/traditional SDLC guidance,
a durable single-host orchestrator and owner approval gates.

Product code lives in independent Git repositories **outside AIOS**. No previous
client, technology stack, design system, hosting service or credentials are defaults.

## Repository map

- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`: shared agent contract and harness pointers.
- `factory/`: Python standard-library CLI and SQLite state machine.
- `agents/roles/`: discovery, requirements, architecture, backlog, implementation,
  QA, security and release planning roles.
- `governance/`: security boundaries and owner approval policy.
- `docs/`, `directives/`, `execution/`: engineering knowledge, SOPs and tools.
- `projects/INDEX.md`: owner-selected project registry; no active registrations.
- `projects/_template/`: optional generic template to copy into an external repo.
- `tests/`, `scripts/`: regression checks and classified legacy-reference audit.
- `output/`, `raw/`: control reports and temporary work.
- `.factory-runtime/`: ignored local state, events and stage outputs; preserve and
  back it up separately.
- `vault/`: optional external knowledge junction; excluded from repository scans.
- `.aios-update-backups/`: ignored recovery data; never clean it automatically.

## Verify locally

From the AIOS control root, without model calls or external services:

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/audit_legacy_projects.py .
git diff --check
```

See [the quick start](README_FACTORY.md) for explicit project paths, task creation,
run/resume commands and owner approvals. Creating and running a task can write
runtime state and an external task worktree; only do so for an authorized product.

The build gate follows discovery, requirements, architecture and backlog. QA,
security and release planning follow implementation. The release gate records
signoff and never deploys. See [architecture](docs/AIOS_SOFTWARE_FACTORY.md),
[hybrid delivery](docs/HYBRID_DELIVERY_METHODOLOGY.md) and
[security policy](governance/SECURITY_AND_APPROVALS.md).

The current MVP executes roles sequentially through one Codex CLI worker. Multiple
independent products are supported; concurrent isolated agents and a distributed
scheduler are future work. Never automatically commit, push, merge or publish.

Migration procedure: [control repository migration](directives/control-repository-migration.md).
Verification evidence: [migration report](output/factory-v2-migration-report.md).
