# Harvest Map: Provenance of Standards & Configurations

This document traces every standard, rule, environment variable, and script seeded into `aios` back to its original source file in Moe's existing projects.

## Provenance Table

| Source File in `aios/projects/` | What Was Harvested | Where It Landed in `aios` / `moevault` |
|---|---|---|
| `AMG/.env.example` | Variable names: `SITE_URL`, `PAYMENT_MODE`, `SETTLEMENT_ACTIVATION_ALLOWED`, `PAYMENT_ADMIN_TOKEN`, `SHKEEPER_BASE_URL`, `SHKEEPER_API_KEY` | Root `aios/.env.example`, `docs/conventions.md` |
| `AMG/package.json` | Tooling choices (Next.js 16, React 19, Tailwind CSS 4, Drizzle ORM, Wrangler, Cloudflare deployment) & verification workflows | `docs/toolchain.md`, `vault/knowledge/nextjs-tailwind-cloudflare.md`, `directives/nextjs-verification.md` |
| `AMG/README.md` & `AMG/design.md` | Bilingual English/Arabic UI requirements, Split Studio and Workbench visual hierarchy, server-authoritative assessment architecture | `vault/projects/AMG.md`, `vault/memory/project-amg-workmerit.md`, `docs/doe.md` |
| `HR odoo/package.json` | Stack versions (`hra-platform`, Next.js 16.3.5, React 19.2.8, Tailwind 4) | `vault/projects/HR odoo.md`, `vault/memory/project-hr-odoo.md`, `docs/toolchain.md` |
| `HR odoo/AGENTS.md` | Next.js 16 breaking changes warning, app router file conventions, checking `node_modules/next/dist/docs/` | `aios/AGENTS.md` (Section 6 & 8 guardrails) |
| `HR odoo/CLAUDE.md` | Pointer pattern `@AGENTS.md` | `aios/CLAUDE.md`, `projects/_template/CLAUDE.md`, `projects/_template/GEMINI.md` |
| System Discovery (Section 0) | User profile, learning goals, Node v24, Git v2.54, GitHub user `QARESA` | `vault/memory/user-moe-profile.md`, `vault/memory/feedback-show-commands-first.md`, `aios/AGENTS.md` |

## Ground Rules Followed
1. **Read-only**: All source project files were inspected without any modification or deletion.
2. **Deduplication**: Repeated conventions across Next.js projects were unified into a single root standard.
3. **No secrets**: Only variable names were captured; zero secret values or credentials exist anywhere in standards or documentation.
