# Control repository migration

## Scope and approval
Safe edits to AIOS policies, templates, documentation and audit tooling only.
Preserve pre-existing work. Product repositories, vault data, credentials, runtime
state, recovery archives and historical task records are outside the write scope.
Never delete, commit, push or publish as part of this procedure.

## Delivery sequence
1. Requirements: record requested removals, reusable lessons and acceptance checks.
2. Architecture: enforce external independent products, project-local configuration,
   role isolation and existing build/release gates.
3. Implementation: generalize active examples; retain historical evidence with an
   explicit retirement notice. Never turn product choices into factory defaults.
4. QA: run `python -m unittest discover -s tests -p 'test_*.py' -v`.
5. Security: run `python scripts/audit_legacy_projects.py .` and review modified
   files for secrets, traversal boundaries and accidental external operations.
6. Release review: run `git diff --check`, review the diff and untracked additions,
   and produce `output/factory-v2-migration-report.md` with actual PASS/FAIL evidence.
   Publication requires separate owner approval.

## Audit interpretation
Exit codes: 0 means no obsolete references; 1 means active/unreviewed references;
2 means a scan failure. Exact historical files and audit definitions are reported
separately, not hidden. Review their exemptions when editing those files; never
put operative product instructions there. New documents fail by default.

The audit prunes protected directories before traversal. Links, junctions, nested
repositories and product folders are excluded; the registry and template are
audited. Generated/installed tools, raw data, communications, runtime state and
recovery archives are outside the audit. Eligible unreadable or oversized text
files fail the scan. This is not a credential scanner or proof about excluded data.
