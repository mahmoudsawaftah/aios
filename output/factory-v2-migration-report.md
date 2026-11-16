# AIOS Software Factory v2 migration report

Date: 2026-11-16 (America/Los_Angeles).

## Decision

**PASS: control-repository migration acceptance checks.** Active product assumptions
and registrations are retired; reusable engineering lessons are generic. No release,
deployment, external migration, commit or push was performed. This is not a claim
of production readiness or concurrent multi-agent execution.

## Requirements and architecture

The migration keeps AIOS as a control repository and products as independent
external repositories. Product configuration, stack, design system, languages,
hosting and credentials are determined locally, never inherited from former clients.
The registry is empty until the owner explicitly selects products.

Reusable lessons remain: version-matched framework verification, design-token and
language requirements, trusted server decisions, deterministic readiness checks,
and backup/recovery review. The optional Next.js SOP is explicitly stack-specific.

Hybrid delivery remains discovery -> requirements -> architecture -> backlog ->
build approval -> implementation -> QA -> security -> release planning -> release
signoff. The existing factory implementation, role prompts, security policy,
SQLite events, approval records, retry/reset behavior and task-worktree mechanism
were not edited during this migration. Runtime logs and recovery data were untouched.

## Verification evidence

| Check | Result | Evidence |
|---|---|---|
| All Python unit tests | PASS | `python -m unittest discover -s tests -p 'test_*.py' -v`: 10 tests, OK, exit 0 |
| Existing factory behavior | PASS | Five existing tests cover build/release gates, early-approval rejection, independent roots, isolated worktrees, retry/reset |
| Audit regression coverage | PASS | Five new tests cover requested aliases, exact classification exceptions, protected/nested roots, reparse pruning, exit codes and decoding failures |
| Legacy-reference audit | PASS | `python scripts/audit_legacy_projects.py .`: obsolete=0, history=5, definition=12; exit 0 |
| Whitespace validation | PASS | `git diff --check`: exit 0; only existing Windows LF/CRLF conversion notices |
| Modified-file review | PASS | Reviewed policy, docs, template, environment example, helper sources, audit, tests, SOP and CI changes; corrected nested-product and automatic-publication contradictions |
| PowerShell syntax | PASS | PowerShell Language.Parser parsed both revised helpers with no errors, exit 0 |
| Health helper runtime | FAIL / BLOCKED | `powershell -NoProfile -File execution/check/Check-AiosHealth.ps1`: exit 1, scripts disabled by host execution policy |
| Review helper runtime | FAIL / BLOCKED | `powershell -NoProfile -File execution/util/Sync-Aios.ps1 -Message 'migration review'`: exit 1, same execution policy |

PowerShell runtime failures are not counted as successful tests. No policy bypass,
policy change or unapproved execution was attempted. Syntax checks do not prove
runtime behavior. CI was updated locally; no hosted CI run or publication occurred.

## Audit interpretation and security review

The historical provenance file and dated bootstrap log contain five matching lines.
They are retained as evidence, not operative instructions. Twelve matching lines in
the audit implementation and regression fixtures define/test detection behavior.
Exceptions are exact file paths and are reported, not silently omitted. New files
fail classification by default; reviewers must inspect changes to exempt files.

The audit prunes protected directories before traversal and excludes symlinks,
Windows reparse points, nested Git repositories and product directories. It checks
the registry/template and eligible hidden text files, including `.env.example`.
It excludes actual environment files, vault data, installed tools, raw data,
communications, runtime state and recovery archives. Unreadable/oversized eligible
text fails instead of silently passing. Source lines are not printed.

No credentials were read or changed. The environment example no longer imports
product variable names or values. The old sync helper now performs read-only Git
review and accepts its old Message argument without staging, committing or pushing.
The health helper checks control metadata instead of entering nested products.

## Remaining issues and limits

1. Optional `vault/memory/MEMORY.md` was absent at session start. No personal vault,
   memory index or junction was created or modified. Updated guidance treats memory
   as explicit optional configuration and reports missing access.
2. Helper runtime validation remains blocked by host execution policy. An owner may
   validate the scripts later in an approved environment; changing policy is outside
   this migration. Required Python/audit/diff acceptance checks passed.
3. The current factory is a sequential single-worker MVP with multiple role prompts,
   not a concurrent multi-agent worker pool. Distributed scheduling, stronger worker
   isolation and restore drills remain documented engineering milestones.
4. Ignored/external products, recovery archives and personal data were intentionally
   not searched. The zero-obsolete result applies to eligible control text, not those
   excluded stores, Git history, binaries or unsupported file formats.
5. Pre-existing uncommitted/untracked Factory v2 work was present. It remains in the
   working tree. This report does not represent it as newly authored or published.
   Runtime audit logs were preserved, not subjected to a restore or integrity drill.
6. Historical exceptions require human review when edited; classification is not
   semantic proof that every sentence in an exempt file is harmless.

## Exact files changed in this migration

- `.env.example`
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README.md`, `README_FACTORY.md`
- `projects/INDEX.md`, `projects/README.md`
- `projects/_template/AGENTS.md`, `projects/_template/README.md`
- `docs/conventions.md`, `docs/doe.md`, `docs/harvest.md`
- `docs/memory-protocol.md`, `docs/onboarding.md`, `docs/operating-rules.md`
- `docs/project-structure.md`, `docs/toolchain.md`
- `directives/nextjs-verification.md`, `directives/weekly-review.md`
- `directives/control-repository-migration.md` (new)
- `execution/check/Check-AiosHealth.ps1`, `execution/util/Sync-Aios.ps1`
- `scripts/audit_legacy_projects.py`
- `tests/test_legacy_audit.py` (new)
- `.github/workflows/aios-factory-tests.yml`
- `output/factory-v2-migration-report.md` (this report, new)

Other existing working-tree additions/modifications, including `.gitignore`,
Factory v2 runtime code, role prompts and governance documents, were preserved.

## Release and recovery

Changes remain uncommitted for owner review. No product worktree or live service
was operated on. For revision, review the listed changes individually and retain
pre-existing Factory v2 work; never use a blanket reset or cleanup. Build/release
approvals and separate authorization for external side effects remain mandatory.
