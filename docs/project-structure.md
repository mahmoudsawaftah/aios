# Independent product structure

Products live outside the AIOS control repository, for example
`C:\Dev\projects\sample-service`. The optional `projects/_template/` provides
documentation scaffolding; it imposes no language, framework or deployment target.

A product can contain a README, project-local AGENTS.md and harness pointers,
source, tests, architecture decisions, project SOPs and ignored local configuration.
Keep existing layouts: do not rename `scripts/`, `src/` or application directories
to match a template.

Project instructions must explicitly name the approved AIOS policy location
(or carry a reviewed local copy) and the product root. Never use a fixed
`../../AGENTS.md` or vault-relative path for arbitrary external repositories.
Record project-specific requirements only in that project's approved context.

Before implementation, verify a clean committed baseline, project-local checks,
secret exclusions and recovery options. The orchestrator creates an isolated
task worktree after planning and build approval. Product changes remain within
the selected product repository and are reviewed separately from AIOS.

Creating remotes, committing, pushing, deploying or changing external knowledge
requires explicit authorization. Never rearrange or delete existing product code,
archives or user data during control repository migration.
