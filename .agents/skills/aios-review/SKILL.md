---
name: aios-review
description: Use before committing, opening a pull request, or when the user asks for an independent code review. Look for correctness, security, regressions, and missing tests; do not implement fixes unless asked.
---
1. Read project instructions and inspect the full diff, not just the summary.
2. Prioritize concrete findings: bugs, security issues, data loss, compatibility problems, and missing coverage.
3. Cite each finding with file and line; state severity and the triggering scenario.
4. If no findings are found, say so and mention any areas that could not be checked.
5. Do not change files during review unless the user also requested fixes.
