---
name: item-space-implement
description: Use when the user asks Codex to implement an in-scope Item Space code, test, or documentation change.
---
1. Inspect the relevant files and Git status; preserve unrelated changes.
2. Follow the approved plan and project patterns. Keep the diff focused.
3. Check version-sensitive behavior against primary documentation.
4. Add focused tests when appropriate; use existing commands and test data.
5. Do not commit, push, merge, deploy, or change production data unless specifically authorized.
6. Summarize changes and run `$item-space-verify` before saying the task is complete.
