# Agent Memory Protocol

This document defines the unified long-term memory system shared across **Antigravity**, **Codex**, and **Claude Code**.

## 1. Physical Architecture

All persistent memory lives inside Moe's Obsidian vault (`moevault`) under the `memory/` folder.
To make it accessible to every agent working inside `aios`:
- An NTFS junction at `aios/vault` links directly to `moevault`.
- Relative path from `aios` root: `vault/memory/MEMORY.md`.
- External projects configure an explicit memory location; there is no universal relative path. If memory is unavailable, report it and continue using repository guidance. Do not create or alter external vault data without authorization.
- Harness-specific memory locations are optional local configuration, never a shared user-specific path requirement.

> **Critical Rule**: The junction means editing `aios/vault/...` directly edits the real Obsidian vault. Never commit `vault/` to Git. Always exclude `vault/` from recursive file searches.

---

## 2. Memory Format: One File, One Fact

Every memory note is saved as a discrete markdown file with YAML frontmatter:

```markdown
---
name: short-kebab-case-slug
description: One-line summary scanned by agents to determine relevance
metadata:
  type: user | feedback | project | reference
---

The fact, stated plainly and factually.

**Why:** Rationale or background context.
**How to apply:** Clear instruction for agent behavior.

Related notes: [[another-memory-slug]].
```

### Memory Types
- **`user`**: Who Moe is: role, experience level, tools, preferences.
  - *Example*: Final-year IT student; explain new concepts clearly, do not assume prior knowledge.
- **`feedback`**: Corrections and confirmed working habits with rationale.
  - *Example*: Show terminal commands before executing them — he is learning by reading.
- **`project`**: Ongoing goals, client constraints, and non-obvious requirements not derivable from code.
  - *Example*: Client site hosted on shared server with PHP 7.4 and no SSH/composer access.
- **`reference`**: Pointers to external repositories, dashboards, portals, and registries.
  - *Example*: GitHub repo URLs, ECC framework install status.

---

## 3. The Memory Index: `MEMORY.md`

`vault/memory/MEMORY.md` is the index loaded at the start of every agent session.
It contains only 4 headings and clean markdown links with one-line descriptions. It **never** contains raw memory content:

```markdown
# Memory

## Who Moe is
- [Beginner, final year IT](user-moe-profile.md) - explain concepts, don't assume prior knowledge

## How to work with him
- [Show commands before running](feedback-show-commands-first.md) - he is learning by reading

## Projects
- [Example product constraints](project-example.md) - owner-approved requirements for this product only

## Reference
- [Obsidian vault location](reference-vault-location.md) - reachable at aios/vault, shared across Antigravity, Codex, Claude
- [aios standards repository](reference-aios-repo.md) - control layer, publication requires owner authorization
- [ECC skills under aios](reference-ecc-installed.md) - 292 skills, run doctor to verify
```

---

## 4. The Six Rules Every Agent Must Follow

1. **Read `vault/memory/MEMORY.md` at session start.** Then read only the specific memory notes relevant to the user's prompt. Do not blindly read all notes.
2. **Record durable facts immediately within authorized scope.** External vault writes require authorization; if unavailable, record the constraint and limitation in the repository task report.
3. **Do not record what code already shows.** Never write "this project uses React" or "the database is Postgres" if `package.json` or `docker-compose.yml` already says so. Record *why* choices were made and non-derivable constraints.
4. **Update existing files instead of duplicating.** Check `MEMORY.md` before creating a new note. Mark stale memories as superseded; deletion requires owner approval.
5. **Fix the record in the same turn as discovery.** Never leave a correction only in chat output. Update the memory file and `MEMORY.md` in the current turn so future sessions do not repeat the mistake.
6. **Never write credentials or secrets.** Passwords, tokens, API keys, and connection strings live solely in `.env`.

---

## 5. Bidirectional Project Linking

Every project repo and its vault note link to each other:
- A configured project note links to the external product root and its Git remote.
- The product README may link to its explicitly configured note; never assume AIOS or vault directory placement.
