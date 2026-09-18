# Toolchain & Skills Reference

This document tracks all developer tools, runtimes, package managers, and agent skills configured across `aios`.

---

## 1. System Runtimes & CLIs

| Tool | Installed Version | Purpose | Verification Command |
|---|---|---|---|
| **Node.js** | `v24.16.0` | JavaScript/TypeScript runtime for Next.js and scripts | `node -v` |
| **npm** | `11.13.0` | Node package manager | `npm -v` |
| **Git** | `2.54.0.windows.1` | Distributed version control | `git --version` |
| **GitHub CLI (`gh`)** | Installed (Account: `QARESA`) | GitHub repository management, auth, and PRs | `gh auth status` |
| **ECC Universal** | `2.2.1` | Multi-harness agent skills, agents, and rules framework | `npx -y ecc-universal@2.2.1 doctor` |

---

## 2. ECC Framework (Everything Claude Code)

ECC provides **292 skills, 68 agents, and 94 commands** designed for full-stack development.
It is installed project-scoped under `aios` so that your global user configuration remains clean and reproducible.

### Scoped Installation Paths
- **Claude Code**: `./.claude/skills/` and `./.claude/agents/`
- **Antigravity**: `./.agents/skills/` and `./.agents/rules/`
- **Git status**: Both `.claude/skills/` and `.claude/agents/` are **gitignored** in `aios/.gitignore`. They are generated artifacts easily restored from a single command.

### Rebuild & Health Commands
- Check installation health:
  ```powershell
  npx -y ecc-universal@2.2.1 doctor
  ```
- Repair any missing or drifted skill files:
  ```powershell
  npx -y ecc-universal@2.2.1 repair
  ```
- Re-run full project install:
  ```powershell
  npx -y ecc-universal@2.2.1 install --profile full --target claude-project --enable-hooks
  npx -y ecc-universal@2.2.1 install --profile full --target antigravity
  ```

---

## 3. Ten Essential ECC Skills for Moe

With 292 skills available, browsing the catalogue is overwhelming. Here are the 10 most relevant skills for your real projects (**Next.js**, **WorkMerit**, **HRA Platform**, **Cloudflare**):

1. **`nextjs-app-router`**: Best practices for Next.js Server Components, client boundaries, metadata, and dynamic routing.
2. **`typescript-strict`**: Enforces strict typing, eliminates `any` types, and handles async inference safely.
3. **`tailwind-v4-tokens`**: Working with modern Tailwind CSS v4 design tokens, CSS variables, and fluid typography without legacy config.
4. **`drizzle-orm-migrations`**: Schema definitions, Drizzle migrations, relational queries, and safe schema rollbacks.
5. **`cloudflare-wrangler-deploy`**: Configuring `wrangler.json`, Cloudflare Workers bindings, and secrets management.
6. **`security-secrets-guard`**: Automated checks to detect exposed `.env` credentials, API tokens, and private keys.
7. **`api-endpoint-design`**: Standardized HTTP status codes, request body validation with Zod, and clear error responses.
8. **`git-conventional-commits`**: Formatting clean, atomic Git commits and managing release tags.
9. **`auth-session-management`**: Secure cookies, CSRF protection, and role-based access control (RBAC) patterns.
10. **`continuous-learning-v2`**: How agents extract durable lessons from mistakes and persist them into vault memory.
