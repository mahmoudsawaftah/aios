# Standard Project Structure

Every project in `aios/projects/` follows the same predictable layout so that you — and any AI agent — can navigate it immediately.

---

## 1. Project Directory Layout

```
projects/<project-name>/
  README.md              <- Purpose, tech stack, quickstart, and link to vault note
  AGENTS.md              <- 4-line pointer to root AGENTS.md and memory
  CLAUDE.md              <- Pointer: @AGENTS.md
  GEMINI.md              <- Pointer: @AGENTS.md
  notes.md               <- Daily running log; durable insights graduate to vault
  .gitignore             <- Must ignore .env and local build artifacts
  .env                   <- Secret credentials (NEVER committed, NEVER printed)
  .env.example           <- Variable names only (safe to commit)
  docs/                  <- Architecture and project documentation for humans
  directives/            <- Project-specific SOPs (deployments, data imports, releases)
  execution/             <- Project-specific helper scripts (recon, check, maint, util)
  output/                <- Client deliverables, built assets, reports
  raw/                   <- Working area (inbox, analysis, scratch)
  <source-code>          <- Untouched application code (app/, src/, etc.)
```

---

## 2. Why Per-Project `AGENTS.md` Matters

AI agents (Codex, Antigravity, Claude Code) look for instruction files (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`) in the **working directory where the editor or terminal was opened**.

When you open `projects/AMG` directly in VS Code or Antigravity:
- If there is no `AGENTS.md` inside `projects/AMG/`, the agent will **not** know about your preferences, rules, or the memory vault!
- With a 4-line pointer file in the project folder:
  ```markdown
  # <project> - agent instructions

  Inherit the standards in `../../AGENTS.md`. They apply in full.
  Long-term memory: `../../vault/memory/MEMORY.md` - read it at session start.
  Vault note for this project: `../../vault/projects/<name>.md`.

  ## Project-specific
  - Stack: <tech stack>
  - Run locally: <local dev command>
  - Deploy: see directives/ - never deploy without reading it
  - Gotchas: <critical notes>
  ```
The agent immediately inherits the entire root standards layer and knows how to access long-term memory.

---

## 3. Ground Rules for Existing Projects

1. **Add Additively Only**: Never rearrange, delete, or move existing source code.
2. **Respect Existing Structure**: If a project uses `scripts/` instead of `execution/` or `app/` instead of `src/`, do not force a rename. Fit the standards around the project.
3. **Protect `.env`**: Always ensure `.env` is listed in the project's own `.gitignore`.
4. **Independent Commits**: Changes made to adopt structure inside a project repository are committed inside that project repository, never in `aios`.
