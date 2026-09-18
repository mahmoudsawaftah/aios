# aios - AI Operating System for Moe

Welcome to `aios`, the centralized standards, operating procedures, and tooling repository for Moe's development projects across **Antigravity**, **Codex**, and **Claude Code**.

---

## 1. What `aios` Is

`aios` versions the **standards layer only**. It does not hold project code or client files.
- **Projects** live in `projects/<name>/` as independent Git repositories.
- **Personal Knowledge & AI Memory** live in your Obsidian vault (`moevault`), connected via junction at `aios/vault/`.
- **Operating Guidelines & SOPs** live in `docs/` and `directives/`.
- **Reusable Automation Scripts** live in `execution/`.

---

## 2. Directory Layout

```
aios/
  AGENTS.md              <- Canonical instructions for all AI agents
  CLAUDE.md              <- Pointer to AGENTS.md for Claude Code
  GEMINI.md              <- Pointer to AGENTS.md for Antigravity
  .env.example           <- Consolidated environment variable template (names only)
  .gitignore             <- Protects vault/, projects/*, and secrets

  vault/                 <- NTFS Junction to moevault (Obsidian vault). Gitignored.

  docs/                  <- Core documentation:
    doe.md               <- Document -> Orchestrate -> Execute methodology
    operating-rules.md   <- Twenty foundational operating guidelines
    memory-protocol.md   <- Shared memory structure and rules
    conventions.md       <- Repository model and naming conventions
    project-structure.md <- Standard shape for all projects
    toolchain.md         <- Installed tools & curated ECC skills
    harvest.md           <- Provenance of standards harvested from real projects
    onboarding.md        <- Plain-language guide for Moe

  directives/            <- Shared SOPs across projects
  execution/             <- Reusable automation scripts:
    recon/               <- Read-only discovery
    check/               <- Health checks (Check-AiosHealth.ps1)
    maint/               <- State-modifying maintenance
    util/                <- Synchronization & utility tools (Sync-Aios.ps1)

  projects/              <- Your projects (each is its own Git repository):
    INDEX.md             <- Central registry of all projects and remotes
    _template/           <- Standard copyable template for new projects
    AMG/                 <- WorkMerit platform repo
    HR odoo/             <- HRA platform repo

  output/                <- Client deliverables & final exports
  raw/                   <- Working scratch area (inbox, query dumps, analysis)
  comms/                 <- Email & message drafts (gitignored)
  mytasks/               <- Session task logs (YYYY-MM-DD-*.md)
  reminders/             <- Actionable dated reminders (YYYY-MM-DD-*.md)
```

---

## 3. Quick Start Commands

- **Run System Health Check**:
  ```powershell
  powershell -File execution/check/Check-AiosHealth.ps1
  ```
- **Sync & Push Standards Layer**:
  ```powershell
  powershell -File execution/util/Sync-Aios.ps1 -Message "docs: update guidelines"
  ```
- **Start a New Project**:
  ```powershell
  Copy-Item -Recurse "projects/_template" "projects/my-new-project"
  ```
  Then see `projects/_template/README.md` for initialization steps.
