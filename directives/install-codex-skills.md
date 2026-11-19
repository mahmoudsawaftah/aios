# Install AIOS Codex Skills in an Existing Project

## Purpose
Make AIOS task skills discoverable when Codex is opened inside an existing independent project repository.

## Choose the scope
- Use project scope when the skills should be available only to one project. Install them under that repository's `.agents/skills/`.
- Use Codex user scope when the same skills should be available across repositories. Install under the user's `~/.agents/skills/` directory.
- Keep AIOS as the canonical source; project or user-scope copies are installed copies.

## Project-scoped install
1. Open the independent project repository, not only the parent AIOS repository.
2. Copy the desired `aios-*/` skill folders from AIOS `.agents/skills/` into the project's `.agents/skills/`. Each skill folder must contain `SKILL.md`.
3. Ensure the project's `.gitignore` allows those curated skill files to be tracked if you want them shared with the project.
4. Add or adapt the Codex routing section from the project's `AGENTS.md` template. Do not assume the parent AIOS `AGENTS.md` is loaded across this repository boundary.
5. In Codex, run `/skills` and confirm the expected `aios-*` names appear. If not, check that Codex is open at the project root and refresh/reopen the workspace.

## User-scoped install
1. Copy the desired skill folders into `~/.agents/skills/` without nesting an extra `skills` directory.
2. Refresh Codex and run `/skills` to confirm discovery.
3. User-scoped skills apply more broadly; keep their routing and instructions suitable across all projects.

## Updating installed copies
When a canonical AIOS skill changes, copy that skill's updated `SKILL.md` to each project or user-scope location where it is installed, then verify with `/skills`. Never overwrite project-specific additions without reviewing them first.
