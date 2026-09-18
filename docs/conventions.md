# System Conventions & Architecture Model

This document explains how files, directories, repositories, and junctions are structured across `aios` and `moevault`.

---

## 1. The Three-Repo-Type Architecture

Understanding the division between your repositories is essential for keeping your work safe and organized:

```
[ aios Repository ]                     [ moevault Vault ]
  - Standards & SOPs                     - Personal Obsidian Vault
  - Shared Scripts (execution/)          - Notes & Understanding
  - Documentation (docs/)                - Shared AI Memory (memory/)
  - Registry (projects/INDEX.md)                       |
       |                                               |
       +---------------- (NTFS Junction) --------------+
       |                  aios/vault/
       |
  [ projects/ ]
       +---> [ AMG/ ] -------------> Standalone Git Repo (github.com/danar-capital/AMG)
       +---> [ HR odoo/ ] ---------> Standalone Git Repo (Needs remote!)
       +---> [ _template/ ] -------> Copyable starter template
```

### Repo 1: `aios` (Standards Layer)
- **What it contains**: SOPs (`directives/`), reusable tools (`execution/`), architecture guides (`docs/`), and the central registry (`projects/INDEX.md`).
- **Remote**: `aios` GitHub repository.
- **Rule**: Never holds project code or client files. It versions the standards only.

### Repo 2: Project Repositories (`projects/<name>/`)
- **What they contain**: Application code, tests, build configurations, and project-specific `.env` files.
- **Remotes**: Each project has its own separate Git repository and remote URL.
- **Why no Git Submodules?**: Git submodules create detached HEAD issues, recursive update headaches, and merge conflicts that are fragile for day-to-day work. Instead, each project is completely self-contained, and `projects/INDEX.md` serves as the map between them.

### Repo 3: `moevault` (Knowledge & Memory)
- **What it contains**: Human knowledge, client requirements, study logs, and agent memory notes.
- **Nature**: It is an Obsidian vault, **not** part of the `aios` Git repository.
- **Access**: Reached inside `aios` through an NTFS junction (`aios/vault/`).

---

## 2. The Junction Rules (Crucial!)

Because `aios/vault` is an NTFS junction (symbolic directory link) pointing to your real Obsidian vault:
1. **Never commit `vault/`**: `aios/.gitignore` ignores `vault/`. Committing it would suck your entire personal vault into GitHub.
2. **Always exclude `vault/` in recursive commands**: Any recursive command (like `Get-ChildItem -Recurse`, `ripgrep`, or code search tools) run inside `aios` will traverse through the junction into your vault unless explicitly excluded:
   ```powershell
   # Correct recursive scan:
   Get-ChildItem -Path . -Recurse -Exclude "vault","node_modules",".git",".claude"
   ```
3. **Link, not a copy**: Editing a file under `aios/vault/` directly modifies the original file in `moevault`.

---

## 3. Naming Conventions

- **Directories & Files**: All lowercase kebab-case (e.g. `check-health.ps1`, `user-moe-profile.md`).
- **Dates**: Always ISO 8601 `YYYY-MM-DD` (e.g. `2026-09-18-environment-bootstrap.md`).
- **Scripts**:
  - `execution/recon/Recon-*.ps1` (read-only discovery)
  - `execution/check/Check-*.ps1` (read-only health verification)
  - `execution/maint/Maint-*.ps1` (mutating changes, requires confirmation)
  - `execution/util/*.ps1` or `*.py` (parsers, sync tools)

---

## 4. Git Hygiene & Safety

- **Conventional Commits**: Format commit messages as `<type>: <description>`:
  - `feat`: new feature or capability
  - `fix`: bug fix or correction
  - `docs`: documentation or memory update
  - `chore`: maintenance, dependencies, scaffolding
- **Secret Scanning**: Staged files are scanned before pushing for accidental credential leaks.
- **Session End Push Rule**: At the end of every working session where files under `aios/` changed, commit and push to GitHub using `execution/util/Sync-Aios.ps1`.
