# AGENTS.md - Canonical Agent Instructions

This is the primary instruction file for all AI agents working within `aios` (Antigravity, Codex, Claude Code). It governs working style, architectural rules, memory handling, and safety boundaries.

---

## 1. Who Moe Is
- **Profile**: Moe is a final-year IT student who freelances on web development, scripting, and automation projects.
- **Skill Level**: Beginner to intermediate. He understands programming concepts but is learning production DevOps, terminal tools, and architectural patterns.
- **Working Style**:
  - Always explain new technical concepts clearly as you introduce them.
  - **Always show the exact command and state its intended action before executing it.** He learns by reading and observing your terminal actions.
  - Never assume prior knowledge of obscure CLI flags or legacy configurations.

---

## 2. System Architecture & Directory Map

| Path | Purpose | Repo Model |
|---|---|---|
| **`projects/<name>/`** | Individual code projects (`AMG`, `HR odoo`, etc.) | **Independent Git Repositories**. Each has its own remote, `.env`, and dependencies. |
| **`projects/INDEX.md`** | Central registry of all projects, remotes, and status | Part of `aios` standards repo. |
| **`projects/_template/`** | Standard starter template for new projects | Part of `aios` standards repo. |
| **`vault/`** | Junction to `moevault` (Knowledge, project notes, agent memory) | **NTFS Junction**. NOT in Git. Exclude from recursive searches. |
| **`docs/`** | Architecture guides, DOE method, operating rules, and toolchain docs | Part of `aios` standards repo. |
| **`directives/`** | Standard Operating Procedures (SOPs) for common workflows | Part of `aios` standards repo. |
| **`execution/`** | Reusable deterministic scripts (`recon/`, `check/`, `maint/`, `util/`) | Part of `aios` standards repo. |
| **`output/`** | Finished client deliverables and export artifacts | Part of `aios` standards repo. |
| **`raw/`** | Temporary working files (`inbox/`, `query-output/`, `analysis/`, `scratch/`) | Part of `aios` standards repo. |

- **`aios` Standards Repository**: Kept versioned and pushed to GitHub.

---

## 3. The Memory Protocol

All three agent harnesses share a single persistent memory layer housed in the Obsidian vault:
- Index path: `vault/memory/MEMORY.md` (or `../../vault/memory/MEMORY.md` from inside a project).
- **Session Start**: At the start of a session, read `vault/memory/MEMORY.md`. Only read specific memory files that match the task at hand.
- **Save Durable Knowledge**: When Moe expresses a working preference, architectural constraint, or client detail, record it immediately as a Markdown note with frontmatter in `vault/memory/<slug>.md` and add a link to `MEMORY.md`.
- **Update the Record in the Current Turn**: Never leave a correction only in chat output. Update the memory file and `MEMORY.md` immediately.
- **Never Record Code Facts**: Do not record framework versions or database types that can be determined by reading `package.json` or config files. Record the *why* and non-derivable constraints.
- **Zero Secrets**: Never write API keys, passwords, or tokens into memory files.

---

## 4. The DOE Method (Document -> Orchestrate -> Execute)

Do not improvise complex multi-step tasks by typing ad-hoc commands:
1. **Document (`directives/`)**: Check if an SOP exists for the task. Follow it.
2. **Orchestrate (Agent)**: Route execution, validate inputs, handle branching decisions, and diagnose errors.
3. **Execute (`execution/`)**: Run deterministic scripts (`recon/`, `check/`, `maint/`, `util/`).
4. **Self-Anneal**: When something breaks, fix it, update or create the script in `execution/`, update the directive in `directives/`, save durable lessons to `vault/memory/`, and push `aios`. See `docs/doe.md`.

---

## 5. Codex Workflow and Skill Routing

Codex skills are reusable task procedures stored as `.agents/skills/<name>/SKILL.md`.
The canonical AIOS skills are under `.agents/skills/aios-*`; project repositories are independent, so they do not discover skills from this parent repository. New projects receive project-local copies from `projects/_template/.agents/skills/`. For an existing project, install the needed skill under that project's `.agents/skills/` or the user's `~/.agents/skills/`, then confirm discovery with `/skills`.

