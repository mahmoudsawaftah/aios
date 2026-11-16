# Repository conventions

## Control, product and knowledge boundaries

AIOS versions shared policies, roles, orchestration code, SOPs, tests and control
reports. Every product owns a separate Git repository outside the AIOS root,
for example `C:\Dev\projects\sample-service`. The registry at
`projects/INDEX.md` is metadata, not a dependency or a source checkout.
`projects/_template/` is a copyable optional scaffold.

Products select their own language, framework, database, hosting, design system
and verification commands. Inspect their manifests; never inherit another
product's configuration or credentials. Use explicit paths to shared guidance
instead of assuming `../../AGENTS.md` resolves.

Optional knowledge lives in an external vault. `vault/` may be an NTFS junction,
so writing through it changes live user data. Do not create it automatically,
recurse into it, or commit it. Missing memory is an environmental limitation,
not permission to reconstruct personal notes.

## Scanning and recovery

Use the classified audit in `scripts/audit_legacy_projects.py` for migrations.
It prunes protected data before traversal and excludes junctions, symlinks and
nested repositories. Do not use recursive PowerShell exclusions as proof that
a junction was not traversed.

Preserve `.factory-runtime/`, recovery archives, external repositories and
credentials. Git does not back up ignored files, uncommitted work or databases.
Restore testing and off-device backup configuration require owner planning.

## Naming and review

Use focused files, kebab-case names where practical, ISO dates and conventional
commit messages when a commit is authorized. Keep changes surgical.
End sessions with test evidence and a reviewed diff. Never automatically stage,
commit, push, merge, publish or run the legacy sync helper. Follow
`governance/SECURITY_AND_APPROVALS.md` for irreversible and external actions.
