# Welcome to Your AI Operating System (aios)

Hi Moe! This document is your starting guide. It explains how your new workspace works in plain English without confusing jargon.

---

## 1. The Big Picture: The Four Pieces

You now have an integrated, professional engineering environment composed of four pieces:

1. **Your Obsidian Vault (`moevault`)**:
   - Located at `Documents\moevault`.
   - This is the "brain" of your setup. It holds your personal study notes, freelance client requirements, and shared AI memory.
2. **The Standards Layer (`aios`)**:
   - Located at `Documents\aios`.
   - This contains your rules, documentation, reusable scripts, and operating guidelines. It is backed up to GitHub so you can never lose your setup.
3. **Your Projects (`aios/projects/`)**:
   - Each project (like `AMG` and `HR odoo`) is its own self-contained Git repository.
   - They live in `aios/projects/` for easy access, but their code is independent of the `aios` repo.
4. **The ECC Skill Library**:
   - Over 290 agent skills installed directly inside `aios`.
   - When an AI agent assists you, it uses these skills to write higher-quality TypeScript, React, Next.js, and SQL.

---

## 2. How Shared Memory Works

Previously, every time you switched between **Antigravity**, **Codex**, or **Claude Code**, the agent had forgotten everything you taught it in the previous chat.

Now, all three agents share a single memory system:
- It lives in your Obsidian vault under `moevault/memory/`.
- Inside `aios`, it is reached through `aios/vault/memory/MEMORY.md`.
- Every memory is a plain Markdown file you can open, read, edit, or delete in Obsidian at any time.

Whenever an agent learns a preference (e.g., *"always show commands before running them"*), it saves a note in `memory/`. In future sessions, any of the three agents will automatically read that note.

---

## 3. How to Start a New Project

Starting a new project the right way takes only 60 seconds:
1. Copy the starter template:
   ```powershell
   Copy-Item -Recurse "aios/projects/_template" "aios/projects/my-new-app"
   ```
2. Open terminal in the new folder and connect GitHub:
   ```powershell
   cd aios/projects/my-new-app
   git init
   gh repo create my-new-app --private --source=. --remote=origin --push
   ```
3. Add a row to `aios/projects/INDEX.md` describing what the project is.
4. Create a vault note in Obsidian at `projects/my-new-app.md` noting the client or purpose.

---

## 4. The Three Habits That Matter

If you only remember three things, remember these:

1. **Push `aios` when you change standards**:
   Whenever you add a directive, script, or change documentation, run:
   ```powershell
   powershell -File execution/util/Sync-Aios.ps1 -Message "docs: update operating guidelines"
   ```
2. **Teach the agents your habits**:
   Whenever an agent does something you dislike or makes a mistake, don't just fix it in chat — say: *"Save that correction as a memory note."* After 10 saved corrections, the environment will feel like it was tailor-made for you.
3. **Do the 10-minute Friday check**:
   Every Friday, run the health check:
   ```powershell
   powershell -File execution/check/Check-AiosHealth.ps1
   ```
   It will alert you if any project is missing a remote, if you have unpushed code, or if any `.env` file is accidentally exposed.