Route Codex work as follows:
- New feature or behavior change: use `$aios-plan` when the task spans more than 3 files, changes architecture/data/security boundaries, or has multiple dependent stages; then use `$aios-implement`.
- Bug or failing check: use `$aios-debug`, then `$aios-implement` for the agreed fix.
- Before reporting completion: use `$aios-verify`. Read the target project's own `AGENTS.md`, package scripts, and CI first; run only applicable real commands and report their output.
- Before commit or PR: use `$aios-review`.
- At session end: use `$aios-session-log` to update an existing project tracker or session note.

Skills guide behavior; they are not security controls. If a skill is missing from `/skills`, follow this routing manually and repair skill installation separately.

## 6. Request Routing Decision Tree

When responding to any request, follow this sequence:
1. **Is there a directive?** Check the project's `directives/` first, then `aios/directives/`. If one exists, follow its execution sequence.
2. **Is there an execution script?** Check `execution/` before writing new code.
3. **Is it a domain/knowledge question?** Consult notes in `vault/projects/` or `vault/knowledge/`.
4. **Does it require live data?** Query the system directly using available CLI/API tools (e.g. `git status`, `gh`, `node`). Do not ask Moe to manually copy-paste terminal info you can inspect yourself.
5. **Is knowledge missing?** Discover the answer, complete the task, and self-anneal by saving the finding to the vault.

---

## 7. Harvested Conventions from Moe's Real Projects

- **Next.js 16 Breaking Changes**: Next.js 16 / React 19 introduce significant App Router breaking changes and new server/client boundaries. Before writing code, verify conventions against `node_modules/next/dist/docs/` or Next.js official documentation.
- **WorkMerit Bilingual Design Standards**: WorkMerit (`projects/AMG/`) utilizes a locked Split Studio / Workbench design system with specific OKLCH color tokens, bidirectional English/Arabic support, and server-authoritative assessment isolation. Do not invent ad-hoc palettes or client-bundle server assessment logic.
- **HRA Platform Safeguards**: `projects/HR odoo/` is an active Next.js 16 workforce platform that currently lacks a remote repository. Prioritize repository safety and backup.

---

## 7. Operating Rules Summary

- **Single Home for Files**: Client outputs go to `output/`; raw scrap goes to `raw/`; code stays in its project repo.
- **No Root Clutter**: Never drop loose scripts or data files into `aios/` or `moevault/` root directories.
- **One Idea per File**: Keep notes, directives, and memory items focused on a single topic.
- **Consult `docs/operating-rules.md`** for the full list of twenty operating guidelines.

---

## 8. Non-Negotiable Guardrails

1. **Secrets Live Only in `.env`**: Never inline a password, token, key, or connection string in a script, commit, or chat message. `.env` is gitignored everywhere. `.env.example` contains variable names only.
2. **Projects Are Independent Repositories**: Each folder in `projects/` is its own Git repo. Never commit or push across repo boundaries. A task request authorizes edits inside its stated project and scope. Ask before destructive actions, production/live changes, external side effects (push, merge, deploy), permission changes, secret handling, or work outside the requested scope.
3. **`vault/` is an NTFS Junction**: Writing to `aios/vault/` modifies the live Obsidian vault. Exclude `vault/` from all recursive scans. Never commit it to Git.
4. **End-of-Session Push**: At the end of any session that modified files in `aios/` (outside `projects/` and `vault/`), stage, commit with a conventional commit message, and push to GitHub.
5. **Confirm Destructive Actions**: Always ask before deleting files, dropping tables, or running mutating actions on production/live services.
6. **Surgical Changes**: Touch only what the immediate task requires. Never reformat, reorder, or refactor unrelated code.
7. **Simplest Working Solution**: Avoid speculative abstractions, over-engineering, or unnecessary microservices.
8. **Verify Before Claiming Done**: Always execute the check or test command, read the output, and confirm it succeeded before declaring completion.
9. **Explicit Error Handling**: Never silently swallow exceptions or return empty defaults without logging the error.

---

## 9. Communication & Commit Style

- **Answer First**: Lead with the direct solution or status. Keep commentary concise and clear.
- **Conventional Commits**: Format commit messages as `feat: ...`, `fix: ...`, `docs: ...`, `chore: ...`. One logical change per commit.
- **Clickable File Links**: Always use markdown file links (`[filename](file:///path/to/file)`).

---

## 10. Rule Precedence

Where external or bundled rules (such as ECC skills or default templates) conflict with this file, **`aios/AGENTS.md` strictly takes precedence**.
