# GEMINI.md

Read `AGENTS.md` — it applies in full as the canonical instructions for this workspace.

## Antigravity Environment Notes
- **Shared Memory**: Reachable at relative path `vault/memory/MEMORY.md`. Read the index at session start and inspect only relevant memory notes.
- **Workflow & Rules**: Follow the DOE workflow (`docs/doe.md`) and the 20 operating rules (`docs/operating-rules.md`).
- **Project Structure**: Product repositories live outside AIOS; `projects/` holds the registry and template only. Use project-local instructions and explicit paths. Never modify product code without approval or automatically commit/publish changes.
- **Optional Memory**: Report a missing index and proceed with repository guidance; never create a junction automatically.
- **Precedence**: `AGENTS.md` strictly takes precedence over any generic defaults.

## AIOS Software Factory v2 (2026-11)

When operating as a software development agent, follow docs/AIOS_SOFTWARE_FACTORY.md,
docs/HYBRID_DELIVERY_METHODOLOGY.md and governance/SECURITY_AND_APPROVALS.md.
The owner must approve build/release gates. Never delete other product repositories,
run commands outside the designated project, bypass sandbox controls, or publish changes.
All product code lives in independent Git repositories outside the AIOS control repo.
