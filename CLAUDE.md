# CLAUDE.md

Read `AGENTS.md` — it applies in full as the canonical instructions for this workspace.

## Claude Code Environment Notes
- **Shared Memory**: Optionally configured at `vault/memory/MEMORY.md`. Report a missing index; never assume a user-specific directory or create junctions automatically.
- **Project Isolation**: Product repositories live outside AIOS and use their own explicit configuration. Never automatically commit or publish changes.
- **Project Scoped Skills**: ECC skills and agents are located in `.claude/skills/` and `.claude/agents/`.
- **Precedence**: When any ECC rule conflicts with `AGENTS.md`, `AGENTS.md` wins.

## AIOS Software Factory v2 (2026-11)

When operating as a software development agent, follow docs/AIOS_SOFTWARE_FACTORY.md,
docs/HYBRID_DELIVERY_METHODOLOGY.md and governance/SECURITY_AND_APPROVALS.md.
The owner must approve build/release gates. Never delete other product repositories,
run commands outside the designated project, bypass sandbox controls, or publish changes.
All product code lives in independent Git repositories outside the AIOS control repo.
