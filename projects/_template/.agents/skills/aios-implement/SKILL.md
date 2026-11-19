---
name: aios-implement
description: Use when the user has asked Codex to implement or change code, tests, configuration, or documentation in a project. Do not use for review-only or planning-only requests.
---
1. Read the project instructions and relevant files; inspect current Git state before editing.
2. Follow an existing plan when one applies. Keep the change limited to the requested outcome.
3. Match local patterns and framework versions; check primary documentation when behavior is version-sensitive.
4. Add or update focused tests when appropriate and safe. Never invent successful results.
5. Do not perform push, merge, deploy, destructive production actions, or permission changes without explicit authorization.
6. Summarize changed areas and remaining risks; use `$aios-verify` before claiming completion.
